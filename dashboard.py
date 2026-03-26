import streamlit as st
import plotly.graph_objects as go
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Quant Research", layout="wide")
st.title("Quant Research Dashboard")

# 사이드바
with st.sidebar:
    st.header("Backtest Settings")
    bt_period = st.selectbox("Backtest period", ["1y", "2y", "3y"], index=1)
    initial_cash = st.number_input("Initial cash", value=10_000_000, step=1_000_000)
    threshold = st.slider("ML threshold", 0.3, 0.7, 0.5, 0.05)
    run_backtest = st.button("Run Backtest", type="primary")

# 메인
col1, col2 = st.columns([3, 1])
with col1:
    ticker = st.text_input("Enter ticker", value="AAPL",
                           placeholder="AAPL / 005930.KS / 005930")
with col2:
    period = st.selectbox("Period", ["1y", "2y", "3y"], index=1)

if st.button("Analyze", type="primary"):
    with st.spinner("Fetching data and running ML model..."):
        try:
            res = requests.get(f"{API_URL}/analyze/{ticker}",
                               params={"period": period}, timeout=120)
            data = res.json()
        except Exception as e:
            st.error(f"API connection failed: {e}")
            st.stop()

    if res.status_code != 200:
        st.error(f"Error: {data.get('detail', 'Unknown error')}")
        st.stop()

    sig = data["latest_signal"]
    fund = data["fundamentals"]
    ml = data["ml_prediction"]

    # 신호 헤더
    emoji = "🟢" if sig["signal"] == "Up" else "🔴"
    st.subheader(f"{data['ticker']}  {emoji} {sig['signal']}")

    # 기술 지표
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Close", f"{sig['close']:,.2f}")
    m2.metric("RSI", f"{sig['rsi']:.1f}")
    m3.metric("MACD Hist", f"{sig['macd_hist']:.4f}")
    m4.metric("BB %", f"{sig['bb_pct']:.3f}")
    m5.metric("Composite", f"{sig['composite']:.3f}")

    # ML 예측
    st.subheader("ML Prediction")
    p1, p2, p3, p4, p5 = st.columns(5)
    p1.metric("Prediction", ml["prediction"])
    p2.metric("Prob Up", f"{ml['prob_up']:.2%}")
    p3.metric("Accuracy", f"{ml['accuracy']:.2%}")
    p4.metric("AUC-ROC", f"{ml['auc_roc']:.4f}")
    p5.metric("WF AUC", f"{ml.get('walkforward_auc', 0):.4f}")

    # WF AUC 신뢰도 표시
    wf_auc = ml.get("walkforward_auc", 0)
    if wf_auc >= 0.55:
        st.success(f"WF AUC {wf_auc:.4f} — High signal reliability")
    elif wf_auc >= 0.50:
        st.warning(f"WF AUC {wf_auc:.4f} — Moderate signal reliability")
    else:
        st.error(f"WF AUC {wf_auc:.4f} — Low signal reliability (this ticker is difficult to predict)")

    st.caption(f"Train: {ml['train_size']} days / Test: {ml['test_size']} days")

    # Feature 중요도
    with st.expander("Feature Importance & SHAP"):
        fi_df = pd.DataFrame(
            list(ml["top_features"].items()),
            columns=["Feature", "Importance"]
        ).sort_values("Importance", ascending=True)

        fig_fi = go.Figure(go.Bar(
            x=fi_df["Importance"], y=fi_df["Feature"],
            orientation="h", marker_color="#4f8ef7"
        ))
        fig_fi.update_layout(title="Top 10 Feature Importance",
                             height=350, margin=dict(t=40, b=20))
        st.plotly_chart(fig_fi, use_container_width=True)

        shap_df = pd.DataFrame(
            list(ml["shap_values"].items()),
            columns=["Feature", "SHAP"]
        ).sort_values("SHAP", ascending=True)

        fig_shap = go.Figure(go.Bar(
            x=shap_df["SHAP"], y=shap_df["Feature"],
            orientation="h",
            marker_color=["#2ecc71" if v > 0 else "#e74c3c"
                          for v in shap_df["SHAP"]]
        ))
        fig_shap.update_layout(title="SHAP Values (latest prediction)",
                               height=350, margin=dict(t=40, b=20))
        st.plotly_chart(fig_shap, use_container_width=True)

    # 펀더멘털
    with st.expander("Fundamentals"):
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("52W High", f"{fund.get('52w_high', 'N/A'):,}"
                  if fund.get('52w_high') else "N/A")
        f2.metric("52W Low", f"{fund.get('52w_low', 'N/A'):,}"
                  if fund.get('52w_low') else "N/A")
        f3.metric("Market Cap", f"{fund.get('market_cap', 0):,.0f}"
                  if fund.get('market_cap') else "N/A")
        f4.metric("Last Price", f"{fund.get('last_price', 'N/A'):,}"
                  if fund.get('last_price') else "N/A")

    # AI 분석
    if "ai_analysis" in data:
        st.subheader("AI Analysis")
        st.info(data["ai_analysis"])

    # 뉴스
    st.subheader("Latest News")
    for news in data["news"]:
        st.markdown(f"- [{news['title']}]({news['url']})")

# 백테스트
if run_backtest:
    with st.spinner("Running backtest..."):
        try:
            res = requests.get(f"{API_URL}/backtest/{ticker}",
                               params={
                                   "period": bt_period,
                                   "threshold": threshold,
                                   "initial_cash": initial_cash,
                               }, timeout=120)
            bt_data = res.json()
        except Exception as e:
            st.error(f"Backtest failed: {e}")
            st.stop()

    if res.status_code != 200:
        st.error(f"Backtest error: {bt_data.get('detail', 'Unknown error')}")
        st.stop()

    st.divider()
    st.subheader(f"Backtest Results - {ticker} ({bt_period})")

    b1, b2, b3, b4, b5 = st.columns(5)
    b1.metric("Total Return", f"{bt_data['total_return_pct']}%",
              delta=f"{bt_data['total_return_pct'] - bt_data['buy_and_hold_pct']:.2f}% vs B&H")
    b2.metric("Buy & Hold", f"{bt_data['buy_and_hold_pct']}%")
    b3.metric("Sharpe Ratio", f"{bt_data['sharpe_ratio']}")
    b4.metric("Max Drawdown", f"{bt_data['max_drawdown_pct']}%")
    b5.metric("Win Rate", f"{bt_data['win_rate']}%")

    # 누적 수익률 차트
    if "cumulative_returns" in bt_data:
        cum_df = pd.DataFrame(bt_data["cumulative_returns"])
        cum_df["date"] = pd.to_datetime(cum_df["date"])

        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(
            x=cum_df["date"], y=cum_df["cumulative_strategy"],
            name="ML Strategy", line=dict(color="#2ecc71", width=2)
        ))
        fig_cum.add_trace(go.Scatter(
            x=cum_df["date"], y=cum_df["cumulative_bah"],
            name="Buy & Hold", line=dict(color="#e74c3c", width=2)
        ))
        fig_cum.update_layout(
            title="Cumulative Return: ML Strategy vs Buy & Hold",
            height=400, margin=dict(t=40, b=20)
        )
        st.plotly_chart(fig_cum, use_container_width=True)