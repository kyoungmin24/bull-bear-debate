import FinanceDataReader as fdr

# 종목 리스트
krx = fdr.StockListing("KRX")
print("[KRX 종목수]", len(krx))
print(krx.head(3))

# 환율
usd_krw = fdr.DataReader("USD/KRW", "2026-01-01")
print("\n[USD/KRW]")
print(usd_krw.tail(3))

# 지수
kospi = fdr.DataReader("KS11", "2026-01-01")
print("\n[KOSPI]")
print(kospi.tail(3))