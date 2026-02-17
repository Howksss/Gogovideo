import { Play, Image, Mic, Music } from 'lucide-react'

export const fmt = {
  duration: (s: number) => {
    const h = Math.floor(s / 3600)
    const m = Math.floor((s % 3600) / 60)
    const sec = s % 60
    return h > 0
      ? `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
      : `${m}:${String(sec).padStart(2, '0')}`
  },
  size: (mb: number) => mb >= 1024 ? `${(mb / 1024).toFixed(1)} ГБ` : `${Math.round(mb)} МБ`,
  date: (iso: string) => {
    const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 86400000)
    if (diff === 0) return 'Сегодня'
    if (diff === 1) return 'Вчера'
    if (diff < 7) return `${diff} дн. назад`
    return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  },
  resolution: (h: number) => h >= 2160 ? '4K' : `${h}p`
}

export const mediaIcon = (type?: string) => {
  switch (type) {
    case 'photo': return <Image size={18} style={{ color: 'var(--primary)', opacity: 0.6 }} />
    case 'voice': return <Mic size={18} style={{ color: 'var(--primary)', opacity: 0.6 }} />
    case 'audio': return <Music size={18} style={{ color: 'var(--primary)', opacity: 0.6 }} />
    default: return <Play size={18} style={{ color: 'var(--primary)', opacity: 0.5 }} />
  }
}

export const mediaTypeLabel = (type?: string) => {
  switch (type) {
    case 'photo': return 'Фото'
    case 'voice': return 'Голосовое'
    case 'audio': return 'Аудио'
    case 'forwarded_video': return 'Видео'
    default: return 'Медиа'
  }
}
