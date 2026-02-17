import { useCallback } from 'react'
import confetti from 'canvas-confetti'

export const useConfetti = () => {
  const celebrate = useCallback(() => {
    const duration = 2 * 1000
    const animationEnd = Date.now() + duration
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 }

    const randomInRange = (min: number, max: number) => {
      return Math.random() * (max - min) + min
    }

    const interval = setInterval(() => {
      const timeLeft = animationEnd - Date.now()

      if (timeLeft <= 0) {
        return clearInterval(interval)
      }

      const particleCount = 50 * (timeLeft / duration)

      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
      })
      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
      })
    }, 250)
  }, [])

  const fireworks = useCallback(() => {
    const duration = 3 * 1000
    const animationEnd = Date.now() + duration
    const defaults = { startVelocity: 25, spread: 360, ticks: 50, zIndex: 0 }

    const randomInRange = (min: number, max: number) => {
      return Math.random() * (max - min) + min
    }

    const interval = setInterval(() => {
      const timeLeft = animationEnd - Date.now()

      if (timeLeft <= 0) {
        return clearInterval(interval)
      }

      const particleCount = 100 * (timeLeft / duration)

      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.1, 0.9), y: randomInRange(0.2, 0.5) },
        colors: ['#0088cc', '#764ba2', '#00a8ff', '#9c6ade', '#ff6b9d']
      })
    }, 400)
  }, [])

  const burst = useCallback((x: number = 0.5, y: number = 0.5) => {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { x, y },
      colors: ['#0088cc', '#764ba2', '#00a8ff']
    })
  }, [])

  return { celebrate, fireworks, burst }
}
