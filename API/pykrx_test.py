from dotenv import load_dotenv
load_dotenv()

from pykrx import stock

def safe(label, fn):
     try:
          result = fn()
          print(f"\n[{label}] OK")
          print(result if not hasattr(result, "tail") else result.tail(3))
     except Exception as e:
          print(f"\n[{label}] FAIL: {type(e).__name__}: {e}")

safe("OHLCV 삼성전자",
     lambda: stock.get_market_ohlcv("20250101", "20260508", "005930"))

safe("투자자별 매매동향 — 005930",
     lambda: stock.get_market_trading_value_by_date("20260101", "20260508", "005930"))

safe("공매도 잔고 — 005930",
     lambda: stock.get_shorting_balance_by_ticker("20260508", market="KOSPI").loc["005930"])

safe("공매도 거래량 — 005930",
     lambda: stock.get_shorting_volume_by_ticker("20260508", market="KOSPI").loc["005930"])

safe("PER/PBR",
     lambda: stock.get_market_fundamental("20260101", "20260508", "005930"))