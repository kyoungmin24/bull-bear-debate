import argparse
import hashlib
import html
import os
import re
import sqlite3
import time
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "identifier.sqlite"
NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"


load_dotenv(BASE_DIR / ".env")


TAG_RE = re.compile(r"<[^>]+>")


def clean_text(value):
    if not value:
        return None

    text = html.unescape(value)
    text = TAG_RE.sub("", text)
    return " ".join(text.split())


def parse_pubdate(value):
    if not value:
        return None

    try:
        dt = parsedate_to_datetime(value)
        return dt.isoformat()
    except Exception:
        return value


def source_from_url(value):
    if not value:
        return None

    host = urlparse(value).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host or None


def article_id(ticker, url, title):
    raw = f"{ticker}|{url or ''}|{title or ''}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def get_target_companies(limit=None):
    query = """
        SELECT ticker, corp_name
        FROM companies
        ORDER BY market_cap DESC
    """

    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(query).fetchall()

    if limit:
        return rows[:limit]

    return rows


def fetch_naver_news(client_id, client_secret, query, display=20, sort="date"):
    response = requests.get(
        NAVER_NEWS_URL,
        headers={
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
        },
        params={
            "query": query,
            "display": display,
            "start": 1,
            "sort": sort,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json().get("items", [])


def ingest_articles(limit=None, display=20, sleep_sec=0.2, query_suffix="전망 OR 실적 OR 수주 OR 투자"):
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError("NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET 환경 변수가 설정되지 않았습니다.")

    companies = get_target_companies(limit=limit)
    if not companies:
        print("companies 테이블에 대상 기업이 없습니다.")
        return

    insert_query = """
        INSERT INTO articles (
            id, faiss_id, ticker, source, title, summary, url, published_at
        )
        VALUES (?, NULL, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            ticker = excluded.ticker,
            source = excluded.source,
            title = excluded.title,
            summary = excluded.summary,
            url = excluded.url,
            published_at = excluded.published_at
    """

    print(f"articles 수집 시작: 대상 기업 {len(companies)}개, 기업당 최대 {display}건")

    success_count = 0
    failed_count = 0

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for idx, (ticker, corp_name) in enumerate(companies, start=1):
            query = f"{corp_name} {query_suffix}".strip()

            try:
                items = fetch_naver_news(client_id, client_secret, query, display=display)

                for item in items:
                    title = clean_text(item.get("title"))
                    summary = clean_text(item.get("description"))
                    url = item.get("originallink") or item.get("link")
                    published_at = parse_pubdate(item.get("pubDate"))
                    source = source_from_url(url)
                    row_id = article_id(ticker, url, title)

                    cursor.execute(
                        insert_query,
                        (
                            row_id,
                            ticker,
                            source,
                            title,
                            summary,
                            url,
                            published_at,
                        ),
                    )
                    success_count += 1

                print(f"  [{idx}/{len(companies)}] {ticker} {corp_name}: {len(items)}건")

            except Exception as e:
                failed_count += 1
                print(f"  [{idx}/{len(companies)}] {ticker} {corp_name}: 조회 실패 - {e}")

            time.sleep(sleep_sec)

        conn.commit()

    print(f"완료: 기사 {success_count}건 저장, 실패 기업 {failed_count}개")


def parse_args():
    parser = argparse.ArgumentParser(description="Naver 뉴스 검색 결과를 articles 테이블에 저장합니다.")
    parser.add_argument("--limit", type=int, default=None, help="시가총액 상위 N개 기업만 테스트")
    parser.add_argument("--display", type=int, default=20, help="기업당 수집 기사 수. Naver 최대 100")
    parser.add_argument("--sleep", type=float, default=0.2, help="기업별 API 호출 간 대기 초")
    parser.add_argument(
        "--query-suffix",
        default="전망 OR 실적 OR 수주 OR 투자",
        help="회사명 뒤에 붙일 검색어",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    ingest_articles(
        limit=args.limit,
        display=args.display,
        sleep_sec=args.sleep,
        query_suffix=args.query_suffix,
    )
