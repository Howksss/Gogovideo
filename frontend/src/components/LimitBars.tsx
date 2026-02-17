import { Upload, Eye } from 'lucide-react'
import { fmt } from './formatters'
import type { User } from '../types'

interface Props {
  userStats: User | null
  mounted: boolean
}

export default function LimitBars({ userStats, mounted }: Props) {
  const dailyUsed = userStats?.daily_uploaded_mb ?? 0
  const dailyTotal = userStats?.daily_limit_mb ?? 1
  const pct = userStats?.daily_percentage ?? 0
  const streamedMb = userStats?.daily_streamed_mb ?? 0
  const streamLimitMb = userStats?.daily_stream_limit_mb ?? 3072
  const streamPct = Math.min((streamedMb / streamLimitMb) * 100, 100)

  return (
    <div className="px-4 pt-3 pb-2">
      <div
        className="px-4 py-3 rounded-2xl space-y-2.5"
        style={{
          background: 'var(--card)',
          boxShadow: 'var(--shadow-sm)',
          border: '1px solid var(--border)',
        }}
      >
        <div className="flex items-center gap-3">
          <Upload size={14} className="flex-shrink-0" style={{ color: pct > 80 ? 'var(--danger)' : 'var(--primary)' }} />
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-semibold">
                {pct > 90
                  ? 'Лимит загрузки почти исчерпан'
                  : <>Загружено {fmt.size(dailyUsed)} <span style={{ color: 'var(--text-3)', fontWeight: 400 }}>из {fmt.size(dailyTotal)}</span></>
                }
              </span>
            </div>
            <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
              <div
                className={mounted ? 'bar-spring h-full rounded-full' : 'h-full rounded-full'}
                style={{
                  width: `${pct}%`,
                  background: pct > 80
                    ? 'linear-gradient(90deg, var(--warm), var(--danger))'
                    : 'linear-gradient(90deg, var(--primary), #00E5D0)',
                }}
              />
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Eye size={14} className="flex-shrink-0" style={{ color: 'var(--purple)' }} />
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-semibold">
                Просмотрено {fmt.size(streamedMb)} <span style={{ color: 'var(--text-3)', fontWeight: 400 }}>из {fmt.size(streamLimitMb)}</span>
              </span>
            </div>
            <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
              <div
                className={mounted ? 'bar-spring h-full rounded-full' : 'h-full rounded-full'}
                style={{
                  width: `${streamPct}%`,
                  background: 'linear-gradient(90deg, #8B5CF6, #A78BFA)',
                }}
              />
            </div>
          </div>
        </div>

        <div className="text-[10px]" style={{ color: 'var(--text-3)' }}>Обновляется ежедневно в 00:00 МСК</div>
      </div>
    </div>
  )
}
