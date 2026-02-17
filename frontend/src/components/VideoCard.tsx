import { Play, MoreVertical, Pencil, Trash2 } from 'lucide-react'
import { fmt } from './formatters'
import { API_BASE_URL } from '../services/api'
import type { Video } from '../types'

interface Props {
  video: Video
  index: number
  menuOpen: boolean
  pressed: string | null
  onShare: (video: Video) => void
  onMenuToggle: (id: number | null) => void
  onRename: (video: Video) => void
  onDelete: (id: number) => void
  pressHandlers: (id: string) => Record<string, () => void>
  scaleStyle: (id: string, down?: number) => React.CSSProperties
}

export default function VideoCard({
  video, index, menuOpen, pressed,
  onShare, onMenuToggle, onRename, onDelete,
  pressHandlers, scaleStyle,
}: Props) {
  return (
    <div
      className="card-spring"
      style={{
        animationDelay: `${index * 60}ms`,
        position: 'relative',
        zIndex: menuOpen ? 50 : 1,
      }}
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
          onClick={() => onShare(video)}
          {...pressHandlers(`card-${video.id}`)}
          className="w-full text-left p-3 flex items-center gap-3 rounded-2xl"
          style={scaleStyle(`card-${video.id}`, 0.975)}
        >
          <div
            className="w-[72px] h-[50px] rounded-xl flex items-center justify-center flex-shrink-0 relative overflow-hidden"
            style={{ background: 'linear-gradient(135deg, rgba(0,201,183,0.08), rgba(0,229,208,0.12))' }}
          >
            {video.thumbnail_file_id ? (
              <img
                src={`${API_BASE_URL}/videos/${video.id}/thumbnail`}
                alt=""
                className="w-full h-full object-cover"
                style={{ position: 'absolute', inset: 0 }}
              />
            ) : (
              <Play size={18} style={{ color: 'var(--primary)', opacity: 0.5 }} />
            )}
            {video.duration != null && (
              <div
                className="absolute bottom-0.5 right-0.5 px-1 py-px rounded text-[9px] font-bold"
                style={{ background: 'rgba(0,0,0,0.65)', color: '#fff' }}
              >
                {fmt.duration(video.duration)}
              </div>
            )}
          </div>

          <div className="flex-1 min-w-0 pr-10">
            <h3 className="text-sm font-semibold truncate mb-0.5">{video.title}</h3>
            <div className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-2)' }}>
              <span>{fmt.size(video.size_mb)}</span>
              <span style={{ color: 'var(--text-3)' }}>·</span>
              <span>{fmt.date(video.created_at)}</span>
            </div>
          </div>
        </button>

        <div className="absolute right-1 top-1/2 -translate-y-1/2">
          <button
            onClick={e => {
              e.stopPropagation()
              onMenuToggle(menuOpen ? null : video.id)
            }}
            {...pressHandlers(`dot-${video.id}`)}
            className="w-10 h-10 flex items-center justify-center rounded-xl"
            style={{
              background: pressed === `dot-${video.id}` ? 'var(--primary-soft)' : 'transparent',
              ...scaleStyle(`dot-${video.id}`, 0.85),
            }}
          >
            <MoreVertical size={20} style={{ color: 'var(--text-2)' }} />
          </button>

          {menuOpen && (
            <div
              className="menu-pop absolute right-0 top-full mt-1.5 z-[60] py-1.5 rounded-xl min-w-[180px]"
              style={{
                background: 'var(--card)',
                border: '1px solid var(--border)',
                boxShadow: 'var(--shadow-lg)',
              }}
              onClick={e => e.stopPropagation()}
            >
              <button
                onClick={() => onRename(video)}
                className="w-full px-4 py-2.5 text-left text-sm font-medium flex items-center gap-3"
                style={{ transition: 'background 120ms ease' }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--primary-soft)'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                <Pencil size={16} style={{ color: 'var(--primary)' }} />
                Переименовать
              </button>
              <button
                onClick={() => onDelete(video.id)}
                className="w-full px-4 py-2.5 text-left text-sm font-medium flex items-center gap-3"
                style={{ color: 'var(--danger)', transition: 'background 120ms ease' }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--danger-soft)'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                <Trash2 size={16} />
                Удалить
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
