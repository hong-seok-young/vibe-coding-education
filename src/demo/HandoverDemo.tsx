import { useMemo, useState } from 'react'
import { addDays, fmtDate, pad } from '../lib/dates'
import { USERS } from './data'
import type { HandoverItem } from './data'
import { useDemo } from './store'

type Role = 'from' | 'to'

const STATUS_LABEL: Record<HandoverItem['status'], string> = {
  TODO: '대기',
  IN_PROGRESS: '진행중',
  BLOCKED: '막힘',
  DONE: '완료',
}

const STATUS_STYLE: Record<HandoverItem['status'], string> = {
  TODO: 'surface-2 text-muted',
  IN_PROGRESS: 'bg-brand-500/15 text-brand-500',
  BLOCKED: 'bg-red-500/15 text-red-500',
  DONE: 'bg-emerald-500/15 text-emerald-500',
}

const FLOW: { key: string; label: string }[] = [
  { key: 'REQUESTED', label: '요청' },
  { key: 'ACCEPTED', label: '인수자 확인' },
  { key: 'DONE', label: '복귀 확인' },
]

export function HandoverDemo() {
  const { handover, acceptHandover, setItemStatus, addHandoverItem, finishHandover, resetHandover } = useDemo()
  const [role, setRole] = useState<Role>('to')
  const [newTitle, setNewTitle] = useState('')
  const [blockingId, setBlockingId] = useState<string | null>(null)
  const [blockReason, setBlockReason] = useState('')

  const fromUser = USERS.find((u) => u.id === handover.fromUserId)!
  const toUser = USERS.find((u) => u.id === handover.toUserId)!
  const currentStage = FLOW.findIndex((f) => f.key === handover.status)

  const blocked = handover.items.filter((i) => i.status === 'BLOCKED')
  const openItems = handover.items.filter((i) => i.status !== 'DONE')

  const canAccept = role === 'to' && handover.status === 'REQUESTED'
  const canFinish = role === 'from' && handover.status === 'ACCEPTED'

  const stale = useMemo(
    () => handover.status === 'REQUESTED' && handover.absentFrom.getTime() <= Date.now(),
    [handover],
  )

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-6">
      {/* 시점 전환 — 인계자/인수자 두 사람의 화면을 비교해볼 수 있게 */}
      <div className="border-hair surface mb-5 flex flex-wrap items-center gap-3 rounded-xl border px-4 py-3">
        <span className="text-[12px] font-semibold">지금 보는 사람</span>
        <div className="surface-2 border-hair flex rounded-lg border p-0.5">
          {(['from', 'to'] as Role[]).map((r) => (
            <button
              key={r}
              onClick={() => setRole(r)}
              className={
                'rounded-md px-3 py-1 text-xs font-medium transition ' +
                (role === r ? 'bg-brand-500 text-white' : 'text-muted hover:text-brand-500')
              }
            >
              {r === 'from' ? `인계자 ${fromUser.name}` : `인수자 ${toUser.name}`}
            </button>
          ))}
        </div>
        <span className="text-muted text-[11.5px]">
          같은 인수인계를 각자 다른 권한으로 본다. 확인은 인수자만, 복귀 확인은 인계자만 할 수 있다.
        </span>
        <button
          onClick={resetHandover}
          className="border-hair text-muted hover:text-brand-500 ml-auto rounded-md border px-2.5 py-1.5 text-xs"
        >
          데모 초기화
        </button>
      </div>

      {/* 헤더 */}
      <div className="border-hair surface mb-5 rounded-xl border p-5">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-[16px] font-semibold tracking-tight">
              {fromUser.name} → {toUser.name} 인수인계
            </h2>
            <p className="text-muted mt-1 text-[13px]">
              부재 기간 · {fmtDate(handover.absentFrom)} ~ {fmtDate(handover.absentTo)} ({handover.reason})
            </p>
          </div>
          <span
            className={
              'rounded-full px-3 py-1 text-[11.5px] font-semibold ' +
              (handover.status === 'DONE'
                ? 'bg-emerald-500/15 text-emerald-500'
                : handover.status === 'ACCEPTED'
                  ? 'bg-brand-500/15 text-brand-500'
                  : 'bg-amber-500/15 text-amber-500')
            }
          >
            {FLOW.find((f) => f.key === handover.status)?.label}
          </span>
        </div>

        {/* 상태 흐름 */}
        <div className="flex flex-wrap items-center gap-2">
          {FLOW.map((f, i) => (
            <div key={f.key} className="flex items-center gap-2">
              <div
                className={
                  'flex items-center gap-2 rounded-lg border px-3 py-1.5 text-[12.5px] ' +
                  (i < currentStage
                    ? 'border-emerald-500/40 text-emerald-500'
                    : i === currentStage
                      ? 'border-brand-500 text-brand-500 font-semibold'
                      : 'border-hair text-muted')
                }
              >
                <span className="font-mono text-[10px]">{i + 1}</span>
                {f.label}
                {i < currentStage && <span>✓</span>}
              </div>
              {i < FLOW.length - 1 && <span className="text-muted text-xs">→</span>}
            </div>
          ))}
        </div>

        {stale && (
          <div className="mt-4 rounded-lg border border-red-500/40 bg-red-500/5 px-3 py-2 text-[13px]">
            ⚠ 부재 기간이 시작됐는데 아직 인수자 확인이 없다. 이 경고는 양쪽 화면 최상단에 표시된다.
          </div>
        )}

        {blocked.length > 0 && (
          <div className="mt-3 rounded-lg border border-red-500/40 bg-red-500/5 px-3 py-2 text-[13px]">
            🚧 막힌 항목 {blocked.length}개 — {blocked.map((b) => b.title).join(', ')}
            <div className="text-muted mt-0.5 text-[12px]">
              "막힘" 상태가 없으면 진행이 멈춘 사람은 아무 표시도 못 하고 침묵한다.
            </div>
          </div>
        )}

        <div className="mt-4 flex flex-wrap gap-2">
          {canAccept && (
            <button
              onClick={acceptHandover}
              className="bg-brand-500 hover:bg-brand-600 rounded-md px-4 py-2 text-[13px] font-semibold text-white"
            >
              전체 확인 (인수자만 가능)
            </button>
          )}
          {role === 'from' && handover.status === 'REQUESTED' && (
            <div className="text-muted rounded-md border border-dashed border-current px-3 py-2 text-[12.5px]">
              인계자는 확인 버튼을 누를 수 없다. "확인했다"는 기록은 대신할 수 없다.
            </div>
          )}
          {canFinish && (
            <button
              onClick={finishHandover}
              className="rounded-md bg-emerald-600 px-4 py-2 text-[13px] font-semibold text-white hover:bg-emerald-700"
            >
              복귀 확인 · 인수인계 완료
            </button>
          )}
          {handover.status === 'DONE' && (
            <div className="text-muted text-[12.5px]">
              완료된 인수인계는 읽기 전용이다. 종료된 기간의 기록을 바꾸면 기록의 의미가 없어진다.
            </div>
          )}
        </div>
      </div>

      {/* 항목 */}
      <div className="space-y-3">
        {handover.items.map((item) => (
          <div key={item.id} className="border-hair surface rounded-xl border p-4">
            <div className="mb-2 flex flex-wrap items-start justify-between gap-2">
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="text-[14px] font-semibold">{item.title}</h3>
                  <span className={'rounded px-1.5 py-0.5 text-[10.5px] font-semibold ' + STATUS_STYLE[item.status]}>
                    {STATUS_LABEL[item.status]}
                  </span>
                  {item.acked && (
                    <span className="text-muted text-[10.5px]">인수자 확인됨</span>
                  )}
                </div>
                {item.fromEvent && (
                  <p className="text-muted mt-1 text-[11.5px]">
                    캘린더 일정에서 생성 · {item.fromEvent}
                  </p>
                )}
              </div>
            </div>

            <p className="text-[13px] leading-6 whitespace-pre-line">{item.detail}</p>

            {item.blockReason && (
              <p className="mt-2 rounded border border-red-500/30 bg-red-500/5 px-2.5 py-1.5 text-[12.5px]">
                막힘 사유 · {item.blockReason}
              </p>
            )}

            {role === 'to' && handover.status === 'ACCEPTED' && (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {(['TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE'] as HandoverItem['status'][]).map((s) => (
                  <button
                    key={s}
                    onClick={() => {
                      if (s === 'BLOCKED') {
                        setBlockingId(item.id)
                        setBlockReason('')
                      } else {
                        setItemStatus(item.id, s)
                      }
                    }}
                    className={
                      'rounded-md border px-2.5 py-1 text-[12px] transition ' +
                      (item.status === s ? 'border-brand-500 text-brand-500' : 'border-hair text-muted')
                    }
                  >
                    {STATUS_LABEL[s]}
                  </button>
                ))}
              </div>
            )}

            {blockingId === item.id && (
              <div className="mt-2 flex gap-2">
                <input
                  autoFocus
                  value={blockReason}
                  onChange={(e) => setBlockReason(e.target.value)}
                  placeholder="무엇 때문에 막혔는지 (필수)"
                  className="border-hair surface-2 min-w-0 flex-1 rounded-md border px-2.5 py-1.5 text-[13px] outline-none focus:border-red-500"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && blockReason.trim()) {
                      setItemStatus(item.id, 'BLOCKED', blockReason.trim())
                      setBlockingId(null)
                    } else if (e.key === 'Escape') {
                      setBlockingId(null)
                    }
                  }}
                />
                <button
                  onClick={() => {
                    if (blockReason.trim()) {
                      setItemStatus(item.id, 'BLOCKED', blockReason.trim())
                      setBlockingId(null)
                    }
                  }}
                  className="rounded-md bg-red-600 px-3 py-1.5 text-[12px] font-semibold text-white"
                >
                  막힘으로 표시
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 항목 추가 — 인계자만, 완료 전까지만 */}
      {role === 'from' && handover.status !== 'DONE' && (
        <div className="border-hair surface mt-4 rounded-xl border p-4">
          <div className="text-muted mb-2 text-[11.5px] font-semibold">항목 추가 (인계자만)</div>
          <div className="flex gap-2">
            <input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="예: 월말 정산 마감 체크"
              className="border-hair surface-2 min-w-0 flex-1 rounded-md border px-2.5 py-1.5 text-[13px] outline-none focus:border-brand-500"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && newTitle.trim()) {
                  addHandoverItem(newTitle.trim(), '진행 상황: / 다음 할 일: / 막히면 연락: ')
                  setNewTitle('')
                }
              }}
            />
            <button
              onClick={() => {
                if (newTitle.trim()) {
                  addHandoverItem(newTitle.trim(), '진행 상황: / 다음 할 일: / 막히면 연락: ')
                  setNewTitle('')
                }
              }}
              className="border-hair rounded-md border px-3 py-1.5 text-[12px] hover:border-brand-500/60"
            >
              추가
            </button>
          </div>
        </div>
      )}

      {/* 복귀 요약 */}
      {handover.status !== 'REQUESTED' && (
        <div className="border-hair surface mt-5 rounded-xl border p-4">
          <h3 className="mb-2 text-[13px] font-semibold">복귀 요약 (인계자가 보는 화면)</h3>
          <ul className="space-y-1">
            {openItems.length === 0 && (
              <li className="text-[13px] text-emerald-500">모든 항목이 완료되었다.</li>
            )}
            {openItems.map((i) => (
              <li key={i.id} className="flex items-center gap-2 text-[13px]">
                <span className={'rounded px-1.5 py-0.5 text-[10.5px] font-semibold ' + STATUS_STYLE[i.status]}>
                  {STATUS_LABEL[i.status]}
                </span>
                {i.title}
                {i.blockReason && <span className="text-muted">· {i.blockReason}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 감사 로그 */}
      <div className="border-hair surface mt-5 rounded-xl border p-4">
        <h3 className="mb-1 text-[13px] font-semibold">감사 로그</h3>
        <p className="text-muted mb-3 text-[11.5px]">
          상태는 덮어써지지만 이력은 남아야 한다. "저는 못 받았습니다"라는 분쟁의 답이 여기 있다.
        </p>
        <ul className="space-y-1 font-mono text-[11.5px]">
          {handover.log.map((l, i) => (
            <li key={i} className="text-muted flex gap-3">
              <span className="shrink-0">
                {pad(l.at.getMonth() + 1)}-{pad(l.at.getDate())} {pad(l.at.getHours())}:{pad(l.at.getMinutes())}
              </span>
              <span className="text-brand-500 shrink-0">{l.action}</span>
              <span className="shrink-0">{l.actor}</span>
              {l.detail && <span className="truncate">{l.detail}</span>}
            </li>
          ))}
        </ul>
      </div>

      <p className="text-muted mt-6 text-[12px] leading-6">
        인계 항목은 <strong>부재 기간에 걸치는 캘린더 일정에서 자동으로 수집</strong>된 것이다 (다음 주 일정 기준).
        휴가 전날 밤에 "뭘 넘겨야 하지"를 기억해내지 않아도 된다는 것이 이 기능의 핵심이다.
        기간 계산 기준은 {fmtDate(handover.absentFrom)} ~ {fmtDate(addDays(handover.absentTo, 0))} 이다.
      </p>
    </div>
  )
}
