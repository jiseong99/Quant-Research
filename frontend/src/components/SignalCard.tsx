interface Props {
  label: string
  value: string | number
  sub?: string
  color?: 'green' | 'red' | 'yellow' | 'default'
}

export default function SignalCard({ label, value, sub, color = 'default' }: Props) {
  const colorMap = {
    green: 'border-green-500 bg-green-950',
    red: 'border-red-500 bg-red-950',
    yellow: 'border-yellow-500 bg-yellow-950',
    default: 'border-gray-700 bg-gray-800',
  }

  return (
    <div className={`rounded-xl border p-4 ${colorMap[color]}`}>
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}