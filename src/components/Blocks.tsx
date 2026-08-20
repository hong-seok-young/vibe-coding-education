import type { Block } from '../content/types'
import { CodeBlock } from './CodeBlock'
import { Inline } from './Inline'

const CALLOUT: Record<string, { icon: string; ring: string; label: string }> = {
  info: { icon: 'ℹ️', ring: 'border-brand-500/40 bg-brand-500/5', label: '알아두기' },
  tip: { icon: '💡', ring: 'border-emerald-500/40 bg-emerald-500/5', label: '팁' },
  warn: { icon: '⚠️', ring: 'border-amber-500/40 bg-amber-500/5', label: '주의' },
  dx: { icon: '🛠️', ring: 'border-violet-500/40 bg-violet-500/5', label: 'dX팀 지원 포인트' },
}

export function Blocks({ blocks }: { blocks: Block[] }) {
  return (
    <div className="space-y-5">
      {blocks.map((b, i) => (
        <BlockView key={i} block={b} />
      ))}
    </div>
  )
}

function BlockView({ block }: { block: Block }) {
  switch (block.type) {
    case 'h':
      return (
        <h3 className="border-hair mt-2 border-b pb-2 text-[15px] font-semibold tracking-tight">
          <Inline text={block.text} />
        </h3>
      )
    case 'p':
      return (
        <p className="text-[14.5px] leading-7">
          <Inline text={block.text} />
        </p>
      )
    case 'ul':
      return (
        <ul className="space-y-1.5">
          {block.items.map((it, i) => (
            <li key={i} className="flex gap-2.5 text-[14.5px] leading-7">
              <span className="text-brand-500 mt-[9px] h-1.5 w-1.5 shrink-0 rounded-full bg-current" />
              <span>
                <Inline text={it} />
              </span>
            </li>
          ))}
        </ul>
      )
    case 'ol':
      return (
        <ol className="space-y-1.5">
          {block.items.map((it, i) => (
            <li key={i} className="flex gap-2.5 text-[14.5px] leading-7">
              <span className="surface-2 border-hair text-muted mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded border font-mono text-[11px]">
                {i + 1}
              </span>
              <span>
                <Inline text={it} />
              </span>
            </li>
          ))}
        </ol>
      )
    case 'code':
      return <CodeBlock code={block.code} lang={block.lang} filename={block.filename} />
    case 'callout': {
      const c = CALLOUT[block.tone]
      return (
        <div className={`rounded-xl border px-4 py-3 ${c.ring}`}>
          <div className="mb-1 flex items-center gap-2 text-[13px] font-semibold">
            <span aria-hidden>{c.icon}</span>
            <span>{block.title ?? c.label}</span>
          </div>
          <p className="text-[14px] leading-7">
            <Inline text={block.text} />
          </p>
        </div>
      )
    }
    case 'table':
      return (
        <div className="border-hair overflow-x-auto rounded-xl border">
          <table className="w-full border-collapse text-[13.5px]">
            <thead className="surface-2">
              <tr>
                {block.head.map((h, i) => (
                  <th
                    key={i}
                    className="border-hair border-b px-3 py-2 text-left font-semibold whitespace-nowrap"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {block.rows.map((r, i) => (
                <tr key={i} className="border-hair border-b last:border-0">
                  {r.map((c, j) => (
                    <td key={j} className="px-3 py-2 align-top leading-6">
                      <Inline text={c} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    case 'flow':
      return (
        <div className="border-hair surface rounded-xl border p-4">
          {block.title && <div className="text-muted mb-3 text-xs font-semibold">{block.title}</div>}
          <div className="flex flex-wrap items-stretch gap-2">
            {block.steps.map((s, i) => (
              <div key={i} className="flex items-center gap-2">
                <div className="surface-2 border-hair max-w-[220px] rounded-lg border px-3 py-2 text-[13px] leading-5">
                  <Inline text={s} />
                </div>
                {i < block.steps.length - 1 && (
                  <span className="text-brand-500 shrink-0 text-sm">→</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )
    case 'files':
      return (
        <div className="border-hair surface overflow-hidden rounded-xl border">
          <div className="border-hair surface-2 text-muted border-b px-3 py-2 font-mono text-xs">
            {block.title ?? '파일 구조'}
          </div>
          <pre className="overflow-x-auto px-4 py-3 font-mono text-[12.5px] leading-6">
            {block.tree}
          </pre>
        </div>
      )
  }
}
