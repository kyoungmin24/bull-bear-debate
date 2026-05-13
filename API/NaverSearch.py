import os, requests
from dotenv import load_dotenv

load_dotenv()

cid = os.environ["NAVER_CLIENT_ID"]
csec = os.environ["NAVER_CLIENT_SECRET"]

r = requests.get(
    "https://openapi.naver.com/v1/search/news.json",
    headers={
        "X-Naver-Client-Id": cid,
        "X-Naver-Client-Secret": csec,
    },
    params={
        "query": "삼성전자 전망",
        "display": 100,    # 최대 100
        "start": 1,        # 최대 1000까지 페이징
        "sort": "date",    # date | sim
    },
)
news = r.json()["items"]
# 각 item: title, originallink, link, description, pubDate

print(f"총 {len(news)}건 수신")
for n in news[:50]:
    print("-", n["title"])
    print(" ", n["pubDate"])
    print(" ", n["link"])