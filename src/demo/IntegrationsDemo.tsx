import { useState } from 'react'
import { pad } from '../lib/dates'

interface Capability {
  kind: string
  label: string
  authKind: 'oauth' | 'caldav' | 'url'
  canRead: boolean
  canWrite: boolean
  incrementalSync: boolean
  notes: string
}

const CAPABILITIES: Capability[] = [
  {
    kind: 'google',
    label: '구글 캘린더',
    authKind: 'oauth',
    canRead: true,
    canWrite: true,
    incrementalSync: true,
    notes: '양방향 연동. syncToken으로 변경분만 가져온다.',
  },
  {
    kind: 'naver',
    label: '네이버 캘린더',
    authKind: 'caldav',
    canRead: true,
    canWrite: false,
    incrementalSync: false,
    notes: '읽기 전용으로 연동된다. 쓰기 지원 범위는 공식 문서 확인 필요.',
  },
  {
    kind: 'outlook',
    label: 'Outlook / M365',
    authKind: 'oauth',
    canRead: true,
    canWrite: true,
    incrementalSync: true,
    notes: '미구현 — 등록소에 한 줄 추가하면 붙는다.',
  },
  {
    kind: 'ics',
    label: 'ICS URL 구독',
    authKind: 'url',
    canRead: true,
    canWrite: false,
    incrementalSync: false,
    notes: '읽기 전용 · 변경 반영이 최대 1시간 늦을 수 있다. 거의 모든 캘린더에 대한 폴백.',
  },
]

interface Account {
  id: string
  kind: string
  email: string
  color: string
  syncEnabled: boolean
  writeEnabled: boolean
  lastSyncedAt: Date | null
  stats?: { created: number; updated: number; deleted: number; skipped: number; failed: number }
  needsReconnect?: boolean
}

