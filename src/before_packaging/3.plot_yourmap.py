import geopandas as gpd
import pandas as pd
import numpy as np
from plotly import graph_objects as go
from plotly import express as px
from shapely import wkt
import chart_studio
import chart_studio.plotly as py
from shapely.geometry import Point
from datetime import datetime

if __name__ == "__main__":

    # 1. data setup
    mon = str(datetime.today().month).zfill(2)
    day = str(datetime.today().day).zfill(2)
    api_id = 'niceguy1575'
    api_key = ''

    # 2. to gdf
    people = pd.read_csv("../result/people_with_area.txt", sep = "|")
    people['grp_rn'] = people.groupby(['sgg_cd']).cumcount() + 1
    people_xy = gpd.GeoDataFrame(people, geometry = [Point(x,y) for x,y in zip(people.x, people.y)], crs = 4326)
    people_xy = people_xy.to_crs(epsg = 5179)

    # 3. jittering
    # random number concept
    # 1. 무수히 많은 random number generation
    # 2. 이 중 가로/세로 거리가 250m 이상인 점들만을 도출
    n = people.shape[0]
    cnt = 9999
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
    people_xy['x_utmk'] = people_xy.geometry.x + width_rn * width_idx
    people_xy['y_utmk'] = people_xy.geometry.y + height_rn * height_idx

    people_xy_moving = gpd.GeoDataFrame(people_xy[['people_nm','mega_nm', 'sgg_nm', 'mega_cd', 'sgg_cd', 'x_utmk', 'y_utmk']],
                                geometry = [Point(x,y) for x,y in zip(people_xy.x_utmk, people_xy.y_utmk)],crs = 5179)
    people_xy_moving = people_xy_moving.to_crs(epsg = 4326)
    people_xy_moving['lon'] = people_xy_moving.geometry.x
    people_xy_moving['lat'] = people_xy_moving.geometry.y

    # 4. color data frame
    color_df = pd.DataFrame({'sgg_nm':pd.unique(people_xy_moving.sgg_nm)})
    color_df['color'] = color_df.index
    people_xy_moving_color = pd.merge(people_xy_moving, color_df, on = 'sgg_nm', how = 'left')

    lon_mean = people_xy_moving.lon.mean() 
    lat_mean = people_xy_moving.lat.mean()
    people_xy_moving_color['size'] = 4
    fig = px.scatter_mapbox(
                            people_xy_moving_color, lat = 'lat', lon = 'lon',
                            hover_name = 'people_nm',
                            zoom = 9, center = {"lat": lat_mean, "lon": lon_mean},
                            size = 'size', size_max = 8,
                            color_continuous_scale=px.colors.sequential.Rainbow,
                            color = 'color', labels = {},
                            mapbox_style = 'carto-darkmatter'
                            )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_showscale=False)
    fig.show()

    # 5. chart-studio
    # chart-studio
    # API ID: niceguy1575
    # API PW: ca9QST3zpIW8HPGxoi16
    chart_layer = 'yourmap_ver_openmate_' + mon + day
    chart_studio.tools.set_credentials_file(username = api_id, api_key = api_key)
    chart = py.plot(fig, filename = chart_layer, auto_open = False, fileopt = 'overwrite', sharing = 'public')