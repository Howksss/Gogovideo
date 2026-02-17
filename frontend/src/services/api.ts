import axios, { AxiosError } from 'axios'
import type { AuthResponse, VideoListResponse, UploadResponse, User, Video, InitResponse } from '../types'

export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  try {
    const initData = localStorage.getItem('tg_init_data')
    if (initData) {
      config.headers.Authorization = initData
    }
  } catch {
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.code === 'ECONNABORTED') {
      error.message = 'Request timed out. Please try again.'
    } else if (!error.response) {
      error.message = 'Network error. Check your connection.'
    }
    return Promise.reject(error)
  }
)

export const api = {
  auth: {
    validate: async (initData: string): Promise<AuthResponse> => {
      const response = await apiClient.post<AuthResponse>('/auth/validate', {
        init_data: initData,
      })
      return response.data
    },
    init: async (initData: string): Promise<InitResponse> => {
      const response = await apiClient.post<InitResponse>('/auth/init', {
        init_data: initData,
      })
      return response.data
    },
  },

  videos: {
    list: async (params?: { limit?: number; offset?: number; search?: string; media_type?: string }): Promise<VideoListResponse> => {
      const response = await apiClient.get<VideoListResponse>('/videos', { params })
      return response.data
    },

    upload: async (file: File, onProgress?: (progress: number) => void): Promise<UploadResponse> => {
      const formData = new FormData()
      formData.append('file', file)

      const response = await apiClient.post<UploadResponse>('/videos/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 600000,
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total && onProgress) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            onProgress(progress)
          }
        },
      })

      return response.data
    },

    delete: async (videoId: number): Promise<{ success: boolean; message: string }> => {
      const response = await apiClient.delete(`/videos/${videoId}`)
      return response.data
    },

    rename: async (videoId: number, title: string): Promise<Video> => {
      const response = await apiClient.patch<Video>(`/videos/${videoId}`, { title })
      return response.data
    },
  },

  user: {
    stats: async (): Promise<User> => {
      const response = await apiClient.get<User>('/user/stats')
      return response.data
    },

    usage: async (days: number = 30) => {
      const response = await apiClient.get('/user/usage', { params: { days } })
      return response.data
    },

    activateReferral: async (code: string): Promise<User> => {
      const response = await apiClient.post<User>('/user/activate-referral', { code })
      return response.data
    },
  },
}
