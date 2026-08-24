import { Link } from 'react-router-dom'
import { parts, steps, stepsOf, totalPrompts } from '../content'
import { useProgress } from '../lib/progress'

export function HomePage() {
  const { isDone, reset } = useProgress()
  const doneCount = steps.filter((s) => isDone(s.id)).length
  const percent = Math.round((doneCount / steps.length) * 100)

  // 이어서 할 단계 = 아직 완료로 표시하지 않은 첫 단계
  const nextStep = steps.find((s) => !isDone(s.id)) ?? steps[0]
  const started = doneCount > 0

  return (
    <div className="mx-auto w-full max-w-4xl px-5 py-8">
      {/* 무엇을 하는 곳인지 한 문단 */}
      <section className="mb-7">
        <span className="bg-brand-500/15 text-brand-500 inline-block rounded-full px-2.5 py-1 text-[11.5px] font-semibold">
          dX팀 사내 교육
        </span>
        <h1 className="mt-3 text-2xl leading-tight font-bold tracking-tight sm:text-[30px]">
          업무용 웹앱 하나를
          <br />
          15단계로 함께 만들어 봅니다
        </h1>
        <p className="text-muted mt-3 max-w-2xl text-[14.5px] leading-7">
          만드는 것은 <strong>업무 캘린더 · 주간보고 · 인수인계 웹앱</strong>입니다. 캘린더에 업무를 적으면 그게
          주간보고가 되고, 주간회의에서 화면에 띄워 넘겨보고, 휴가 때 다른 사람에게 넘길 수 있는 도구입니다.
        </p>
      </section>

      {/* 시작 버튼 하나 */}
      <section className="border-brand-500/40 bg-brand-500/5 mb-8 rounded-2xl border p-5">
        <div className="flex flex-wrap items-center gap-4">
          <div className="min-w-0 flex-1">
            <p className="text-muted text-[12px] font-semibold tracking-wider">
              {started ? '이어서 하기' : '여기서 시작'}
            </p>
            <p className="mt-1 text-[17px] font-bold">
              <span className="text-muted mr-2 font-mono text-[15px]">STEP {nextStep.id}</span>
              {nextStep.title}
            </p>
            <p className="text-muted mt-0.5 text-[13px]">{nextStep.tagline}</p>
          </div>
          <Link
            to={`/steps/${nextStep.slug}`}
            className="bg-brand-500 hover:bg-brand-600 shrink-0 rounded-xl px-6 py-3 text-[14px] font-semibold text-white transition"
          >
            {started ? '이어서 하기 →' : '시작하기 →'}
          </Link>
        </div>

        {started && (
          <div className="mt-4 flex items-center gap-3">
            <div className="surface-2 h-1.5 flex-1 overflow-hidden rounded-full">
              <div className="bg-brand-500 h-full transition-all" style={{ width: percent + '%' }} />
            </div>
            <span className="text-muted shrink-0 text-[12px] tabular-nums">
              {doneCount}/{steps.length} 완료
            </span>
            <button onClick={reset} className="text-muted hover:text-brand-500 shrink-0 text-[12px] underline">
              초기화
            </button>
          </div>
        )}
      </section>

      {/* 한 단계는 이렇게 진행된다 — 화면의 탭 순서와 같은 그림 */}
      <section className="mb-8">
        <h2 className="mb-3 text-[15px] font-semibold tracking-tight">한 단계는 이렇게 진행됩니다</h2>
        <ol className="grid gap-2 sm:grid-cols-5">
          {[
            ['1', '이번 시간', '무엇을 만드는지 직접 만져봅니다'],
            ['2', '프롬프트', '복사해서 AI에게 시킵니다'],
            ['3', '샘플 결과', '기다리기 싫으면 미리 준비된 결과를 봅니다'],
            ['4', '원리', '왜 그렇게 하는지 이해합니다'],
            ['5', '확인', '제대로 됐는지 점검합니다'],
          ].map(([n, t, d]) => (
            <li key={n} className="border-hair surface rounded-xl border p-3">
              <span className="bg-brand-500/15 text-brand-500 flex h-6 w-6 items-center justify-center rounded-full text-[12px] font-bold">
                {n}
              </span>
              <p className="mt-2 text-[13px] font-semibold">{t}</p>
              <p className="text-muted mt-0.5 text-[11.5px] leading-5">{d}</p>
            </li>
          ))}
        </ol>
        <p className="text-muted mt-2.5 text-[12.5px] leading-6">
          프롬프트는 전부 {totalPrompts}개입니다.{' '}
          <Link to="/prompts" className="text-brand-500 underline">
            한 곳에 모아 보기
          </Link>
          . ▶ 표시가 있는 단계는 결과물을 직접 만져볼 수 있습니다.
        </p>
      </section>

      {/* 커리큘럼 */}
      <section>
        <h2 className="mb-3 text-[15px] font-semibold tracking-tight">전체 15단계</h2>

        <div className="space-y-5">
          {parts.map((part) => (
            <div key={part}>
              <div className="text-muted mb-2 text-[11px] font-semibold tracking-wider">{part}</div>
              <ul className="border-hair surface divide-y overflow-hidden rounded-xl border">
                {stepsOf(part).map((s) => (
                  <li key={s.id} className="border-hair">
                    <Link
                      to={`/steps/${s.slug}`}
                      className="hover:surface-2 flex items-center gap-3 px-4 py-2.5 transition"
                    >
                      <span
                        className={
                          'flex h-6 w-6 shrink-0 items-center justify-center rounded font-mono text-[10.5px] font-semibold ' +
                          (isDone(s.id) ? 'bg-emerald-500 text-white' : 'surface-2 text-muted')
                        }
                      >
                        {isDone(s.id) ? '✓' : s.id}
                      </span>
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-[13.5px] font-medium">{s.title}</span>
                        <span className="text-muted block truncate text-[12px]">{s.tagline}</span>
                      </span>
                      {s.demo && (
                        <span className="bg-brand-500/15 text-brand-500 shrink-0 rounded px-1.5 py-0.5 text-[10.5px] font-semibold">
                          ▶ 체험
                        </span>
                      )}
                      <span className="text-muted hidden shrink-0 text-[11.5px] sm:block">{s.duration}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section className="border-hair mt-8 rounded-xl border border-dashed p-5">
        <h2 className="text-[14px] font-semibold">끝까지 못 따라와도 괜찮습니다</h2>
        <p className="text-muted mt-2 text-[13px] leading-7">
          필요한 기능은 <strong>dX팀에서 만들어 드립니다.</strong> 이 과정의 목표는 혼자 다 만드는 것이 아니라,{' '}
          <strong>무엇을 원하는지 정확히 말하고, 왜 어려운지 이해하고, 결과를 검증할 수 있게</strong> 되는
          것입니다. 마지막 단계에 dX팀에 그대로 전달할 수 있는{' '}
          <Link to="/steps/operate-and-next" className="text-brand-500 underline">
            개발 요청서 양식
          </Link>
          이 있습니다.
        </p>
      </section>
    </div>
  )
}
