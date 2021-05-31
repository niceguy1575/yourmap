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
gdf2.to_file("/Users/jongwon/git/yourmap/result/sgg_json", driver = "GeoJSON")

with open("/Users/jongwon/git/yourmap/result/sgg_json") as geofile:
    j_file = json.load(geofile)

i=0
for feature in j_file["features"]:
    feature['id'] = gdf2.iloc[i:i+1].sgg_cd.to_list()[0]
    i += 1


# figure
gdf2['col'] = gdf2.index
gdf_data = gdf2[['sgg_cd', 'sgg_nm','col']].copy()

# help
#https://plotly.github.io/plotly.py-docs/generated/plotly.express.choropleth_mapbox.html
fig = px.choropleth_mapbox(gdf_data, geojson=j_file, locations='sgg_cd', color='col',
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           mapbox_style="carto-positron",
                           zoom=7, center = {"lat": 37, "lon": 126.5},
                           opacity=0.5,
                           hover_name = 'sgg_nm'
                          )
fig.show()


# chart-studio
# API ID: niceguy1575
# API PW: ca9QST3zpIW8HPGxoi16
chart_studio.tools.set_credentials_file(username='niceguy1575', api_key='ca9QST3zpIW8HPGxoi16')
chart = py.plot(fig, filename = 'sgg_test', auto_open = False, fileopt = 'overwrite', sharing = 'public')
