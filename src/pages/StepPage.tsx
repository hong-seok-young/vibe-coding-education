import { useEffect } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import { Blocks } from '../components/Blocks'
import { Inline } from '../components/Inline'
import { PromptCard } from '../components/PromptCard'
import { findStep, neighbors, steps } from '../content'
import { findGuide } from '../content/guides'
import type { Step } from '../content'
import { DEMOS } from '../demo/registry'
import { DownloadCard } from '../components/DownloadCard'
import { downloadForDemo } from '../download'
import { useCopy } from '../lib/useCopy'
import { useProgress } from '../lib/progress'

/**
 * 수업 진행 순서를 그대로 탭으로 만든다.
 * 교육생이 "지금 몇 번째를 하고 있고 다음에 뭘 하는지" 늘 보이게 하는 것이 이 화면의 목적이다.
 */
type Tab = 'start' | 'prompt' | 'sample' | 'explain' | 'check'

const TABS: Array<{ key: Tab; no: string; label: string; what: string }> = [
  { key: 'start', no: '1', label: '이번 시간', what: '무엇을 만드는지 보기' },
  { key: 'prompt', no: '2', label: '프롬프트', what: 'AI에게 시키기' },
  { key: 'sample', no: '3', label: '샘플 결과', what: '내 결과와 비교하기' },
  { key: 'explain', no: '4', label: '원리', what: '왜 그렇게 하는지' },
  { key: 'check', no: '5', label: '확인', what: '제대로 됐는지 점검' },
]

/** 예전 주소(/demo, /overview)도 그대로 열리게 한다 */
const ALIAS: Record<string, Tab> = { demo: 'start', overview: 'start' }

