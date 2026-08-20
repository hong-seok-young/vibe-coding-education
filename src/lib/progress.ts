import { useCallback, useEffect, useState } from 'react'

const KEY = 'vibe-edu:progress:v1'

type ProgressMap = Record<string, { done: boolean; checked: number[] }>

function read(): ProgressMap {
  try {
    const raw = localStorage.getItem(KEY)
    return raw ? (JSON.parse(raw) as ProgressMap) : {}
  } catch {
    return {}
  }
}

function write(map: ProgressMap) {
  try {
    localStorage.setItem(KEY, JSON.stringify(map))
  } catch {
    /* 사파리 프라이빗 모드 등 — 진행상황 저장 실패는 조용히 무시 */
  }
  window.dispatchEvent(new Event('vibe-edu:progress'))
}

export function useProgress() {
  const [map, setMap] = useState<ProgressMap>(() => read())

  useEffect(() => {
    const sync = () => setMap(read())
    window.addEventListener('vibe-edu:progress', sync)
    window.addEventListener('storage', sync)
    return () => {
      window.removeEventListener('vibe-edu:progress', sync)
      window.removeEventListener('storage', sync)
    }
  }, [])

  const isDone = useCallback((id: string) => !!map[id]?.done, [map])

  const toggleDone = useCallback((id: string) => {
    const next = read()
    const cur = next[id] ?? { done: false, checked: [] }
    next[id] = { ...cur, done: !cur.done }
    write(next)
  }, [])

  const checked = useCallback((id: string) => map[id]?.checked ?? [], [map])

  const toggleCheck = useCallback((id: string, index: number) => {
    const next = read()
    const cur = next[id] ?? { done: false, checked: [] }
    const set = new Set(cur.checked)
    set.has(index) ? set.delete(index) : set.add(index)
    next[id] = { ...cur, checked: [...set].sort((a, b) => a - b) }
    write(next)
  }, [])

  const reset = useCallback(() => write({}), [])

  return { isDone, toggleDone, checked, toggleCheck, reset, map }
}
