import { Link } from 'react-router-dom'
import type { Guide, GuideStep } from '../content/types'
import { useCopy } from '../lib/useCopy'

const REPO = 'https://github.com/hong-seok-young/vibe-coding-education.git'

/** 지금 보고 있는 사이트의 원본(origin). 구글 콘솔에 그대로 넣는 값이다. */
function currentOrigin() {
  return typeof window === 'undefined' ? 'https://example.com' : window.location.origin
}

/** 안내서 안의 자리표시자를 실제 값으로 바꾼다. */
function fillTokens(text: string) {
  return text.replace(/\{\{origin\}\}/g, currentOrigin()).replace(/\{\{repo\}\}/g, REPO)
}

/** `#/steps/x` → 앱 안 이동, 그 외 → 새 탭 외부 링크 */
function GuideLink({ href, label }: { href: string; label: string }) {
  if (href.startsWith('#/')) {
    return (
      <Link
        to={href.slice(1)}
        className="border-brand-500/50 text-brand-500 hover:bg-brand-500/10 inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-[12.5px] font-semibold transition"
      >
        {label} →
      </Link>
    )
  }
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer noopener"
      className="border-brand-500/50 text-brand-500 hover:bg-brand-500/10 inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-[12.5px] font-semibold transition"
    >
      {label} ↗
    </a>
  )
}

/** 붙여넣을 값 + 복사 버튼 */
function InputBox({ label, value, note }: { label: string; value: string; note?: string }) {
  const { copied, copy } = useCopy()
  const filled = fillTokens(value)
  const multiline = filled.includes('\n')

  return (
    <div className="border-brand-500/30 bg-brand-500/5 mt-2.5 rounded-lg border p-3">
      <div className="text-muted mb-1.5 text-[11.5px] font-semibold tracking-wide">✎ {label}</div>
      <div className="flex items-start gap-2">
        <code
          className={
            'surface min-w-0 flex-1 rounded border-hair border px-2.5 py-2 font-mono text-[12.5px] leading-6 ' +
            (multiline ? 'whitespace-pre' : 'break-all')
          }
        >
          {filled}
        </code>
        <button
          onClick={() => copy(filled)}
          className="border-hair surface hover:border-brand-500/60 shrink-0 rounded border px-2.5 py-2 text-[11.5px] font-medium transition"
        >
          {copied ? '복사됨 ✓' : '복사'}
        </button>
      </div>
      {note && <p className="text-muted mt-1.5 text-[12px] leading-6">{note}</p>}
    </div>
  )
}

function StepRow({ step, n }: { step: GuideStep; n: number }) {
  return (
    <li className="relative pl-11">
      {/* 번호 + 세로선 */}
      <span className="bg-brand-500 absolute top-0 left-0 flex h-7 w-7 items-center justify-center rounded-full text-[13px] font-bold text-white">
        {n}
      </span>
      <span className="border-hair absolute top-8 bottom-0 left-[13.5px] w-px border-l" aria-hidden />

      <div className="pb-7">
        {/* 어디서 */}
        <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
          <span className="text-[14px] leading-7 font-semibold">{step.where}</span>
          {step.link && <GuideLink href={step.link.href} label={step.link.label} />}
        </div>

        {/* 무엇을 누르나 */}
        <ol className="mt-2 space-y-1.5">
          {step.click.map((c, i) => (
            <li key={i} className="flex gap-2 text-[13.5px] leading-7">
              <span className="text-muted shrink-0 tabular-nums">{i + 1})</span>
              <span className="min-w-0">{c}</span>
            </li>
          ))}
        </ol>

        {step.input && <InputBox {...step.input} />}

        {/* 이렇게 되면 성공 */}
        <p className="mt-2.5 rounded-lg border border-emerald-500/35 bg-emerald-500/5 px-3 py-2 text-[13px] leading-7">
          <b className="text-emerald-600 dark:text-emerald-400">이러면 성공</b> · {step.expect}
        </p>

        {step.trouble && (
          <p className="mt-2 rounded-lg border border-amber-500/35 bg-amber-500/5 px-3 py-2 text-[13px] leading-7">
            <b className="text-amber-600 dark:text-amber-400">막히면</b> · {step.trouble}
          </p>
        )}

        {step.note && <p className="text-muted mt-2 text-[12.5px] leading-6">{step.note}</p>}
      </div>
    </li>
  )
}

export function GuideView({ guide }: { guide: Guide }) {
  return (
    <article>
      <header className="mb-6">
        <div className="text-muted flex flex-wrap items-center gap-2 text-[11.5px] font-semibold tracking-wide">
          <span
            className={
              'rounded px-1.5 py-0.5 ' +
              (guide.who === 'dX팀' ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400' : 'bg-brand-500/15 text-brand-500')
            }
          >
            {guide.who}
          </span>
          <span>{guide.minutes}</span>
          <span>· {guide.steps.length}칸</span>
        </div>
        <h1 className="mt-2 text-[22px] leading-tight font-bold tracking-tight">{guide.title}</h1>
        <p className="text-muted mt-2 text-[14px] leading-7">{guide.why}</p>
      </header>

      {guide.before && guide.before.length > 0 && (
        <section className="border-hair surface-2 mb-6 rounded-xl border p-4">
          <h2 className="text-[13px] font-semibold">시작하기 전에 있어야 하는 것</h2>
          <ul className="mt-2 space-y-1.5">
            {guide.before.map((b, i) => (
              <li key={i} className="text-muted flex gap-2 text-[13px] leading-7">
                <span className="shrink-0">□</span>
                <span>{b}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <ol className="mt-2">
        {guide.steps.map((s, i) => (
          <StepRow key={i} step={s} n={i + 1} />
        ))}
      </ol>

      <section className="border-brand-500/40 bg-brand-500/5 mt-2 rounded-xl border p-4">
        <h2 className="text-[13.5px] font-semibold">다 하면 이렇게 됩니다</h2>
        <p className="mt-1.5 text-[13.5px] leading-7">{guide.result}</p>
      </section>

      {guide.dxNote && (
        <section className="mt-4 rounded-xl border border-amber-500/35 bg-amber-500/5 p-4">
          <h2 className="text-[13.5px] font-semibold">dX팀이 대신 하는 부분</h2>
          <p className="mt-1.5 text-[13.5px] leading-7">{guide.dxNote}</p>
        </section>
      )}

      <p className="text-muted border-hair mt-6 rounded-xl border border-dashed px-4 py-3 text-[12px] leading-6">
        구글 클라우드 콘솔·깃허브 화면은 수시로 개편됩니다. 버튼 이름이 안내서와 다르면, 각 칸의 <b>「이러면 성공」</b>
        을 목표로 삼고 비슷한 이름의 버튼을 찾으세요. 실제로 달라진 곳을 발견하면 dX팀에 알려주시면 안내서를
        고치겠습니다.
      </p>
    </article>
  )
}
