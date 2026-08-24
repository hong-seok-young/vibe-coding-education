import { useState } from 'react'
import { Link } from 'react-router-dom'
import { fmtDate, fmtTime } from '../lib/dates'
import { useCopy } from '../lib/useCopy'
import { useDemo } from './store'
import { useGoogleLive } from './google/useGoogleLive'

/**
 * 실제 구글 캘린더에 붙어서 동기화를 시연하는 데모.
 * STEP 06 이 글로 설명한 것(증분 동기화, 중복 방지, 삭제 반영, syncToken 만료 폴백)을
 * 학습자 본인 캘린더로 직접 확인하게 하는 화면이다.
 */
export function GoogleLiveDemo() {
  const g = useGoogleLive()
  const { events } = useDemo()
  const [showSetup, setShowSetup] = useState(false)
  const origin = typeof window !== 'undefined' ? window.location.origin : ''
  const { copied, copy } = useCopy()

  const googleEvents = events
    .filter((e) => e.source === 'GOOGLE' && e.externalId)
    .sort((a, b) => a.start.getTime() - b.start.getTime())

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-6">
      {/* 이 데모의 성격을 먼저 밝힌다 */}
      <div className="mb-5 rounded-xl border border-amber-500/40 bg-amber-500/5 px-4 py-3.5">
        <div className="mb-1.5 text-[13px] font-semibold">⚠️ 이 데모는 브라우저 전용 흐름이다</div>
        <p className="text-[13px] leading-7">
          이 교육 프로그램은 서버가 없는 정적 사이트다. 그래서 STEP 06 이 가르치는 정식 흐름(서버가 클라이언트
          시크릿으로 토큰을 교환하고 <code className="surface-2 rounded px-1">refresh_token</code>을 암호화해
          보관)을 쓸 수 없다. 대신 구글이 자바스크립트 앱에 제공하는 토큰 흐름을 쓴다.{' '}
          <strong>실제 사내 앱은 반드시 서버 흐름으로 만들어야 한다.</strong>
        </p>
        <div className="border-hair mt-3 overflow-x-auto rounded-lg border">
          <table className="w-full text-[12.5px]">
            <thead className="surface-2">
              <tr>
                <th className="border-hair border-b px-3 py-1.5 text-left font-semibold">항목</th>
                <th className="border-hair border-b px-3 py-1.5 text-left font-semibold">서버 흐름 (실제 앱)</th>
                <th className="border-hair border-b px-3 py-1.5 text-left font-semibold">브라우저 흐름 (이 데모)</th>
              </tr>
            </thead>
            <tbody>
              {[
                ['클라이언트 시크릿', '서버에만 보관', '쓰지 않음 (클라이언트 ID만)'],
                ['refresh_token', '받아서 암호화 저장', '받을 수 없음'],
                ['토큰 보관', '서버 DB (암호화)', '메모리만 — 새로고침하면 사라짐'],
                ['자동 주기 동기화', '가능 (서버 스케줄러)', '불가능 — 화면을 열고 눌러야 함'],
                ['내보내기', '가능', '가능 (쓰기 권한 선택 시)'],
              ].map((r) => (
                <tr key={r[0]} className="border-hair border-b last:border-0">
                  <td className="px-3 py-1.5 font-medium">{r[0]}</td>
                  <td className="text-muted px-3 py-1.5">{r[1]}</td>
                  <td className="px-3 py-1.5">{r[2]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {g.scriptBlocked && (
        <div className="mb-5 rounded-xl border border-red-500/40 bg-red-500/5 px-4 py-3">
          <div className="mb-1 text-[13px] font-semibold">이 환경에서는 실제 연동을 시연할 수 없다</div>
          <p className="text-[13px] leading-7">
            지금 보고 있는 곳이 외부 스크립트를 차단하고 있다. GitHub Pages 로 배포된 주소나 로컬 개발 서버에서
            열면 실제 연동을 시도할 수 있다. 아래 준비 절차와 실습 순서는 그대로 읽어볼 수 있다.
          </p>
        </div>
      )}

      {/* 준비 절차 */}
      <div className="border-hair surface mb-5 rounded-xl border">
        <button
          onClick={() => setShowSetup((v) => !v)}
          className="flex w-full items-center justify-between px-4 py-3 text-left"
        >
          <span className="text-[13px] font-semibold">
            준비 절차 — 구글 클라우드 콘솔에서 클라이언트 ID 만들기 (5분, 1회)
          </span>
          <span className="text-muted text-xs">{showSetup ? '접기' : '펼치기'}</span>
        </button>

        {showSetup && (
          <div className="border-hair space-y-3 border-t px-4 py-4 text-[13.5px] leading-7">
            <ol className="space-y-2">
              <li>
                <strong>1.</strong>{' '}
                <a
                  href="https://console.cloud.google.com/projectcreate"
                  target="_blank"
                  rel="noreferrer noopener"
                  className="text-brand-500 underline"
                >
                  구글 클라우드 콘솔
                </a>
                에서 프로젝트를 만든다. (예: <code className="surface-2 rounded px-1">vibe-edu-test</code>)
              </li>
              <li>
                <strong>2.</strong> API 라이브러리에서 <strong>Google Calendar API</strong> 를 활성화한다.
                이걸 빼먹으면 나중에 <code className="surface-2 rounded px-1">403</code> 이 뜬다.
              </li>
              <li>
                <strong>3.</strong> OAuth 동의 화면을 구성한다. 사용자 유형은 조직 계정이면 "내부",
                개인 계정이면 "외부"로 두고, <strong>외부라면 테스트 사용자에 본인 계정을 추가</strong>한다.
                (추가하지 않으면 동의 화면에서 막힌다)
              </li>
              <li>
                <strong>4.</strong> 사용자 인증 정보 → OAuth 클라이언트 ID → 애플리케이션 유형{' '}
                <strong>웹 애플리케이션</strong>. <strong>승인된 JavaScript 원본</strong>에 지금 이 페이지의
                주소를 넣는다.
                <div className="surface-2 border-hair mt-2 flex flex-wrap items-center gap-2 rounded-lg border px-3 py-2">
                  <code className="min-w-0 flex-1 truncate font-mono text-[12px]">{origin}</code>
                  <button
                    onClick={() => copy(origin)}
                    className="border-hair hover:border-brand-500/60 shrink-0 rounded border px-2 py-1 text-[11.5px]"
                  >
                    {copied ? '복사됨 ✓' : '복사'}
                  </button>
                </div>
                <span className="text-muted text-[12.5px]">
                  리디렉션 URI 는 이 흐름에서 쓰지 않는다. 원본(origin)만 정확해야 한다.
                </span>
              </li>
              <li>
                <strong>5.</strong> 만들어진 <strong>클라이언트 ID</strong>(
                <code className="surface-2 rounded px-1">...apps.googleusercontent.com</code>)를 아래에 붙여넣는다.
                클라이언트 시크릿은 이 데모에서 쓰지 않는다 — 브라우저에 시크릿을 두면 안 되기 때문이다.
              </li>
            </ol>
            <p className="text-muted text-[12.5px] leading-6">
              클라이언트 ID는 비밀값이 아니다. 브라우저에 노출되는 것이 정상이며, 허용된 원본에서만 동작한다.
              반대로 <strong>클라이언트 시크릿은 절대 브라우저에 두지 않는다.</strong>
            </p>
          </div>
        )}
      </div>

      {/* 연결 */}
      <div className="border-hair surface mb-5 rounded-xl border p-4">
        <h3 className="mb-3 text-[13px] font-semibold">1. 연결</h3>

        <label className="mb-3 block">
          <span className="text-muted mb-1 block text-[11.5px] font-medium">
            OAuth 클라이언트 ID {g.clientIdFromEnv && '(배포 설정값이 미리 채워져 있다)'}
          </span>
          <input
            value={g.clientId}
            onChange={(e) => g.setClientId(e.target.value)}
            placeholder="1234567890-abcdef.apps.googleusercontent.com"
            spellCheck={false}
            className="border-hair surface-2 w-full rounded-md border px-2.5 py-2 font-mono text-[12.5px] outline-none focus:border-brand-500"
          />
          <span className="text-muted mt-1 block text-[11.5px]">
            이 값은 이 브라우저에만 저장된다 (localStorage). 다른 사람에게 전송되지 않는다.
          </span>
        </label>

        {g.phase === 'connected' ? (
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 rounded-lg border border-emerald-500/40 bg-emerald-500/5 px-3 py-2.5 text-[13px]">
              <span className="font-semibold text-emerald-500">연결됨</span>
              <span>{g.account?.summary}</span>
              <span className="text-muted">{g.account?.timeZone}</span>
              <span
                className={
                  'rounded px-1.5 py-0.5 text-[11px] font-semibold ' +
                  (g.canWrite ? 'bg-amber-500/15 text-amber-500' : 'surface-2 text-muted')
                }
              >
                {g.canWrite ? '읽기 + 쓰기' : '읽기 전용'}
              </span>
              <span className="text-muted ml-auto font-mono text-[12px] tabular-nums">
                토큰 만료까지 {Math.floor(g.secondsLeft / 60)}:
                {String(g.secondsLeft % 60).padStart(2, '0')}
              </span>
            </div>
            <button
              onClick={() => void g.disconnect()}
              disabled={!!g.busy}
              className="border-hair text-muted hover:text-red-500 rounded-md border px-3 py-1.5 text-[12.5px] disabled:opacity-50"
            >
              {g.busy === 'disconnect' ? '해제 중…' : '연결 해제 (권한 회수 + 가져온 일정 정리)'}
            </button>
          </div>
        ) : (
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => void g.connect(false)}
              disabled={!g.clientId.trim() || !!g.busy}
              className="bg-brand-500 hover:bg-brand-600 rounded-md px-3.5 py-2 text-[13px] font-semibold text-white disabled:opacity-45"
            >
              {g.busy === 'connect' ? '구글 창 대기 중…' : '읽기 전용으로 연결'}
            </button>
            <button
              onClick={() => void g.connect(true)}
              disabled={!g.clientId.trim() || !!g.busy}
              className="border-hair hover:border-brand-500/60 rounded-md border px-3.5 py-2 text-[13px] disabled:opacity-45"
            >
              읽기 + 쓰기로 연결
            </button>
            {g.expired && (
              <span className="text-[12.5px] text-amber-500">
                토큰이 만료됐다. 다시 연결하면 이어서 실습할 수 있다.
              </span>
            )}
            <p className="text-muted mt-1 w-full text-[12px] leading-6">
              내보내기 실습(4번)을 하려면 쓰기 권한이 필요하다. 필요 없다면 <strong>읽기 전용</strong>으로
              연결하는 것이 원칙이다 — 최소 권한만 요청하는 것이 STEP 06 의 규칙이다.
            </p>
          </div>
        )}

        {g.error && (
          <div className="mt-3 rounded-lg border border-red-500/40 bg-red-500/5 px-3 py-2">
            <div className="text-[13px] font-semibold">{g.error.message}</div>
            {g.error.remedy && <div className="text-muted mt-0.5 text-[12.5px]">{g.error.remedy}</div>}
          </div>
        )}
      </div>

      {/* 실습 */}
      <div className="border-hair surface mb-5 rounded-xl border p-4">
        <h3 className="mb-1 text-[13px] font-semibold">2. 실습 — STEP 06 이 글로 설명한 것을 직접 확인</h3>
        <p className="text-muted mb-4 text-[12.5px] leading-6">
          순서대로 해보면 동기화의 3대 고질병(중복·핑퐁·유령 일정)이 왜 생기고 어떻게 막는지 눈으로 보인다.
        </p>

        <div className="space-y-3">
          <Exercise
            n={1}
            title="전체 동기화"
            desc="최근 1개월 ~ 향후 2개월 범위의 일정을 모두 가져온다. 범위를 자르지 않으면 평생 일정을 끌어온다는 것이 이 단계의 교훈이다."
            action={
              <button
                onClick={() => void g.sync({ forceFull: true })}
                disabled={g.phase !== 'connected' || !!g.busy}
                className="bg-brand-500 hover:bg-brand-600 rounded-md px-3 py-1.5 text-[12.5px] font-semibold text-white disabled:opacity-45"
              >
                {g.busy === 'sync' ? '동기화 중…' : '전체 동기화'}
              </button>
            }
          />

          <Exercise
            n={2}
            title="증분 동기화 — 변경분만 오는지"
            desc="구글 캘린더를 새 탭에서 열어 일정 하나를 추가하거나 제목을 바꾼 뒤 이 버튼을 눌러보라. 전체가 아니라 방금 바꾼 것만 잡히고, 이미 가져온 일정은 '건너뜀'으로 처리된다."
            hint={
              g.syncToken
                ? `저장된 syncToken: ${g.syncToken.slice(0, 14)}… (이게 "지난번에 어디까지 봤다"는 책갈피다)`
                : '아직 syncToken 이 없다. 먼저 1번 전체 동기화를 해야 발급된다.'
            }
            action={
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => void g.sync()}
                  disabled={g.phase !== 'connected' || !!g.busy}
                  className="bg-brand-500 hover:bg-brand-600 rounded-md px-3 py-1.5 text-[12.5px] font-semibold text-white disabled:opacity-45"
                >
                  증분 동기화
                </button>
                <a
                  href="https://calendar.google.com"
                  target="_blank"
                  rel="noreferrer noopener"
                  className="border-hair hover:border-brand-500/60 rounded-md border px-3 py-1.5 text-[12.5px]"
                >
                  구글 캘린더 열기 ↗
                </a>
                {g.syncToken && (
                  <button
                    onClick={g.resetSyncToken}
                    className="text-muted hover:text-brand-500 text-[12px] underline"
                  >
                    syncToken 버리기 (다음 동기화가 전체로 돌아가는 것 확인)
                  </button>
                )}
              </div>
            }
          />

          <Exercise
            n={3}
            title="원격 삭제가 반영되는지"
            desc="구글 캘린더에서 일정 하나를 지우고 증분 동기화를 눌러보라. 우리 쪽에서도 사라진다. 이 처리를 빼먹으면 지운 일정이 주간보고에 계속 등장하는 '유령 일정'이 된다."
            action={
              <button
                onClick={() => void g.sync()}
                disabled={g.phase !== 'connected' || !!g.busy}
                className="border-hair hover:border-brand-500/60 rounded-md border px-3 py-1.5 text-[12.5px] disabled:opacity-45"
              >
                증분 동기화로 확인
              </button>
            }
          />

          <Exercise
            n={4}
            title="내보내기 — 그리고 중복이 안 생기는지"
            desc='우리 앱에서 구글로 일정을 하나 내보낸다("[교육 데모] 내보내기 테스트"). 그 다음 증분 동기화를 하면 방금 만든 일정이 되돌아오는데, externalId 로 짝을 찾기 때문에 새 일정이 하나 더 생기지 않고 기존 것과 연결된다.'
            warn="실제 구글 캘린더에 일정이 생성된다. 아래 정리 버튼으로 지울 수 있다."
            action={
              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={() => void g.exportTest()}
                  disabled={!g.canWrite || !!g.busy}
                  className="bg-brand-500 hover:bg-brand-600 rounded-md px-3 py-1.5 text-[12.5px] font-semibold text-white disabled:opacity-45"
                >
                  {g.busy === 'export' ? '생성 중…' : '구글로 내보내기'}
                </button>
                <button
                  onClick={() => void g.cleanupCreated()}
                  disabled={!g.canWrite || g.createdCount === 0 || !!g.busy}
                  className="border-hair hover:border-red-500/60 rounded-md border px-3 py-1.5 text-[12.5px] disabled:opacity-45"
                >
                  {g.busy === 'cleanup' ? '정리 중…' : `만든 일정 정리 (${g.createdCount})`}
                </button>
                {!g.canWrite && (
                  <span className="text-muted text-[12px]">
                    쓰기 권한으로 연결해야 이 실습이 열린다
                  </span>
                )}
              </div>
            }
          />
        </div>
      </div>

      {/* 동기화 로그 */}
      <div className="border-hair surface mb-5 overflow-hidden rounded-xl border">
        <div className="border-hair surface-2 flex items-center justify-between border-b px-4 py-2.5">
          <h3 className="text-[13px] font-semibold">동기화 기록</h3>
          <span className="text-muted text-[11.5px]">
            조용히 실패하는 동기화를 막으려면 결과 숫자를 사람에게 보여줘야 한다
          </span>
        </div>
        {g.log.length === 0 ? (
          <p className="text-muted px-4 py-6 text-center text-[13px]">
            아직 기록이 없다. 연결한 뒤 위 실습을 눌러보라.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-[12.5px]">
              <thead className="surface-2 text-muted">
                <tr>
                  {['시각', '방식', '받은 항목', '신규', '갱신', '건너뜀', '삭제', '페이지', '소요'].map((h) => (
                    <th key={h} className="border-hair border-b px-3 py-1.5 text-left font-medium whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {g.log.map((l, i) => (
                  <tr key={i} className="border-hair border-b last:border-0">
                    <td className="px-3 py-1.5 font-mono tabular-nums">{fmtTime(l.at)}</td>
                    <td className="px-3 py-1.5">
                      <span
                        className={
                          'rounded px-1.5 py-0.5 text-[11px] font-semibold ' +
                          (l.mode === 'full'
                            ? 'bg-amber-500/15 text-amber-500'
                            : 'bg-brand-500/15 text-brand-500')
                        }
                      >
                        {l.mode === 'full' ? '전체' : '증분'}
                      </span>
                    </td>
                    <td className="px-3 py-1.5 tabular-nums">{l.fetched}</td>
                    <td className="px-3 py-1.5 tabular-nums">{l.created}</td>
                    <td className="px-3 py-1.5 tabular-nums">{l.updated}</td>
                    <td className="text-muted px-3 py-1.5 tabular-nums">{l.skipped}</td>
                    <td className="px-3 py-1.5 tabular-nums">{l.deleted}</td>
                    <td className="text-muted px-3 py-1.5 tabular-nums">{l.pages}</td>
                    <td className="text-muted px-3 py-1.5 tabular-nums">{l.ms}ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {g.log.some((l) => l.note) && (
              <ul className="border-hair space-y-1 border-t px-4 py-2.5">
                {g.log
                  .filter((l) => l.note)
                  .slice(0, 4)
                  .map((l, i) => (
                    <li key={i} className="text-muted text-[12px] leading-6">
                      {fmtTime(l.at)} · {l.note}
                    </li>
                  ))}
              </ul>
            )}
          </div>
        )}
      </div>

      {/* 가져온 일정 */}
      <div className="border-hair surface overflow-hidden rounded-xl border">
        <div className="border-hair surface-2 flex flex-wrap items-center justify-between gap-2 border-b px-4 py-2.5">
          <h3 className="text-[13px] font-semibold">가져온 구글 일정 {g.googleEventCount}건</h3>
          <Link to="/steps/calendar-ui/demo" className="text-brand-500 text-[12px] hover:underline">
            캘린더 데모에서 겹쳐 보기 →
          </Link>
        </div>
        {googleEvents.length === 0 ? (
          <p className="text-muted px-4 py-6 text-center text-[13px]">
            동기화하면 여기에 실제 구글 일정이 나타난다.
          </p>
        ) : (
          <ul className="divide-y">
            {googleEvents.slice(0, 12).map((e) => (
              <li key={e.id} className="border-hair flex items-center gap-3 px-4 py-2 text-[13px]">
                <span className="text-muted w-24 shrink-0 tabular-nums">
                  {fmtDate(e.start)} {e.allDay ? '종일' : fmtTime(e.start)}
                </span>
                <span className="min-w-0 flex-1 truncate">{e.title}</span>
                <span className="text-muted shrink-0 font-mono text-[10.5px]">
                  {e.externalId?.slice(0, 8)}…
                </span>
              </li>
            ))}
            {googleEvents.length > 12 && (
              <li className="text-muted px-4 py-2 text-[12px]">그 외 {googleEvents.length - 12}건</li>
            )}
          </ul>
        )}
      </div>

      <p className="text-muted mt-5 text-[12px] leading-6">
        이 데모는 사용자의 기본 캘린더(primary)만 읽는다. 액세스 토큰은 메모리에만 두므로 새로고침하면 다시
        연결해야 한다 — 브라우저에 토큰을 저장하지 않는 것이 원칙이고, 그 불편함이 곧 실제 앱에 서버가 필요한
        이유다. "연결 해제"를 누르면 권한을 회수하고 가져온 일정도 정리한다.
      </p>
    </div>
  )
}

function Exercise({
  n, title, desc, hint, warn, action,
}: {
  n: number
  title: string
  desc: string
  hint?: string
  warn?: string
  action: React.ReactNode
}) {
  return (
    <div className="border-hair rounded-lg border p-3.5">
      <div className="mb-1 flex items-center gap-2">
        <span className="surface-2 flex h-5 w-5 items-center justify-center rounded font-mono text-[10.5px] font-semibold">
          {n}
        </span>
        <span className="text-[13px] font-semibold">{title}</span>
      </div>
      <p className="text-muted mb-2 text-[12.5px] leading-6">{desc}</p>
      {hint && <p className="text-brand-500 mb-2 font-mono text-[11.5px] break-all">{hint}</p>}
      {warn && (
        <p className="mb-2 rounded border border-amber-500/40 bg-amber-500/5 px-2 py-1 text-[12px] leading-6">
          ⚠️ {warn}
        </p>
      )}
      {action}
    </div>
  )
}
