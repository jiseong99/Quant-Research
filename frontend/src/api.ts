import axios from 'axios'

const API = axios.create({ baseURL: 'http://localhost:8000' })

export interface LatestSignal {
  date: string
  close: number
  rsi: number
  macd_hist: number
  bb_pct: number
  composite: number
  signal: string
}

export interface MLPrediction {
  prediction: string
  prob_up: number
  prob_down: number
  accuracy: number
  auc_roc: number
  walkforward_auc: number
  train_size: number
  test_size: number
  top_features: Record<string, number>
  shap_values: Record<string, number>
}

export interface BacktestResult {
  ticker: string
  period: string
  initial_cash: number
  final_value: number
  total_return_pct: number
  buy_and_hold_pct: number
  sharpe_ratio: number
  max_drawdown_pct: number
  total_trades: number
  win_rate: number
  cumulative_returns: Array<{
    date: string
    cumulative_strategy: number
    cumulative_bah: number
  }>
}

export interface AnalyzeResponse {
  ticker: string
  fundamentals: Record<string, number | null>
  latest_signal: LatestSignal
  ml_prediction: MLPrediction
  backtest: BacktestResult
  news: Array<{ title: string; url: string }>
  ai_analysis: string
}

export const analyzeStock = async (
  ticker: string,
  period: string
): Promise<AnalyzeResponse> => {
  const res = await API.get(`/analyze/${ticker}`, { params: { period } })
  return res.data
}

export const runBacktest = async (
  ticker: string,
  period: string,
  threshold: number,
  initialCash: number
): Promise<BacktestResult> => {
  const res = await API.get(`/backtest/${ticker}`, {
    params: { period, threshold, initial_cash: initialCash },
  })
  return res.data
}