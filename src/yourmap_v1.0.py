import geopandas as gpd
import pandas as pd
import numpy as np
import requests
import re
import os
import json
import chart_studio
import chart_studio.plotly as py
from datetime import datetime

from shapely.geometry import Point
from plotly.offline import plot
from plotly import graph_objects as go
from plotly import express as px
import pickle as pck


def postUrl(url, headers, param = None, retries=10):
    resp = None

    try:
        resp = requests.post(url, params = param, headers = headers)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if 500 <= resp.status_code < 600 and retries > 0:
            print('Retries : {0}'.format(retries))
            return postUrl(url, param, retries - 1)
        else:
            print(resp.status_code)
            print(resp.reason)
            print(resp.request.headers)
    return resp

# data setup

class notion_map: 
	def __init__(self,shp):
		self.shp = gpd.read_file(shp)

	def get_data(self, sites, key):
		# 1. 사전에 notion에서 사전에 페이지 획득 필요!
		url = 'https://api.notion.com/v1/databases/' + sites + '/query'
		header = {
    		"Notion-Version": "2021-05-13",
    		"Authorization": "Bearer " + key,
    		"Content-Type": "application/json"
		}

		result_json = postUrl(url, headers = header)
		data = json.loads(result_json.content)

		people_nm = [nm_list['properties']['Name']['title'][0]['text']['content'] for nm_list in data['results'] ]

		sgg_list = [sgg_list['properties']['시군구명'] for sgg_list in data['results']]
		sgg_nm = [sgg['select']['name'] for sgg in sgg_list]

		mega_list = [mega_list['properties']['시도명'] for mega_list in data['results']]
		mega_nm = [mega['select']['name'] for mega in mega_list]

		area_nm_df = pd.DataFrame({"people_nm": people_nm, "mega_nm": mega_nm, "sgg_nm": sgg_nm})

		self.people = area_nm_df

	def get_centroid (self):
		self.people = self.people[self.people.columns[:3]].dropna()
		megas = self.people.mega_nm.apply(lambda x: x.replace(" ",""))
		sggs= self.people.sgg_nm.apply(lambda x: x.replace(" ",''))
		self.megas = megas
		self.sggs = sggs
		centroid = [self.shp[((self.shp.MEGA_NM.apply(lambda x: re.search(mega,x)).isna()==False)&(self.shp.SIG_KOR_NM.apply(lambda x: re.search(sgg,x)).isna()==False))].centroid.tolist()[0] for mega,sgg in zip(megas,sggs)]
		self.people['centroid'] = centroid

		return self.people

	def __del__(self):
		print("clear attribution") 

		
		
