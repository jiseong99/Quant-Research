import yfinance as yf
import pandas as pd

# 자주 쓰는 한국 주식 티커 매핑
KR_TICKERS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "삼성바이오로직스": "207940.KS",
    "현대차": "005380.KS",
    "카카오": "035720.KS",
    "네이버": "035420.KS",
    "셀트리온": "068270.KS",
    "KB금융": "105560.KS",
    "POSCO홀딩스": "005490.KS",
}

class DataCollector:
    def normalize_ticker(self, ticker: str) -> str:
        # 한글 회사명으로 입력하면 티커로 변환
        if ticker in KR_TICKERS:
            return KR_TICKERS[ticker]
        # 숫자 6자리면 한국 주식으로 판단해서 .KS 붙여줌
        if ticker.isdigit() and len(ticker) == 6:
            return f"{ticker}.KS"
        return ticker

    def get_price_data(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        import yfinance as yf
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period=period, timeout=30)
        if df.empty:
            df = ticker_obj.history(period="1y", timeout=30)
        df.index = pd.to_datetime(df.index).tz_localize(None)
        return df[["Open", "High", "Low", "Close", "Volume"]]

    def get_fundamentals(self, ticker: str) -> dict:
        ticker = self.normalize_ticker(ticker)
        try:
            info = yf.Ticker(ticker).fast_info
            return {
                "52w_high": getattr(info, "year_high", None),
                "52w_low": getattr(info, "year_low", None),
                "market_cap": getattr(info, "market_cap", None),
                "last_price": getattr(info, "last_price", None),
            }
        except Exception:
            return {}

    def get_news(self, ticker: str) -> list:
        ticker = self.normalize_ticker(ticker)
        try:
            news = yf.Ticker(ticker).news
            return [{"title": n["content"]["title"],
                     "url": n["content"]["canonicalUrl"]["url"]}
                    for n in news[:5]]
        except Exception:
            return []