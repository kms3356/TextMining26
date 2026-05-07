import urllib.request
import json
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
naver_headers = {
    "X-Naver-Client-Id": client_id,
    "X-Naver-Client-Secret": client_secret
}

def crawlNaverNews(url, start=1, display=10):
    url += f'&start={start}&display={display}'
    request = urllib.request.Request(url, headers=naver_headers)
    response = urllib.request.urlopen(request)
    rescode = response.getcode() 

    if(rescode==200): # HTTP 응답 코드가 200이면 성공적으로 데이터를 가져온 것
        news_data = response.read().decode('utf-8')
        return json.loads(news_data) # JSON 문자열을 Python 객체로 변환하여 반환
    else:
        print("Error Code:" + rescode)
        return None
    
def mergeResultToList(result_list, merged_list):
    if result_list is not None:
        merged_list += result_list['items']
        return True
    else: return False

def saveJsonToCSV(merged_list, csv_filename):
    df = pd.DataFrame(merged_list)
    df.to_csv(f'result/{csv_filename}', index=False, encoding='utf-8-sig')

def crawlMain(keyword):
    encText = urllib.parse.quote(keyword)
    url = "https://openapi.naver.com/v1/search/news?query=" + encText
    news_corpus = []
    start = 1
    display = 10

    while start <= 100:
        news_data = crawlNaverNews(url, start, display)
        mer = mergeResultToList(news_data, news_corpus)
        if not mer: break
        start += display
    return news_corpus

