import { MLPrediction } from '../api'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts'

interface Props {
  ml: MLPrediction
}

export default function MLSection({ ml }: Props) {
  const wfAuc = ml.walkforward_auc

  const reliabilityColor =
    wfAuc >= 0.55 ? 'text-green-400' :
    wfAuc >= 0.50 ? 'text-yellow-400' : 'text-red-400'

  const reliabilityText =
    wfAuc >= 0.55 ? 'High signal reliability' :
    wfAuc >= 0.50 ? 'Moderate signal reliability' :
    'Low signal reliability (difficult to predict)'

  const featureData = Object.entries(ml.top_features)
    .slice(0, 10)
    .map(([name, value]) => ({ name, value: parseFloat(value.toFixed(4)) }))
    .sort((a, b) => a.value - b.value)

  const shapData = Object.entries(ml.shap_values)
    .slice(0, 10)
    .map(([name, value]) => ({ name, value: parseFloat(value.toFixed(4)) }))
    .sort((a, b) => a.value - b.value)

  return (
    <div className="bg-gray-800 rounded-xl p-6 space-y-4">
      <h2 className="text-lg font-semibold text-white">ML Prediction</h2>

      {/* 지표 카드 */}
      <div className="grid grid-cols-5 gap-3">
        {[
          { label: 'Prediction', value: ml.prediction },
          { label: 'Prob Up', value: `${(ml.prob_up * 100).toFixed(2)}%` },
          { label: 'Accuracy', value: `${(ml.accuracy * 100).toFixed(2)}%` },
          { label: 'AUC-ROC', value: ml.auc_roc.toFixed(4) },
          { label: 'WF AUC', value: ml.walkforward_auc.toFixed(4) },
        ].map((item) => (
          <div key={item.label} className="bg-gray-700 rounded-lg p-3">
            <p className="text-xs text-gray-400">{item.label}</p>
            <p className="text-xl font-bold text-white">{item.value}</p>
          </div>
        ))}
      </div>

      {/* WF AUC 신뢰도 */}
      <p className={`text-sm font-medium ${reliabilityColor}`}>
        WF AUC {wfAuc.toFixed(4)} — {reliabilityText}
      </p>
      <p className="text-xs text-gray-400">
        Train: {ml.train_size} days / Test: {ml.test_size} days
      </p>

      {/* Feature Importance */}
      <div>
        <p className="text-sm text-gray-300 mb-2">Top 10 Feature Importance</p>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={featureData} layout="vertical"
                    margin={{ left: 100, right: 20 }}>
            <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 11 }} />
            <YAxis type="category" dataKey="name"
                   tick={{ fill: '#9ca3af', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#1f2937', border: 'none' }}
              labelStyle={{ color: '#fff' }}
            />
            <Bar dataKey="value" fill="#4f8ef7" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* SHAP Values */}
      <div>
        <p className="text-sm text-gray-300 mb-2">SHAP Values (latest prediction)</p>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={shapData} layout="vertical"
                    margin={{ left: 100, right: 20 }}>
            <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 11 }} />
            <YAxis type="category" dataKey="name"
                   tick={{ fill: '#9ca3af', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#1f2937', border: 'none' }}
              labelStyle={{ color: '#fff' }}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {shapData.map((entry, index) => (
                <Cell
                  key={index}
                  fill={entry.value >= 0 ? '#2ecc71' : '#e74c3c'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}