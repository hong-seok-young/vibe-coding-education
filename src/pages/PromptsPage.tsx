import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { steps, totalPrompts } from '../content'
import { useCopy } from '../lib/useCopy'

export function PromptsPage() {
  const [q, setQ] = useState('')
  const { copied, copy } = useCopy()

  const rows = useMemo(() => {
    const keyword = q.trim().toLowerCase()
    return steps.flatMap((s) =>
      s.prompts
        .map((p, i) => ({ step: s, prompt: p, index: i }))
        .filter(
          ({ step, prompt }) =>
            !keyword ||
            step.title.toLowerCase().includes(keyword) ||
            prompt.label.toLowerCase().includes(keyword) ||
            prompt.body.toLowerCase().includes(keyword),
        ),
    )
  }, [q])

  const allText = useMemo(
    () =>
      steps
        .map(
          (s) =>
            `# STEP ${s.id} · ${s.title}\n\n` +
            s.prompts.map((p) => `## ${p.label}\n${p.when}\n\n${p.body}`).join('\n\n'),
        )
        .join('\n\n---\n\n'),
    [],
  )

  return (
    <div className="mx-auto w-full max-w-4xl px-5 py-7">
      <div className="mb-6">
        <h1 className="text-xl font-bold tracking-tight">프롬프트 모음</h1>
        <p className="text-muted mt-2 text-[13.5px] leading-7">
          15단계에 나오는 프롬프트 {totalPrompts}개를 한 곳에 모았다. AI 대화창을 옆에 띄워두고 필요한 것만 골라
          복사해 쓸 수 있다. 각 프롬프트의 배경과 주의사항은 해당 스텝에서 확인한다.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="검색 (예: 구글, 동기화, 배포, 권한)"
            className="border-hair surface min-w-[220px] flex-1 rounded-lg border px-3 py-2 text-[13px] outline-none focus:border-brand-500"
          />
          <button
            onClick={() => copy(allText)}
            className="border-hair hover:border-brand-500/60 rounded-lg border px-3 py-2 text-[12.5px]"
          >
            {copied ? '복사됨 ✓' : '전체 복사'}
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {rows.map(({ step, prompt, index }) => (
          <Row key={step.id + prompt.id} step={step} prompt={prompt} index={index} />
        ))}
        {rows.length === 0 && (
          <p className="text-muted py-10 text-center text-[13px]">검색 결과가 없다.</p>
        )}
      </div>
    </div>
  )
}

function Row({
  step, prompt, index,
}: {
  step: (typeof steps)[number]
  prompt: (typeof steps)[number]['prompts'][number]
  index: number
}) {
  const [open, setOpen] = useState(false)
  const { copied, copy } = useCopy()

  return (
    <div className="border-hair surface overflow-hidden rounded-xl border">
      <div className="flex flex-wrap items-center gap-3 px-4 py-3">
        <Link
          to={`/steps/${step.slug}`}
          className="surface-2 text-muted hover:text-brand-500 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10.5px]"
        >
          STEP {step.id}
        </Link>
        <div className="min-w-0 flex-1">
          <div className="truncate text-[13.5px] font-medium">{prompt.label}</div>
          <div className="text-muted truncate text-[11.5px]">{prompt.when}</div>
        </div>
        <button
          onClick={() => setOpen((v) => !v)}
          className="border-hair text-muted hover:text-brand-500 shrink-0 rounded-md border px-2 py-1.5 text-[11.5px]"
        >
          {open ? '접기' : '내용 보기'}
        </button>
        <button
          onClick={() => copy(prompt.body)}
          className="bg-brand-500 hover:bg-brand-600 shrink-0 rounded-md px-2.5 py-1.5 text-[11.5px] font-semibold text-white"
        >
          {copied ? '복사됨 ✓' : '복사'}
        </button>
      </div>
      {open && (
        <pre className="border-hair surface-2 overflow-x-auto border-t px-4 py-3 font-mono text-[12px] leading-6 whitespace-pre-wrap">
          {prompt.body}
        </pre>
      )}
      {open && prompt.tips && (
        <ul className="border-hair space-y-1 border-t px-4 py-3">
          {prompt.tips.map((t, i) => (
            <li key={i} className="text-muted text-[12.5px] leading-6">
              · {t.replace(/\*\*/g, '')}
            </li>
          ))}
        </ul>
      )}
      <div className="border-hair text-muted border-t px-4 py-2 text-[11px]">
        프롬프트 {index + 1} · {step.title}
      </div>
    </div>
  )
}
