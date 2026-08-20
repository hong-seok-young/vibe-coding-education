import type { ReactNode } from 'react'

/**
 * 아주 작은 인라인 렌더러.
 * `코드`, **강조**, [링크](url) 세 가지만 지원한다. (마크다운 파서 의존성 없이)
 */
export function Inline({ text }: { text: string }) {
  const out: ReactNode[] = []
  const re = /`([^`]+)`|\*\*([^*]+)\*\*|\[([^\]]+)\]\(([^)]+)\)/g
  let last = 0
  let m: RegExpExecArray | null
  let key = 0

  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(text.slice(last, m.index))
    if (m[1]) {
      out.push(
        <code
          key={key++}
          className="surface-2 border-hair rounded border px-1.5 py-0.5 font-mono text-[0.85em]"
        >
          {m[1]}
        </code>,
      )
    } else if (m[2]) {
      out.push(
        <strong key={key++} className="font-semibold">
          {m[2]}
        </strong>,
      )
    } else if (m[3] && m[4]) {
      const href = m[4]
      const external = /^https?:\/\//.test(href)
      out.push(
        <a
          key={key++}
          href={href}
          target={external ? '_blank' : undefined}
          rel={external ? 'noreferrer noopener' : undefined}
          className="text-brand-500 underline decoration-brand-500/40 underline-offset-2 hover:decoration-brand-500"
        >
          {m[3]}
        </a>,
      )
    }
    last = m.index + m[0].length
  }
  if (last < text.length) out.push(text.slice(last))
  return <>{out}</>
}
