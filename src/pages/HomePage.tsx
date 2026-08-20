import { Link } from 'react-router-dom'
import { parts, steps, stepsOf, totalPrompts } from '../content'
import { useProgress } from '../lib/progress'

export function HomePage() {
  const { isDone, reset } = useProgress()
  const doneCount = steps.filter((s) => isDone(s.id)).length

  return (
    <div className="mx-auto w-full max-w-5xl px-5 py-8">
      {/* 히어로 */}
      <section className="mb-10">
        <span className="bg-brand-500/15 text-brand-500 inline-block rounded-full px-2.5 py-1 text-[11.5px] font-semibold">
          dX팀 사내 교육
        </span>
        <h1 className="mt-3 text-2xl leading-tight font-bold tracking-tight sm:text-3xl">
          프롬프트를 복사해 붙여넣으면서
          <br />
          업무용 웹앱 하나를 끝까지 만들어 봅니다
        </h1>
        <p className="text-muted mt-4 max-w-2xl text-[14.5px] leading-7">
          만드는 것은 <strong>업무 캘린더 · 주간보고 · 인수인계 웹앱</strong>입니다. 노션 캘린더 같은 캘린더에 업무를
          기록하면, 그 기록이 주간보고가 되고, 주간회의에서 한 명이 화면을 띄워 팀원별로 넘겨보고, 휴가 때는 그
          업무를 다른 사람에게 넘길 수 있는 도구입니다. 구글 캘린더 연동, RADIUS 로그인, Coolify 배포, 사내 웍스 AI
          연동까지 각 기능을 <strong>어떻게 붙이는지와 왜 그렇게 하는지</strong>를 15단계로 나눠 다룹니다.
        </p>

        <div className="mt-6 flex flex-wrap gap-2.5">
          <Link
            to="/steps/orientation"
            className="bg-brand-500 hover:bg-brand-600 rounded-lg px-4 py-2.5 text-[13.5px] font-semibold text-white transition"
          >
            STEP 00부터 시작하기
          </Link>
          <Link
            to="/demo/calendar"
            className="border-hair hover:border-brand-500/60 rounded-lg border px-4 py-2.5 text-[13.5px] font-semibold transition"
          >
            완성된 결과물 먼저 보기
          </Link>
          <Link
            to="/prompts"
            className="border-hair hover:border-brand-500/60 rounded-lg border px-4 py-2.5 text-[13.5px] transition"
          >
            프롬프트 {totalPrompts}개 한눈에
          </Link>
        </div>
      </section>

      {/* 사용법 */}
      <section className="mb-10 grid gap-3 sm:grid-cols-3">
        {[
          {
            n: '01',
            t: '프롬프트를 복사한다',
            d: '각 스텝에는 그대로 붙여넣을 수 있는 프롬프트가 있다. AI 대화창(Claude Code / Cursor / 사내 AI)에 붙여넣고 실행한다.',
          },
          {
            n: '02',
            t: '기다리기 싫으면 샘플을 본다',
            d: '프롬프트마다 실행하면 나올 결과물을 미리 넣어 두었다. AI 응답을 기다리지 않고 샘플만 읽어도 흐름을 이해할 수 있다.',
          },
          {
            n: '03',
            t: '원리를 확인한다',
            d: 'dX팀이 대신 만들어 줄 수 있지만, 왜 어렵고 무엇을 결정해야 하는지는 알아야 한다. 그게 요청의 품질을 바꾼다.',
          },
        ].map((c) => (
          <div key={c.n} className="border-hair surface rounded-xl border p-4">
            <div className="text-brand-500 font-mono text-[11px] font-semibold">{c.n}</div>
            <h3 className="mt-1 text-[13.5px] font-semibold">{c.t}</h3>
            <p className="text-muted mt-1.5 text-[12.5px] leading-6">{c.d}</p>
          </div>
        ))}
      </section>

      {/* 만들 것 */}
      <section className="mb-10">
        <h2 className="mb-3 text-[15px] font-semibold tracking-tight">이 과정에서 만드는 것</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { to: '/demo/calendar', t: '캘린더', d: '월/주 뷰, 빠른 입력, 드래그 이동, 카테고리·공개범위', tag: 'STEP 04–05' },
            { to: '/demo/integrations', t: '외부 캘린더 연동', d: '구글 양방향, 네이버·ICS 읽기 전용, 증분 동기화', tag: 'STEP 06–07' },
            { to: '/demo/weekly', t: '주간보고', d: '캘린더 자동 집계, 수정 보존, 시간 배분 통계', tag: 'STEP 08' },
            { to: '/demo/present', t: '발표 모드', d: '주간회의용 전체화면, 키보드 조작, 회의록 복사', tag: 'STEP 09' },
            { to: '/demo/handover', t: '인수인계', d: '부재 기간 자동 수집, 요청→확인→완료, 감사 로그', tag: 'STEP 10' },
            { to: '/steps/works-ai', t: 'AI · 인증 · 배포', d: '웍스 AI 연동, RADIUS 로그인, Coolify 배포', tag: 'STEP 11–13' },
          ].map((f) => (
            <Link
              key={f.to}
              to={f.to}
              className="border-hair surface hover:border-brand-500/60 group rounded-xl border p-4 transition"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-[13.5px] font-semibold">{f.t}</h3>
                <span className="text-muted font-mono text-[10px]">{f.tag}</span>
              </div>
              <p className="text-muted mt-1.5 text-[12.5px] leading-6">{f.d}</p>
              <span className="text-brand-500 mt-2 inline-block text-[12px] opacity-0 transition group-hover:opacity-100">
                열어보기 →
              </span>
            </Link>
          ))}
        </div>
      </section>

      {/* 커리큘럼 */}
      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-[15px] font-semibold tracking-tight">커리큘럼 · 15단계</h2>
          {doneCount > 0 && (
            <button onClick={reset} className="text-muted hover:text-brand-500 text-[12px] underline">
              진행 상황 초기화 ({doneCount}개 완료)
            </button>
          )}
        </div>

        <div className="space-y-6">
          {parts.map((part) => (
            <div key={part}>
              <div className="text-muted mb-2 text-[11px] font-semibold tracking-wider">{part}</div>
              <ul className="border-hair surface divide-y overflow-hidden rounded-xl border">
                {stepsOf(part).map((s) => (
                  <li key={s.id} className="border-hair">
                    <Link
                      to={`/steps/${s.slug}`}
                      className="hover:surface-2 flex items-center gap-3 px-4 py-3 transition"
                    >
                      <span
                        className={
                          'flex h-6 w-6 shrink-0 items-center justify-center rounded font-mono text-[10.5px] font-semibold ' +
                          (isDone(s.id) ? 'bg-emerald-500 text-white' : 'surface-2 text-muted')
                        }
                      >
                        {isDone(s.id) ? '✓' : s.id}
                      </span>
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-[13.5px] font-medium">{s.title}</span>
                          <span
                            className={
                              'rounded px-1.5 py-0.5 text-[10px] font-medium ' +
                              (s.level === '심화'
                                ? 'bg-amber-500/15 text-amber-500'
                                : s.level === '기본'
                                  ? 'bg-brand-500/15 text-brand-500'
                                  : 'surface-2 text-muted')
                            }
                          >
                            {s.level}
                          </span>
                        </div>
                        <p className="text-muted mt-0.5 truncate text-[12px]">{s.tagline}</p>
                      </div>
                      <span className="text-muted shrink-0 text-[11.5px]">{s.duration}</span>
                      <span className="text-muted shrink-0 text-[11.5px]">프롬프트 {s.prompts.length}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section className="border-hair mt-10 rounded-xl border border-dashed p-5">
        <h2 className="text-[14px] font-semibold">이 과정을 다 따라오지 않아도 됩니다</h2>
        <p className="text-muted mt-2 text-[13px] leading-7">
          최종적으로 필요한 기능은 <strong>dX팀에서 구축해 드립니다.</strong> 이 교육의 목표는 혼자 다 만들 수 있게
          되는 것이 아니라, <strong>무엇을 원하는지 정확히 말하고, 왜 어려운지 이해하고, 만들어진 것을 검증할 수
          있게</strong> 되는 것입니다. 마지막 스텝에는 dX팀에 그대로 전달할 수 있는{' '}
          <Link to="/steps/operate-and-next" className="text-brand-500 underline">
            개발 요청서 양식
          </Link>
          이 들어 있습니다.
        </p>
      </section>
    </div>
  )
}
