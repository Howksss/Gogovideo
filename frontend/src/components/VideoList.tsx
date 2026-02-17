import { Search, X, Upload, Loader2, AlertCircle } from 'lucide-react'
import VideoCard from './VideoCard'
import type { Video } from '../types'

interface Props {
  videos: Video[]
  search: string
  onSearchChange: (value: string) => void
  loading: boolean
  error: string | null
  menuOpen: number | null
  pressed: string | null
  onShare: (video: Video) => void
  onMenuToggle: (id: number | null) => void
  onRename: (video: Video) => void
  onDelete: (id: number) => void
  pressHandlers: (id: string) => Record<string, () => void>
  scaleStyle: (id: string, down?: number) => React.CSSProperties
}

export default function VideoList({
  videos, search, onSearchChange, loading, error,
  menuOpen, pressed,
  onShare, onMenuToggle, onRename, onDelete,
  pressHandlers, scaleStyle,
}: Props) {
  const filtered = videos.filter(v =>
    v.title.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <>
      <div className="px-4 pb-3">
        <div
          className="search-box flex items-center gap-3 px-4 py-2.5 rounded-xl"
          style={{
            background: 'var(--card)',
            border: '1.5px solid var(--border)',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <Search size={18} style={{ color: 'var(--text-3)', flexShrink: 0 }} />
          <input
            type="text"
            value={search}
            onChange={e => onSearchChange(e.target.value)}
            placeholder="Поиск видео..."
            className="flex-1 bg-transparent text-sm font-medium outline-none"
            style={{ color: 'var(--text)' }}
          />
          {search && (
            <button
              onClick={() => onSearchChange('')}
              {...pressHandlers('x-search')}
              className="p-1 rounded-full"
              style={{
                background: 'var(--border)',
                ...scaleStyle('x-search', 0.85),
              }}
            >
              <X size={12} style={{ color: 'var(--text-2)' }} />
            </button>
          )}
        </div>
      </div>

      <div className="px-4 space-y-2.5">
        {loading ? (
          <div className="float-up py-20 text-center">
            <Loader2 size={36} className="mx-auto mb-4 animate-spin" style={{ color: 'var(--primary)' }} />
            <p className="text-sm" style={{ color: 'var(--text-2)' }}>Загрузка...</p>
          </div>
        ) : error ? (
          <div className="float-up py-20 text-center">
            <AlertCircle size={36} className="mx-auto mb-5" style={{ color: 'var(--danger)' }} />
            <p className="text-lg font-bold mb-1">Ошибка</p>
            <p className="text-sm" style={{ color: 'var(--text-2)' }}>{error}</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="float-up py-20 text-center">
            <Upload size={36} className="mx-auto mb-5" style={{ color: 'var(--primary)' }} />
            <p className="text-lg font-bold mb-1">
              {search ? 'Ничего не найдено' : 'Пока пусто'}
            </p>
            <p className="text-sm" style={{ color: 'var(--text-2)' }}>
              {search ? 'Попробуйте другой запрос' : 'Загрузите первое видео'}
            </p>
          </div>
        ) : (
          filtered.map((video, idx) => (
            <VideoCard
              key={video.id}
              video={video}
              index={idx}
              menuOpen={menuOpen === video.id}
              pressed={pressed}
              onShare={onShare}
              onMenuToggle={onMenuToggle}
              onRename={onRename}
              onDelete={onDelete}
              pressHandlers={pressHandlers}
              scaleStyle={scaleStyle}
            />
          ))
        )}
      </div>
    </>
  )
}
