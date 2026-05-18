"""
Bull Agent — 강세 논거 제시
"""

from agents.base_agent import BaseAgent


class BullAgent(BaseAgent):

    @property
    def system_prompt(self) -> str:
        return """당신은 주식 투자 강세론자(Bull Analyst)입니다.
제공된 뉴스 기사를 근거로 해당 종목에 대한 매수 논거를 제시하는 역할입니다.

[규칙]
- 반드시 제공된 기사 내용을 근거로 주장하세요. 근거 없는 주장은 금지합니다.
- 데이터와 팩트 중심으로 논리적으로 서술하세요.
- 3~5문장으로 간결하게 핵심만 제시하세요.
- 2라운드 이후에는 Bear의 주장에 대한 반박을 포함하세요.
- 과도한 낙관론은 피하고, 합리적 근거에 집중하세요.

[응답 형식 - 반드시 JSON으로 반환]
{
  "content": "발언 내용 (3~5문장)",
  "tags": ["핵심 근거 키워드 1", "핵심 근거 키워드 2", "핵심 근거 키워드 3"]
}"""

    def speak(
        self,
        topic: str,
        articles_common: list[dict],
        articles_bull: list[dict],
        debate_history: list[dict],
        round_num: int,
        quant_text: str = "",
    ) -> dict:
        """
        Bull 발언 생성

        Args:
            topic: 토론 주제 (예: "삼성전자")
            articles_common: 공통 기사 목록
            articles_bull: Bull 관점 추가 기사
            debate_history: 이전 라운드 발언 기록
            round_num: 현재 라운드 번호
            quant_text: 정량 데이터 텍스트 (Round 2+)

        Returns:
            {"content": "...", "tags": [...]}
        """
        prompt = _build_prompt(
            role="Bull",
            topic=topic,
            articles_common=articles_common,
            articles_side=articles_bull,
            debate_history=debate_history,
            round_num=round_num,
            quant_text=quant_text,
        )
        return self._chat(prompt)


# ── 프롬프트 빌더 (bull/bear 공용) ───────────────────────
def _build_prompt(
    role: str,
    topic: str,
    articles_common: list[dict],
    articles_side: list[dict],
    debate_history: list[dict],
    round_num: int,
    quant_text: str = "",   # Round 2+에서만 전달
) -> str:

    # 기사 포맷팅
    def fmt_articles(articles: list[dict]) -> str:
        if not articles:
            return "  (관련 기사 없음)"
        lines = []
        for i, a in enumerate(articles, 1):
            content_preview = (a.get("content") or a.get("summary") or "")[:500]
            lines.append(
                f"  [{i}] {a.get('title', '')}\n"
                f"      출처: {a.get('source', '')} | {a.get('published_at', '')[:10]}\n"
                f"      내용: {content_preview}"
            )
        return "\n\n".join(lines)

    # 이전 토론 기록 포맷팅
    def fmt_history(history: list[dict]) -> str:
        if not history:
            return "  (첫 번째 발언입니다)"
        lines = []
        for h in history:
            lines.append(f"  [Round {h['round']} {h['role']}] {h['content']}")
        return "\n".join(lines)

    if round_num == 1:
        round_instruction = "제공된 뉴스 기사를 근거로 핵심 논거를 제시하세요."
    elif round_num == 2:
        round_instruction = "뉴스 기사 없이 제공된 정량 데이터(재무/컨센서스/주가)만을 근거로 논거를 제시하고, 1라운드 상대방 주장에 반박하세요."
    else:
        round_instruction = "뉴스 기사와 정량 데이터를 모두 활용해 최종 주장을 완성하고, 이전 논거를 종합 정리하세요."

    quant_section = f"\n━━━ 정량 데이터 ━━━\n{quant_text}" if quant_text else ""

    return f"""[토론 주제]: {topic}
[현재 라운드]: Round {round_num}
[당신의 역할]: {role}

━━━ 공통 참고 기사 ━━━
{fmt_articles(articles_common)}

━━━ {role} 관점 추가 기사 ━━━
{fmt_articles(articles_side)}
{quant_section}
━━━ 이전 토론 내용 ━━━
{fmt_history(debate_history)}

━━━ 지시 ━━━
{round_instruction}
반드시 JSON 형식으로 응답하세요."""
