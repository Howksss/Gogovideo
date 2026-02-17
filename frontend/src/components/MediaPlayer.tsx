import { ChevronLeft, Download, Mic, Music } from 'lucide-react'
import { fmt, mediaTypeLabel } from './formatters'
import type { Video } from '../types'

interface Props {
  media: Video
  getStreamUrl: (id: number) => string
  onClose: () => void
}

export default function MediaPlayer({ media, getStreamUrl, onClose }: Props) {
  const url = getStreamUrl(media.id)

  return (
    <div className="fixed inset-0 z-50 flex flex-col">
      <div
        className="overlay-in absolute inset-0"
        style={{ background: 'rgba(0,0,0,0.9)' }}
        onClick={onClose}
      />

      <div className="relative z-10 flex items-center gap-3 px-4 py-3" style={{ background: 'rgba(0,0,0,0.5)' }}>
        <button
          onClick={onClose}
          className="w-10 h-10 flex items-center justify-center rounded-xl"
          style={{ background: 'rgba(255,255,255,0.1)' }}
        >
          <ChevronLeft size={22} color="#fff" />
        </button>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-white truncate">{media.title}</h3>
          <div className="text-xs" style={{ color: 'rgba(255,255,255,0.5)' }}>
            {mediaTypeLabel(media.media_type)} · {fmt.size(media.size_mb)}
          </div>
        </div>
        <button
          onClick={() => {
            const tg = (window as any).Telegram?.WebApp
            if (tg?.openLink) {
              tg.openLink(url)
            } else {
              window.open(url, '_blank')
            }
          }}
          className="w-10 h-10 flex items-center justify-center rounded-xl shrink-0"
          style={{ background: 'rgba(255,255,255,0.1)' }}
        >
          <Download size={20} color="#fff" />
        </button>
      </div>

      <div className="relative z-10 flex-1 flex items-center justify-center px-4">
        {media.media_type === 'forwarded_video' && (
          <video
            controls
            autoPlay
            playsInline
            src={url}
            className="max-w-full max-h-full rounded-xl"
            style={{ background: '#000' }}
          />
        )}
        {media.media_type === 'photo' && (
          <img
            src={url}
            alt={media.title}
            className="max-w-full max-h-full rounded-xl object-contain"
          />
        )}
        {(media.media_type === 'voice' || media.media_type === 'audio') && (
          <div className="w-full max-w-sm">
            <div
              className="w-24 h-24 mx-auto mb-6 rounded-2xl flex items-center justify-center"
              style={{ background: 'rgba(0,201,183,0.15)' }}
            >
              {media.media_type === 'voice' ? (
                <Mic size={40} style={{ color: 'var(--primary)' }} />
              ) : (
                <Music size={40} style={{ color: 'var(--primary)' }} />
              )}
            </div>
            <audio controls autoPlay src={url} className="w-full" />
          </div>
        )}
      </div>
    </div>
  )
}
