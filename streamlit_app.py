"""
Bull vs Bear AI 토론
실행: streamlit run streamlit_app.py
"""

import datetime
import streamlit as st
from agents.orchestrator import DebateOrchestrator

# ── 페이지 설정 ───────────────────────────────────────────
st.set_page_config(
    page_title="Bull vs Bear AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
/* 전체 배경 */
.stApp { background-color: #0e1117; color: #ffffff; }

/* 입력창 */
.stTextInput > div > div > input {
    background-color: #1e2130;
    color: #ffffff;
    border: 1px solid #2e3250;
    border-radius: 10px;
    padding: 14px 16px;
    font-size: 16px;
}

/* 버튼 */
.stButton > button {
    background: linear-gradient(135deg, #4f8ef7, #6c63ff);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 28px;
    font-size: 16px;
    font-weight: 600;
    width: 100%;
    cursor: pointer;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

/* 모드 카드 */
.mode-card {
    background-color: #1e2130;
    border: 2px solid #2e3250;
    border-radius: 14px;
    padding: 20px;
    cursor: pointer;
    transition: border-color 0.2s;
    height: 110px;
}
.mode-card:hover { border-color: #4f8ef7; }
.mode-card.selected { border-color: #4f8ef7; background-color: #1a2340; }
.mode-card h4 { margin: 6px 0 4px 0; font-size: 15px; }
.mode-card p  { margin: 0; font-size: 12px; color: #8b95b0; }

/* 샘플 주제 칩 */
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }
.chip {
    background-color: #1e2130;
    border: 1px solid #2e3250;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 13px;
    color: #aab0c8;
    cursor: pointer;
    display: inline-block;
}

/* 라운드 선택 */
.round-btn {
    background-color: #1e2130;
    border: 2px solid #2e3250;
    border-radius: 8px;
    padding: 6px 18px;
    font-size: 14px;
    font-weight: 600;
    color: #aab0c8;
    cursor: pointer;
    display: inline-block;
    margin-right: 8px;
}
.round-btn.selected { border-color: #4f8ef7; color: #4f8ef7; }

/* Bull 메시지 버블 (좌측) */
.bubble-bull {
    background-color: #1a3a2a;
    border: 1px solid #2a5a3a;
    border-radius: 0px 14px 14px 14px;
    padding: 14px 16px;
    margin: 8px 80px 8px 0;
    font-size: 14px;
    line-height: 1.6;
    color: #d4f0d4;
}

/* Bear 메시지 버블 (우측) */
.bubble-bear {
    background-color: #3a1a1a;
    border: 1px solid #5a2a2a;
    border-radius: 14px 0px 14px 14px;
    padding: 14px 16px;
    margin: 8px 0 8px 80px;
    font-size: 14px;
    line-height: 1.6;
    color: #f0d4d4;
    text-align: left;
}

/* Moderator 버블 */
.bubble-moderator {
    background-color: #1e2130;
    border: 1px solid #4f8ef7;
    border-radius: 14px;
    padding: 16px 20px;
    margin: 16px 0;
    font-size: 14px;
    line-height: 1.7;
    color: #c8d8f8;
}

/* 페르소나 헤더 */
.persona-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
}
.persona-name { font-weight: 700; font-size: 13px; }
.stance-bull {
    background-color: #1a4a2a;
    color: #4caf80;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}
.stance-bear {
    background-color: #4a1a1a;
    color: #f07070;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

/* 요약 태그 */
.tag-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.tag {
    background-color: rgba(255,255,255,0.07);
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 11px;
    color: #8b95b0;
}

/* 히스토리 카드 */
.history-card {
    background-color: #1e2130;
    border: 1px solid #2e3250;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 13px;
}
.history-card .topic { font-weight: 600; margin-bottom: 4px; }
.history-card .meta  { color: #8b95b0; font-size: 12px; }

/* 구분선 */
hr { border-color: #2e3250 !important; }

/* 섹션 레이블 */
.section-label {
    font-size: 13px;
    font-weight: 600;
    color: #8b95b0;
    margin: 18px 0 8px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Moderator 배지 */
.moderator-badge {
    text-align: center;
    margin: 24px 0 8px 0;
}
.moderator-badge span {
    background-color: #1e2130;
    border: 1px solid #4f8ef7;
    border-radius: 20px;
    padding: 4px 16px;
    font-size: 13px;
    color: #4f8ef7;
}

/* 뉴스 카드 */
.news-card {
    background-color: #1e2130;
    border: 1px solid #2e3250;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
}
.news-score {
    color: #4f8ef7;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 4px;
}
.news-title { font-size: 14px; margin-bottom: 4px; }
.news-meta  { color: #8b95b0; font-size: 12px; }

/* verdict 배지 */
.verdict-badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 700;
    margin-top: 10px;
}
.verdict-buy      { background-color: #1a4a2a; color: #4caf80; border: 1px solid #4caf80; }
.verdict-split    { background-color: #1a3a4a; color: #4f8ef7; border: 1px solid #4f8ef7; }
.verdict-watch    { background-color: #2e2a1a; color: #f0c040; border: 1px solid #f0c040; }
.verdict-sell     { background-color: #4a1a1a; color: #f07070; border: 1px solid #f07070; }
</style>
""", unsafe_allow_html=True)


# ── 세션 초기화 ───────────────────────────────────────────
if "page"    not in st.session_state: st.session_state.page    = "setup"
if "rounds"  not in st.session_state: st.session_state.rounds  = 3
if "mode"    not in st.session_state: st.session_state.mode    = "stock"
if "history" not in st.session_state: st.session_state.history = []


# ── 헬퍼: 라운드 HTML 생성 ────────────────────────────────
def _render_round(round_num: int, bull: dict, bear: dict):
    """라운드 Bull/Bear 버블을 st.markdown으로 직접 출력"""
    label_map = {1: "정성 (기사)", 2: "정량 (재무·주가)", 3: "통합"}
    label = label_map.get(round_num, f"Round {round_num}")

    def tags_html(tags):
        return "".join(f"<span class='tag'>{t}</span>" for t in (tags or []))

    st.markdown(
        f"<div style='font-size:11px;color:#8b95b0;text-align:center;margin:12px 0 8px;'>"
        f"— Round {round_num} · {label} —</div>",
        unsafe_allow_html=True,
    )
    # Bull 버블
    st.markdown(
        f"<div style='display:flex;align-items:flex-start;gap:10px;margin-bottom:16px;'>"
        f"<div style='font-size:28px;margin-top:4px;'>🐄</div>"
        f"<div style='flex:1;'>"
        f"<div class='persona-header'>"
        f"<span class='persona-name'>Bull 애널리스트</span>"
        f"<span class='stance-bull'>매수 관점</span>"
        f"<span style='font-size:11px;color:#8b95b0;'>[Round {round_num}]</span>"
        f"</div>"
        f"<div class='bubble-bull'>{bull.get('content','')}"
        f"<div class='tag-row'>{tags_html(bull.get('tags',[]))}</div>"
        f"</div></div>"
        f"<div style='width:60px;'></div></div>",
        unsafe_allow_html=True,
    )
    # Bear 버블
    st.markdown(
        f"<div style='display:flex;align-items:flex-start;gap:10px;margin-bottom:16px;'>"
        f"<div style='width:60px;'></div>"
        f"<div style='flex:1;'>"
        f"<div class='persona-header' style='justify-content:flex-end;'>"
        f"<span style='font-size:11px;color:#8b95b0;'>[Round {round_num}]</span>"
        f"<span class='stance-bear'>매도 관점</span>"
        f"<span class='persona-name'>Bear 애널리스트</span>"
        f"</div>"
        f"<div class='bubble-bear'>{bear.get('content','')}"
        f"<div class='tag-row'>{tags_html(bear.get('tags',[]))}</div>"
        f"</div></div>"
        f"<div style='font-size:28px;margin-top:4px;'>🐻</div></div>",
        unsafe_allow_html=True,
    )


def _verdict_html(verdict: str) -> str:
    mapping = {
        "매수 적극": ("verdict-buy",   "🚀 매수 적극"),
        "분할 매수": ("verdict-split",  "📈 분할 매수"),
        "관망":      ("verdict-watch",  "👀 관망"),
        "매도 고려": ("verdict-sell",   "📉 매도 고려"),
    }
    css, text = mapping.get(verdict, ("verdict-watch", verdict))
    return f"<span class='verdict-badge {css}'>{text}</span>"


# ════════════════════════════════════════════════════════
#  PAGE 1 — 설정 화면
# ════════════════════════════════════════════════════════
def page_setup():
    st.markdown("<h1 style='text-align:center; font-size:28px; margin-bottom:4px;'>⚖️ Bull vs Bear AI 토론</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8b95b0; margin-bottom:28px;'>AI 전문가들이 주식 토론을 진행합니다</p>", unsafe_allow_html=True)

    # ── 모드 선택 ────────────────────────────────────────
    st.markdown("<div class='section-label'>분석 모드</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        sel1 = "selected" if st.session_state.mode == "stock" else ""
        st.markdown(f"""
        <div class='mode-card {sel1}'>
            <div style='font-size:22px'>🔬</div>
            <h4>개별 종목 분석</h4>
            <p>Bull · Bear 2인이 종목을 집중 토론</p>
        </div>""", unsafe_allow_html=True)
        if st.button("개별 종목 선택", key="mode_stock", use_container_width=True):
            st.session_state.mode = "stock"
            st.rerun()

    with col2:
        sel2 = "selected" if st.session_state.mode == "market" else ""
        st.markdown(f"""
        <div class='mode-card {sel2}'>
            <div style='font-size:22px'>🏛️</div>
            <h4>시황 토론</h4>
            <p>시장 전반 흐름을 다각도로 분석</p>
        </div>""", unsafe_allow_html=True)
        if st.button("시황 토론 선택", key="mode_market", use_container_width=True):
            st.session_state.mode = "market"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 토론 주제 입력 ───────────────────────────────────
    placeholder = "예) 삼성전자 (005930)" if st.session_state.mode == "stock" else "예) 2분기 코스피 방향성"
    st.markdown("<div class='section-label'>토론 주제</div>", unsafe_allow_html=True)
    topic = st.text_input("", placeholder=placeholder, label_visibility="collapsed", key="topic_input")

    samples = (
        ["삼성전자", "SK하이닉스", "현대차"]
        if st.session_state.mode == "stock"
        else ["2분기 코스피 방향성", "원/달러 환율 전망", "미국 금리 인하 시나리오"]
    )
    chips_html = "<div class='chip-row'>" + "".join(f"<span class='chip'>{s}</span>" for s in samples) + "</div>"
    st.markdown(chips_html, unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px; color:#8b95b0;'>실시간 뉴스/데이터는 자동으로 검색되어 토론에 반영됩니다.</p>", unsafe_allow_html=True)

    # ── 라운드 선택 ──────────────────────────────────────
    st.markdown("<div class='section-label'>라운드</div>", unsafe_allow_html=True)
    r_col1, r_col2, r_col3, _ = st.columns([1, 1, 1, 5])
    with r_col1:
        if st.button("3", key="r3", use_container_width=True):
            st.session_state.rounds = 3; st.rerun()
    with r_col2:
        if st.button("5", key="r5", use_container_width=True):
            st.session_state.rounds = 5; st.rerun()
    with r_col3:
        if st.button("7", key="r7", use_container_width=True):
            st.session_state.rounds = 7; st.rerun()
    st.markdown(f"<p style='font-size:12px; color:#4f8ef7;'>현재 선택: {st.session_state.rounds} 라운드</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 시작 버튼 ────────────────────────────────────────
    if st.button("토론 시작 →", key="start_btn"):
        if not topic.strip():
            st.error("토론 주제를 입력해주세요.")
        else:
            st.session_state.topic = topic.strip()
            st.session_state.page  = "debate"
            # 이전 토론 결과 초기화
            st.session_state.pop("debate_result", None)
            st.rerun()

    # ── 이전 토론 히스토리 ───────────────────────────────
    if st.session_state.history:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>이전 토론</div>", unsafe_allow_html=True)
        for h in st.session_state.history:
            st.markdown(f"""
            <div class='history-card'>
                <div class='topic'>💬 {h['topic']}</div>
                <div class='meta'>라운드 {h['rounds']} · {h['date']}</div>
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
#  PAGE 2 — 토론 화면
# ════════════════════════════════════════════════════════
def page_debate():
    topic  = st.session_state.get("topic", "종목 분석")
    rounds = st.session_state.rounds

    # ── 상단 헤더 ─────────────────────────────────────────
    col_back, col_title = st.columns([1, 6])
    with col_back:
        if st.button("← 돌아가기"):
            st.session_state.page = "setup"
            st.rerun()
    with col_title:
        st.markdown(f"<h2 style='margin:0; font-size:22px;'>⚖️ {topic}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#8b95b0; font-size:13px; margin:0;'>{rounds} 라운드 · Round 1 정성 / Round 2 정량 / Round 3 통합</p>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    debate_col, news_col = st.columns([3, 1])

    with debate_col:

        # ── 결과 없으면 orchestrator 실행 ────────────────
        if "debate_result" not in st.session_state:
            with st.spinner(f"🤖 {topic} 토론 진행 중... (약 1~2분 소요)"):
                orchestrator = DebateOrchestrator()
                result = orchestrator.run(topic=topic, rounds=rounds)
            st.session_state.debate_result = result

            now = datetime.datetime.now().strftime("%m-%d %H:%M")
            entry = {"topic": topic, "rounds": rounds, "date": now}
            if entry not in st.session_state.history:
                st.session_state.history.insert(0, entry)

        # ── 결과 출력 ────────────────────────────────────
        result = st.session_state.debate_result
        for r_data in result["rounds"]:
            _render_round(r_data["round"], r_data["bull"], r_data["bear"])
        _render_moderator(result["moderator"])

    # ── 뉴스 사이드바 ────────────────────────────────────
    with news_col:
        st.markdown("<div class='section-label'>📰 참고 기사 (RAG)</div>", unsafe_allow_html=True)
        articles = []
        if "debate_result" in st.session_state:
            articles = st.session_state.debate_result["articles"]["common"]

        if articles:
            for a in articles:
                score   = a.get("score", 0)
                title   = a.get("title", "")
                source  = a.get("source", "")
                pub     = (a.get("published_at") or "")[:10]
                preview = (a.get("content") or "")[:60]
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-score">유사도 {score:.2f}</div>
                    <div class="news-title">{title}</div>
                    <div class="news-meta">{pub} · {source}</div>
                    <div style="font-size:12px; color:#8b95b0; margin-top:6px;">{preview}...</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#8b95b0; font-size:13px;'>토론 완료 후 표시됩니다.</p>",
                        unsafe_allow_html=True)


def _render_moderator(mod: dict):
    verdict    = mod.get("verdict", "")
    bull_sum   = mod.get("bull_summary", "")
    bear_sum   = mod.get("bear_summary", "")
    conclusion = mod.get("conclusion", "")

    st.markdown(
        "<div class='moderator-badge'><span>⚖️ 사회자 (Moderator)</span></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='bubble-moderator'>"
        f"<b>📈 Bull 요약</b><br>{bull_sum}<br><br>"
        f"<b>📉 Bear 요약</b><br>{bear_sum}<br><br>"
        f"<b>💡 종합 의견</b><br>{conclusion}<br><br>"
        f"{_verdict_html(verdict)}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ── 라우터 ────────────────────────────────────────────────
if st.session_state.page == "setup":
    page_setup()
else:
    page_debate()
