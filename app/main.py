from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.data_collector import DataCollector
from app.feature_engineer import FeatureEngineer
from app.ml_model import MLModel
from app.backtester import Backtester
from app.rag_analyzer import RAGAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Quant Research API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://quant-research-1.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dc  = DataCollector()
fe  = FeatureEngineer()
bt  = Backtester()
rag = RAGAnalyzer()


@app.get("/analyze/{ticker}")
def analyze(ticker: str, period: str = "2y"):
    try:
        df = dc.get_price_data(ticker, period)
        if df.empty:
            raise HTTPException(404, f"No data found for {ticker}")
        df = fe.generate(df)
        feature_cols = fe.get_feature_cols()
        return {
            "ticker": ticker,
            "rows": len(df),
            "feature_cols": feature_cols,
            "feature_count": len(feature_cols),
            "sample": df[feature_cols + ["target"]].tail(5).to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/predict/{ticker}")
def predict(ticker: str, period: str = "2y"):
    try:
        df = dc.get_price_data(ticker, period)
        if df.empty:
            raise HTTPException(404, f"No data found for {ticker}")
        df = fe.generate(df)
        feature_cols = fe.get_feature_cols()
        ml = MLModel()
        result = ml.train_and_predict(df, feature_cols)
        return {
            "ticker": ticker,
            "prediction":     result["prediction"],
            "prob_up":        result["prob_up"],
            "prob_neutral":   result["prob_neutral"],
            "prob_down":      result["prob_down"],
            "accuracy":       result["accuracy"],
            "auc_roc":        result["auc_roc"],
            "walkforward_auc": result["walkforward_auc"],
            "train_size":     result["train_size"],
            "test_size":      result["test_size"],
            "top_features":   dict(list(result["feature_importance"].items())[:10]),
            "shap_values":    result["shap_values"],
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/backtest/{ticker}")
def backtest(ticker: str, period: str = "2y",
             threshold: float = 0.5,
             initial_cash: float = 10_000_000):
    try:
        df = dc.get_price_data(ticker, period)
        if df.empty:
            raise HTTPException(404, f"No data found for {ticker}")
        df = fe.generate(df)
        feature_cols = fe.get_feature_cols()
        ml = MLModel()
        ml.train(df, feature_cols)
        df["prob_up"] = ml.predict_all(df)
        bt_result = bt.run(
            df, prob_up_col="prob_up",
            threshold=threshold,
            initial_cash=initial_cash
        )
        return {"ticker": ticker, "period": period, **bt_result}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/analyze/{ticker}")
def analyze(ticker: str, period: str = "2y"):
    try:
        normalized = dc.normalize_ticker(ticker)
        logger.info(f"[analyze] {ticker} -> {normalized}")

        df = dc.get_price_data(ticker, period)
        if df.empty:
            raise HTTPException(404, f"No data found for {ticker}")

        fundamentals = dc.get_fundamentals(ticker)
        news         = dc.get_news(ticker)

        df = fe.generate(df)
        feature_cols = fe.get_feature_cols()

        ml = MLModel()
        ml_result = ml.train_and_predict(df, feature_cols)

        df["prob_up"] = ml.predict_all(df)
        bt_result = bt.run(df, prob_up_col="prob_up")

        latest = df.iloc[-1]
        signals = {
            "rsi":       round(float(latest["rsi_14"]), 1),
            "macd_hist": round(float(latest["macd_hist"]), 4),
            "bb_pct":    round(float(latest["bb_pct"]), 3),
            "composite": float(latest["composite"]),
            "signal":    ml_result["prediction"],
        }

        ai_analysis = rag.analyze(
            ticker=ticker,
            signals={
                **signals,
                "prob_up":        ml_result["prob_up"],
                "prob_neutral":   ml_result["prob_neutral"],
                "prob_down":      ml_result["prob_down"],
                "accuracy":       ml_result["accuracy"],
                "walkforward_auc": ml_result["walkforward_auc"],
                "top_features":   list(ml_result["feature_importance"].keys())[:5],
            },
            fundamentals=fundamentals,
            news=news,
        )

        return {
            "ticker": normalized,
            "fundamentals": fundamentals,
            "latest_signal": {
                "date":  str(latest.name.date()),
                "close": round(float(latest["Close"]), 2),
                **signals,
            },
            "ml_prediction": {
                "prediction":      ml_result["prediction"],
                "prob_up":         ml_result["prob_up"],
                "prob_neutral":    ml_result["prob_neutral"],
                "prob_down":       ml_result["prob_down"],
                "accuracy":        ml_result["accuracy"],
                "auc_roc":         ml_result["auc_roc"],
                "walkforward_auc": ml_result["walkforward_auc"],
                "train_size":      ml_result["train_size"],
                "test_size":       ml_result["test_size"],
                "top_features":    dict(list(
                    ml_result["feature_importance"].items())[:10]),
                "shap_values":     ml_result["shap_values"],
            },
            "backtest": {
                "ticker": normalized,
                "period": period,
                **bt_result,
            },
            "news":        news,
            "ai_analysis": ai_analysis,
        }
    except Exception as e:
        logger.error(f"[analyze] Error: {e}")
        raise HTTPException(500, str(e))


@app.get("/health")
def health():
    return {"status": "ok"}