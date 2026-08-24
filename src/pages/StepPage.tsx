import { useEffect } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import { Blocks } from '../components/Blocks'
import { Inline } from '../components/Inline'
import { PromptCard } from '../components/PromptCard'
import { findStep, neighbors } from '../content'
import type { Step } from '../content'
import { DEMOS } from '../demo/registry'
import { useCopy } from '../lib/useCopy'
import { useProgress } from '../lib/progress'

type Tab = 'overview' | 'demo' | 'prompt' | 'sample' | 'explain' | 'check'

const TAB_LABEL: Record<Tab, string> = {
  overview: '개요',
  demo: '완성 데모',
  prompt: '프롬프트',
  sample: '샘플 결과물',
  explain: '원리 설명',
  check: '체크리스트',
}

const TAB_HINT: Record<Tab, string> = {
  overview: '이 단계에서 무엇을 하는지',
  demo: '만들 결과물을 먼저 만져보기',
  prompt: 'AI에 복사해서 붙여넣기',
  sample: '기다리기 싫으면 여기',
  explain: '왜 그렇게 하는지',
  check: '제대로 됐는지 확인',
}

function tabsOf(step: Step): Tab[] {
  return step.demo
    ? ['overview', 'demo', 'prompt', 'sample', 'explain', 'check']
    : ['overview', 'prompt', 'sample', 'explain', 'check']
}

export function StepPage() {
  const { slug = '', tab: tabParam } = useParams()
  const navigate = useNavigate()
  const step = findStep(slug)
  const { isDone, toggleDone, checked, toggleCheck } = useProgress()
  const { copied, copy } = useCopy()

  const tabs = step ? tabsOf(step) : []
  const tab: Tab = (tabs as string[]).includes(tabParam ?? '') ? (tabParam as Tab) : 'overview'

  useEffect(() => {
    window.scrollTo({ top: 0 })
  }, [slug, tab])

  if (!step) return <Navigate to="/" replace />

  const go = (t: Tab) => navigate(t === 'overview' ? `/steps/${step.slug}` : `/steps/${step.slug}/${t}`)

  const { prev, next } = neighbors(slug)
  const done = isDone(step.id)
  const checkedList = checked(step.id)
  const allPrompts = step.prompts.map((p) => `# ${p.label}\n\n${p.body}`).join('\n\n---\n\n')

  // 데모는 캘린더처럼 넓은 화면이 필요하므로 본문 폭 제한 밖으로 빼서 그린다
  const isWide = tab === 'demo'

  return (
    <div className={isWide ? 'w-full' : 'mx-auto w-full max-w-3xl px-5 py-7'}>
      <div className={isWide ? 'mx-auto w-full max-w-3xl px-5 py-7 pb-0' : ''}>
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
                (done ? 'bg-emerald-500/15 text-emerald-500' : 'bg-brand-500 hover:bg-brand-600 text-white')
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
          </div>
        </div>

        {/* 탭 */}
        <div className="border-hair surface sticky top-[53px] z-10 -mx-5 mb-6 border-b px-5">
          <div className="scrollbar-none flex gap-1 overflow-x-auto">
            {tabs.map((t) => (
              <button
                key={t}
                onClick={() => go(t)}
                title={TAB_HINT[t]}
                className={
                  'shrink-0 border-b-2 px-3 py-2.5 text-[13px] font-medium transition ' +
                  (tab === t
                    ? 'border-brand-500 text-brand-500'
                    : 'text-muted hover:text-brand-500 border-transparent')
                }
              >
                {TAB_LABEL[t]}
                {t === 'prompt' && (
                  <span className="surface-2 ml-1.5 rounded px-1 py-0.5 font-mono text-[10px]">
                    {step.prompts.length}
                  </span>
                )}
                {t === 'demo' && <span className="ml-1.5 text-[10px]">▶</span>}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 본문 */}
      <div className={isWide ? '' : ''}>
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
              {step.demo ? (
                <>
                  <button
                    onClick={() => go('demo')}
                    className="bg-brand-500 hover:bg-brand-600 rounded-lg px-4 py-2.5 text-[13px] font-semibold text-white"
                  >
                    ▶ 완성 데모 먼저 보기
                  </button>
                  <button
                    onClick={() => go('prompt')}
                    className="border-hair hover:border-brand-500/60 rounded-lg border px-4 py-2.5 text-[13px]"
                  >
                    바로 프롬프트로
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => go('prompt')}
                    className="bg-brand-500 hover:bg-brand-600 rounded-lg px-4 py-2.5 text-[13px] font-semibold text-white"
                  >
                    프롬프트로 이동 →
                  </button>
                  <button
                    onClick={() => go('sample')}
                    className="border-hair hover:border-brand-500/60 rounded-lg border px-4 py-2.5 text-[13px]"
                  >
                    AI 없이 샘플만 보기
                  </button>
                </>
              )}
            </div>
          </div>
        )}

        {tab === 'demo' && step.demo && (
          <DemoSection step={step} onNext={() => go('prompt')} />
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
                <button onClick={() => go('sample')} className="text-brand-500 underline">
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
      </div>

      {/* 이전/다음 */}
      <div
        className={
          'border-hair mt-10 flex gap-3 border-t pt-6 ' +
          (isWide ? 'mx-auto w-full max-w-3xl px-5 pb-7' : '')
        }
      >
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

/** 단계 안에 들어가는 완성 데모. 캘린더처럼 넓은 화면이 필요해서 폭 제한 없이 그린다. */
function DemoSection({ step, onNext }: { step: Step; onNext: () => void }) {
  const demo = DEMOS[step.demo!.kind]

  return (
    <div>
      <div className="mx-auto w-full max-w-3xl px-5">
        <div className="border-brand-500/40 bg-brand-500/5 mb-5 rounded-xl border px-4 py-3.5">
          <div className="mb-1.5 flex items-center gap-2">
            <span className="bg-brand-500 rounded px-1.5 py-0.5 text-[10.5px] font-semibold text-white">
              완성 데모
            </span>
            <span className="text-[13px] font-semibold">{demo.title}</span>
          </div>
          <p className="text-[13.5px] leading-7">
            <Inline text={step.demo!.hint} />
          </p>
          <p className="text-muted mt-2 text-[12px] leading-6">
            목업이 아니라 실제로 동작하는 화면이다. 여기서 <strong>무엇을 만들지 눈으로 확인한 뒤</strong>{' '}
            프롬프트 탭으로 넘어가면, AI가 만든 결과가 맞는지 스스로 판단할 수 있다.
          </p>
        </div>
      </div>

      {demo.controls && (
        <p className="text-muted border-hair surface-2 border-y px-5 py-2 text-[12px] leading-6">
          {demo.controls}
        </p>
      )}

      <div className="border-hair min-h-[520px] border-b">{demo.render()}</div>

      <div className="mx-auto w-full max-w-3xl px-5 pt-6">
        <div className="border-hair flex flex-wrap items-center gap-3 rounded-xl border border-dashed p-4">
          <p className="text-muted min-w-0 flex-1 text-[13px] leading-7">
            무엇을 만들지 확인했으면, 이제 직접 만들어 볼 차례다.
          </p>
          <button
            onClick={onNext}
            className="bg-brand-500 hover:bg-brand-600 shrink-0 rounded-lg px-4 py-2.5 text-[13px] font-semibold text-white"
          >
            프롬프트 탭으로 →
          </button>
        </div>
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
