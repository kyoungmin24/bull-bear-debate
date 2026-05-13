"""
FAISS 검색 → SQLite 메타데이터 조회

사용 예:
    from rag.retriever import search
    results = search("삼성전자 반도체 수익성", source="articles", top_k=5)
"""

import sqlite3
from pathlib import Path

import faiss
import numpy as np

from rag.embedder import embed_query

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "identifier.sqlite"
FAISS_DIR = Path(__file__).resolve().parent / "faiss_store"

# 인덱스 캐시 (한 번 로드 후 메모리 유지)
_indexes: dict[str, faiss.Index] = {}


def _load_index(source: str) -> faiss.Index:
    if source not in _indexes:
        index_path = FAISS_DIR / f"{source}.index"
        if not index_path.exists():
            raise FileNotFoundError(
                f"{index_path} 없음. 먼저 index_builder.py를 실행하세요."
            )
        _indexes[source] = faiss.read_index(str(index_path))
    return _indexes[source]


def _fetch_articles(faiss_ids: list[int]) -> list[dict]:
    placeholders = ",".join("?" * len(faiss_ids))
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(f"""
            SELECT a.faiss_id, a.ticker, c.corp_name,
                   a.title, a.summary, a.source, a.published_at
            FROM articles a
            JOIN companies c ON a.ticker = c.ticker
            WHERE a.faiss_id IN ({placeholders})
        """, faiss_ids).fetchall()

    # FAISS 반환 순서(유사도 순) 보존
    id_to_row = {row["faiss_id"]: dict(row) for row in rows}
    return [id_to_row[fid] for fid in faiss_ids if fid in id_to_row]


def _fetch_dart(faiss_ids: list[int]) -> list[dict]:
    placeholders = ",".join("?" * len(faiss_ids))
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(f"""
            SELECT d.faiss_id, d.ticker, c.corp_name,
                   d.report_name, d.submitted_at, d.rcept_no
            FROM dart_disclosures d
            JOIN companies c ON d.ticker = c.ticker
            WHERE d.faiss_id IN ({placeholders})
        """, faiss_ids).fetchall()

    id_to_row = {row["faiss_id"]: dict(row) for row in rows}
    return [id_to_row[fid] for fid in faiss_ids if fid in id_to_row]


def search(
    query: str,
    source: str = "articles",  # "articles" | "dart"
    top_k: int = 5,
    ticker: str = None,         # 특정 종목만 필터링 (선택)
) -> list[dict]:
    """
    query를 임베딩해 FAISS로 유사 문서를 검색하고 SQLite 메타데이터를 반환

    Args:
        query: 검색 쿼리 (자연어)
        source: "articles" 또는 "dart"
        top_k: 반환할 결과 수 (ticker 필터 시 여유있게 크게 설정)
        ticker: 특정 종목 코드로 필터링 (예: "005930")

    Returns:
        유사도 순으로 정렬된 문서 메타데이터 리스트
    """
    index = _load_index(source)

    # 쿼리 임베딩 → 정규화
    query_vec = np.array([embed_query(query)], dtype="float32")
    faiss.normalize_L2(query_vec)

    # ticker 필터 있을 경우 여유있게 검색 후 필터
    search_k = top_k * 10 if ticker else top_k
    scores, faiss_ids = index.search(query_vec, search_k)

    valid_ids = [int(fid) for fid in faiss_ids[0] if fid >= 0]

    # SQLite에서 메타데이터 조회
    if source == "articles":
        results = _fetch_articles(valid_ids)
    else:
        results = _fetch_dart(valid_ids)

    # 유사도 점수 추가
    score_map = {int(fid): float(score) for fid, score in zip(faiss_ids[0], scores[0])}
    for r in results:
        r["score"] = score_map.get(r["faiss_id"], 0.0)

    # ticker 필터링 (FAISS는 메타데이터 필터 미지원 → 검색 후 처리)
    if ticker:
        results = [r for r in results if r.get("ticker") == ticker]

    return results[:top_k]
