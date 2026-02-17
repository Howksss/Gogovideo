import { useState, useCallback, useEffect } from 'react'
import { api, API_BASE_URL } from './services/api'
import type { Video, User } from './types'
import { appStyles } from './components/styles'
import Header from './components/Header'
import LimitBars from './components/LimitBars'
import VideoList from './components/VideoList'
import MediaTab from './components/MediaTab'
import ReferralTab from './components/ReferralTab'
import UploadButton from './components/UploadButton'
import BottomNav from './components/BottomNav'
import MediaPlayer from './components/MediaPlayer'
import RenameSheet from './components/RenameSheet'

export default function PolishedApp() {
  const [videos, setVideos] = useState<Video[]>([])
  const [search, setSearch] = useState('')
  const [menuOpen, setMenuOpen] = useState<number | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadComplete, setUploadComplete] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')
  const [mounted, setMounted] = useState(false)
  const [pressed, setPressed] = useState<string | null>(null)
  const [renamingId, setRenamingId] = useState<number | null>(null)
  const [renameValue, setRenameValue] = useState('')
  const [userStats, setUserStats] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'videos' | 'media' | 'referrals'>('videos')
  const [mediaList, setMediaList] = useState<Video[]>([])
  const [playingMedia, setPlayingMedia] = useState<Video | null>(null)

  useEffect(() => {
    const init = async () => {
      try {
        const initData = window.Telegram?.WebApp?.initData
        if (initData) localStorage.setItem('tg_init_data', initData)

        const data = await api.auth.init(initData || '')
        if (!data.success) {
          setError(data.message || 'Не удалось загрузить данные')
          return
        }
        if (data.user) setUserStats(data.user)
        setVideos(data.videos || [])
        setMediaList(data.media || [])
      } catch (err: any) {
        console.error('Init error:', err)
        setError(err.message || 'Не удалось загрузить данные')
      } finally {
        setLoading(false)
        setMounted(true)
      }
    }
    init()
  }, [])

  useEffect(() => {
    if (menuOpen === null) return
    const close = () => setMenuOpen(null)
    document.addEventListener('click', close)
    return () => document.removeEventListener('click', close)
  }, [menuOpen])

  const getStreamUrl = useCallback((videoId: number) => {
    const initData = localStorage.getItem('tg_init_data') || ''
    return `${API_BASE_URL}/videos/${videoId}/stream?auth=${encodeURIComponent(initData)}`
  }, [])

  const pressHandlers = (id: string) => ({
    onMouseDown: () => setPressed(id),
    onMouseUp: () => setPressed(null),
    onTouchStart: () => setPressed(id),
    onTouchEnd: () => setPressed(null),
    onMouseLeave: () => pressed === id && setPressed(null),
  })

  const scaleStyle = (id: string, down = 0.97) => ({
    transform: pressed === id ? `scale(${down})` : 'scale(1)',
    transition: pressed === id
      ? 'transform 80ms ease-out'
      : 'transform 300ms var(--spring)',
  })

  const handleShare = useCallback((video: Video) => {
    if (window.Telegram?.WebApp?.switchInlineQuery) {
      window.Telegram.WebApp.switchInlineQuery(video.title, ['users', 'groups', 'channels'])
    } else {
      alert(`В Telegram откроется выбор чата для отправки: "${video.title}"`)
    }
  }, [])

  const handleDelete = useCallback((id: number) => {
    const doDelete = async () => {
      try {
        setMenuOpen(null)
        setVideos(prev => prev.filter(v => v.id !== id))
        await api.videos.delete(id)
        const [videosRes, stats] = await Promise.all([
          api.videos.list({ limit: 100, media_type: 'video' }),
          api.user.stats(),
        ])
        setVideos(videosRes.videos)
        setUserStats(stats)
        window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('success')
      } catch (err) {
        console.error('Delete error:', err)
        try {
          const videosRes = await api.videos.list({ limit: 100, media_type: 'video' })
          setVideos(videosRes.videos)
        } catch {}
        window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('error')
      }
    }
    if (window.Telegram?.WebApp?.showConfirm) {
      window.Telegram.WebApp.showConfirm('Удалить это видео?', ok => { if (ok) doDelete() })
    } else {
      doDelete()
    }
  }, [])

  const handleDeleteMedia = useCallback((id: number) => {
    const doDelete = async () => {
      try {
        setMediaList(prev => prev.filter(v => v.id !== id))
        await api.videos.delete(id)
        const stats = await api.user.stats()
        setUserStats(stats)
        window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('success')
      } catch (err) {
        console.error('Delete media error:', err)
        window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('error')
      }
    }
    if (window.Telegram?.WebApp?.showConfirm) {
      window.Telegram.WebApp.showConfirm('Удалить это медиа?', ok => { if (ok) doDelete() })
    } else {
      doDelete()
    }
  }, [])

  const handleRenameStart = useCallback((video: Video) => {
    setMenuOpen(null)
    setRenamingId(video.id)
    setRenameValue(video.title)
  }, [])

  const handleRenameSave = useCallback(async () => {
    if (renamingId === null || !renameValue.trim()) return
    try {
      const updated = await api.videos.rename(renamingId, renameValue.trim())
      setVideos(prev => prev.map(v =>
        v.id === renamingId ? { ...v, title: updated.title } : v
      ))
      window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('success')
    } catch (err) {
      console.error('Rename error:', err)
      window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('error')
    }
    setRenamingId(null)
    setRenameValue('')
  }, [renamingId, renameValue])

  const handleActivateReferral = useCallback(async (code: string) => {
    const stats = await api.user.activateReferral(code)
    setUserStats(stats)
    window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('success')
  }, [])

  const handleUpload = useCallback(async (file: File) => {
    setIsUploading(true)
    setUploadProgress(0)
    setUploadComplete(false)
    setUploadStatus('Загрузка...')
    try {
      const res = await api.videos.upload(file, (progress) => {
        setUploadProgress(Math.min(Math.round(progress * 0.9), 90))
        if (progress >= 100) setUploadStatus('Обработка...')
      })
      setUploadProgress(100)
      setUploadStatus('')
      if (res.success && res.video) {
        setVideos(prev => [res.video!, ...prev])
        const stats = await api.user.stats()
        setUserStats(stats)
        window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('success')
      } else {
        window.Telegram?.WebApp?.showAlert?.(res.message || 'Ошибка загрузки')
      }
      setUploadComplete(true)
      setTimeout(() => { setIsUploading(false); setUploadComplete(false) }, 1000)
    } catch (err: any) {
      console.error('Upload error:', err)
      setIsUploading(false)
      setUploadComplete(false)
      const msg = err.message || 'Ошибка загрузки'
      if (window.Telegram?.WebApp?.showAlert) {
        window.Telegram.WebApp.showAlert(msg)
      } else {
        alert(msg)
      }
      window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('error')
    }
  }, [])

  return (
    <>
      <style>{appStyles}</style>
      <div className="v-app grid-bg min-h-screen pb-40" style={{ color: 'var(--text)' }}>
        <Header />
        <LimitBars userStats={userStats} mounted={mounted} />

        {activeTab === 'videos' && (
          <VideoList
            videos={videos}
            search={search}
            onSearchChange={setSearch}
            loading={loading}
            error={error}
            menuOpen={menuOpen}
            pressed={pressed}
            onShare={handleShare}
            onMenuToggle={setMenuOpen}
            onRename={handleRenameStart}
            onDelete={handleDelete}
            pressHandlers={pressHandlers}
            scaleStyle={scaleStyle}
          />
        )}

        {activeTab === 'media' && (
          <MediaTab
            mediaList={mediaList}
            pressed={pressed}
            getStreamUrl={getStreamUrl}
            onPlay={setPlayingMedia}
            onDelete={handleDeleteMedia}
            pressHandlers={pressHandlers}
            scaleStyle={scaleStyle}
          />
        )}

        {activeTab === 'referrals' && (
          <ReferralTab
            userStats={userStats}
            mounted={mounted}
            onActivateReferral={handleActivateReferral}
            pressHandlers={pressHandlers}
            scaleStyle={scaleStyle}
          />
        )}

        {activeTab === 'videos' && (
          <UploadButton
            isUploading={isUploading}
            uploadProgress={uploadProgress}
            uploadComplete={uploadComplete}
            uploadStatus={uploadStatus}
            onUpload={handleUpload}
            pressHandlers={pressHandlers}
            scaleStyle={scaleStyle}
          />
        )}

        <BottomNav activeTab={activeTab} onChange={setActiveTab} />

        {playingMedia && (
          <MediaPlayer
            media={playingMedia}
            getStreamUrl={getStreamUrl}
            onClose={() => setPlayingMedia(null)}
          />
        )}

        {renamingId !== null && (
          <RenameSheet
            value={renameValue}
            onChange={setRenameValue}
            onSave={handleRenameSave}
            onClose={() => { setRenamingId(null); setRenameValue('') }}
            pressHandlers={pressHandlers}
            scaleStyle={scaleStyle}
          />
        )}
      </div>
    </>
  )
}
