export interface User {
  user_id: number
  daily_uploaded_mb: number
  daily_limit_mb: number
  daily_percentage: number
  video_count: number
  referral_link: string
  referral_count: number
  referral_max: number
  referral_bonus_mb: number
  is_referred: boolean
  daily_streamed_mb: number
  daily_stream_limit_mb: number
}

export interface Video {
  id: number
  file_id: string
  thumbnail_file_id?: string
  title: string
  size_mb: number
  duration?: number
  width?: number
  height?: number
  mime_type?: string
  media_type?: 'video' | 'forwarded_video' | 'photo' | 'voice' | 'audio'
  created_at: string
  user_id: number
}

export interface VideoListResponse {
  videos: Video[]
  total: number
  limit: number
  offset: number
}

export interface UploadResponse {
  success: boolean
  message: string
  video?: Video
}

export interface AuthResponse {
  success: boolean
  user?: User
  message?: string
}

export interface InitResponse {
  success: boolean
  user?: User
  videos: Video[]
  media: Video[]
  message?: string
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        ready: () => void
        expand: () => void
        close: () => void
        initData: string
        initDataUnsafe: {
          user?: {
            id: number
            first_name: string
            last_name?: string
            username?: string
            language_code?: string
          }
        }
        MainButton: {
          text: string
          color: string
          textColor: string
          isVisible: boolean
          isActive: boolean
          isProgressVisible: boolean
          setText: (text: string) => void
          show: () => void
          hide: () => void
          enable: () => void
          disable: () => void
          showProgress: (leaveActive?: boolean) => void
          hideProgress: () => void
          onClick: (callback: () => void) => void
          offClick: (callback: () => void) => void
        }
        BackButton: {
          isVisible: boolean
          show: () => void
          hide: () => void
          onClick: (callback: () => void) => void
          offClick: (callback: () => void) => void
        }
        HapticFeedback: {
          impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void
          notificationOccurred: (type: 'error' | 'success' | 'warning') => void
          selectionChanged: () => void
        }
        showAlert: (message: string) => void
        showConfirm: (message: string, callback?: (confirmed: boolean) => void) => void
        switchInlineQuery: (query: string, choose_chat_types?: string[]) => void
        showPopup: (params: any, callback?: (buttonId: string) => void) => void
        themeParams: {
          bg_color?: string
          text_color?: string
          hint_color?: string
          link_color?: string
          button_color?: string
          button_text_color?: string
          secondary_bg_color?: string
        }
      }
    }
  }
}
