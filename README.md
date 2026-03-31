# Quant Research Dashboard

An AI-powered quantitative research tool that collects and analyzes financial data — including price history, technical indicators, volume, and news — to generate quantitative signals and investment insights.

## 🔗 Live Demo

- **Frontend**: https://quant-research-1.onrender.com
- **Backend API**: https://quant-research-442q.onrender.com/docs

---

## 🧠 Key Features

### 📊 Data Collection
- Real-time price, volume, and fundamental data via **Yahoo Finance**
- Supports both **US stocks** (e.g. `AAPL`) and **Korean stocks** (e.g. `005930.KS`)
- Macro indicators: **VIX**, **10Y Treasury Yield**, **S&P 500 returns**
- Latest news headlines per ticker

### ⚙️ Feature Engineering (50+ features)
- **Momentum**: RSI-7/14/28, ROC-5/10/20, Stochastic K/D, Williams %R, CCI
- **Trend**: MACD, SMA/EMA gaps, ADX, 52-week position
- **Volatility**: Bollinger Bands, ATR, Keltner Channel, Donchian Channel
- **Volume**: OBV, MFI, CMF, VWAP gap, volume ratios
- **Macro**: VIX, TNX, S&P500 return & volatility
- **Composite Signal**: rule-based signal used as an additional ML feature

### 🤖 Machine Learning (XGBoost)
- **3-class classification**: Up / Neutral / Down (based on 5-day forward return)
- **Walk-forward validation** to prevent data leakage
- **SHAP values** for model explainability
- Feature importance visualization

### 📈 Backtesting Engine
- Pure **pandas-based** backtesting (no Backtrader dependency)
- Metrics: Cumulative Return, Sharpe Ratio, Max Drawdown, Win Rate
- Comparison against **Buy & Hold** benchmark
- Cumulative return chart

### 🧾 RAG + AI Analysis
- **FAISS**-based vector search over recent news
- **LLaMA 3.3-70B** (via Groq API) for natural language analysis
- Structured output: market summary, risk factors, ML model insight, outlook
- **Citation-style references** ([1], [2], [3]) linked to source articles

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.11 |
| ML Model | XGBoost, scikit-learn, SHAP |
| Feature Engineering | pandas, ta (Technical Analysis) |
| Data Source | yfinance (Yahoo Finance) |
| AI / LLM | Groq API (LLaMA 3.3-70B) |
| RAG | FAISS, newspaper3k |
| Frontend | React, TypeScript, Vite |
| UI Styling | Tailwind CSS |
| Charts | Recharts |
| Deployment | Render (Docker + Static Site) |

---

## 📁 Project Structure
```
quant-research/
├── app/
│   ├── data_collector.py      # yfinance data collection
│   ├── feature_engineer.py    # 50+ feature generation
│   ├── ml_model.py            # XGBoost 3-class classifier
│   ├── backtester.py          # pandas-based backtesting
│   ├── rag_analyzer.py        # FAISS + Groq LLM analysis
│   ├── schemas.py             # Pydantic response schemas
│   └── main.py                # FastAPI server & endpoints
├── frontend/
│   └── src/
│       ├── App.tsx
│       ├── api.ts
│       └── components/
│           ├── MLSection.tsx
│           ├── BacktestSection.tsx
│           ├── AIAnalysis.tsx
│           └── SignalCard.tsx
├── Dockerfile
├── requirements.txt
└── dashboard.py               # Streamlit prototype (legacy)
```

---

## 🚀 Getting Started (Local)

### Prerequisites
- Python 3.11+
- Node.js 20+
- Groq API Key (free at https://console.groq.com)

### Backend Setup
```bash
git clone https://github.com/jiseong99/Quant-Research.git
cd Quant-Research

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Create .env file
echo GROQ_API_KEY=your_key_here > .env

uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/analyze/{ticker}` | Full analysis: signals + ML + backtest + AI |
| GET | `/predict/{ticker}` | ML prediction only |
| GET | `/backtest/{ticker}` | Backtest results only |
| GET | `/features/{ticker}` | Raw feature data |
| GET | `/health` | Health check |

**Example:**
```
GET /analyze/AAPL?period=2y
GET /analyze/005930.KS?period=1y
```

---

## 📌 Usage Guide

1. Enter a ticker symbol (e.g. `AAPL`, `005930.KS`, `TSLA`)
2. Select a time period (1y / 2y / 3y)
3. Click **Analyze** to run the full pipeline
4. Review:
   - Technical indicators (RSI, MACD, BB, Composite Signal)
   - ML prediction with probability scores and SHAP values
   - AI-generated analysis with news citations
5. Use **Run Backtest** in the sidebar to evaluate strategy performance

> **Note**: WF AUC ≥ 0.55 indicates high signal reliability for a given ticker. Lower values suggest the ticker is difficult to predict with technical indicators alone.

---

## ⚠️ Disclaimer

This tool is for **research and educational purposes only**. It does not constitute financial advice. Past performance of backtested strategies does not guarantee future results. Always do your own research before making investment decisions.

---

## 📄 License

MIT License
