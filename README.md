# Bull vs Bear — AI 주식 토론 시스템

> 한국 주식 종목을 입력하면 **Bull**(매수)·**Bear**(매도) 두 AI 에이전트가 실제 뉴스·정량 데이터를 근거로 토론하고, **Moderator** 가 최종 투자 의견을 종합하는 멀티 에이전트 RAG 시스템.

> 📚 AI Agent 수업 팀 프로젝트(4인). 커밋 author 정보는 그대로 보존되어 있습니다.

---

## 📌 한눈에 보기

```
사용자 입력 ("삼성전자")
        │
        ▼
 ┌──────────────────────────────────────────────────────────┐
 │  Profiler   설문 → 독자 페르소나(수준·용어·설명깊이·투자기간)   │
 ├──────────────────────────────────────────────────────────┤
 │  RAG        관점별 쿼리 확장 → 뉴스 검색 + 정량 데이터 결합     │
 ├──────────────────────────────────────────────────────────┤
 │  Round 1 (정성)   뉴스 기사 기반 주장·반론                    │
 │  Round 2 (정량)   재무·컨센서스·주가 기반 주장·반론           │
 │  Round 3 (통합)   양측 최종 결론                             │
 │     ↳ 동적 라운드: 수렴 판정으로 조기 종료 / 자유 토론 연장     │
 ├──────────────────────────────────────────────────────────┤
 │  가드        Self-Reflection 자기검토 + 결정적 수치 검증기      │
 ├──────────────────────────────────────────────────────────┤
 │  Moderator  전체 토론 종합 → 투자 판단                       │
 └──────────────────────────────────────────────────────────┘
        │
        ▼
   React UI에 Bull/Bear 메시지 순차 출력 + 근거 기사
```

---

## ✨ 주요 기능

| 기능 | 설명 | 핵심 파일 |
|:---|:---|:---|
| **관점 분리 멀티 에이전트** | Bull·Bear를 단일 `AnalystAgent`(role 파라미터)로 통합, 주장→반론→결론 의존 관계를 가진 워크플로 | `agents/analyst.py`, `agents/orchestrator.py` |
| **라운드별 데이터 스코핑** | R1=뉴스(정성), R2=정량, R3=통합. 각 라운드가 정해진 데이터만 사용 | `agents/config.py` (`DEBATE_FLOW`) |
| **Tool Calling 조사** | 에이전트가 직접 검색·정량 도구 호출(function calling). `hybrid` 기본(사전 조사 후 부족 시 추가 조사) | `agents/tools.py` |
| **동적 라운드** | 수렴 판정 기반으로 토론 조기 종료 또는 자유 토론 연장 | `agents/orchestrator.py` |
| **사용자 페르소나** | 설문 → LLM 독자 프로필 → 설명 tier·분량·논거 강조를 답변에 반영(판단은 불변) | `agents/profiler.py`, `agents/prompts.py` |
| **환각 가드** | Self-Reflection 자기검토 + 출력 수치를 입력 데이터와 대조하는 결정적 검증기 | `agents/verifier.py` |
| **의존성 기반 병렬 실행** | 서로 의존하지 않는 LLM 호출은 `ThreadPoolExecutor`로 동시 실행 | `agents/orchestrator.py` |

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
python -m venv myenv
source myenv/bin/activate        # Windows: myenv\Scripts\activate
pip install -r requirements.txt
pip install fastapi "uvicorn[standard]" pydantic   # API 서버 실행용
```

루트에 `.env` 생성:
```bash
OPENAI_API_KEY=sk-...
```

### 2. 데이터 수집 (최초 1회)

```bash
python -m collection.companies              # 시총 상위 기업 초기화
python -m collection.naver_news_crawling    # 네이버 증권 뉴스
python -m collection.financials             # 재무제표
python -m collection.consensus              # 증권사 컨센서스
python -m collection.quant_macro_daily      # 주가·수급·PER·PBR
```

### 3. FAISS 인덱스 빌드

```bash
python -m rag.index_builder --articles                 # 전체 기사 임베딩
python -m rag.index_builder --articles --ticker 005930 # 특정 종목만(테스트)
```

### 4. 실행

```bash
# 웹 UI (정식 진입점)
cd frontend && npm install && npm run build && cd ..
uvicorn main:app --reload --port 8000
# → http://localhost:8000

