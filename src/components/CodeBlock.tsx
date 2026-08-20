import { useCopy } from '../lib/useCopy'

interface Props {
  code: string
  lang?: string
  filename?: string
}

export function CodeBlock({ code, lang, filename }: Props) {
  const { copied, copy } = useCopy()
  const label = filename ?? lang ?? 'code'

  return (
    <div className="border-hair surface overflow-hidden rounded-xl border">
      <div className="border-hair surface-2 flex items-center justify-between gap-3 border-b px-3 py-2">
        <span className="text-muted truncate font-mono text-xs">{label}</span>
        <button
          type="button"
          onClick={() => copy(code)}
          className="border-hair text-muted hover:text-brand-500 hover:border-brand-500/50 shrink-0 rounded-md border px-2 py-1 text-xs transition"
        >
          {copied ? '복사됨 ✓' : '복사'}
        </button>
      </div>
      <pre className="overflow-x-auto px-4 py-3 text-[13px] leading-relaxed">
        <code className="font-mono">{code}</code>
      </pre>
    </div>
  )
}
