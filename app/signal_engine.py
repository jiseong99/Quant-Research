import pandas as pd
import ta

class SignalEngine:
    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["Close"]
        volume = df["Volume"]

        # 모멘텀 지표
        df["rsi"] = ta.momentum.RSIIndicator(close).rsi()

        # 추세 지표
        macd = ta.trend.MACD(close)
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()
        df["macd_hist"] = macd.macd_diff()

        # 변동성 지표
        bb = ta.volatility.BollingerBands(close)
        df["bb_upper"] = bb.bollinger_hband()
        df["bb_lower"] = bb.bollinger_lband()
        df["bb_pct"] = bb.bollinger_pband()

        # 거래량 지표
        df["volume_sma20"] = volume.rolling(20).mean()
        df["volume_ratio"] = volume / df["volume_sma20"]

        # 복합 신호 계산 (-1 강한 매도 ~ +1 강한 매수)
        rsi_s  = (50 - df["rsi"]) / 50
        macd_s = df["macd_hist"].clip(-1, 1)
        bb_s   = (0.5 - df["bb_pct"]).clip(-0.5, 0.5) * 2

        df["composite"] = ((rsi_s + macd_s + bb_s) / 3).round(3)
        df["signal_label"] = df["composite"].apply(self._label)

        return df.dropna()

    def _label(self, v):
        if v >  0.3: return "Strong Buy"
        if v >  0.1: return "Buy"
        if v < -0.3: return "Strong Sell"
        if v < -0.1: return "Sell"
        return "Neutral"