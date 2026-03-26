import { useState } from 'react'
import { analyzeStock, runBacktest, AnalyzeResponse, BacktestResult } from './api'
import SignalCard from './components/SignalCard'
import MLSection from './components/MLSection'
import BacktestSection from './components/BacktestSection'
import AIAnalysis from './components/AIAnalysis'

export default function App() {
  const [ticker, setTicker] = useState('AAPL')
  const [period, setPeriod] = useState('2y')
  const [btPeriod, setBtPeriod] = useState('2y')
  const [threshold, setThreshold] = useState(0.5)
  const [initialCash, setInitialCash] = useState(10_000_000)

  const [data, setData] = useState<AnalyzeResponse | null>(null)
  const [btData, setBtData] = useState<BacktestResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [btLoading, setBtLoading] = useState(false)
  const [error, setError] = useState('')

  const handleAnalyze = async () => {
    setLoading(true)
    setError('')
    setData(null)
    setBtData(null)
    try {
      const result = await analyzeStock(ticker, period)
      setData(result)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'API connection failed')
    } finally {
      setLoading(false)
    }
  }

  const handleBacktest = async () => {
    setBtLoading(true)
    try {
      const result = await runBacktest(ticker, btPeriod, threshold, initialCash)
      setBtData(result)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Backtest failed')
    } finally {
      setBtLoading(false)
    }
  }

  const sig = data?.latest_signal


  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-6 py-8">

        {/* 헤더 */}
        <h1 className="text-3xl font-bold mb-8 text-white">
          Quant Research Dashboard
        </h1>

        {/* 입력 + 사이드바 레이아웃 */}
        <div className="flex gap-6 mb-8">
          {/* 메인 입력 */}
          <div className="flex-1 bg-gray-800 rounded-xl p-6 space-y-4">
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="text-xs text-gray-400 mb-1 block">Ticker</label>
                <input
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  placeholder="AAPL / 005930.KS"
                  className="w-full bg-gray-700 rounded-lg px-4 py-2 text-white
                             border border-gray-600 focus:border-blue-500
                             focus:outline-none"
                />
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Period</label>
                <select
                  value={period}
                  onChange={(e) => setPeriod(e.target.value)}
                  className="bg-gray-700 rounded-lg px-4 py-2 text-white
                             border border-gray-600 focus:outline-none"
                >
                  {['1y', '2y', '3y'].map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
            </div>
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600
                         rounded-lg py-2 font-semibold transition-colors"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>

          {/* 백테스트 설정 */}
          <div className="w-72 bg-gray-800 rounded-xl p-6 space-y-4">
            <h3 className="text-sm font-semibold text-gray-300">
              Backtest Settings
            </h3>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Period</label>
              <select
                value={btPeriod}
                onChange={(e) => setBtPeriod(e.target.value)}
                className="w-full bg-gray-700 rounded-lg px-3 py-2 text-white
                           border border-gray-600 focus:outline-none text-sm"
              >
                {['1y', '2y', '3y'].map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">
                ML Threshold: {threshold}
              </label>
              <input type="range" min={0.3} max={0.7} step={0.05}
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="w-full accent-blue-500"
              />
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">
                Initial Cash
              </label>
              <input
                type="number"
                value={initialCash}
                onChange={(e) => setInitialCash(Number(e.target.value))}
                className="w-full bg-gray-700 rounded-lg px-3 py-2 text-white
                           border border-gray-600 focus:outline-none text-sm"
              />
            </div>
            <button
              onClick={handleBacktest}
              disabled={btLoading}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600
                         rounded-lg py-2 font-semibold text-sm transition-colors"
            >
              {btLoading ? 'Running...' : 'Run Backtest'}
            </button>
          </div>
        </div>

        {/* 에러 */}
        {error && (
          <div className="bg-red-900 border border-red-500 rounded-xl p-4 mb-6">
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}

        {/* 로딩 */}
        {loading && (
          <div className="text-center py-20">
            <p className="text-gray-400 text-lg animate-pulse">
              Fetching data and running ML model...
            </p>
          </div>
        )}

        {/* 결과 */}
        {data && sig && (
          <div className="space-y-6">
            {/* 신호 헤더 */}
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-bold">{data.ticker}</h2>
              <span className={`text-2xl font-bold
                ${sig.signal === 'Up' ? 'text-green-400' : 'text-red-400'}`}>
                {sig.signal === 'Up' ? '▲' : '▼'} {sig.signal}
              </span>
            </div>

            {/* 기술 지표 */}
            <div className="grid grid-cols-5 gap-3">
              <SignalCard label="Close" value={sig.close.toLocaleString()} />
              <SignalCard label="RSI" value={sig.rsi.toFixed(1)} />
              <SignalCard label="MACD Hist" value={sig.macd_hist.toFixed(4)} />
              <SignalCard label="BB %" value={sig.bb_pct.toFixed(3)} />
              <SignalCard label="Composite" value={sig.composite.toFixed(3)}
                color={sig.composite > 0.1 ? 'green' :
                       sig.composite < -0.1 ? 'red' : 'default'} />
            </div>

            {/* 펀더멘털 */}
            <div className="bg-gray-800 rounded-xl p-4">
              <details>
                <summary className="text-sm text-gray-300 cursor-pointer">
                  Fundamentals
                </summary>
                <div className="grid grid-cols-4 gap-3 mt-3">
                  {[
                    { label: '52W High', value: data.fundamentals['52w_high'] },
                    { label: '52W Low', value: data.fundamentals['52w_low'] },
                    { label: 'Market Cap', value: data.fundamentals['market_cap'] },
                    { label: 'Last Price', value: data.fundamentals['last_price'] },
                  ].map((f) => (
                    <div key={f.label} className="bg-gray-700 rounded-lg p-3">
                      <p className="text-xs text-gray-400">{f.label}</p>
                      <p className="text-sm font-bold text-white">
                        {f.value ? Number(f.value).toLocaleString() : 'N/A'}
                      </p>
                    </div>
                  ))}
                </div>
              </details>
            </div>

            {/* ML 예측 */}
            <MLSection ml={data.ml_prediction} />

            {/* AI 분석 + 뉴스 */}
            <AIAnalysis
              analysis={data.ai_analysis}
              news={data.news}
            />
          </div>
        )}

        {/* 백테스트 결과 */}
        {btData && (
          <div className="mt-6">
            <BacktestSection bt={btData} />
          </div>
        )}
      </div>
    </div>
  )
}