from pydantic import BaseModel
from typing import Optional


class LatestSignal(BaseModel):
    date: str
    close: float
    rsi: float
    macd_hist: float
    bb_pct: float
    composite: float
    signal: str


class MLPrediction(BaseModel):
    prediction: str
    prob_up: float
    prob_down: float
    accuracy: float
    auc_roc: float
    train_size: int
    test_size: int
    top_features: dict
    shap_values: dict


class BacktestResult(BaseModel):
    ticker: str
    period: str
    initial_cash: float
    final_value: float
    total_return_pct: float
    buy_and_hold_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    total_trades: int
    win_rate: float


class AnalyzeResponse(BaseModel):
    ticker: str
    fundamentals: dict
    latest_signal: LatestSignal
    ml_prediction: MLPrediction
    backtest: BacktestResult
    ai_analysis: str
    news: list