import { useEffect, useState } from 'react'

const KEY = 'vibe-edu:theme'
export type Theme = 'light' | 'dark'

export function initTheme(): Theme {
  let saved: string | null = null
  try {
    saved = localStorage.getItem(KEY)
  } catch {
    /* noop */
  }

  // 호스트가 테마를 지정한 경우(아티팩트 뷰어 등) 그 값을 먼저 따른다.
  const hosted = document.documentElement.dataset.theme

  const theme: Theme =
    saved === 'light' || saved === 'dark'
      ? saved
      : hosted === 'light' || hosted === 'dark'
        ? hosted
        : window.matchMedia('(prefers-color-scheme: light)').matches
          ? 'light'
          : 'dark'

  document.documentElement.classList.toggle('dark', theme === 'dark')
  return theme
}

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => initTheme())

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    try {
      localStorage.setItem(KEY, theme)
    } catch {
      /* noop */
    }
  }, [theme])

  return { theme, toggle: () => setTheme((t) => (t === 'dark' ? 'light' : 'dark')) }
}