export function StepPage() {
  const { slug = '', tab: tabParam } = useParams()
  const navigate = useNavigate()
  const step = findStep(slug)
  const { isDone, toggleDone, checked, toggleCheck } = useProgress()

  const raw = tabParam ?? ''
  const tab: Tab = (TABS.some((t) => t.key === raw) ? raw : (ALIAS[raw] ?? 'start')) as Tab

  useEffect(() => {
    window.scrollTo({ top: 0 })
  }, [slug, tab])

  if (!step) return <Navigate to="/" replace />

  const go = (t: Tab) => navigate(t === 'start' ? `/steps/${step.slug}` : `/steps/${step.slug}/${t}`)

  const index = steps.findIndex((s) => s.slug === step.slug)
  const { prev, next } = neighbors(slug)
  const done = isDone(step.id)
  const checkedList = checked(step.id)
  const tabIndex = TABS.findIndex((t) => t.key === tab)
  const wide = tab === 'start' && !!step.demo

  return (
    <div className="w-full">
      <div className="mx-auto w-full max-w-3xl px-5 pt-6">
        {/* 지금 어디에 있는지 */}
        <div className="text-muted mb-3 flex flex-wrap items-center gap-x-2 gap-y-1 text-[11.5px]">
          <span>{step.part}</span>
          <span>·</span>
          <span className="tabular-nums">
            15단계 중 <strong className="text-brand-500">{index + 1}번째</strong>
          </span>
          <span>·</span>
          <span>{step.duration}</span>
          {done && <span className="rounded bg-emerald-500/15 px-1.5 py-0.5 text-emerald-500">완료</span>}
        </div>

        <h1 className="text-xl font-bold tracking-tight sm:text-[26px]">
          <span className="text-muted mr-2 font-mono text-[18px]">{step.id}</span>
          {step.title}
        </h1>
        <p className="text-muted mt-1.5 text-[14px] leading-7">{step.tagline}</p>
      </div>

      {/* 수업 순서 탭 — 번호와 "무엇을 하는 시간인지"를 같이 보여준다 */}
      <div className="border-hair surface sticky top-[53px] z-10 mt-5 border-y">
        <div className="mx-auto w-full max-w-3xl px-5">
          <div className="scrollbar-none flex gap-0.5 overflow-x-auto">
            {TABS.map((t, i) => {
              const active = t.key === tab
              const passed = i < tabIndex
              return (
                <button
                  key={t.key}
                  onClick={() => go(t.key)}
                  className={
                    'group flex shrink-0 items-center gap-2 border-b-2 px-3 py-2.5 transition ' +
                    (active ? 'border-brand-500' : 'hover:surface-2 border-transparent')
                  }
                >
                  <span
                    className={
                      'flex h-5 w-5 items-center justify-center rounded-full text-[11px] font-bold ' +
                      (active
                        ? 'bg-brand-500 text-white'
                        : passed
                          ? 'bg-brand-500/20 text-brand-500'
                          : 'surface-2 text-muted')
                    }
                  >
                    {t.no}
                  </span>
                  <span className="text-left">
                    <span
                      className={
                        'block text-[13px] leading-tight font-medium ' + (active ? 'text-brand-500' : '')
                      }
                    >
                      {t.label}
                      {t.key === 'prompt' && (
                        <span className="text-muted ml-1 font-mono text-[10px]">{step.prompts.length}</span>
                      )}
                    </span>
                    <span className="text-muted hidden text-[10.5px] leading-tight sm:block">{t.what}</span>
                  </span>
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* 본문 */}
      <div className={wide ? 'py-6' : 'mx-auto w-full max-w-3xl px-5 py-6'}>
        {tab === 'start' && <StartTab step={step} onNext={() => go('prompt')} />}

        {tab === 'prompt' && (
          <div className="space-y-5">
            <TabHint>
              아래 프롬프트를 <strong>순서대로 하나씩</strong> AI 대화창에 붙여넣는다. 하나가 끝나고 결과를 확인한
              뒤 다음으로 넘어간다. 한 번에 여러 개를 붙여넣으면 결과가 섞인다.
            </TabHint>
            {step.prompts.map((p, i) => (
              <PromptCard key={p.id} prompt={p} index={i} />
            ))}
          </div>
        )}

        {tab === 'sample' && (
          <div className="space-y-5">
            <TabHint>
              프롬프트를 실행하면 나올 결과를 미리 넣어둔 것이다. <strong>AI를 기다리지 않고 이 탭만 읽어도</strong>{' '}
              전체 흐름을 이해할 수 있다.
            </TabHint>
            <Blocks blocks={step.sample} />
          </div>
        )}

        {tab === 'explain' && (
          <div className="space-y-5">
            <TabHint>
              dX팀이 대신 만들어 주더라도 <strong>왜 그렇게 하는지, 무엇을 결정해야 하는지</strong>는 알아야 한다.
              이 탭이 그 내용이다.
            </TabHint>
            <Blocks blocks={step.explain} />
          </div>
        )}

        {tab === 'check' && (
          <CheckTab
            step={step}
            checkedList={checkedList}
            done={done}
            onToggle={(i) => toggleCheck(step.id, i)}
            onDone={() => toggleDone(step.id)}
          />
        )}
      </div>

      {/* 다음에 할 일 — 교육생이 길을 잃지 않게 항상 아래에 둔다 */}
      <div className="mx-auto w-full max-w-3xl px-5 pb-10">
        <div className="border-hair flex flex-wrap items-center gap-3 rounded-xl border p-4">
          {tabIndex > 0 ? (
            <button
              onClick={() => go(TABS[tabIndex - 1].key)}
              className="border-hair text-muted hover:text-brand-500 rounded-lg border px-3 py-2 text-[12.5px]"
            >
              ← {TABS[tabIndex - 1].no}. {TABS[tabIndex - 1].label}
            </button>
          ) : (
            <span />
          )}

          <div className="ml-auto flex flex-wrap items-center gap-2">
            {tabIndex < TABS.length - 1 ? (
              <button
                onClick={() => go(TABS[tabIndex + 1].key)}
                className="bg-brand-500 hover:bg-brand-600 rounded-lg px-4 py-2 text-[13px] font-semibold text-white"
              >
                다음 · {TABS[tabIndex + 1].no}. {TABS[tabIndex + 1].label} →
              </button>
            ) : next ? (
              <Link
                to={`/steps/${next.slug}`}
                className="bg-brand-500 hover:bg-brand-600 rounded-lg px-4 py-2 text-[13px] font-semibold text-white"
              >
                다음 단계 · STEP {next.id} {next.title} →
              </Link>
            ) : (
              <Link
                to="/"
                className="bg-brand-500 hover:bg-brand-600 rounded-lg px-4 py-2 text-[13px] font-semibold text-white"
              >
                과정 완료 · 처음으로 →
              </Link>
            )}
          </div>
        </div>

        {/* 단계 이동 */}
        <div className="text-muted mt-3 flex items-center justify-between text-[12px]">
          {prev ? (
            <Link to={`/steps/${prev.slug}`} className="hover:text-brand-500 truncate">
              ← STEP {prev.id} {prev.title}
            </Link>
          ) : (
            <span />
          )}
          {next && (
            <Link to={`/steps/${next.slug}`} className="hover:text-brand-500 truncate">
              STEP {next.id} {next.title} →
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}

/** 1. 이번 시간 — 목표와 결과물을 짧게 보여주고, 데모가 있으면 바로 만져보게 한다 */
function StartTab({ step, onNext }: { step: Step; onNext: () => void }) {
  const { copied, copy } = useCopy()
  const allPrompts = step.prompts.map((p) => `# ${p.label}\n\n${p.body}`).join('\n\n---\n\n')
  const demo = step.demo ? DEMOS[step.demo.kind] : null
  // 이 단계의 데모를 파일로 받아 갈 수 있으면 데모 아래에 내려받기 카드를 붙인다
  const download = step.demo ? downloadForDemo(step.demo.kind) : undefined
  const stepGuides = (step.guides ?? []).map(findGuide).filter((g) => !!g)

  return (
    <div>
      <div className="mx-auto w-full max-w-3xl px-5">
        <div className="grid gap-3 sm:grid-cols-2">
          <section className="border-hair surface rounded-xl border p-4">
            <h2 className="text-muted mb-2 text-[11px] font-semibold tracking-wider">이번 시간에 배우는 것</h2>
            <ul className="space-y-1.5">
              {step.goals.map((g, i) => (
                <li key={i} className="flex gap-2 text-[13.5px] leading-6">
                  <span className="text-brand-500 mt-[9px] h-1.5 w-1.5 shrink-0 rounded-full bg-current" />
                  <span>
                    <Inline text={g} />
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section className="border-hair surface rounded-xl border p-4">
            <h2 className="text-muted mb-2 text-[11px] font-semibold tracking-wider">끝나면 손에 남는 것</h2>
            <ul className="space-y-1.5">
              {step.deliverables.map((d, i) => (
                <li key={i} className="flex gap-2 text-[13.5px] leading-6">
                  <span className="text-emerald-500">✓</span>
                  <span>
                    <Inline text={d} />
                  </span>
                </li>
              ))}
            </ul>
          </section>
        </div>

        {step.dxNote && (
          <p className="text-muted mt-3 rounded-xl border border-violet-500/40 bg-violet-500/5 px-4 py-2.5 text-[12.5px] leading-6">
            🛠️ <Inline text={step.dxNote} />
          </p>
        )}

        {stepGuides.length > 0 && (
          <section className="border-hair mt-3 rounded-xl border border-dashed p-4">
            <h2 className="text-[13px] font-semibold">이 단계에서 손이 막히면 — 클릭 단위 안내서</h2>
            <p className="text-muted mt-1 text-[12.5px] leading-6">
              어느 링크로 들어가서 어느 버튼을 누르는지까지 적혀 있습니다.
            </p>
            <ul className="mt-2.5 flex flex-wrap gap-2">
              {stepGuides.map((g) => (
                <li key={g.id}>
                  <Link
                    to={`/guides/${g.id}`}
                    className="border-brand-500/50 text-brand-500 hover:bg-brand-500/10 inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-[12.5px] font-semibold transition"
                  >
                    {g.title}
                    <span className="text-muted font-normal">· {g.minutes}</span>
                    <span>→</span>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        )}

        {demo && step.demo && (
          <div className="border-brand-500/40 bg-brand-500/5 mt-5 rounded-xl border px-4 py-3.5">
            <div className="mb-1.5 flex items-center gap-2">
              <span className="bg-brand-500 rounded px-1.5 py-0.5 text-[10.5px] font-semibold text-white">
                직접 만져보기
              </span>
              <span className="text-[13px] font-semibold">{demo.title}</span>
            </div>
            <p className="text-[13.5px] leading-7">
              <Inline text={step.demo.hint} />
            </p>
          </div>
        )}

        {!demo && (
          <div className="mt-5 flex flex-wrap gap-2">
            <button
              onClick={onNext}
              className="bg-brand-500 hover:bg-brand-600 rounded-lg px-4 py-2.5 text-[13px] font-semibold text-white"
            >
              2. 프롬프트로 →
            </button>
            {step.prompts.length > 1 && (
              <button
                onClick={() => copy(allPrompts)}
                className="border-hair text-muted hover:text-brand-500 rounded-lg border px-3 py-2.5 text-[12.5px]"
              >
                {copied ? '복사됨 ✓' : `프롬프트 ${step.prompts.length}개 전체 복사`}
              </button>
            )}
          </div>
        )}
      </div>

      {/* 데모는 넓은 화면이 필요하므로 폭 제한 밖에서 그린다 */}
      {demo && (
        <div className="mt-5">
          {demo.controls && (
            <p className="text-muted border-hair surface-2 border-y px-5 py-2 text-[12px] leading-6">
              {demo.controls}
            </p>
          )}
          <div className="border-hair min-h-[480px] border-b">{demo.render()}</div>
          {download && (
            <div className="mx-auto w-full max-w-[860px] px-5 pt-5">
              <DownloadCard app={download} dense />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

/** 5. 확인 */
function CheckTab({
  step, checkedList, done, onToggle, onDone,
}: {
  step: Step
  checkedList: number[]
  done: boolean
  onToggle: (i: number) => void
  onDone: () => void
}) {
  const all = checkedList.length === step.checklist.length

  return (
    <div className="space-y-5">
      <TabHint>
        하나씩 직접 눌러 확인한다. AI는 "동작할 것 같은 코드"를 아주 잘 만들지만,{' '}
        <strong>실제로 동작하는지는 실행해봐야 안다.</strong>
      </TabHint>

      <ul className="border-hair surface divide-y overflow-hidden rounded-xl border">
        {step.checklist.map((c, i) => {
          const on = checkedList.includes(i)
          return (
            <li key={i} className="border-hair">
              <button
                onClick={() => onToggle(i)}
                className="hover:surface-2 flex w-full items-start gap-3 px-4 py-3 text-left transition"
              >
                <span
                  className={
                    'mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border text-[11px] ' +
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

      <div className="border-hair flex flex-wrap items-center gap-3 rounded-xl border p-4">
        <span className="text-[13px] tabular-nums">
          {checkedList.length} / {step.checklist.length} 확인
          {all && !done && ' · 다 됐으면 완료로 표시해 보세요'}
        </span>
        <button
          onClick={onDone}
          className={
            'ml-auto rounded-lg px-4 py-2 text-[13px] font-semibold transition ' +
            (done ? 'bg-emerald-500/15 text-emerald-500' : 'bg-brand-500 hover:bg-brand-600 text-white')
          }
        >
          {done ? '완료됨 ✓ (해제하려면 클릭)' : '이 단계 완료'}
        </button>
      </div>
    </div>
  )
}

/** 탭마다 맨 위에 붙는 한 줄 안내 — "지금 뭘 하는 시간인지" */
function TabHint({ children }: { children: React.ReactNode }) {
  return (
    <p className="border-hair surface-2 rounded-xl border px-4 py-3 text-[13px] leading-7">{children}</p>
  )
}
