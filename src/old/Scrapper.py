import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd

def getDownload(url, headers, param=None, retries=3):
    resp = None

    try:
        resp = requests.get(url, params=param, headers = headers)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if 500 <= resp.status_code < 600 and retries > 0:
            print('Retries : {0}'.format(retries))
            return getDownload(url, param, retries - 1)
        else:
            print(resp.status_code)
            print(resp.reason)
            print(resp.request.headers)
    return resp

# 최신화 수
naver_webtoon_url = 'https://comic.naver.com/webtoon/weekday.nhn'
naver_webtoon_main = requests.get(naver_webtoon_url)
naver_webtoon_dom = BeautifulSoup(naver_webtoon_main.text, 'lxml')
naver_webtoon_find = naver_webtoon_dom.find_all('div', {'class':'col_inner'})

day_top3 = []
for i in range(0, len(naver_webtoon_find)):
    found = naver_webtoon_find[i].find_all(recursive = True)[2].find_all('a', {'class':'title'})
    href_list = [f.get('href') for f in found]
    day_top3.extend(href_list[:3])

for episode in day_top3:
    #episode_url = "https://comic.naver.com/webtoon/list.nhn?titleId=710751&weekday=sun"
    episode_url = "https://comic.naver.com" + episode
    cookies = {'NNB' : 'ONOA4BJMECDFW'}
    headers = {'Referer': episode_url,
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}

    html = getDownload(episode_url, headers)
    dom = BeautifulSoup(html.text)
    toon_list = dom.find_all('table', {'class':'viewList'})
    toon_nm = dom.find_all('div', {'class':'detail'})
    toon_nm = toon_nm[0].find_all('h2')[0].text.strip()

    nm_compile = re.compile("^.*?\n")
    toon_nm = nm_compile.findall(toon_nm)[0][:-1]

    toon = toon_list[0]
    toon_re = toon.find_all(recursive=False)

    ts_to_string = ' '.join([t.text.strip() for t in toon_re])

    get_hwa = re.compile('[0-9]{1,3}화|[0-9]{1,4}\.')
    last_hwa = get_hwa.findall(ts_to_string)[0]
    last_hwa = last_hwa[:-1]
    comment_num = '30'
    n = int(last_hwa)+1
    print(toon_nm)

    episode_num_compile = re.compile('[0-9]')
    epi_num = episode_num_compile.findall(episode)
    epi_num = ''.join(epi_num)

    comment_df = pd.DataFrame({'만화_명': [],'회차': [], '댓글': []})

    add_num = 0
    cnt = 0
    h = 1
    while(h < n):
        hwa = str(h)
        print(hwa + ' is on scrapping.')

        src_url = 'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=comic&templateId=webtoon&pool=cbox3&lang=ko&country=KR&objectId=' + epi_num + '_' + hwa + '&categoryId=&pageSize=' + comment_num + '&indexSize=10&groupId=&listType=OBJECT&pageType=default&page=1&initialize=true&userType=&useAltSort=true&replyPageSize=10'
        # src_url = 'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=comic&templateId=webtoon&pool=cbox3&lang=ko&country=KR&objectId=703846_100&categoryId=&pageSize=30&indexSize=10&groupId=&listType=OBJECT&pageType=default&page=1&initialize=true&userType=&useAltSort=true&replyPageSize=10'
        toon_json = requests.get(src_url, headers=headers, cookies=cookies)

        start = re.compile('\(')
        text_compile = start.search(toon_json.text)

        end_idx = text_compile.end()
        except_tail = -2
        toon_json_txt = toon_json.text[end_idx:except_tail]
        toon_json_load = json.loads(toon_json_txt)

        toon_json_result = toon_json_load.get('result')
        toon_comment_list = toon_json_result.get('commentList')
        comment_list = [dict(t).get('contents') for t in toon_comment_list]

        anime_nm = [toon_nm] * len(comment_list)
        hwa_rep = [hwa] * len(comment_list)
        result = pd.DataFrame(zip(anime_nm, hwa_rep, comment_list), columns=['만화_명', '회차', '댓글'])

        comment_df = pd.concat([comment_df, result])

        if(cnt > 200):
            add_num += 1
            layer = './2020_NLP_STUDY/data/comment_' + toon_nm + '_comments_' + str(add_num) + '.csv'
            comment_df.to_csv(layer, encoding='utf-8-sig', index=False)
            comment_df = pd.DataFrame({'만화_명': [], '회차': [], '댓글': []})
            cnt = 0
        h += 1
        cnt += 1
    add_num += 1
    layer = './2020_NLP_STUDY/data/comment_' + toon_nm + '_comments_' + str(add_num) + '.csv'
    comment_df.to_csv(layer, encoding = 'utf-8-sig', index = False)
