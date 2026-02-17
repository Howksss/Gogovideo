import { useEffect, useRef } from 'react'

interface Props {
  value: string
  onChange: (value: string) => void
  onSave: () => void
  onClose: () => void
  pressHandlers: (id: string) => Record<string, () => void>
  scaleStyle: (id: string, down?: number) => React.CSSProperties
}

export default function RenameSheet({
  value, onChange, onSave, onClose,
  pressHandlers, scaleStyle,
}: Props) {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    setTimeout(() => inputRef.current?.focus(), 100)
  }, [])

  return (
    <div className="fixed inset-0 z-50 flex flex-col justify-end">
      <div
        className="overlay-in absolute inset-0"
        style={{ background: 'rgba(0,0,0,0.35)', backdropFilter: 'blur(4px)' }}
        onClick={onClose}
      />

      <div
        className="sheet-up relative rounded-t-3xl px-5 pb-6"
        style={{ background: 'var(--card)', boxShadow: '0 -4px 32px rgba(0,0,0,0.12)' }}
      >
        <div className="flex justify-center pt-3 pb-4">
          <div className="w-9 h-1 rounded-full" style={{ background: 'var(--border)' }} />
        </div>

        <h2 className="text-lg font-bold mb-1">Переименовать</h2>
        <p className="text-sm mb-4" style={{ color: 'var(--text-2)' }}>
          Короткое имя — быстрее найти и отправить
        </p>

        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={e => onChange(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter') onSave()
            if (e.key === 'Escape') onClose()
          }}
          className="rename-input w-full px-4 py-3 rounded-xl text-sm font-medium"
          style={{ background: 'var(--bg)', border: '1.5px solid var(--border)', color: 'var(--text)' }}
          placeholder="Новое название..."
        />

        <div className="flex gap-3 mt-4">
          <button
            onClick={onClose}
            {...pressHandlers('rename-cancel')}
            className="flex-1 py-3.5 rounded-xl font-bold text-sm"
            style={{ background: 'var(--bg)', color: 'var(--text-2)', ...scaleStyle('rename-cancel', 0.96) }}
          >
            Отмена
          </button>
          <button
            onClick={onSave}
            {...pressHandlers('rename-save')}
            className="flex-[2] py-3.5 rounded-xl font-bold text-sm"
            style={{
              background: value.trim()
                ? 'linear-gradient(135deg, var(--primary), #00E5D0)'
                : 'var(--border)',
              color: value.trim() ? '#fff' : 'var(--text-3)',
              boxShadow: value.trim() ? 'var(--shadow-sm)' : 'none',
              ...scaleStyle('rename-save', 0.97),
            }}
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
  )
}
