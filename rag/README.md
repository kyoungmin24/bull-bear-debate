```
BullBear/
└── rag/
    ├── __init__.py        ← Python 패키지 선언 (내용 없음, 있어야 import 가능)
    ├── embedder.py        ← 텍스트 → 벡터 변환 (OpenAI API 호출)
    ├── index_builder.py   ← SQLite 읽어서 FAISS 인덱스 파일 빌드
    ├── retriever.py       ← 쿼리 입력 → FAISS 검색 → SQLite 메타데이터 반환
    ├── chat_test.py       ← 대화형 테스트 도구
    └── faiss_store/
        ├── articles.index ← 기사 벡터 저장 파일 (바이너리)
        └── dart.index     ← 공시 벡터 저장 파일 (바이너리)
```