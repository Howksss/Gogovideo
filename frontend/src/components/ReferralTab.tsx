import { useState } from 'react'
import { Copy, Check, Gift, Users, Loader2 } from 'lucide-react'
import { fmt } from './formatters'
import type { User } from '../types'

interface Props {
  userStats: User | null
  mounted: boolean
  onActivateReferral: (code: string) => Promise<void>
  pressHandlers: (id: string) => Record<string, () => void>
  scaleStyle: (id: string, down?: number) => React.CSSProperties
}

export default function ReferralTab({
  userStats, mounted,
  onActivateReferral,
  pressHandlers, scaleStyle,
}: Props) {
  const [copied, setCopied] = useState(false)
  const [refCode, setRefCode] = useState('')
  const [refActivating, setRefActivating] = useState(false)
  const [refError, setRefError] = useState('')

  const handleActivate = async () => {
    if (!refCode.trim()) return
    setRefActivating(true)
    setRefError('')
    try {
      await onActivateReferral(refCode.trim())
      setRefCode('')
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Ошибка активации'
      setRefError(msg)
    } finally {
      setRefActivating(false)
    }
  }

  return (
    <div className="px-4 space-y-3 float-up">
      <div
        className="rounded-2xl p-4"
        style={{ background: 'var(--card)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}
      >
        <h3 className="text-sm font-bold mb-1">Ваша реферальная ссылка</h3>
        <p className="text-xs mb-3" style={{ color: 'var(--text-2)' }}>
          Поделитесь ссылкой — получите бонус к дневному лимиту
        </p>
        <div className="flex items-center gap-2">
          <div
            className="flex-1 px-3 py-2.5 rounded-xl text-xs font-medium truncate"
            style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-2)' }}
          >
            {userStats?.referral_link || '...'}
          </div>
          <button
            onClick={() => {
              if (userStats?.referral_link) {
                navigator.clipboard.writeText(userStats.referral_link)
                setCopied(true)
                setTimeout(() => setCopied(false), 2000)
                window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('success')
              }
            }}
            {...pressHandlers('copy-ref')}
            className="px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-1.5 flex-shrink-0"
            style={{
              background: copied ? 'var(--success)' : 'linear-gradient(135deg, var(--primary), #00E5D0)',
              color: '#fff',
              boxShadow: 'var(--shadow-sm)',
              ...scaleStyle('copy-ref', 0.95),
            }}
          >
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? 'Скопировано' : 'Копировать'}
          </button>
        </div>
      </div>

      {!userStats?.is_referred && (
        <div
          className="rounded-2xl p-4"
          style={{ background: 'var(--card)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}
        >
          <h3 className="text-sm font-bold mb-1">Есть код друга?</h3>
          <p className="text-xs mb-3" style={{ color: 'var(--text-2)' }}>
            Активируйте и получите +1 ГБ/день к лимиту загрузки
          </p>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={refCode}
              onChange={e => { setRefCode(e.target.value); setRefError('') }}
              placeholder="Вставьте ссылку или код"
              className="flex-1 px-3 py-2.5 rounded-xl text-xs"
              style={{
                background: 'var(--bg)',
                border: `1px solid ${refError ? 'var(--danger)' : 'var(--border)'}`,
                color: 'var(--text)',
                outline: 'none',
              }}
            />
            <button
              onClick={handleActivate}
              disabled={refActivating || !refCode.trim()}
              className="px-4 py-2.5 rounded-xl text-xs font-bold flex-shrink-0"
              style={{
                background: refActivating || !refCode.trim()
                  ? 'var(--border)'
                  : 'linear-gradient(135deg, var(--primary), #00E5D0)',
                color: refActivating || !refCode.trim() ? 'var(--text-3)' : '#fff',
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              {refActivating ? <Loader2 size={14} className="animate-spin" /> : 'Активировать'}
            </button>
          </div>
          {refError && (
            <p className="text-xs mt-1.5" style={{ color: 'var(--danger)' }}>{refError}</p>
          )}
        </div>
      )}

      <div
        className="rounded-2xl p-4"
        style={{ background: 'var(--card)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}
      >
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-bold">Приглашено</h3>
          <span className="text-sm font-bold" style={{ color: 'var(--primary)' }}>
            {userStats?.referral_count ?? 0}/{userStats?.referral_max ?? 10}
          </span>
        </div>
        <div className="h-2 rounded-full overflow-hidden mb-3" style={{ background: 'var(--border)' }}>
          <div
            className={mounted ? 'bar-spring h-full rounded-full' : 'h-full rounded-full'}
            style={{
              width: `${((userStats?.referral_count ?? 0) / (userStats?.referral_max ?? 10)) * 100}%`,
              background: 'linear-gradient(90deg, var(--primary), #00E5D0)',
            }}
          />
        </div>
        <div className="space-y-2.5">
          <div className="flex items-center gap-2.5 text-xs" style={{ color: 'var(--text-2)' }}>
            <Gift size={14} style={{ color: 'var(--primary)', flexShrink: 0 }} />
            <span>+0.2 ГБ/день за каждого приглашённого</span>
          </div>
          {userStats?.is_referred && (
            <div className="flex items-center gap-2.5 text-xs" style={{ color: 'var(--success)' }}>
              <Check size={14} style={{ flexShrink: 0 }} />
              <span>Ваш лимит увеличен на +1 ГБ/день</span>
            </div>
          )}
          {(userStats?.referral_bonus_mb ?? 0) > 0 && (
            <div className="flex items-center gap-2.5 text-xs" style={{ color: 'var(--text-2)' }}>
              <Users size={14} style={{ color: 'var(--primary)', flexShrink: 0 }} />
              <span>Бонус от рефералов: <span style={{ color: 'var(--primary)', fontWeight: 600 }}>+{fmt.size(userStats!.referral_bonus_mb)}/день</span></span>
            </div>
          )}
        </div>
      </div>

      <div
        className="rounded-2xl p-4"
        style={{ background: 'var(--card)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}
      >
        <h3 className="text-sm font-bold mb-2">Как это работает</h3>
        <div className="space-y-2 text-xs" style={{ color: 'var(--text-2)' }}>
          <p>1. Скопируйте реферальную ссылку и отправьте другу</p>
          <p>2. Друг вставляет ссылку в поле выше или переходит по ней</p>
          <p>3. Вы получаете +0.2 ГБ/день, друг — +1 ГБ/день</p>
          <p>4. Бонусы не сгорают и не имеют срока годности</p>
        </div>
      </div>
    </div>
  )
}
