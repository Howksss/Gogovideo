export const getTelegramTheme = () => {
  if (typeof window === 'undefined' || !window.Telegram?.WebApp) {
    return null
  }

  return window.Telegram.WebApp.themeParams
}

export const isDarkTheme = () => {
  const theme = getTelegramTheme()
  if (!theme) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  }

  const bgColor = theme.bg_color || '#ffffff'
  const rgb = parseInt(bgColor.replace('#', ''), 16)
  const r = (rgb >> 16) & 0xff
  const g = (rgb >> 8) & 0xff
  const b = (rgb >> 0) & 0xff
  const brightness = (r * 299 + g * 587 + b * 114) / 1000

  return brightness < 128
}

export const applyTelegramTheme = () => {
  const theme = getTelegramTheme()
  if (!theme) return

  const root = document.documentElement

  if (theme.bg_color) root.style.setProperty('--tg-bg', theme.bg_color)
  if (theme.text_color) root.style.setProperty('--tg-text', theme.text_color)
  if (theme.hint_color) root.style.setProperty('--tg-hint', theme.hint_color)
  if (theme.link_color) root.style.setProperty('--tg-link', theme.link_color)
  if (theme.button_color) root.style.setProperty('--tg-button', theme.button_color)
  if (theme.button_text_color) root.style.setProperty('--tg-button-text', theme.button_text_color)
  if (theme.secondary_bg_color) root.style.setProperty('--tg-secondary-bg', theme.secondary_bg_color)

  const isDark = isDarkTheme()
  if (isDark) {
    root.style.setProperty('--gradient-start', '#00a8ff')
    root.style.setProperty('--gradient-end', '#9c6ade')
    root.style.setProperty('--glass-bg', 'rgba(0, 0, 0, 0.3)')
    root.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.1)')
  } else {
    root.style.setProperty('--gradient-start', '#0088cc')
    root.style.setProperty('--gradient-end', '#764ba2')
    root.style.setProperty('--glass-bg', 'rgba(255, 255, 255, 0.1)')
    root.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.2)')
  }
}

export const triggerHaptic = (style: 'light' | 'medium' | 'heavy' | 'success' | 'warning' | 'error' = 'medium') => {
  if (typeof window === 'undefined' || !window.Telegram?.WebApp?.HapticFeedback) {
    return
  }

  const haptic = window.Telegram.WebApp.HapticFeedback

  switch (style) {
    case 'light':
      haptic.impactOccurred('light')
      break
    case 'medium':
      haptic.impactOccurred('medium')
      break
    case 'heavy':
      haptic.impactOccurred('heavy')
      break
    case 'success':
      haptic.notificationOccurred('success')
      break
    case 'warning':
      haptic.notificationOccurred('warning')
      break
    case 'error':
      haptic.notificationOccurred('error')
      break
  }
}
