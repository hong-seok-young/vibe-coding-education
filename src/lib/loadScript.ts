/**
 * 외부 스크립트를 한 번만 로드한다.
 *
 * 이 앱은 백엔드가 없는 정적 사이트이므로, 구글 실연동 데모는 브라우저에서 직접
 * 구글 스크립트를 불러야 한다. 그런데 배포 환경에 따라 외부 스크립트가 아예
 * 차단되는 경우가 있어(콘텐츠 보안 정책), 실패를 구분해서 알려줄 수 있어야 한다.
 */
const cache = new Map<string, Promise<void>>()

export class ScriptBlocked extends Error {
  constructor(public url: string) {
    super('외부 스크립트를 불러올 수 없습니다: ' + url)
  }
}

export function loadScript(url: string, timeoutMs = 10_000): Promise<void> {
  const hit = cache.get(url)
  if (hit) return hit

  const p = new Promise<void>((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(`script[src="${url}"]`)
    if (existing?.dataset.loaded === 'true') {
      resolve()
      return
    }

    const el = existing ?? document.createElement('script')
    const timer = setTimeout(() => reject(new ScriptBlocked(url)), timeoutMs)

    el.addEventListener('load', () => {
      clearTimeout(timer)
      el.dataset.loaded = 'true'
      resolve()
    })
    el.addEventListener('error', () => {
      clearTimeout(timer)
      reject(new ScriptBlocked(url))
    })

    if (!existing) {
      el.src = url
      el.async = true
      document.head.appendChild(el)
    }
  })

  // 실패는 캐시하지 않는다 (재시도 가능해야 한다)
  cache.set(
    url,
    p.catch((e) => {
      cache.delete(url)
      throw e
    }),
  )
  return cache.get(url)!
}
