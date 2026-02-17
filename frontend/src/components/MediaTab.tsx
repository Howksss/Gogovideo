import { Eye } from 'lucide-react'
import MediaCard from './MediaCard'
import type { Video } from '../types'

interface Props {
  mediaList: Video[]
  pressed: string | null
  getStreamUrl: (id: number) => string
  onPlay: (item: Video) => void
  onDelete: (id: number) => void
  pressHandlers: (id: string) => Record<string, () => void>
  scaleStyle: (id: string, down?: number) => React.CSSProperties
}

export default function MediaTab({
  mediaList, pressed, getStreamUrl,
  onPlay, onDelete, pressHandlers, scaleStyle,
}: Props) {
  return (
    <div className="px-4 space-y-2.5">
      <div className="text-xs px-1" style={{ color: 'var(--text-3)' }}>
        Перешлите видео, фото или голосовое в бота — они появятся здесь
      </div>

      {mediaList.length === 0 ? (
        <div className="float-up py-16 text-center">
          <Eye size={36} className="mx-auto mb-5" style={{ color: 'var(--purple)' }} />
          <p className="text-lg font-bold mb-1">Пока пусто</p>
          <p className="text-sm" style={{ color: 'var(--text-2)' }}>
            Перешлите медиа боту в чат
          </p>
        </div>
      ) : (
        mediaList.map((item, idx) => (
          <MediaCard
            key={item.id}
            item={item}
            index={idx}
            pressed={pressed}
            getStreamUrl={getStreamUrl}
            onPlay={onPlay}
            onDelete={onDelete}
            pressHandlers={pressHandlers}
            scaleStyle={scaleStyle}
          />
        ))
      )}
    </div>
  )
}
