import geopandas as gpd
import pandas as pd
import numpy as np
from plotly import graph_objects as go
from plotly import express as px
from shapely import wkt
import json
import chart_studio
import chart_studio.plotly as py

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

fig = px.scatter_mapbox(res,lat = 'lat',lon = 'lon',hover_name = 'sgg_nm',mapbox_style = 'open-street-map')
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

# chart-studio
# API ID: niceguy1575
# API PW: ca9QST3zpIW8HPGxoi16
chart_studio.tools.set_credentials_file(username='niceguy1575', api_key='ca9QST3zpIW8HPGxoi16')
chart = py.plot(fig, filename = 'sgg_test_0609', auto_open = False, fileopt = 'overwrite', sharing = 'public')