# 또는 터미널에서 빠르게 토론 확인
python test_debate.py
```

---

## 📂 폴더 구조

```
Bull-Bear/
├── main.py                    # FastAPI 서버 (정식 진입점)
├── test_debate.py             # 터미널 토론 테스트 (CLI 진입점)
│
├── agents/                    # ★ 멀티 에이전트 토론 로직
│   ├── config.py                 # ⭐ 설정 (모델·온도·DEBATE_FLOW·기능 플래그)
│   ├── prompts.py                # ⭐ 프롬프트·Few-shot·페르소나 빌더
│   ├── orchestrator.py           # 토론 흐름 실행 엔진(병렬·동적 라운드)
│   ├── analyst.py                # Bull/Bear 통합 (AnalystAgent)
│   ├── moderator.py              # 사회자 (최종 종합)
│   ├── profiler.py               # 설문 → 독자 페르소나
│   ├── tools.py                  # function calling 도구 (검색·정량)
│   ├── verifier.py               # 결정적 수치 검증기 (환각 가드)
│   ├── memory.py                 # 과거 토론 참조(옵션)
│   ├── base_agent.py             # OpenAI 호출 기반 클래스
│   └── query_expander.py         # 주제 → 관점별 검색 쿼리
│
├── rag/                       # 검색 증강 생성
│   ├── retriever.py              # FAISS 검색 + SQLite 메타 조회
│   ├── index_builder.py          # 벡터 인덱스 빌드 (IndexFlatIP=cosine)
│   ├── embedder.py               # OpenAI 임베딩 래퍼
│   └── quant_fetcher.py          # 정량 데이터 조회·포맷
│
├── collection/                # 데이터 수집 스크립트
│   ├── companies.py / naver_news_crawling.py
│   ├── financials.py / consensus.py / quant_macro_daily.py
│   └── dart_disclosures.py
│
├── frontend/                  # React + Vite + Tailwind (UI)
│   └── src/app/components/       # InputScreen, LoadingScreen, DebateChat ...
│
├── docs/                      # 설계·실험 문서
└── streamlit_app.py           # (구버전, 레거시) Streamlit UI
```

---

## 🎭 토론 구조

| 라운드 | 데이터 | 선공 | 발언 순서 |
|:---:|:---|:---:|:---|
| **R1** | 뉴스 기사 | Bull | ① Bull 주장 → ② Bear 반론 → ③ Bear 주장 → ④ Bull 반론 |
| **R2** | 재무·주가 | Bear | ① Bear 주장 → ② Bull 반론 → ③ Bull 주장 → ④ Bear 반론 |
| **R3** | 통합 | — | ① Bull 최종 결론 → ② Bear 최종 결론 |
| **Mod** | 전체 | — | 투자 판단 (매수 적극 / 분할 매수 / 관망 / 매도 고려) |

**핵심 원칙**
1. 반론은 상대의 직전 주장을 입력으로 받아 생성한다.
2. 각 라운드는 정해진 raw 데이터만 사용한다(라운드 간 출력 비참조).
3. 의존성 없는 발언은 병렬 호출한다.
4. 동적 모드에서는 수렴 판정으로 조기 종료하거나 자유 토론을 연장한다.

---

## ⚙️ 커스터마이징

모든 설정은 **`agents/config.py`** 한 곳에 모여 있다.

```python
MODEL_NAME = "gpt-4o-mini"        # "gpt-4o", "o3-mini" 등으로 교체 가능

ENABLE_REFLECTION     = True       # Self-Reflection 자기검토
ENABLE_TOOL_CALLING   = True       # 에이전트 도구 호출
ENABLE_DYNAMIC_ROUNDS = True       # 수렴 기반 동적 라운드
ENABLE_FEW_SHOT       = True
ENABLE_COT            = False
RESEARCH_MODE         = "hybrid"   # "per_step" | "upfront" | "hybrid"

DEBATE_FLOW = [ ... ]              # 라운드·발언 순서·데이터 종류 자유 편집
```

> 발언 순서/라운드는 `DEBATE_FLOW` 리스트만 바꾸면 되고, 의존성 없는 step은 자동 병렬 실행된다.

---

## 🔍 RAG 동작

```
사용자 입력
   │  query_expander → 3종 쿼리 (룰 기반)
   │     • common(중립) / bull(긍정) / bear(부정)
   ▼
embedder (text-embedding-3-small, 1536차원)
   ▼
FAISS (IndexFlatIP = cosine) → 유사도 검색
   ▼
SQLite → faiss_id로 원문·메타데이터(title, content, url) 조회
   ▼
Bull: common(3) + bull(2)   /   Bear: common(3) + bear(2)
정량 데이터(재무·컨센서스·주가)는 종목 코드로 최신 레코드 조회·결합
```

---

## 🛠️ 기술 스택

| 구분 | 기술 |
|:---|:---|
| AI | OpenAI Chat Completions (`gpt-4o-mini`), function calling, JSON response format |
| RAG | `text-embedding-3-small`, FAISS `IndexFlatIP` |
| 백엔드 | FastAPI, Pydantic, `ThreadPoolExecutor` |
| 프론트엔드 | React 18, Vite, Tailwind CSS |
| 데이터 | SQLite, pandas, BeautifulSoup / 네이버 증권, OpenDART, pykrx, FinanceDataReader |

---

## 🚧 트러블슈팅

| 증상 | 해결 |
|:---|:---|
| `ModuleNotFoundError: faiss` | `pip install faiss-cpu` |
| `OPENAI_API_KEY` 없음 | 루트에 `.env` 생성 |
| `database is locked` | 크롤링 진행 중 → 잠시 후 재시도 |
| 빈 흰 화면 | 브라우저 강제 새로고침 (`Ctrl/Cmd + Shift + R`) |
| 빌드 변경 반영 안 됨 | `cd frontend && npm run build` 후 uvicorn 재시작 |

---

## 📚 더 보기

- [`docs/tool-calling-and-persona.md`](docs/tool-calling-and-persona.md) — 도구 호출·페르소나 설계
- [`docs/reliability-and-trust.md`](docs/reliability-and-trust.md) — 신뢰성·환각 가드
