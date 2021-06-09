import geopandas as gpd
import pandas as pd
import numpy as np
from plotly import graph_objects as go
from plotly import express as px
from shapely import wkt
import json
import chart_studio
import chart_studio.plotly as py
from shapely.geometry import Point


# data setup
data = pd.read_csv("/Users/jongwon/git/yourmap/result/sgg_bind.txt", sep = "|")
data['wkt'] = data.geometry.apply(wkt.loads)

gdf = gpd.GeoDataFrame(data, geometry = 'wkt')
gdf['ptr_wkt'] = gdf.centroid

gdf2 = gdf[['sgg_cd', 'sgg_nm','ptr_wkt']].copy()
gdf2 = gpd.GeoDataFrame(gdf2, geometry = 'ptr_wkt')
gdf2 = gdf2.set_crs(epsg = 5179)
gdf2 = gdf2.to_crs(epsg = 4326)

# json processing
res = gdf2.copy()
res['lon'] = res.geometry.x
res['lat'] = res.geometry.y

config = dict({
    'scrollZoom': True,
    'displayModeBar': True,
    'editable': True
})

fig = px.scatter_mapbox(res,lat = 'lat',lon = 'lon',hover_name = 'sgg_nm',mapbox_style = 'open-street-map')
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show(config=config)

# chart-studio
# API ID: niceguy1575
# API PW: ca9QST3zpIW8HPGxoi16
chart_studio.tools.set_credentials_file(username='niceguy1575', api_key='ca9QST3zpIW8HPGxoi16')
chart = py.plot(fig, filename = 'sgg_test_0609', auto_open = False, fileopt = 'overwrite', sharing = 'public')


################ 중복 데이터 jittering ################
# sample data 구축
k = 10
a = res.iloc[1:k].copy()
b = res.iloc[1:k].copy()
c = res.iloc[1:k].copy()
d = res.iloc[1:k].copy()

e = pd.concat([a,b,c,d], axis = 0)

# utmk 좌표계 변환
e2 = e.to_crs(epsg = 5179)
e2['grp_rn'] = e2.groupby(['sgg_nm']).cumcount() + 1

# random number concept
# 1. 무수히 많은 random number generation
# 2. 이 중 가로/세로 거리가 250m 이상인 점들만을 도출
n = e2.shape[0]
cnt = 99999
width_m = 500
height_m = 500
threshold = 250

np.random.seed(1575)
rn = np.random.rand(cnt)
rn = rn[rn * width_m > threshold][:n] 
width_rn = rn * width_m

rn = np.random.rand(cnt)
rn = rn[rn * height_m > threshold][:n]
height_rn = rn * height_m

width_idx = np.where(np.random.rand(n) < 0.5, -1, 1)
height_idx = np.where(np.random.rand(n) < 0.5, -1, 1)

# 이동한 좌표 기준으로 gdf 재생산
e2['x_utmk'] = e2.ptr_wkt.x + width_rn * width_idx
e2['y_utmk'] = e2.ptr_wkt.y + height_rn * height_idx

e2_res = gpd.GeoDataFrame(e2[['sgg_nm', 'x_utmk', 'y_utmk']],geometry = [Point(x,y) for x,y in zip(e2.x_utmk,e2.y_utmk)],crs = 5179)
e2_res = e2_res.to_crs(epsg = 4326)

e2_res['lon'] = e2_res.geometry.x
e2_res['lat'] = e2_res.geometry.y

fig = px.scatter_mapbox(e2_res,lat = 'lat',lon = 'lon',hover_name = 'sgg_nm',mapbox_style = 'open-street-map')
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
