import pandas as pd
import geopandas as gpd
from shapely import wkt
from pyproj import Proj
from pyproj import transform
import re
import os
import numpy as np
import time

#main definition
if __name__ == "__main__":

    emd_path = "/Users/jongwon/git/yourmap/data/shp/target/emd/"
    sgg_path = "/Users/jongwon/git/yourmap/data/shp/target/sgg/"
    save_path = "/Users/jongwon/git/yourmap/result/"

    emd_files = os.listdir(emd_path)
    sgg_files = os.listdir(sgg_path)

    emd_files = [f for f in emd_files if re.search(".shp$", f)]
    sgg_files = [f for f in sgg_files if re.search(".shp$", f)]

    # 1. do emd bind
    emd_result = gpd.GeoDataFrame()
    for file in emd_files:
        print("emd "+ file)
        data = gpd.read_file(emd_path + file, encoding = 'euc-kr')
        data = data[['EMD_CD', 'EMD_KOR_NM', 'geometry']]
        data.columns = ['emd_cd','emd_nm','geometry']
        emd_result = pd.concat([emd_result,data], axis = 0)
        
    emd_layer = save_path + "emd_bind.txt"
    emd_result.to_csv(emd_layer, sep = "|", index = False)

    # 2. do sgg bind
    sgg_result = gpd.GeoDataFrame()
    for file in sgg_files:
        print("sgg "+ file)
        data = gpd.read_file(sgg_path + file, encoding = 'euc-kr')
        data = data[['SIG_CD', 'SIG_KOR_NM', 'geometry']]
        data.columns = ['sgg_cd','sgg_nm','geometry']

        sgg_result = pd.concat([sgg_result,data], axis = 0)
        
    sgg_layer = save_path + "sgg_bind.txt"
    sgg_result.to_csv(sgg_layer, sep = "|", index = False)