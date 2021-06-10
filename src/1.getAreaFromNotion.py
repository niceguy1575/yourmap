import geopandas as gpd
import pandas as pd
import requests
import re
import json
from shapely import wkt

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

if __name__ == "__main__":
    # 1. 사전에 notion에서 사전에 페이지 획득 필요!
    url = 'https://api.notion.com/v1/databases/b8e198c5c45149bca0a64cca996c7a37/query'
    header = {
    #    "Notion-Version": "2021-05-13",
        "Authorization": "Bearer secret_pPWC3kHqaPaHTHaAANpHa1RXVzv8Z5akflOyJZX7mQi",
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

    # 4. 개인정보의 문제로 특정 노션 페이지에서 가져와 작업할 수 있도록 동작시킴
    # 시군구 매핑
    mega_data = pd.read_csv("../result/mega.txt", sep = "|")
    sgg_data = pd.read_csv("../result/sgg_bind.txt", sep = "|")

    sgg_data['wkt'] = sgg_data.geometry.apply(wkt.loads)
    sgg_gdf = gpd.GeoDataFrame(sgg_data, geometry = 'wkt')
    sgg_gdf = sgg_gdf.set_crs(epsg = 5179)
    sgg_gdf = sgg_gdf.to_crs(epsg = 4326)
    sgg_gdf['x'] = sgg_gdf.wkt.centroid.x
    sgg_gdf['y'] = sgg_gdf.wkt.centroid.y

    sgg_gdf['mega_cd'] = sgg_gdf['sgg_cd'].astype(str).str[:2]
    mega_data['mega_cd'] = mega_data['mega_cd'].astype(str)
    sgg_join = pd.merge(sgg_gdf, mega_data, on = 'mega_cd', how = 'left')
    sgg_select = sgg_join[['mega_cd', 'sgg_cd', 'mega_nm', 'sgg_nm', 'x', 'y']].copy()

    # 시군구 보정
    sgg_select.loc[sgg_select.sgg_nm=='안양시만안구','sgg_nm']='안양시 만안구'
    sgg_select.loc[sgg_select.sgg_nm=='안양시동안구','sgg_nm']='안양시 동안구'
    sgg_select.loc[sgg_select.sgg_nm=='안산시상록구','sgg_nm']='안산시 상록구'
    sgg_select.loc[sgg_select.sgg_nm=='안산시상록구','sgg_nm']='안산시 상록구'
    sgg_select.loc[sgg_select.sgg_nm=='안산시단원구','sgg_nm']='안산시 단원구'
    sgg_select.loc[sgg_select.sgg_nm=='고양시덕양구','sgg_nm']='고양시 덕양구'
    sgg_select.loc[sgg_select.sgg_nm=='고양시일산동구','sgg_nm']='고양시 일산동구'
    sgg_select.loc[sgg_select.sgg_nm=='고양시일산서구','sgg_nm']='고양시 일산서구'
    sgg_select.loc[sgg_select.sgg_nm=='용인시처인구','sgg_nm']='용인시 처인구'
    sgg_select.loc[sgg_select.sgg_nm=='용인시기흥구','sgg_nm']='용인시 기흥구'
    sgg_select.loc[sgg_select.sgg_nm=='용인시수지구','sgg_nm']='용인시 수지구'

    area_with_crd = pd.merge(area_nm_df, sgg_select, on = ['mega_nm', 'sgg_nm'])
    area_with_crd.to_csv("../result/people_with_area.txt", sep = "|")