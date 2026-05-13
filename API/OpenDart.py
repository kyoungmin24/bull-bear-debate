import os, requests
from dotenv import load_dotenv
load_dotenv()

KEY = os.environ["DART_API_KEY"]

# 1) 기업 corp_code 매핑 파일 받기 (zip 안 xml, 한 번만)
# https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key=...

# 2) 공시 목록 (삼성전자 = corp_code 00126380)
r = requests.get(
    "https://opendart.fss.or.kr/api/list.json",
    params={
        "crtfc_key": KEY,
        "corp_code": "00126380",
        "bgn_de": "20260101",
        "end_de": "20260510",
        "page_count": 100,
    },
)
disclosures = r.json().get("list", [])
print(f"[공시] {len(disclosures)}건")
for d in disclosures[:3]:
    print("-", d.get("rcept_dt"), d.get("report_nm"))

# 3) 단일회사 전체 재무제표 (2025 사업보고서)
r = requests.get(
    "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json",
    params={
        "crtfc_key": KEY,
        "corp_code": "00126380",
        "bsns_year": "2025",
        "reprt_code": "11011",  # 11011=사업보고서, 11012=반기, 11013=1Q, 11014=3Q
        "fs_div": "CFS",         # CFS=연결, OFS=별도
    },
)
fs = r.json().get("list", [])
print(f"[재무] {len(fs)}개 계정과목")
for f in fs[:5]:
    print("-", f.get("sj_nm"), "|", f.get("account_nm"), "|", f.get("thstrm_amount"))