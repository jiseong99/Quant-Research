import pandas as pd
import numpy as np


class Backtester:
    def run(self, df: pd.DataFrame, prob_up_col: str = "prob_up",
            threshold: float = 0.5,
            initial_cash: float = 10_000_000) -> dict:

        df = df.copy()

        # ML 확률 기반 signal 생성 (미래정보 누수 방지: shift(1))
        df["signal"] = (df[prob_up_col] > threshold).astype(int).shift(1)
        df = df.dropna(subset=["signal"])

        # 일간 수익률
        df["return_1d"] = df["Close"].pct_change()
        df = df.dropna(subset=["return_1d"])

        # 전략 수익률
        df["strategy_return"] = df["signal"] * df["return_1d"]

        # 누적 수익률
        df["cumulative_strategy"] = (1 + df["strategy_return"]).cumprod()
        df["cumulative_bah"] = (1 + df["return_1d"]).cumprod()

        # 최종 수익률
        total_return = (df["cumulative_strategy"].iloc[-1] - 1) * 100
        bah_return = (df["cumulative_bah"].iloc[-1] - 1) * 100

        # Sharpe Ratio (연간화)
        sharpe = 0.0
        if df["strategy_return"].std() > 0:
            sharpe = (df["strategy_return"].mean() /
                      df["strategy_return"].std() * np.sqrt(252))

        # Max Drawdown
        rolling_max = df["cumulative_strategy"].cummax()
        drawdown = (df["cumulative_strategy"] - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100

        # 거래 분석
        trades = df[df["signal"] == 1]
        win_trades = trades[trades["strategy_return"] > 0]
        win_rate = len(win_trades) / len(trades) * 100 if len(trades) > 0 else 0

        final_value = initial_cash * df["cumulative_strategy"].iloc[-1]

        return {
            "initial_cash": initial_cash,
            "final_value": round(final_value, 2),
            "total_return_pct": round(total_return, 2),
            "buy_and_hold_pct": round(bah_return, 2),
            "sharpe_ratio": round(sharpe, 3),
            "max_drawdown_pct": round(max_drawdown, 2),
            "total_trades": len(trades),
            "win_rate": round(win_rate, 2),
            "cumulative_returns": df[["cumulative_strategy", "cumulative_bah"]]
                                    .reset_index()
                                    .rename(columns={"index": "date"})
                                    .to_dict(orient="records"),
        }