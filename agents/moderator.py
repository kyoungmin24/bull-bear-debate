"""
Moderator Agent — 전체 토론 종합 및 최종 결론 도출
"""

import json
from agents.base_agent import BaseAgent


class ModeratorAgent(BaseAgent):

    @property
    def system_prompt(self) -> str:
        return """당신은 주식 투자 토론의 중립적인 사회자(Moderator)입니다.
Bull과 Bear의 토론 내용을 종합하여 균형 잡힌 최종 의견을 제시하는 역할입니다.

[규칙]
- 어느 한쪽 편을 들지 말고 양측 논거를 공정하게 평가하세요.
- Bull의 핵심 근거 요약, Bear의 핵심 리스크 요약을 모두 포함하세요.
- 최종 판단(매수 적극 / 분할 매수 / 관망 / 매도 고려)을 명확히 제시하세요.
- 투자는 본인 책임임을 언급하세요.

[응답 형식 - 반드시 JSON으로 반환]
{
  "bull_summary": "Bull 측 핵심 논거 요약 (2~3문장)",
  "bear_summary": "Bear 측 핵심 리스크 요약 (2~3문장)",
  "conclusion": "최종 종합 의견 (3~4문장)",
  "verdict": "매수 적극 | 분할 매수 | 관망 | 매도 고려"
}"""

    def conclude(
        self,
        topic: str,
        debate_history: list[dict],
        articles_common: list[dict],
    ) -> dict:
        """
        전체 토론을 바탕으로 최종 결론 생성

        Args:
            topic: 토론 주제
            debate_history: 전체 라운드 발언 기록
            articles_common: 공통 참고 기사

        Returns:
            {"bull_summary": "...", "bear_summary": "...",
             "conclusion": "...", "verdict": "..."}
        """
        history_text = "\n\n".join([
            f"[Round {h['round']} - {h['role']}]\n{h['content']}"
            for h in debate_history
        ])

        articles_text = "\n".join([
            f"- {a.get('title', '')} ({a.get('source', '')})"
            for a in articles_common
        ])

        prompt = f"""[토론 주제]: {topic}

━━━ 참고 기사 목록 ━━━
{articles_text}

━━━ 전체 토론 내용 ━━━
{history_text}

위 토론을 종합하여 최종 결론을 JSON 형식으로 제시하세요.
투자 판단(verdict)은 반드시 다음 중 하나로 명시하세요:
매수 적극 | 분할 매수 | 관망 | 매도 고려"""

        return self._chat(prompt, temperature=0.3)  # 결론은 낮은 temperature
