import { useRef } from 'react'
import { Upload, Check } from 'lucide-react'

interface Props {
  isUploading: boolean
  uploadProgress: number
  uploadComplete: boolean
  uploadStatus: string
  onUpload: (file: File) => void
  pressHandlers: (id: string) => Record<string, () => void>
  scaleStyle: (id: string, down?: number) => React.CSSProperties
}

export default function UploadButton({
  isUploading, uploadProgress, uploadComplete, uploadStatus,
  onUpload, pressHandlers, scaleStyle,
}: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  return (
    <div className="fixed bottom-[68px] left-4 right-4 z-30">
      <button
        onClick={() => { if (!isUploading) fileInputRef.current?.click() }}
        {...(!isUploading ? pressHandlers('upload') : {})}
        disabled={isUploading}
        className="w-full py-4 rounded-2xl font-bold text-sm flex items-center justify-center gap-2.5"
        style={{
          background: isUploading
            ? 'var(--card)'
            : 'linear-gradient(135deg, var(--primary), #00E5D0)',
          color: isUploading ? 'var(--text)' : '#fff',
          border: isUploading ? '1px solid var(--border)' : 'none',
          boxShadow: isUploading ? 'var(--shadow-sm)' : undefined,
          ...(!isUploading ? scaleStyle('upload', 0.97) : {}),
        }}
      >
        {isUploading ? (
          uploadComplete ? (
            <div className="check-bounce flex items-center gap-2">
              <Check size={20} style={{ color: 'var(--success)' }} />
              <span className="font-bold" style={{ color: 'var(--success)' }}>Готово!</span>
            </div>
          ) : (
            <>
              <svg width="22" height="22" className="progress-ring">
                <circle cx="11" cy="11" r="8" stroke="var(--border)" strokeWidth="2.5" />
                <circle
                  cx="11" cy="11" r="8"
                  stroke="var(--primary)"
                  strokeWidth="2.5"
                  strokeDasharray={2 * Math.PI * 8}
                  strokeDashoffset={(2 * Math.PI * 8) - (uploadProgress / 100) * (2 * Math.PI * 8)}
                  style={{ transition: 'stroke-dashoffset 80ms ease-out' }}
                />
              </svg>
              <span className="tabular-nums font-semibold">{uploadProgress}%</span>
              {uploadStatus && uploadProgress >= 90 && (
                <span className="text-xs ml-1" style={{ color: 'var(--text-2)' }}>{uploadStatus}</span>
              )}
            </>
          )
        ) : (
          <>
            <Upload size={18} strokeWidth={2.5} />
            <span>Загрузить видео</span>
          </>
        )}
      </button>
      <input
        ref={fileInputRef}
        type="file"
        accept="video/*"
        className="hidden"
        onChange={e => {
          const file = e.target.files?.[0]
          if (file) {
            onUpload(file)
            e.target.value = ''
          }
        }}
      />
    </div>
  )
}
