import { Trash2 } from 'lucide-react'
import { fmt, mediaIcon, mediaTypeLabel } from './formatters'
import { API_BASE_URL } from '../services/api'
import type { Video } from '../types'

interface Props {
  item: Video
  index: number
  pressed: string | null
  getStreamUrl: (id: number) => string
  onPlay: (item: Video) => void
  onDelete: (id: number) => void
  pressHandlers: (id: string) => Record<string, () => void>
  scaleStyle: (id: string, down?: number) => React.CSSProperties
}

export default function MediaCard({
  item, index, pressed,
  getStreamUrl, onPlay, onDelete,
  pressHandlers, scaleStyle,
}: Props) {
  return (
    <div
      className="card-spring"
      style={{ animationDelay: `${index * 60}ms` }}
    >
      <div
        className="relative rounded-2xl"
        style={{
          background: 'var(--card)',
          border: '1px solid var(--border)',
          boxShadow: 'var(--shadow-sm)',
          transition: 'box-shadow 200ms ease, border-color 200ms ease',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.boxShadow = 'var(--shadow-md)'
          e.currentTarget.style.borderColor = 'rgba(0,201,183,0.2)'
        }}
        onMouseLeave={e => {
          e.currentTarget.style.boxShadow = 'var(--shadow-sm)'
          e.currentTarget.style.borderColor = 'var(--border)'
        }}
      >
        <button
          onClick={() => onPlay(item)}
          {...pressHandlers(`media-${item.id}`)}
          className="w-full text-left p-3 flex items-center gap-3 rounded-2xl"
          style={scaleStyle(`media-${item.id}`, 0.975)}
        >
          <div
            className="w-[50px] h-[50px] rounded-xl flex items-center justify-center flex-shrink-0 overflow-hidden"
            style={{ background: 'linear-gradient(135deg, rgba(0,201,183,0.08), rgba(0,229,208,0.12))' }}
          >
            {item.media_type === 'photo' ? (
              <img src={getStreamUrl(item.id)} alt="" className="w-full h-full object-cover" />
            ) : item.media_type === 'forwarded_video' && item.thumbnail_file_id ? (
              <img src={`${API_BASE_URL}/videos/${item.id}/thumbnail`} alt="" className="w-full h-full object-cover" />
            ) : (
              mediaIcon(item.media_type)
            )}
          </div>

          <div className="flex-1 min-w-0 pr-10">
            <h3 className="text-sm font-semibold truncate mb-0.5">{item.title}</h3>
            <div className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-2)' }}>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-medium" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}>
                {mediaTypeLabel(item.media_type)}
              </span>
              <span style={{ color: 'var(--text-3)' }}>·</span>
              <span>{fmt.size(item.size_mb)}</span>
              <span style={{ color: 'var(--text-3)' }}>·</span>
              <span>{fmt.date(item.created_at)}</span>
            </div>
          </div>
        </button>

        <div className="absolute right-1 top-1/2 -translate-y-1/2">
          <button
            onClick={e => {
              e.stopPropagation()
              onDelete(item.id)
            }}
            {...pressHandlers(`del-media-${item.id}`)}
            className="w-10 h-10 flex items-center justify-center rounded-xl"
            style={{
              background: pressed === `del-media-${item.id}` ? 'var(--danger-soft)' : 'transparent',
              ...scaleStyle(`del-media-${item.id}`, 0.85),
            }}
          >
            <Trash2 size={16} style={{ color: 'var(--text-3)' }} />
          </button>
        </div>
      </div>
    </div>
  )
}
