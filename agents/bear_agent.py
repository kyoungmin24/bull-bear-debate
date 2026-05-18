"""
Bear Agent — 약세 논거 제시
"""

from agents.base_agent import BaseAgent
from agents.bull_agent import _build_prompt


class BearAgent(BaseAgent):

    @property
    def system_prompt(self) -> str:
        return """당신은 주식 투자 약세론자(Bear Analyst)입니다.
제공된 뉴스 기사를 근거로 해당 종목에 대한 매도/관망 논거를 제시하는 역할입니다.

[규칙]
- 반드시 제공된 기사 내용을 근거로 주장하세요. 근거 없는 주장은 금지합니다.
- 리스크, 불확실성, 부정적 요인을 데이터 기반으로 서술하세요.
- 3~5문장으로 간결하게 핵심만 제시하세요.
- 2라운드 이후에는 Bull의 주장에 대한 반박을 포함하세요.
- 과도한 비관론은 피하고, 합리적 리스크 분석에 집중하세요.

[응답 형식 - 반드시 JSON으로 반환]
{
  "content": "발언 내용 (3~5문장)",
  "tags": ["핵심 리스크 키워드 1", "핵심 리스크 키워드 2", "핵심 리스크 키워드 3"]
}"""

    def speak(
        self,
        topic: str,
        articles_common: list[dict],
        articles_bear: list[dict],
        debate_history: list[dict],
        round_num: int,
        quant_text: str = "",
    ) -> dict:
        """
        Bear 발언 생성

        Args:
            topic: 토론 주제
            articles_common: 공통 기사 목록
            articles_bear: Bear 관점 추가 기사
            debate_history: 이전 라운드 발언 기록
            round_num: 현재 라운드 번호
            quant_text: 정량 데이터 텍스트 (Round 2+)

        Returns:
            {"content": "...", "tags": [...]}
        """
        prompt = _build_prompt(
            role="Bear",
            topic=topic,
            articles_common=articles_common,
            articles_side=articles_bear,
            debate_history=debate_history,
            round_num=round_num,
            quant_text=quant_text,
        )
        return self._chat(prompt)
