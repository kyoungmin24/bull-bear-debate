"""
RAG 대화형 테스트
실행: python -m rag.chat_test
"""

from rag.retriever import search


def print_results(results: list[dict], source: str):
    if not results:
        print("  결과 없음\n")
        return
    for i, r in enumerate(results, 1):
        print(f"\n  [{i}] score={r['score']:.4f} | {r.get('corp_name')} ({r.get('ticker')})")
        if source == "articles":
            print(f"       제목: {r.get('title')}")
            print(f"       요약: {(r.get('summary') or '')[:100]}...")
            print(f"       날짜: {r.get('published_at', '')[:10]} | 출처: {r.get('source')}")
        else:
            print(f"       공시: {r.get('report_name')}")
            print(f"       날짜: {r.get('submitted_at')}")
    print()


def run():
    print("=" * 60)
    print("  RAG 검색 테스트  (종료: q)")
    print("=" * 60)
    print("  소스 선택: [1] articles(기사)  [2] dart(공시)  [3] 둘 다")
    print("  종목 필터: 쿼리 끝에  @005930  형식으로 추가 가능")
    print("  예) 삼성전자 반도체 전망 @005930")
    print("=" * 60)

    while True:
        raw = input("\n쿼리 입력 > ").strip()
        if raw.lower() in ("q", "quit", "exit"):
            break
        if not raw:
            continue

        # 종목 필터 파싱 (@005930 형식)
        ticker = None
        query = raw
        if "@" in raw:
            parts = raw.rsplit("@", 1)
            query = parts[0].strip()
            ticker = parts[1].strip()

        # 소스 선택
        src_input = input("소스 [1=기사 / 2=공시 / 3=둘다, 기본=1] > ").strip()
        sources = []
        if src_input == "2":
            sources = ["dart"]
        elif src_input == "3":
            sources = ["articles", "dart"]
        else:
            sources = ["articles"]

        top_k = input("결과 수 [기본=3] > ").strip()
        top_k = int(top_k) if top_k.isdigit() else 3

        for source in sources:
            label = "기사" if source == "articles" else "공시"
            ticker_label = f" | ticker={ticker}" if ticker else ""
            print(f"\n{'─'*60}")
            print(f"  [{label}] \"{query}\"{ticker_label}")
            print(f"{'─'*60}")
            results = search(query, source=source, top_k=top_k, ticker=ticker)
            print_results(results, source)


if __name__ == "__main__":
    run()
