import React from 'react'
import ReactDOM from 'react-dom/client'
import PolishedApp from './PolishedApp'
import './index.css'

if (window.Telegram?.WebApp) {
  const tg = window.Telegram.WebApp
  tg.ready()
  tg.expand()
  if (tg.initData) {
    localStorage.setItem('tg_init_data', tg.initData)
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <PolishedApp />
  </React.StrictMode>,
)