export function IntegrationsDemo() {
  const [accounts, setAccounts] = useState<Account[]>([
    {
      id: 'a1',
      kind: 'google',
      email: 'hong.gildong@company.com',
      color: '#4a6ff0',
      syncEnabled: true,
      writeEnabled: true,
      lastSyncedAt: new Date(Date.now() - 7 * 60_000),
      stats: { created: 12, updated: 3, deleted: 1, skipped: 41, failed: 0 },
    },
    {
      id: 'a2',
      kind: 'ics',
      email: 'https://intranet.company.com/calendar/edu.ics',
      color: '#8b5cf6',
      syncEnabled: true,
      writeEnabled: false,
      lastSyncedAt: new Date(Date.now() - 52 * 60_000),
      stats: { created: 4, updated: 0, deleted: 0, skipped: 8, failed: 0 },
    },
    {
      id: 'a3',
      kind: 'naver',
      email: 'gildong@naver.com',
      color: '#2fa37a',
      syncEnabled: false,
      writeEnabled: false,
      lastSyncedAt: null,
      needsReconnect: true,
    },
  ])
  const [syncing, setSyncing] = useState<string | null>(null)
  const [picker, setPicker] = useState(false)

  const capOf = (kind: string) => CAPABILITIES.find((c) => c.kind === kind)!

  const sync = (id: string) => {
    setSyncing(id)
    // 실제 앱에서는 서버 동기화 호출. 데모에서는 결과 숫자만 갱신한다.
    setTimeout(() => {
      setAccounts((prev) =>
        prev.map((a) =>
          a.id === id
            ? {
                ...a,
                lastSyncedAt: new Date(),
                stats: {
                  created: Math.floor(Math.random() * 3),
                  updated: Math.floor(Math.random() * 4),
                  deleted: 0,
                  skipped: 40 + Math.floor(Math.random() * 10),
                  failed: 0,
                },
              }
            : a,
        ),
      )
      setSyncing(null)
    }, 900)
  }

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-6">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-[16px] font-semibold tracking-tight">연결된 캘린더</h2>
          <p className="text-muted mt-1 text-[12.5px]">
            화면은 프로바이더의 <strong>능력(capability)</strong> 정보만 보고 그려진다. 코드에
            <code className="surface-2 border-hair mx-1 rounded border px-1 py-0.5 font-mono text-[11px]">
              if (provider === 'google')
            </code>
            같은 분기가 흩어지지 않는 이유다.
          </p>
        </div>
        <button
          onClick={() => setPicker((p) => !p)}
          className="bg-brand-500 hover:bg-brand-600 rounded-md px-3 py-2 text-xs font-semibold text-white"
        >
          + 캘린더 추가
        </button>
      </div>

      {picker && (
        <div className="border-brand-500/40 bg-brand-500/5 mb-5 rounded-xl border p-4">
          <div className="mb-3 text-[12px] font-semibold">추가할 캘린더 종류</div>
          <div className="grid gap-2 sm:grid-cols-2">
            {CAPABILITIES.map((c) => {
              const disabled = c.kind === 'outlook'
              return (
                <button
                  key={c.kind}
                  disabled={disabled}
                  onClick={() => {
                    setAccounts((prev) => [
                      ...prev,
                      {
                        id: 'a' + (prev.length + 1),
                        kind: c.kind,
                        email: c.authKind === 'url' ? 'https://example.com/calendar.ics' : 'new.user@company.com',
                        color: '#e0793a',
                        syncEnabled: true,
                        writeEnabled: c.canWrite,
                        lastSyncedAt: null,
                      },
                    ])
                    setPicker(false)
                  }}
                  className={
                    'border-hair surface rounded-lg border p-3 text-left transition ' +
                    (disabled ? 'cursor-not-allowed opacity-45' : 'hover:border-brand-500/60')
                  }
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[13px] font-semibold">{c.label}</span>
                    <span className="text-muted font-mono text-[10px] uppercase">{c.authKind}</span>
                  </div>
                  <div className="mt-1.5 flex flex-wrap gap-1.5">
                    <Badge on={c.canRead}>읽기</Badge>
                    <Badge on={c.canWrite}>쓰기</Badge>
                    <Badge on={c.incrementalSync}>증분</Badge>
                  </div>
                  <p className="text-muted mt-1.5 text-[11.5px] leading-5">{c.notes}</p>
                </button>
              )
            })}
          </div>
        </div>
      )}

      <div className="space-y-3">
        {accounts.map((a) => {
          const cap = capOf(a.kind)
          return (
            <div key={a.id} className="border-hair surface rounded-xl border p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="h-3 w-3 shrink-0 rounded-full" style={{ background: a.color }} />
                    <span className="text-[14px] font-semibold">{cap.label}</span>
                    {a.needsReconnect && (
                      <span className="rounded bg-red-500/15 px-1.5 py-0.5 text-[10.5px] font-semibold text-red-500">
                        재연결 필요
                      </span>
                    )}
                    {!cap.canWrite && (
                      <span className="surface-2 text-muted rounded px-1.5 py-0.5 text-[10.5px]">읽기 전용</span>
                    )}
                  </div>
                  <p className="text-muted mt-1 truncate text-[12px]">{a.email}</p>
                </div>

                <div className="flex shrink-0 items-center gap-2">
                  <button
                    onClick={() => sync(a.id)}
                    disabled={syncing === a.id || a.needsReconnect}
                    className="border-hair rounded-md border px-2.5 py-1.5 text-xs hover:border-brand-500/60 disabled:opacity-45"
                  >
                    {syncing === a.id ? '동기화 중…' : '동기화'}
                  </button>
                  <button
                    onClick={() => setAccounts((prev) => prev.filter((x) => x.id !== a.id))}
                    className="text-muted hover:text-red-500 rounded-md px-2 py-1.5 text-xs"
                  >
                    연결 해제
                  </button>
                </div>
              </div>

              <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2">
                <Toggle
                  label="동기화"
                  on={a.syncEnabled}
                  onChange={(v) =>
                    setAccounts((prev) => prev.map((x) => (x.id === a.id ? { ...x, syncEnabled: v } : x)))
                  }
                />
                <Toggle
                  label="내보내기 허용"
                  on={a.writeEnabled}
                  disabled={!cap.canWrite}
                  disabledReason={cap.notes}
                  onChange={(v) =>
                    setAccounts((prev) => prev.map((x) => (x.id === a.id ? { ...x, writeEnabled: v } : x)))
                  }
                />
                <span className="text-muted text-[11.5px]">
                  마지막 동기화 ·{' '}
                  {a.lastSyncedAt
                    ? `${pad(a.lastSyncedAt.getHours())}:${pad(a.lastSyncedAt.getMinutes())}`
                    : '없음'}
                </span>
              </div>

              {a.stats && (
                <div className="surface-2 border-hair mt-3 flex flex-wrap gap-x-4 gap-y-1 rounded-lg border px-3 py-2 text-[11.5px]">
                  <span>가져옴 <strong>{a.stats.created}</strong></span>
                  <span>갱신 <strong>{a.stats.updated}</strong></span>
                  <span>삭제 <strong>{a.stats.deleted}</strong></span>
                  <span className="text-muted">건너뜀 {a.stats.skipped}</span>
                  <span className={a.stats.failed > 0 ? 'text-red-500' : 'text-muted'}>
                    실패 {a.stats.failed}
                  </span>
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="border-hair mt-6 space-y-3 rounded-xl border border-dashed p-4">
        <h3 className="text-[13px] font-semibold">이 화면이 보여주는 것</h3>
        <ul className="text-muted space-y-1.5 text-[12.5px] leading-6">
          <li>
            · <strong>동기화 결과 숫자</strong>를 화면에 표시한다. 조용히 실패하는 동기화는 몇 주 뒤 "주간보고에
            일정이 안 잡혀요"라는 문의로 돌아온다.
          </li>
          <li>
            · 읽기 전용 프로바이더는 <strong>내보내기 토글이 잠기고 이유가 표시</strong>된다. 화면에서 숨기는 것보다
            "왜 안 되는지" 알려주는 것이 낫다.
          </li>
          <li>
            · 토큰이 무효화된 계정은 <strong>재연결 필요</strong> 상태로 바뀐다. 사용자가 구글에서 권한을 철회하면
            실제로 이렇게 된다.
          </li>
          <li>
            · "캘린더 추가" 목록은 <strong>등록소(registry)에서 자동 생성</strong>된다. Outlook은 등록만 되고 구현이
            없어 비활성 상태로 보인다.
          </li>
        </ul>
      </div>
    </div>
  )
}

function Badge({ on, children }: { on: boolean; children: React.ReactNode }) {
  return (
    <span
      className={
        'rounded px-1.5 py-0.5 text-[10.5px] font-medium ' +
        (on ? 'bg-emerald-500/15 text-emerald-500' : 'surface-2 text-muted line-through')
      }
    >
      {children}
    </span>
  )
}

function Toggle({
  label, on, onChange, disabled, disabledReason,
}: {
  label: string
  on: boolean
  onChange: (v: boolean) => void
  disabled?: boolean
  disabledReason?: string
}) {
  return (
    <button
      onClick={() => !disabled && onChange(!on)}
      disabled={disabled}
      title={disabled ? disabledReason : undefined}
      className={'flex items-center gap-2 text-[12px] ' + (disabled ? 'cursor-not-allowed opacity-50' : '')}
    >
      <span
        className={
          'relative h-4 w-7 rounded-full transition ' + (on && !disabled ? 'bg-brand-500' : 'surface-2 border-hair border')
        }
      >
        <span
          className={
            'absolute top-0.5 h-3 w-3 rounded-full bg-white transition ' + (on && !disabled ? 'left-3.5' : 'left-0.5')
          }
        />
      </span>
      {label}
    </button>
  )
}
