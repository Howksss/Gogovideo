import { Upload, Eye, Users } from 'lucide-react'

type Tab = 'videos' | 'media' | 'referrals'

interface Props {
  activeTab: Tab
  onChange: (tab: Tab) => void
}

export default function BottomNav({ activeTab, onChange }: Props) {
  const tabs: { id: Tab; icon: typeof Upload; label: string; activeColor: string }[] = [
    { id: 'videos', icon: Upload, label: 'Загрузка', activeColor: 'var(--primary)' },
    { id: 'media', icon: Eye, label: 'Просмотр', activeColor: 'var(--purple)' },
    { id: 'referrals', icon: Users, label: 'Рефералы', activeColor: 'var(--primary)' },
  ]

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-40"
      style={{
        background: 'rgba(255,255,255,0.95)',
        backdropFilter: 'blur(12px)',
        borderTop: '1px solid var(--border)',
      }}
    >
      <div className="flex">
        {tabs.map(({ id, icon: Icon, label, activeColor }) => (
          <button
            key={id}
            onClick={() => onChange(id)}
            className="flex-1 flex flex-col items-center gap-1 py-3"
            style={{
              color: activeTab === id ? activeColor : 'var(--text-3)',
              transition: 'color 200ms ease',
            }}
          >
            <Icon size={20} />
            <span className="text-[11px] font-semibold">{label}</span>
          </button>
        ))}
      </div>
    </nav>
  )
}
