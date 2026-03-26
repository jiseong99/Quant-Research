import pandas as pd
import numpy as np
import ta
import yfinance as yf


class FeatureEngineer:
    def _get_macro(self, start: str, end: str) -> pd.DataFrame:
        macro = pd.DataFrame()
        try:
            vix = yf.download("^VIX", start=start, end=end,
                              progress=False, auto_adjust=True)["Close"]
            macro["vix"] = vix
        except Exception:
            pass
        try:
            tnx = yf.download("^TNX", start=start, end=end,
                              progress=False, auto_adjust=True)["Close"]
            macro["tnx"] = tnx
        except Exception:
            pass
        try:
            sp500 = yf.download("^GSPC", start=start, end=end,
                                progress=False, auto_adjust=True)["Close"]
            macro["sp500_ret"] = sp500.pct_change() * 100
            macro["sp500_vol"] = macro["sp500_ret"].rolling(20).std()
        except Exception:
            pass
        if not macro.empty:
            macro.index = pd.to_datetime(macro.index).tz_localize(None)
        return macro

    def generate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.index = pd.to_datetime(df.index)

        close = df["Close"]
        high = df["High"]
        low = df["Low"]
        volume = df["Volume"]

        # ── 모멘텀 ──
        df["rsi_7"]  = ta.momentum.RSIIndicator(close, window=7).rsi()
        df["rsi_14"] = ta.momentum.RSIIndicator(close, window=14).rsi()
        df["rsi_28"] = ta.momentum.RSIIndicator(close, window=28).rsi()
        df["roc_5"]  = close.pct_change(5) * 100
        df["roc_10"] = close.pct_change(10) * 100
        df["roc_20"] = close.pct_change(20) * 100
        stoch = ta.momentum.StochasticOscillator(high, low, close)
        df["stoch_k"] = stoch.stoch()
        df["stoch_d"] = stoch.stoch_signal()
        df["williams_r"] = ta.momentum.WilliamsRIndicator(high, low, close).williams_r()
        df["cci_20"] = ta.trend.CCIIndicator(high, low, close, window=20).cci()

        # ── 추세 ──
        macd = ta.trend.MACD(close)
        df["macd"]        = macd.macd()
        df["macd_signal"] = macd.macd_signal()
        df["macd_hist"]   = macd.macd_diff()
        df["macd_cross"]  = (
            (df["macd"] > df["macd_signal"]).astype(int) -
            (df["macd"] < df["macd_signal"]).astype(int)
        )

        df["sma_5"]  = close.rolling(5).mean()
        df["sma_20"] = close.rolling(20).mean()
        df["sma_60"] = close.rolling(60).mean()
        df["ema_5"]  = close.ewm(span=5).mean()
        df["ema_20"] = close.ewm(span=20).mean()
        df["ema_60"] = close.ewm(span=60).mean()

        df["sma_5_20_gap"]  = (df["sma_5"]  - df["sma_20"]) / df["sma_20"] * 100
        df["sma_20_60_gap"] = (df["sma_20"] - df["sma_60"]) / df["sma_60"] * 100
        df["ema_5_20_gap"]  = (df["ema_5"]  - df["ema_20"]) / df["ema_20"] * 100

        adx = ta.trend.ADXIndicator(high, low, close, window=14)
        df["adx"] = adx.adx()
        df["adx_pos"] = adx.adx_pos()
        df["adx_neg"] = adx.adx_neg()

        # 52주 위치
        rolling_high = close.rolling(252).max()
        rolling_low  = close.rolling(252).min()
        df["week52_position"] = (
            (close - rolling_low) / (rolling_high - rolling_low + 1e-9)
        )

        # ── 변동성 ──
        bb = ta.volatility.BollingerBands(close)
        df["bb_pct"]   = bb.bollinger_pband()
        df["bb_width"] = (bb.bollinger_hband() - bb.bollinger_lband()) / close * 100
        df["bb_squeeze"] = (df["bb_width"] < df["bb_width"].rolling(20).mean()).astype(int)

        df["atr_7"]  = ta.volatility.AverageTrueRange(high, low, close, window=7).average_true_range()
        df["atr_14"] = ta.volatility.AverageTrueRange(high, low, close, window=14).average_true_range()
        df["atr_28"] = ta.volatility.AverageTrueRange(high, low, close, window=28).average_true_range()
        df["atr_pct"]    = df["atr_14"] / close * 100
        df["atr_change"] = df["atr_14"].pct_change(5) * 100

        kc = ta.volatility.KeltnerChannel(high, low, close)
        df["kc_pct"] = (close - kc.keltner_channel_lband()) / (
            kc.keltner_channel_hband() - kc.keltner_channel_lband() + 1e-9
        )

        dc = ta.volatility.DonchianChannel(high, low, close)
        df["dc_pct"] = (close - dc.donchian_channel_lband()) / (
            dc.donchian_channel_hband() - dc.donchian_channel_lband() + 1e-9
        )

        # ── 수익률/변동성 ──
        df["return_1d"] = close.pct_change(1) * 100
        df["return_5d"] = close.pct_change(5) * 100
        df["return_20d"] = close.pct_change(20) * 100
        df["vol_5d"]  = df["return_1d"].rolling(5).std()
        df["vol_20d"] = df["return_1d"].rolling(20).std()
        df["vol_60d"] = df["return_1d"].rolling(60).std()
        df["vol_ratio"] = df["vol_5d"] / (df["vol_20d"] + 1e-9)

        # 가격 가속도
        df["price_accel"] = df["return_1d"] - df["return_1d"].shift(1)

        # 갭 비율
        df["gap_ratio"] = (close - close.shift(1)) / close.shift(1) * 100

        # 고가/저가 비율
        df["hl_ratio"] = (high - low) / (close + 1e-9) * 100

        # ── 거래량 ──
        df["volume_ratio_5"]  = volume / (volume.rolling(5).mean() + 1e-9)
        df["volume_ratio_20"] = volume / (volume.rolling(20).mean() + 1e-9)
        df["volume_ratio_60"] = volume / (volume.rolling(60).mean() + 1e-9)
        df["obv_change"] = ta.volume.OnBalanceVolumeIndicator(
            close, volume).on_balance_volume().pct_change(5) * 100
        df["mfi_14"] = ta.volume.MFIIndicator(
            high, low, close, volume, window=14).money_flow_index()
        df["cmf_20"] = ta.volume.ChaikinMoneyFlowIndicator(
            high, low, close, volume, window=20).chaikin_money_flow()

        # VWAP 괴리율
        vwap = (close * volume).rolling(20).sum() / (volume.rolling(20).sum() + 1e-9)
        df["vwap_gap"] = (close - vwap) / (vwap + 1e-9) * 100

        # ── Composite Signal ──
        rsi_s  = (50 - df["rsi_14"]) / 50
        macd_s = df["macd_hist"].clip(-1, 1)
        bb_s   = (0.5 - df["bb_pct"]).clip(-0.5, 0.5) * 2
        df["composite"] = ((rsi_s + macd_s + bb_s) / 3).round(3)

        # ── 거시지표 ──
        start = str(df.index.min().date())
        end   = str((df.index.max() + pd.Timedelta(days=1)).date())
        macro = self._get_macro(start, end)

        if not macro.empty:
            df = df.join(macro, how="left")
            for col in ["vix", "tnx", "sp500_ret", "sp500_vol"]:
                if col in df.columns:
                    df[col] = df[col].ffill()
                else:
                    df[col] = 0.0
        else:
            for col in ["vix", "tnx", "sp500_ret", "sp500_vol"]:
                df[col] = 0.0

        # ── 타겟: 3-class ──
        # 5일 후 수익률 기준
        # 상승(2): +1% 초과
        # 횡보(1): -1% ~ +1%
        # 하락(0): -1% 미만
        df["future_return_5d"] = close.shift(-5) / close - 1
        df["target"] = 1  # 횡보 기본값
        df.loc[df["future_return_5d"] >  0.01, "target"] = 2  # 상승
        df.loc[df["future_return_5d"] < -0.01, "target"] = 0  # 하락

        df = df.dropna(subset=self.get_feature_cols())
        df["target"] = df["target"].astype(int)

        return df

    def get_feature_cols(self) -> list:
        return [
            # 모멘텀
            "rsi_7", "rsi_14", "rsi_28",
            "roc_5", "roc_10", "roc_20",
            "stoch_k", "stoch_d",
            "williams_r", "cci_20",
            # 추세
            "macd", "macd_signal", "macd_hist", "macd_cross",
            "sma_5_20_gap", "sma_20_60_gap", "ema_5_20_gap",
            "adx", "adx_pos", "adx_neg",
            "week52_position",
            # 변동성
            "bb_pct", "bb_width", "bb_squeeze",
            "atr_pct", "atr_change",
            "kc_pct", "dc_pct",
            # 수익률/변동성
            "return_1d", "return_5d", "return_20d",
            "vol_5d", "vol_20d", "vol_60d", "vol_ratio",
            "price_accel", "gap_ratio", "hl_ratio",
            # 거래량
            "volume_ratio_5", "volume_ratio_20", "volume_ratio_60",
            "obv_change", "mfi_14", "cmf_20", "vwap_gap",
            # Composite + 거시
            "composite",
            "vix", "tnx", "sp500_ret", "sp500_vol",
        ]