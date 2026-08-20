import { useState } from 'react'
import type { Prompt } from '../content/types'
import { useCopy } from '../lib/useCopy'
import { Inline } from './Inline'

export function PromptCard({ prompt, index }: { prompt: Prompt; index: number }) {
  const { copied, copy } = useCopy()
  const [open, setOpen] = useState(true)

  return (
    <div className="border-hair surface overflow-hidden rounded-xl border">
      <div className="border-hair surface-2 flex flex-wrap items-center justify-between gap-3 border-b px-4 py-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="bg-brand-500/15 text-brand-500 rounded px-1.5 py-0.5 font-mono text-[11px] font-semibold">
              PROMPT {index + 1}
            </span>
            <h3 className="truncate text-[14px] font-semibold">{prompt.label}</h3>
          </div>
          <p className="text-muted mt-1 text-[12.5px] leading-5">
            <Inline text={prompt.when} />
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            className="border-hair text-muted hover:text-brand-500 rounded-md border px-2 py-1.5 text-xs transition"
          >
            {open ? '접기' : '펼치기'}
          </button>
          <button
            type="button"
            onClick={() => copy(prompt.body)}
            className="bg-brand-500 hover:bg-brand-600 rounded-md px-3 py-1.5 text-xs font-semibold text-white transition"
          >
            {copied ? '복사됨 ✓ AI에 붙여넣기' : '프롬프트 복사'}
          </button>
        </div>
      </div>

      {open && (
        <pre className="overflow-x-auto px-4 py-4 font-mono text-[12.5px] leading-6 whitespace-pre-wrap">
          {prompt.body}
        </pre>
      )}

      {prompt.tips && prompt.tips.length > 0 && (
        <div className="border-hair border-t px-4 py-3">
          <div className="text-muted mb-1.5 text-[11px] font-semibold tracking-wide">
            이 프롬프트를 쓸 때
          </div>
          <ul className="space-y-1">
            {prompt.tips.map((t, i) => (
              <li key={i} className="text-muted flex gap-2 text-[13px] leading-6">
                <span>·</span>
                <span>
                  <Inline text={t} />
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
