interface Props {
  analysis: string
  news: Array<{ title: string; url: string }>
}

export default function AIAnalysis({ analysis, news }: Props) {
  const lines = analysis.split('\n')

  return (
    <div className="space-y-4">
      {/* AI 분석 */}
      <div className="bg-gray-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">AI Analysis</h2>
        <div className="text-sm text-gray-300 leading-relaxed space-y-2">
          {lines.map((line, i) => {
            if (!line.trim()) return null
            // Sources 섹션 처리
            if (line.startsWith('**Sources:**')) {
              return (
                <p key={i} className="text-gray-400 font-medium mt-4">
                  Sources:
                </p>
              )
            }
            // citation 링크 처리 [1] [2] [3]
            if (line.match(/^\[\d+\]/)) {
              const match = line.match(/\[(\d+)\]\s*\[(.+)\]\((.+)\)/)
              if (match) {
                return (
                  <p key={i}>
                    <span className="text-gray-400">[{match[1]}] </span>
                    <a href={match[3]} target="_blank" rel="noreferrer"
                       className="text-blue-400 hover:text-blue-300 underline">
                      {match[2]}
                    </a>
                  </p>
                )
              }
            }
            // 볼드 텍스트 처리
            const boldProcessed = line.replace(
              /\*\*(.+?)\*\*/g,
              '<strong class="text-white">$1</strong>'
            )
            return (
              <p key={i}
                 dangerouslySetInnerHTML={{ __html: boldProcessed }} />
            )
          })}
        </div>
      </div>

      {/* 최신 뉴스 */}
      <div className="bg-gray-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Latest News</h2>
        <ul className="space-y-2">
          {news.map((n, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="text-gray-500 text-sm mt-0.5">•</span>
              <a href={n.url} target="_blank" rel="noreferrer"
                 className="text-blue-400 hover:text-blue-300 text-sm underline">
                {n.title}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}