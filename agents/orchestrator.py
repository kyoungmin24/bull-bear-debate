"""
DebateOrchestrator — 전체 토론 흐름 제어

흐름:
1. QueryExpander로 쿼리 3종 생성
2. RAGRetriever로 기사 검색
3. 라운드별 Bull → Bear 순서로 발언
4. Moderator 최종 결론
"""

from agents.bull_agent import BullAgent
from agents.bear_agent import BearAgent
from agents.moderator import ModeratorAgent
from query_expander import expand_query
from rag.retriever import search, _detect_ticker
from rag.quant_fetcher import fetch_quant, format_quant


class DebateOrchestrator:
    """
    사용 예:
        orchestrator = DebateOrchestrator()
        result = orchestrator.run(topic="삼성전자", rounds=3)
    """

    def __init__(self):
        self.bull = BullAgent()
        self.bear = BearAgent()
        self.moderator = ModeratorAgent()

    def run(
        self,
        topic: str,
        rounds: int = 3,
        top_k: int = 5,
        on_round_complete=None,   # 라운드 완료 시 콜백 (Streamlit 실시간 출력용)
    ) -> dict:
        """
        토론 전체 실행

        Args:
            topic: 토론 주제 (예: "삼성전자", "삼성전자 005930")
            rounds: 토론 라운드 수 (기본 3)
            top_k: RAG 검색 결과 수
            on_round_complete: 라운드 완료 콜백 fn(round_num, bull_result, bear_result)

        Returns:
            {
                "topic": str,
                "rounds": [
                    {
                        "round": int,
                        "bull": {"content": str, "tags": list},
                        "bear": {"content": str, "tags": list},
                    },
                    ...
                ],
                "moderator": {
                    "bull_summary": str,
                    "bear_summary": str,
                    "conclusion": str,
                    "verdict": str,
                },
                "articles": {
                    "common": list,
                    "bull": list,
                    "bear": list,
                }
            }
        """

        # ── 1단계: 쿼리 확장 ─────────────────────────────
        queries = expand_query(topic)

        # ── 2단계: 기사 검색 ─────────────────────────────
        # ticker 자동 감지는 retriever 내부에서 처리
        articles_common = search(queries["common"], source="articles", top_k=3)
        articles_bull   = search(queries["bull"],   source="articles", top_k=2)
        articles_bear   = search(queries["bear"],   source="articles", top_k=2)

        # ── 2.5단계: 정량 데이터 조회 (Round 2+용) ──────
        # ticker 감지 실패 시 quant_text = "" → Round 2도 기사만 사용
        detected_ticker = _detect_ticker(topic)
        quant_data = fetch_quant(detected_ticker) if detected_ticker else None
        quant_text = format_quant(quant_data) if quant_data else ""

        # ── 3단계: 라운드별 토론 ─────────────────────────
        debate_history: list[dict] = []
        round_results: list[dict] = []

        for r in range(1, rounds + 1):

            # 라운드별 데이터 구성
            # Round 1: 기사(정성)만
            # Round 2: 정량만 (기사 제외)
            # Round 3: 기사 + 정량 통합
            use_articles = (r != 2)
            use_quant    = (r >= 2)

            bull_result = self.bull.speak(
                topic=topic,
                articles_common=articles_common if use_articles else [],
                articles_bull=articles_bull     if use_articles else [],
                debate_history=debate_history,
                round_num=r,
                quant_text=quant_text if use_quant else "",
            )
            debate_history.append({
                "round":   r,
                "role":    "Bull",
                "content": bull_result.get("content", ""),
            })

            bear_result = self.bear.speak(
                topic=topic,
                articles_common=articles_common if use_articles else [],
                articles_bear=articles_bear     if use_articles else [],
                debate_history=debate_history,
                round_num=r,
                quant_text=quant_text if use_quant else "",
            )
            debate_history.append({
                "round":   r,
                "role":    "Bear",
                "content": bear_result.get("content", ""),
            })

            round_results.append({
                "round": r,
                "bull":  bull_result,
                "bear":  bear_result,
            })

            # Streamlit 실시간 출력용 콜백
            if on_round_complete:
                on_round_complete(r, bull_result, bear_result)

        # ── 4단계: Moderator 결론 ─────────────────────────
        moderator_result = self.moderator.conclude(
            topic=topic,
            debate_history=debate_history,
            articles_common=articles_common,
        )

        return {
            "topic":     topic,
            "rounds":    round_results,
            "moderator": moderator_result,
            "articles": {
                "common": articles_common,
                "bull":   articles_bull,
                "bear":   articles_bear,
            },
        }
