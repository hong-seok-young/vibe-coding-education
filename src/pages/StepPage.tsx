import { useEffect, useState } from 'react'
import { Link, Navigate, useParams } from 'react-router-dom'
import { Blocks } from '../components/Blocks'
import { Inline } from '../components/Inline'
import { PromptCard } from '../components/PromptCard'
import { findStep, neighbors } from '../content'
import { useCopy } from '../lib/useCopy'
import { useProgress } from '../lib/progress'

type Tab = 'overview' | 'prompt' | 'sample' | 'explain' | 'check'

const TABS: { key: Tab; label: string; hint: string }[] = [
  { key: 'overview', label: '개요', hint: '이 단계에서 무엇을 하는지' },
  { key: 'prompt', label: '프롬프트', hint: 'AI에 복사해서 붙여넣기' },
  { key: 'sample', label: '샘플 결과물', hint: '기다리기 싫으면 여기' },
  { key: 'explain', label: '원리 설명', hint: '왜 그렇게 하는지' },
  { key: 'check', label: '체크리스트', hint: '제대로 됐는지 확인' },
]

export function StepPage() {
  const { slug = '' } = useParams()
  const step = findStep(slug)
  const [tab, setTab] = useState<Tab>('overview')
  const { isDone, toggleDone, checked, toggleCheck } = useProgress()
  const { copied, copy } = useCopy()

  useEffect(() => {
    setTab('overview')
    window.scrollTo({ top: 0 })
  }, [slug])

  if (!step) return <Navigate to="/" replace />

  const { prev, next } = neighbors(slug)
  const done = isDone(step.id)
  const checkedList = checked(step.id)
  const allPrompts = step.prompts.map((p) => `# ${p.label}\n\n${p.body}`).join('\n\n---\n\n')

  return (
    <div className="mx-auto w-full max-w-3xl px-5 py-7">
      {/* 헤더 */}
      <div className="mb-6">
        <div className="text-muted mb-2 flex flex-wrap items-center gap-2 text-[11.5px]">
          <span className="font-mono">{step.part}</span>
          <span>·</span>
          <span>STEP {step.id}</span>
          <span>·</span>
          <span>{step.duration}</span>
          <span
            className={
              'rounded px-1.5 py-0.5 text-[10px] font-semibold ' +
              (step.level === '심화'
                ? 'bg-amber-500/15 text-amber-500'
                : step.level === '기본'
                  ? 'bg-brand-500/15 text-brand-500'
                  : 'surface-2')
            }
          >
            {step.level}
          </span>
        </div>

        <h1 className="text-xl font-bold tracking-tight sm:text-2xl">{step.title}</h1>
        <p className="text-muted mt-2 text-[14px] leading-7">{step.tagline}</p>

        <div className="mt-4 flex flex-wrap items-center gap-2">
          <button
            onClick={() => toggleDone(step.id)}
            className={
              'rounded-lg px-3.5 py-2 text-[13px] font-semibold transition ' +
              (done
                ? 'bg-emerald-500/15 text-emerald-500'
                : 'bg-brand-500 hover:bg-brand-600 text-white')
            }
          >
            {done ? '완료됨 ✓ (클릭해서 해제)' : '이 단계 완료로 표시'}
          </button>
          {step.prompts.length > 1 && (
            <button
              onClick={() => copy(allPrompts)}
              className="border-hair text-muted hover:text-brand-500 rounded-lg border px-3 py-2 text-[12.5px]"
            >
              {copied ? '복사됨 ✓' : `프롬프트 ${step.prompts.length}개 전체 복사`}
            </button>
          )}
          {step.demo && (
            <Link
              to={step.demo.to}
              className="border-hair hover:border-brand-500/60 rounded-lg border px-3 py-2 text-[12.5px]"
            >
              {step.demo.label} →
            </Link>
          )}
        </div>
      </div>

      {/* 탭 */}
      <div className="border-hair surface sticky top-[53px] z-10 -mx-5 mb-6 border-b px-5">
        <div className="scrollbar-none flex gap-1 overflow-x-auto">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              title={t.hint}
              className={
                'shrink-0 border-b-2 px-3 py-2.5 text-[13px] font-medium transition ' +
                (tab === t.key
                  ? 'border-brand-500 text-brand-500'
                  : 'text-muted hover:text-brand-500 border-transparent')
              }
            >
              {t.label}
              {t.key === 'prompt' && (
                <span className="surface-2 ml-1.5 rounded px-1 py-0.5 font-mono text-[10px]">
                  {step.prompts.length}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* 본문 */}
      {tab === 'overview' && (
        <div className="space-y-6">
          <Card title="학습 목표">
            <ul className="space-y-1.5">
              {step.goals.map((g, i) => (
                <li key={i} className="flex gap-2.5 text-[14px] leading-7">
                  <span className="text-brand-500 mt-[9px] h-1.5 w-1.5 shrink-0 rounded-full bg-current" />
                  <span>
                    <Inline text={g} />
                  </span>
                </li>
              ))}
            </ul>
          </Card>

          <Card title="이 단계가 끝나면 손에 남는 것">
            <ul className="space-y-1.5">
              {step.deliverables.map((d, i) => (
                <li key={i} className="flex gap-2.5 text-[14px] leading-7">
                  <span className="text-emerald-500">✓</span>
                  <span>
                    <Inline text={d} />
                  </span>
                </li>
              ))}
            </ul>
          </Card>

          {step.dxNote && (
            <div className="rounded-xl border border-violet-500/40 bg-violet-500/5 px-4 py-3">
              <div className="mb-1 text-[12.5px] font-semibold">🛠️ dX팀 지원 포인트</div>
              <p className="text-[13.5px] leading-7">
                <Inline text={step.dxNote} />
              </p>
            </div>
          )}

          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setTab('prompt')}
              className="bg-brand-500 hover:bg-brand-600 rounded-lg px-4 py-2.5 text-[13px] font-semibold text-white"
            >
              프롬프트로 이동 →
            </button>
            <button
              onClick={() => setTab('sample')}
              className="border-hair hover:border-brand-500/60 rounded-lg border px-4 py-2.5 text-[13px]"
            >
              AI 없이 샘플만 보기
            </button>
          </div>
        </div>
      )}

      {tab === 'prompt' && (
        <div className="space-y-5">
          <p className="text-muted text-[13px] leading-7">
            아래 프롬프트를 순서대로 AI 대화창에 붙여넣는다. 하나가 끝나고 결과를 확인한 뒤 다음으로 넘어간다.
            한 번에 여러 개를 붙여넣으면 결과가 섞인다.
          </p>
          {step.prompts.map((p, i) => (
            <PromptCard key={p.id} prompt={p} index={i} />
          ))}
          <div className="border-hair rounded-xl border border-dashed p-4">
            <p className="text-muted text-[13px] leading-7">
              AI 응답을 기다리는 동안, 또는 실습 없이 흐름만 보고 싶다면{' '}
              <button onClick={() => setTab('sample')} className="text-brand-500 underline">
                샘플 결과물
              </button>{' '}
              탭에 이 프롬프트들의 결과가 미리 들어 있다.
            </p>
          </div>
        </div>
      )}

      {tab === 'sample' && (
        <div className="space-y-5">
          <div className="border-brand-500/40 bg-brand-500/5 rounded-xl border px-4 py-3">
            <p className="text-[13px] leading-7">
              프롬프트를 실행하면 나올 결과를 미리 넣어둔 것이다. AI 응답은 매번 문장이 조금씩 다르지만 구조는
              거의 같다. <strong>이 탭만 읽어도 전체 흐름을 이해할 수 있다.</strong>
            </p>
          </div>
          <Blocks blocks={step.sample} />
        </div>
      )}

      {tab === 'explain' && <Blocks blocks={step.explain} />}

      {tab === 'check' && (
        <div className="space-y-5">
          <p className="text-muted text-[13px] leading-7">
            하나씩 직접 확인한다. AI는 "동작할 것 같은 코드"를 아주 잘 만들지만, 실제로 동작하는지는 실행해봐야
            안다.
          </p>
          <ul className="border-hair surface divide-y overflow-hidden rounded-xl border">
            {step.checklist.map((c, i) => {
              const on = checkedList.includes(i)
              return (
                <li key={i} className="border-hair">
                  <button
                    onClick={() => toggleCheck(step.id, i)}
                    className="hover:surface-2 flex w-full items-start gap-3 px-4 py-3 text-left transition"
                  >
                    <span
                      className={
                        'mt-0.5 flex h-4.5 w-4.5 shrink-0 items-center justify-center rounded border text-[10px] ' +
                        (on ? 'border-emerald-500 bg-emerald-500 text-white' : 'border-hair')
                      }
                    >
                      {on ? '✓' : ''}
                    </span>
                    <span className={'text-[13.5px] leading-6 ' + (on ? 'text-muted line-through' : '')}>
                      <Inline text={c} />
                    </span>
                  </button>
                </li>
              )
            })}
          </ul>

          <div className="text-muted flex items-center justify-between text-[12.5px]">
            <span>
              {checkedList.length} / {step.checklist.length} 확인
            </span>
            {checkedList.length === step.checklist.length && !done && (
              <button
                onClick={() => toggleDone(step.id)}
                className="bg-brand-500 hover:bg-brand-600 rounded-md px-3 py-1.5 text-[12.5px] font-semibold text-white"
              >
                이 단계 완료로 표시
              </button>
            )}
          </div>
        </div>
      )}

      {/* 이전/다음 */}
      <div className="border-hair mt-10 flex gap-3 border-t pt-6">
        {prev ? (
          <Link
            to={`/steps/${prev.slug}`}
            className="border-hair hover:border-brand-500/60 min-w-0 flex-1 rounded-xl border p-3.5 transition"
          >
            <div className="text-muted text-[11px]">← STEP {prev.id}</div>
            <div className="truncate text-[13px] font-medium">{prev.title}</div>
          </Link>
        ) : (
          <div className="flex-1" />
        )}
        {next ? (
          <Link
            to={`/steps/${next.slug}`}
            className="border-hair hover:border-brand-500/60 min-w-0 flex-1 rounded-xl border p-3.5 text-right transition"
          >
            <div className="text-muted text-[11px]">STEP {next.id} →</div>
            <div className="truncate text-[13px] font-medium">{next.title}</div>
          </Link>
        ) : (
          <Link
            to="/"
            className="border-hair hover:border-brand-500/60 min-w-0 flex-1 rounded-xl border p-3.5 text-right transition"
          >
            <div className="text-muted text-[11px]">과정 완료 →</div>
            <div className="truncate text-[13px] font-medium">개요로 돌아가기</div>
          </Link>
        )}
      </div>
    </div>
  )
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="border-hair surface rounded-xl border p-4">
      <h2 className="text-muted mb-2.5 text-[11.5px] font-semibold tracking-wider">{title}</h2>
      {children}
    </section>
  )
}
