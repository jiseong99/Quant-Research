import { BacktestResult } from '../api'
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Legend
} from 'recharts'

interface Props {
  bt: BacktestResult
}

export default function BacktestSection({ bt }: Props) {
  const chartData = bt.cumulative_returns?.map((d) => ({
    date: new Date(d.date).toLocaleDateString(),
    Strategy: parseFloat(d.cumulative_strategy.toFixed(4)),
    'Buy & Hold': parseFloat(d.cumulative_bah.toFixed(4)),
  })) ?? []

  const metrics = [
    { label: 'Total Return', value: `${bt.total_return_pct}%`,
      delta: bt.total_return_pct - bt.buy_and_hold_pct },
    { label: 'Buy & Hold', value: `${bt.buy_and_hold_pct}%` },
    { label: 'Sharpe Ratio', value: bt.sharpe_ratio },
    { label: 'Max Drawdown', value: `${bt.max_drawdown_pct}%` },
    { label: 'Win Rate', value: `${bt.win_rate}%` },
  ]

  return (
    <div className="bg-gray-800 rounded-xl p-6 space-y-4">
      <h2 className="text-lg font-semibold text-white">
        Backtest Results — {bt.ticker} ({bt.period})
      </h2>

      {/* 지표 카드 */}
      <div className="grid grid-cols-5 gap-3">
        {metrics.map((m) => (
          <div key={m.label} className="bg-gray-700 rounded-lg p-3">
            <p className="text-xs text-gray-400">{m.label}</p>
            <p className="text-xl font-bold text-white">{m.value}</p>
            {m.delta !== undefined && (
              <p className={`text-xs mt-1 ${m.delta >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {m.delta >= 0 ? '+' : ''}{m.delta.toFixed(2)}% vs B&H
              </p>
            )}
          </div>
        ))}
      </div>

      {/* 누적 수익률 차트 */}
      <div>
        <p className="text-sm text-gray-300 mb-2">
          Cumulative Return: ML Strategy vs Buy & Hold
        </p>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <XAxis dataKey="date"
                   tick={{ fill: '#9ca3af', fontSize: 10 }}
                   interval={Math.floor(chartData.length / 6)} />
            <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#1f2937', border: 'none' }}
              labelStyle={{ color: '#fff' }}
            />
            <Legend wrapperStyle={{ color: '#9ca3af' }} />
            <Line type="monotone" dataKey="Strategy"
                  stroke="#2ecc71" dot={false} strokeWidth={2} />
            <Line type="monotone" dataKey="Buy & Hold"
                  stroke="#e74c3c" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}