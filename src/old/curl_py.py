import requests
import json
import pandas as pd
import numpy as np
import re
import os

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
    url = 'https://api.notion.com/v1/databases/29000bbca3e843b9854bf7eb75080efb/query'
    header = {
    #    "Notion-Version": "2021-05-13",
        "Authorization": "Bearer secret_pPWC3kHqaPaHTHaAANpHa1RXVzv8Z5akflOyJZX7mQi",
        "Content-Type": "application/json"
    }

    result_json = postUrl(url, headers = header)
    data = json.loads(result_json.content)

    sgg_list = [sgg_list['properties']['sgg'] for sgg_list in data['results']]
    sgg_nm = [sgg['select']['name'] for sgg in sgg_list]

    mega_list = [mega_list['properties']['mega'] for mega_list in data['results']]
    mega_nm = [mega['select']['name'] for mega in mega_list]

    result_df = pd.DataFrame({"mega_nm": mega_nm, "sgg_nm": sgg_nm})
