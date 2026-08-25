import { useState } from 'react'
import { Link } from 'react-router-dom'
import { fmtDate, fmtTime } from '../lib/dates'
import { GuideView } from '../components/GuideView'
import { findGuide } from '../content/guides'
import { useDemo } from './store'
import { useGoogleLive } from './google/useGoogleLive'

/**
 * 실제 구글 캘린더에 붙어서 동기화를 시연하는 데모.
 *
 * 교육생이 수업 중에 따라오는 화면이므로 "지금 할 일" 하나만 크게 보이게 만든다.
 * 설명·비교표·주의사항은 접어두고, 필요할 때만 펼치게 한다.
 */
/** 이 데모를 하려면 먼저 끝내야 하는 안내서 */
const setupGuide = findGuide('google-client-id')!

export function GoogleLiveDemo() {
  const g = useGoogleLive()
  const { events } = useDemo()
  const [openSetup, setOpenSetup] = useState(false)
  const [openWhy, setOpenWhy] = useState(false)

  const googleEvents = events
    .filter((e) => e.source === 'GOOGLE' && e.externalId)
    .sort((a, b) => a.start.getTime() - b.start.getTime())

  const connected = g.phase === 'connected'
  const hasSynced = g.log.some((l) => l.fetched > 0 || l.created > 0)

  // 화면 맨 위에 "지금 할 일" 한 줄만 띄운다
  const nowDo = g.scriptBlocked
    ? { step: '—', text: '이 환경에서는 실제 연동을 시연할 수 없습니다. 배포된 주소나 로컬 개발 서버에서 열어주세요.' }
    : !g.clientId.trim()
      ? { step: '1', text: '구글 클라우드 콘솔에서 만든 클라이언트 ID를 아래에 붙여넣으세요.' }
      : !connected
        ? { step: '2', text: '"구글 계정 연결" 을 눌러 본인 캘린더에 연결하세요.' }
        : !hasSynced
          ? { step: '3', text: '"전체 동기화" 를 눌러 내 구글 일정을 가져오세요.' }
          : { step: '4', text: '구글 캘린더에서 일정을 바꾼 뒤 "변경분만 가져오기" 를 눌러보세요.' }

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-6">
      {/* 지금 할 일 */}
      <div className="border-brand-500/50 bg-brand-500/5 mb-5 flex items-center gap-3 rounded-xl border px-4 py-3.5">
        <span className="bg-brand-500 flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[13px] font-bold text-white">
          {nowDo.step}
        </span>
        <p className="text-[14px] leading-6 font-medium">{nowDo.text}</p>
      </div>

      {g.scriptBlocked && (
        <p className="mb-5 rounded-xl border border-red-500/40 bg-red-500/5 px-4 py-3 text-[13px] leading-7">
          지금 보고 있는 곳이 외부 스크립트를 차단하고 있습니다. 아래 준비 절차와 실습 순서는 그대로 읽어볼 수
          있습니다.
        </p>
      )}

      {/* 1. 클라이언트 ID */}
      <Card n="1" title="클라이언트 ID 넣기" done={!!g.clientId.trim()}>
        <input
          value={g.clientId}
          onChange={(e) => g.setClientId(e.target.value)}
          placeholder="1234567890-abcdef.apps.googleusercontent.com"
          spellCheck={false}
          className="border-hair surface-2 focus:border-brand-500 w-full rounded-lg border px-3 py-2.5 font-mono text-[12.5px] outline-none"
        />
        <div className="text-muted mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px]">
          <span>이 브라우저에만 저장됩니다.</span>
          <button onClick={() => setOpenSetup((v) => !v)} className="text-brand-500 underline">
            {openSetup ? '안내서 접기' : '클라이언트 ID 만드는 법 — 클릭 단위 안내서'}
          </button>
          {g.clientIdFromEnv && <span>배포 설정값이 미리 채워져 있습니다.</span>}
        </div>

        {openSetup && (
          <div className="border-hair mt-3 rounded-xl border border-dashed p-4">
            <GuideView guide={setupGuide} />
          </div>
        )}
      </Card>

      {/* 2. 연결 */}
      <Card n="2" title="구글 계정 연결" done={connected} dim={!g.clientId.trim()}>
        {connected ? (
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
            <span className="flex items-center gap-2 text-[14px] font-semibold text-emerald-500">
              ● 연결됨
            </span>
            <span className="text-[13.5px]">{g.account?.summary}</span>
            <span
              className={
                'rounded px-1.5 py-0.5 text-[11px] font-semibold ' +
                (g.canWrite ? 'bg-amber-500/15 text-amber-500' : 'surface-2 text-muted')
              }
            >
              {g.canWrite ? '읽기 + 쓰기' : '읽기 전용'}
            </span>
            <span className="text-muted font-mono text-[12px] tabular-nums">
              {Math.floor(g.secondsLeft / 60)}:{String(g.secondsLeft % 60).padStart(2, '0')} 뒤 만료
            </span>
            <button
              onClick={() => void g.disconnect()}
              disabled={!!g.busy}
              className="text-muted hover:text-red-500 ml-auto text-[12.5px] underline disabled:opacity-50"
            >
              연결 해제
            </button>
          </div>
        ) : (
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => void g.connect(false)}
              disabled={!g.clientId.trim() || !!g.busy}
              className="bg-brand-500 hover:bg-brand-600 rounded-lg px-4 py-2.5 text-[13.5px] font-semibold text-white disabled:opacity-40"
            >
              {g.busy === 'connect' ? '구글 창 대기 중…' : '구글 계정 연결 (읽기 전용)'}
            </button>
            <button
              onClick={() => void g.connect(true)}
              disabled={!g.clientId.trim() || !!g.busy}
              className="border-hair hover:border-brand-500/60 rounded-lg border px-3.5 py-2.5 text-[12.5px] disabled:opacity-40"
            >
              쓰기 권한도 함께 (4번 실습용)
            </button>
            {g.expired && <span className="text-[12.5px] text-amber-500">토큰이 만료됐습니다. 다시 연결하세요.</span>}
          </div>
        )}

        {connected && (
          <p className="text-muted mt-2 text-[12px] leading-6">
            실습이 끝나면{' '}
            <Link to="/guides/google-revoke" className="text-brand-500 underline">
              권한 정리 안내서
            </Link>
            대로 구글 계정에서 이 앱의 접근 권한까지 지우세요.
          </p>
        )}

        {g.error && (
          <div className="mt-3 rounded-lg border border-red-500/40 bg-red-500/5 px-3 py-2">
            <div className="text-[13px] font-semibold">{g.error.message}</div>
            {g.error.remedy && <div className="text-muted mt-0.5 text-[12.5px] leading-6">{g.error.remedy}</div>}
          </div>
        )}
      </Card>

      {/* 3. 실습 */}
      <Card n="3" title="동기화 해보기" done={hasSynced} dim={!connected}>
        <div className="grid gap-2.5 sm:grid-cols-2">
          <Try
            title="전체 동기화"
            proves="처음엔 전부 가져온다"
            disabled={!connected || !!g.busy}
            onClick={() => void g.sync({ forceFull: true })}
            busy={g.busy === 'sync'}
            primary
          />
          <Try
            title="변경분만 가져오기"
            proves="바뀐 것만 온다 (증분 동기화)"
            disabled={!connected || !!g.busy}
            onClick={() => void g.sync()}
            busy={g.busy === 'sync'}
            hint={g.syncToken ? `책갈피: ${g.syncToken.slice(0, 10)}…` : '전체 동기화를 먼저 하세요'}
          />
          <Try
            title="구글로 내보내기"
            proves="우리 일정이 구글에 생기고, 다시 받아도 중복이 안 생긴다"
            disabled={!g.canWrite || !!g.busy}
            onClick={() => void g.exportTest()}
            busy={g.busy === 'export'}
            hint={g.canWrite ? '실제 일정이 생성됩니다' : '쓰기 권한으로 연결해야 합니다'}
          />
          <Try
            title={`만든 일정 정리 (${g.createdCount})`}
            proves="데모가 만든 일정만 지운다"
            disabled={!g.canWrite || g.createdCount === 0 || !!g.busy}
            onClick={() => void g.cleanupCreated()}
            busy={g.busy === 'cleanup'}
          />
        </div>

        <div className="text-muted mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-[12px]">
          <a
            href="https://calendar.google.com"
            target="_blank"
            rel="noreferrer noopener"
            className="text-brand-500 underline"
          >
            구글 캘린더 열기 ↗
          </a>
          <span>거기서 일정을 추가·수정·삭제한 뒤 "변경분만 가져오기"를 눌러보세요.</span>
          <Link to="/guides/google-sync-test" className="text-brand-500 underline">
            순서대로 따라 하는 안내서 →
          </Link>
          {g.syncToken && (
            <button onClick={g.resetSyncToken} className="underline hover:text-brand-500">
              책갈피 버리기 (다음이 전체 동기화로 돌아가는 것 확인)
            </button>
          )}
        </div>
      </Card>

      {/* 결과 */}
      {(g.log.length > 0 || googleEvents.length > 0) && (
        <div className="grid gap-4 lg:grid-cols-2">
          <section className="border-hair surface overflow-hidden rounded-xl border">
            <header className="border-hair surface-2 border-b px-4 py-2.5">
              <h3 className="text-[13px] font-semibold">동기화 결과</h3>
              <p className="text-muted text-[11.5px]">전체와 증분이 몇 건씩 오는지 비교해 보세요</p>
            </header>
            {g.log.length === 0 ? (
              <p className="text-muted px-4 py-6 text-center text-[13px]">아직 없습니다.</p>
            ) : (
              <ul className="divide-y">
                {g.log.slice(0, 6).map((l, i) => (
                  <li key={i} className="border-hair px-4 py-2.5">
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[12.5px]">
                      <span
                        className={
                          'rounded px-1.5 py-0.5 text-[11px] font-semibold ' +
                          (l.mode === 'full' ? 'bg-amber-500/15 text-amber-500' : 'bg-brand-500/15 text-brand-500')
                        }
                      >
                        {l.mode === 'full' ? '전체' : '증분'}
                      </span>
                      <span className="text-muted font-mono tabular-nums">{fmtTime(l.at)}</span>
                      <span className="tabular-nums">받음 {l.fetched}</span>
                      <span className="tabular-nums text-emerald-500">신규 {l.created}</span>
                      <span className="tabular-nums">갱신 {l.updated}</span>
                      <span className="text-muted tabular-nums">건너뜀 {l.skipped}</span>
                      {l.deleted > 0 && <span className="tabular-nums text-red-500">삭제 {l.deleted}</span>}
                      <span className="text-muted ml-auto tabular-nums">{l.ms}ms</span>
                    </div>
                    {l.note && <p className="text-muted mt-1 text-[11.5px] leading-6">{l.note}</p>}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="border-hair surface overflow-hidden rounded-xl border">
            <header className="border-hair surface-2 border-b px-4 py-2.5">
              <h3 className="text-[13px] font-semibold">가져온 내 구글 일정 {g.googleEventCount}건</h3>
              <p className="text-muted text-[11.5px]">캘린더 화면(STEP 04·05)에도 함께 표시됩니다</p>
            </header>
            {googleEvents.length === 0 ? (
              <p className="text-muted px-4 py-6 text-center text-[13px]">동기화하면 여기에 나타납니다.</p>
            ) : (
              <ul className="divide-y">
                {googleEvents.slice(0, 8).map((e) => (
                  <li key={e.id} className="border-hair flex items-center gap-3 px-4 py-2 text-[13px]">
                    <span className="text-muted w-20 shrink-0 tabular-nums">
                      {fmtDate(e.start)} {e.allDay ? '종일' : fmtTime(e.start)}
                    </span>
                    <span className="min-w-0 flex-1 truncate">{e.title}</span>
                  </li>
                ))}
                {googleEvents.length > 8 && (
                  <li className="text-muted px-4 py-2 text-[12px]">그 외 {googleEvents.length - 8}건</li>
                )}
              </ul>
            )}
          </section>
        </div>
      )}

      {/* 왜 이렇게 만들었나 — 필요할 때만 펼친다 */}
      <div className="border-hair mt-5 rounded-xl border">
        <button
          onClick={() => setOpenWhy((v) => !v)}
          className="flex w-full items-center justify-between px-4 py-3 text-left"
        >
          <span className="text-[13px] font-semibold">
            ⚠️ 이 데모는 실제 앱과 연결 방식이 다릅니다 — 왜 그런지 보기
          </span>
          <span className="text-muted text-xs">{openWhy ? '접기' : '펼치기'}</span>
        </button>

        {openWhy && (
          <div className="border-hair space-y-3 border-t px-4 py-4">
            <p className="text-[13.5px] leading-7">
              이 교육 프로그램은 서버가 없는 정적 사이트입니다. 그래서 STEP 06 이 가르치는 정식 흐름(서버가 클라이언트
              시크릿으로 토큰을 교환하고 <code className="surface-2 rounded px-1">refresh_token</code> 을 암호화해
              보관)을 쓸 수 없고, 구글이 자바스크립트 앱에 주는 토큰 흐름을 씁니다.
            </p>
            <div className="border-hair overflow-x-auto rounded-lg border">
              <table className="w-full text-[12.5px]">
                <thead className="surface-2">
                  <tr>
                    {['항목', '서버 흐름 (실제 앱)', '브라우저 흐름 (이 데모)'].map((h) => (
                      <th key={h} className="border-hair border-b px-3 py-1.5 text-left font-semibold">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {[
                    ['클라이언트 시크릿', '서버에만 보관', '쓰지 않음'],
                    ['refresh_token', '받아서 암호화 저장', '받을 수 없음'],
                    ['토큰 보관', 'DB에 암호화', '메모리만 — 새로고침하면 재연결'],
                    ['자동 주기 동기화', '가능', '불가능 — 화면에서 눌러야 함'],
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
            <p className="rounded-lg border border-amber-500/40 bg-amber-500/5 px-3 py-2 text-[13px] leading-7">
              <b>주의:</b> "브라우저에서 되니까 서버 없이 만들면 되겠다"는 결론은 틀립니다. 이 방식은 사용자가 화면을
              열어두지 않으면 아무 일도 일어나지 않습니다. 아침에 캘린더가 자동으로 맞춰져 있어야 하는 우리
              요구사항은 서버가 있어야 성립합니다.
            </p>
            <p className="text-muted text-[12.5px] leading-6">
              이 데모는 기본 캘린더만 읽고, 액세스 토큰을 브라우저에 저장하지 않습니다. 읽기는{' '}
              <code className="surface-2 rounded px-1">calendar.events.readonly</code> 만 요청합니다(최소 권한).
              내보내기 실습은 "[교육 데모]" 이름의 일정을 만들고, 정리 버튼은 그 일정만 지웁니다.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

function Card({
  n, title, done, dim, children,
}: {
  n: string
  title: string
  done?: boolean
  dim?: boolean
  children: React.ReactNode
}) {
  return (
    <section className={'border-hair surface mb-4 rounded-xl border p-4 transition ' + (dim ? 'opacity-55' : '')}>
      <h3 className="mb-3 flex items-center gap-2.5">
        <span
          className={
            'flex h-6 w-6 items-center justify-center rounded-full text-[12px] font-bold ' +
            (done ? 'bg-emerald-500 text-white' : 'surface-2 text-muted')
          }
        >
          {done ? '✓' : n}
        </span>
        <span className="text-[14px] font-semibold">{title}</span>
      </h3>
      {children}
    </section>
  )
}

function Try({
  title, proves, hint, disabled, busy, primary, onClick,
}: {
  title: string
  proves: string
  hint?: string
  disabled?: boolean
  busy?: boolean
  primary?: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || busy}
      className={
        'rounded-lg border p-3 text-left transition disabled:opacity-40 ' +
        (primary
          ? 'border-brand-500 bg-brand-500/5 hover:bg-brand-500/10'
          : 'border-hair hover:border-brand-500/60')
      }
    >
      <span className="block text-[13.5px] font-semibold">{busy ? '실행 중…' : title}</span>
      <span className="text-muted mt-0.5 block text-[12px] leading-5">{proves}</span>
      {hint && <span className="text-muted mt-1 block font-mono text-[10.5px] break-all">{hint}</span>}
    </button>
  )
}