class maps_upload(notion_map):
	def __init__(self,shp, sites, key):
		super().__init__(shp)
		super().get_data(sites, key)
		super().get_centroid()

	def visualization(self,api_id,api_key,seed = 1575,cnt = 99999,width_m = 1500,height_m = 1500,threshold = 750):
		# 2. to gdf

		people_xy = gpd.GeoDataFrame(self.people,geometry = self.people.centroid,crs = 5179)
		# jitting 부분 (수정) <- 겹치는 경우가 2개이상일 경우는 고려되지 않았음 
		config = dict({
			'scrollZoom': True,
			'displayModeBar': True,
			'editable': True
		})
		chart_studio.tools.set_credentials_file(api_id,api_key)

		people_xy['x'] = people_xy.geometry.x
		people_xy['y'] = people_xy.geometry.y
		people_xy['grp_rn'] = people_xy.groupby(['x','y']).cumcount() + 1

		people_xy = people_xy.to_crs(epsg = 5179)

		# random number concept
		# 1. 무수히 많은 random number generation
		# 2. 이 중 가로/세로 거리가 250m 이상인 점들만을 도출
		n = people_xy.shape[0]

		np.random.seed(seed)
		rn = np.random.rand(cnt)
		rn = rn[rn * width_m > threshold][:n] 
		width_rn = rn * width_m

		rn = np.random.rand(cnt)
		rn = rn[rn * height_m > threshold][:n]
		height_rn = rn * height_m

		width_idx = np.where(np.random.rand(n) < 0.5, -1, 1)
		height_idx = np.where(np.random.rand(n) < 0.5, -1, 1)

		# 이동한 좌표 기준으로 gdf 재생산
		people_xy['x_utmk'] = people_xy.geometry.x + width_rn * width_idx
		people_xy['y_utmk'] = people_xy.geometry.y + height_rn * height_idx

		people_xy_moving = gpd.GeoDataFrame(people_xy[['people_nm','mega_nm', 'sgg_nm', 'x_utmk', 'y_utmk']],
									geometry = [Point(x,y) for x,y in zip(people_xy.x_utmk, people_xy.y_utmk)],crs = 5179)
		people_xy_moving = people_xy_moving.to_crs(epsg = 4326)
		people_xy_moving['lon'] = people_xy_moving.geometry.x
		people_xy_moving['lat'] = people_xy_moving.geometry.y
		
		# set point color 
		color_df = pd.DataFrame({'sgg_nm':pd.unique(people_xy_moving.sgg_nm)})
		color_df['color'] = color_df.index
		people_xy_moving_color = pd.merge(people_xy_moving, color_df, on = 'sgg_nm', how = 'left')

		lon_mean = people_xy_moving.lon.mean() 
		lat_mean = people_xy_moving.lat.mean()
		people_xy_moving_color['size'] = 4
		# 최종 업로드 fig 설정 
		self.fig = px.scatter_mapbox(
						people_xy_moving_color[['people_nm','mega_nm','sgg_nm','size','color']], lat = people_xy_moving_color.lat, lon = people_xy_moving_color.lon,
						hover_name = 'people_nm',
						hover_data = ['mega_nm','sgg_nm'],
						title = 'In Yourmap',
						zoom = 10, center = {"lat": lat_mean, "lon": lon_mean},
						size = 'size', size_max = 8,
						color_continuous_scale=px.colors.sequential.Rainbow,
						color = 'color', labels = {},
						mapbox_style = 'carto-darkmatter'
						)
		self.fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},coloraxis_showscale=False)
		self.fig.show()
		return people_xy_moving_color

	def to_html(self,api_id,api_key):        
		# 업로드 날짜 지정 
		mon = str(datetime.today().month).zfill(2)
		day = str(datetime.today().day).zfill(2)
		# 해당 차트를 api에 업로드 
		chart_layer = 'yourmap_ver_openmate_' + mon + day
		chart_studio.tools.set_credentials_file(username = api_id, api_key = api_key)
		chart = py.plot(self.fig, filename = chart_layer, auto_open = False, fileopt = 'overwrite', sharing = 'public')
		# html형태로 현재의 위치에 저장
		plot(self.fig, filename=chart_layer+'.html')
		return os.getcwd()+"/"+chart_layer+'.html'

	
if __name__ == '__main__':
	# 초기 변수 입력
	shp = '../data/sgg/SGG_ctr.shp' # 기존 source는 시도 정보가 누락되어있어 꼭 해당 shp을 이용해주시기 바랍니다.
	dump_path = "../result/"

	with open(dump_path + "openmate_key_df.p", 'rb') as f:
		key_df = pck.load(f)

	your_sites = key_df['yourmap_sites'][0]
	yourmap_notion_api_key = key_df['yourmap_notion_api_key'][0]
	chart_studio_api_id = key_df['chart_studio_api_id'][0]
	chart_studio_api_key = key_df['chart_studio_api_key'][0]

	# 클래스 사용 
	maps = maps_upload(shp, your_sites, yourmap_notion_api_key)
	maps.visualization(chart_studio_api_id, chart_studio_api_key)
	maps.to_html(chart_studio_api_id, chart_studio_api_key)

