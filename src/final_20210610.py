import geopandas as gpd
import pandas as pd
import numpy as np
import re
from plotly import graph_objects as go
from plotly import express as px
from shapely import wkt
from glob import glob
import json
import chart_studio
import chart_studio.plotly as py
from shapely.geometry import Point
from plotly.offline import plot


# data setup



class notion_map:
	def __init__(self,people,shp):
		self.shp = gpd.read_file(shp)
		self.people = pd.read_csv(people)



	def get_centroid (self):
		self.people = self.people[self.people.columns[:3]].dropna()
		megas = self.people.시도명.apply(lambda x: x.replace(" ",""))
		sggs= self.people.시군구명.apply(lambda x: x.replace(" ",''))
		self.megas = megas
		self.sggs = sggs
		centroid = [self.shp[((self.shp.MEGA_NM.apply(lambda x: re.search(mega,x)).isna()==False)&(self.shp.SIG_KOR_NM.apply(lambda x: re.search(sgg,x)).isna()==False))].centroid.tolist()[0] for mega,sgg in zip(megas,sggs)]
		self.people['centroid'] = centroid

		return self.people

	def __del__(self):
		print("clear attribution") 

class maps_upload(notion_map):
	def __init__(self,people,shp_path):
		super().__init__(people,shp_path)
		super().get_centroid()

	def visualization(self,user_name,api_key,filename,seed = 1575,cnt = 99999,width_m = 500,height_m = 500,threshold = 250):
		gdf = gpd.GeoDataFrame(self.people,geometry = self.people.centroid,crs = 5179)
		self.filename = filename
		# jitting 부분 (수정) <- 겹치는 경우가 2개이상일 경우는 고려되지 않았음 
		config = dict({
			'scrollZoom': True,
			'displayModeBar': True,
			'editable': True
		})
		chart_studio.tools.set_credentials_file(user_name,api_key)

		gdf['x'] = gdf.geometry.x
		gdf['y'] = gdf.geometry.y
		gdf['grp_rn'] = gdf.groupby(['x','y']).cumcount() + 1

		e2 = gdf.to_crs(epsg = 5179)

		# random number concept
		# 1. 무수히 많은 random number generation
		# 2. 이 중 가로/세로 거리가 250m 이상인 점들만을 도출
		n = e2.shape[0]

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
		e2['x_utmk'] = e2.geometry.x + width_rn * width_idx
		e2['y_utmk'] = e2.geometry.y + height_rn * height_idx

		e2_res = gpd.GeoDataFrame(e2[['Name', 'x_utmk', 'y_utmk']],geometry = [Point(x,y) for x,y in zip(e2.x_utmk,e2.y_utmk)],crs = 5179)
		e2_res = e2_res.to_crs(epsg = 4326)

		e2_res['lon'] = e2_res.geometry.x
		e2_res['lat'] = e2_res.geometry.y
		self.fig = px.scatter_mapbox(e2_res,lat = 'lat',lon = 'lon',hover_name = 'Name',mapbox_style = 'open-street-map')

		chart = py.plot(self.fig, filename = filename, auto_open = False, fileopt = 'overwrite', sharing = 'public')
		return e2_res

	def to_html(self):        
		plot(self.fig, filename=self.filename+'.html')
		return os.getcwd()+"/"+self.filename+'.html'


	
	
if __name__ == '__main__':
	# 초기 변수 입력
	shp = '/home/suyo1207/2021/notion/사내노션업데이트/SGG_ctr.shp' # 기존 source는 시도 정보가 누락되어있어 꼭 해당 shp을 이용해주시기 바랍니다.
	csv_file = "당신의 사는곳을 알려주세요 9572172efb494f81a1243b25bad749d8.csv" # csv파일명
	username='niceguy1575'
	api_key='ca9QST3zpIW8HPGxoi16'
	filename = 'sgg_test_0609'

	# 클래스 사용 
	maps = maps_upload(csv_file,shp)
	maps.visualization(username,api_key,filename,seed = 1874)
	

