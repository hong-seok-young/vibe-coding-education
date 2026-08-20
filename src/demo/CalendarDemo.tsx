import { useEffect, useMemo, useRef, useState } from 'react'
import {
  WEEKDAY_KO, addDays, addMonths, fmtMonthTitle, fmtTime, isSameDay, isSameMonth,
  minutesBetween, monthGrid, startOfDay, weekDays, fmtDuration,
} from '../lib/dates'
import { layoutOverlaps } from '../lib/overlap'
import { parseQuickInput } from '../lib/parseQuickInput'
import { CATEGORIES, categoryOf } from './data'
import type { DemoEvent } from './data'
import { useDemo } from './store'

type View = 'month' | 'week'

export function CalendarDemo() {
  const { events, addEvent, updateEvent, deleteEvent, undoDelete, pendingUndo, reset } = useDemo()
  const [anchor, setAnchor] = useState(() => new Date())
  const [view, setView] = useState<View>('month')
  const [selected, setSelected] = useState<string | null>(null)
  const [composeDay, setComposeDay] = useState<Date | null>(null)

  const selectedEvent = events.find((e) => e.id === selected) ?? null

  // 키보드 단축키 — 입력창에 타이핑 중일 때는 가로채지 않는다
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement | null)?.tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return
      const stepDays = view === 'month' ? 0 : 7
      if (e.key === 'ArrowLeft') setAnchor((d) => (view === 'month' ? addMonths(d, -1) : addDays(d, -stepDays)))
      else if (e.key === 'ArrowRight') setAnchor((d) => (view === 'month' ? addMonths(d, 1) : addDays(d, stepDays)))
      else if (e.key === 't' || e.key === 'T') setAnchor(new Date())
      else if (e.key === 'm' || e.key === 'M') setView('month')
      else if (e.key === 'w' || e.key === 'W') setView('week')
      else if (e.key === 'Escape') {
        setSelected(null)
        setComposeDay(null)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [view])

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <Toolbar
        anchor={anchor}
        view={view}
        onView={setView}
        onPrev={() => setAnchor((d) => (view === 'month' ? addMonths(d, -1) : addDays(d, -7)))}
        onNext={() => setAnchor((d) => (view === 'month' ? addMonths(d, 1) : addDays(d, 7)))}
        onToday={() => setAnchor(new Date())}
        onReset={reset}
      />

      <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
        <div className="min-w-0 flex-1 overflow-auto">
          {view === 'month' ? (
            <MonthView
              anchor={anchor}
              events={events}
              composeDay={composeDay}
              onCompose={setComposeDay}
              onSelect={setSelected}
              onQuickAdd={(day, text) => {
                const q = parseQuickInput(text)
                const start = startOfDay(day)
                start.setMinutes(q.startMinutes)
                const end = startOfDay(day)
                end.setMinutes(q.endMinutes)
                addEvent({
                  title: q.title,
                  start,
                  end,
                  allDay: false,
                  categoryId: guessCategory(q.title),
                  visibility: 'TEAM',
                  source: 'LOCAL',
                })
              }}
              onMove={(id, day) => {
                const ev = events.find((e) => e.id === id)
                if (!ev) return
                const dayDiff = Math.round(
                  (startOfDay(day).getTime() - startOfDay(ev.start).getTime()) / 86_400_000,
                )
                if (dayDiff === 0) return
                updateEvent(id, { start: addDays(ev.start, dayDiff), end: addDays(ev.end, dayDiff) })
              }}
            />
          ) : (
            <WeekView anchor={anchor} events={events} onSelect={setSelected} />
          )}
        </div>

        {selectedEvent && (
          <DetailPanel
            event={selectedEvent}
            onClose={() => setSelected(null)}
            onChange={(patch) => updateEvent(selectedEvent.id, patch)}
            onDelete={() => {
              deleteEvent(selectedEvent.id)
              setSelected(null)
            }}
          />
        )}
      </div>

      {pendingUndo && (
        <div className="border-hair surface fixed bottom-6 left-1/2 z-40 flex -translate-x-1/2 items-center gap-3 rounded-xl border px-4 py-3 shadow-lg">
          <span className="text-[13px]">
            <strong>{pendingUndo.title}</strong> 삭제됨
          </span>
          <button
            onClick={undoDelete}
            className="text-brand-500 rounded-md px-2 py-1 text-[13px] font-semibold hover:underline"
          >
            되돌리기
          </button>
        </div>
      )}
    </div>
  )
}

function guessCategory(title: string) {
  if (/회의|미팅|스크럼|리뷰|논의|면담/.test(title)) return 'meet'
  if (/지원|문의|대응|점검/.test(title)) return 'support'
  if (/교육|워크숍|세미나|학습/.test(title)) return 'edu'
  if (/개발|구현|배포|디버깅|리팩터|설계/.test(title)) return 'dev'
  return 'etc'
}

function Toolbar({
  anchor, view, onView, onPrev, onNext, onToday, onReset,
}: {
  anchor: Date
  view: View
  onView: (v: View) => void
  onPrev: () => void
  onNext: () => void
  onToday: () => void
  onReset: () => void
}) {
  const week = weekDays(anchor)
  return (
    <div className="border-hair surface flex flex-wrap items-center gap-3 border-b px-4 py-3">
      <div className="flex items-center gap-1">
        <IconBtn onClick={onPrev} label="이전">←</IconBtn>
        <button
          onClick={onToday}
          className="border-hair rounded-md border px-2.5 py-1.5 text-xs font-medium hover:border-brand-500/60"
        >
          오늘
        </button>
        <IconBtn onClick={onNext} label="다음">→</IconBtn>
      </div>

      <h2 className="text-[15px] font-semibold tracking-tight">
        {view === 'month'
          ? fmtMonthTitle(anchor)
          : `${fmtMonthTitle(week[0])} ${week[0].getDate()}일 – ${week[6].getDate()}일`}
      </h2>

      <div className="surface-2 border-hair ml-auto flex rounded-lg border p-0.5">
        {(['month', 'week'] as View[]).map((v) => (
          <button
            key={v}
            onClick={() => onView(v)}
            className={
              'rounded-md px-3 py-1 text-xs font-medium transition ' +
              (view === v ? 'bg-brand-500 text-white' : 'text-muted hover:text-brand-500')
            }
          >
            {v === 'month' ? '월' : '주'}
          </button>
        ))}
      </div>

      <div className="text-muted hidden items-center gap-3 text-[11px] xl:flex">
        {CATEGORIES.map((c) => (
          <span key={c.id} className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full" style={{ background: c.color }} />
            {c.name}
          </span>
        ))}
      </div>

      <button
        onClick={onReset}
        className="border-hair text-muted rounded-md border px-2.5 py-1.5 text-xs hover:text-brand-500"
      >
        데모 초기화
      </button>
    </div>
  )
}

function IconBtn({ children, onClick, label }: { children: React.ReactNode; onClick: () => void; label: string }) {
  return (
    <button
      onClick={onClick}
      aria-label={label}
      className="border-hair text-muted hover:border-brand-500/60 hover:text-brand-500 rounded-md border px-2.5 py-1.5 text-xs transition"
    >
      {children}
    </button>
  )
}

function MonthView({
  anchor, events, composeDay, onCompose, onSelect, onQuickAdd, onMove,
}: {
  anchor: Date
  events: DemoEvent[]
  composeDay: Date | null
  onCompose: (d: Date | null) => void
  onSelect: (id: string) => void
  onQuickAdd: (day: Date, text: string) => void
  onMove: (id: string, day: Date) => void
}) {
  const days = useMemo(() => monthGrid(anchor), [anchor])
  const [dragOver, setDragOver] = useState<string | null>(null)
  const [expanded, setExpanded] = useState<string | null>(null)

  // 날짜별로 미리 묶는다. 42칸마다 전체 배열을 훑으면 일정이 많아질 때 느려진다.
  const byDay = useMemo(() => {
    const map = new Map<string, DemoEvent[]>()
    for (const e of events) {
      const key = dayKey(e.start)
      const list = map.get(key) ?? []
      list.push(e)
      map.set(key, list)
    }
    for (const list of map.values()) list.sort((a, b) => a.start.getTime() - b.start.getTime())
    return map
  }, [events])

  return (
    <div className="min-w-[720px]">
      <div className="border-hair grid grid-cols-7 border-b">
        {WEEKDAY_KO.map((w, i) => (
          <div
            key={w}
            className={
              'text-muted px-2 py-2 text-[11px] font-medium ' + (i >= 5 ? 'text-brand-400/80' : '')
            }
          >
            {w}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7">
        {days.map((d) => {
          const key = dayKey(d)
          const all = byDay.get(key) ?? []
          const isExpanded = expanded === key
          const shown = isExpanded ? all : all.slice(0, 3)
          const more = all.length - shown.length
          const today = isSameDay(d, new Date())
          const composing = composeDay ? isSameDay(composeDay, d) : false

          return (
            <div
              key={key}
              onDragOver={(e) => {
                e.preventDefault()
                setDragOver(key)
              }}
              onDragLeave={() => setDragOver((k) => (k === key ? null : k))}
              onDrop={(e) => {
                e.preventDefault()
                setDragOver(null)
                const id = e.dataTransfer.getData('text/plain')
                if (id) onMove(id, d)
              }}
              className={
                'border-hair min-h-[112px] border-r border-b p-1.5 transition-colors ' +
                (isSameMonth(d, anchor) ? '' : 'opacity-45 ') +
                (dragOver === key ? 'bg-brand-500/10' : '')
              }
            >
              <div className="mb-1 flex items-center justify-between">
                <button
                  onClick={() => onCompose(composing ? null : d)}
                  className={
                    'flex h-6 min-w-6 items-center justify-center rounded-full px-1.5 text-[11px] font-medium transition ' +
                    (today ? 'bg-brand-500 text-white' : 'text-muted hover:surface-2')
                  }
                  title="클릭해서 일정 추가"
                >
                  {d.getDate()}
                </button>
                {!composing && (
                  <button
                    onClick={() => onCompose(d)}
                    className="text-muted hover:text-brand-500 text-[13px] leading-none opacity-0 transition hover:opacity-100 focus:opacity-100 [.group:hover_&]:opacity-100"
                    aria-label="일정 추가"
                  >
                    +
                  </button>
                )}
              </div>

              <ul className="space-y-0.5">
                {shown.map((e) => (
                  <li key={e.id}>
                    <button
                      draggable
                      onDragStart={(ev) => ev.dataTransfer.setData('text/plain', e.id)}
                      onClick={() => onSelect(e.id)}
                      className="hover:surface-2 flex w-full items-center gap-1 rounded px-1 py-0.5 text-left text-[11px] transition"
                      title={`${fmtTime(e.start)} ${e.title}`}
                    >
                      {e.allDay ? (
                        <span
                          className="min-w-0 flex-1 truncate rounded px-1 text-white"
                          style={{ background: categoryOf(e.categoryId).color }}
                        >
                          {e.title}
                        </span>
                      ) : (
                        <>
                          <span
                            className="h-1.5 w-1.5 shrink-0 rounded-full"
                            style={{ background: categoryOf(e.categoryId).color }}
                          />
                          <span className="text-muted shrink-0 tabular-nums">{fmtTime(e.start)}</span>
                          <span className="truncate">
                            {e.visibility === 'PRIVATE' ? '비공개 일정' : e.title}
                          </span>
                          {e.source !== 'LOCAL' && (
                            <span className="text-muted ml-auto shrink-0 text-[9px]">
                              {e.source === 'GOOGLE' ? 'G' : 'ICS'}
                            </span>
                          )}
                        </>
                      )}
                    </button>
                  </li>
                ))}

                {more > 0 && (
                  <li>
                    <button
                      onClick={() => setExpanded(key)}
                      className="text-muted hover:text-brand-500 px-1 text-[11px]"
                    >
                      +{more}개 더
                    </button>
                  </li>
                )}
                {isExpanded && (
                  <li>
                    <button onClick={() => setExpanded(null)} className="text-muted px-1 text-[11px]">
                      접기
                    </button>
                  </li>
                )}
              </ul>

              {composing && (
                <QuickInput
                  onSubmit={(text) => onQuickAdd(d, text)}
                  onClose={() => onCompose(null)}
                />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

/** 인라인 빠른 입력. Enter로 저장하고 입력창을 유지해 연속 입력이 가능하다. */
function QuickInput({ onSubmit, onClose }: { onSubmit: (text: string) => void; onClose: () => void }) {
  const [text, setText] = useState('')
  const ref = useRef<HTMLInputElement>(null)
  const [hint, setHint] = useState<string | null>(null)

  useEffect(() => {
    ref.current?.focus()
  }, [])

  useEffect(() => {
    if (!text.trim()) {
      setHint(null)
      return
    }
    const q = parseQuickInput(text)
    setHint(
      q.matched
        ? `${pad2(Math.floor(q.startMinutes / 60))}:${pad2(q.startMinutes % 60)}~${pad2(Math.floor(q.endMinutes / 60))}:${pad2(q.endMinutes % 60)} · ${q.title}`
        : '09:00~10:00 (시간 표현 없음)',
    )
  }, [text])

  return (
    <div className="mt-1">
      <input
        ref={ref}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && text.trim()) {
            onSubmit(text.trim())
            setText('')
          } else if (e.key === 'Escape') {
            onClose()
          }
        }}
        onBlur={() => !text && onClose()}
        placeholder="14시 팀 회의"
        className="border-brand-500/60 surface w-full rounded border px-1.5 py-1 text-[11px] outline-none"
      />
      {hint && <div className="text-muted mt-0.5 px-1 text-[10px] leading-tight">{hint}</div>}
    </div>
  )
}

const pad2 = (n: number) => String(n).padStart(2, '0')

function WeekView({
  anchor, events, onSelect,
}: {
  anchor: Date
  events: DemoEvent[]
  onSelect: (id: string) => void
}) {
  const days = useMemo(() => weekDays(anchor), [anchor])
  const scroller = useRef<HTMLDivElement>(null)
  const [now, setNow] = useState(() => new Date())
  const HOUR_H = 44

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 60_000)
    return () => clearInterval(t)
  }, [])

  // 기본 스크롤 위치를 오전 8시로
  useEffect(() => {
    if (scroller.current) scroller.current.scrollTop = 8 * HOUR_H
  }, [])

  const allDayEvents = events.filter(
    (e) => e.allDay && days.some((d) => isSameDay(d, e.start)),
  )

  return (
    <div className="min-w-[820px]">
      <div className="border-hair surface sticky top-0 z-10 border-b">
        <div className="grid" style={{ gridTemplateColumns: '56px repeat(7, minmax(0,1fr))' }}>
          <div />
          {days.map((d) => {
            const today = isSameDay(d, new Date())
            return (
              <div key={d.toISOString()} className="border-hair border-l px-2 py-2 text-center">
                <div className="text-muted text-[11px]">{WEEKDAY_KO[(d.getDay() + 6) % 7]}</div>
                <div
                  className={
                    'mx-auto mt-0.5 flex h-6 w-6 items-center justify-center rounded-full text-[12px] font-medium ' +
                    (today ? 'bg-brand-500 text-white' : '')
                  }
                >
                  {d.getDate()}
                </div>
              </div>
            )
          })}
        </div>

        {allDayEvents.length > 0 && (
          <div
            className="border-hair grid border-t"
            style={{ gridTemplateColumns: '56px repeat(7, minmax(0,1fr))' }}
          >
            <div className="text-muted px-2 py-1 text-[10px]">종일</div>
            {days.map((d) => (
              <div key={d.toISOString()} className="border-hair border-l p-1">
                {allDayEvents
                  .filter((e) => isSameDay(e.start, d))
                  .map((e) => (
                    <button
                      key={e.id}
                      onClick={() => onSelect(e.id)}
                      className="w-full truncate rounded px-1.5 py-0.5 text-[11px] text-white"
                      style={{ background: categoryOf(e.categoryId).color }}
                    >
                      {e.title}
                    </button>
                  ))}
              </div>
            ))}
          </div>
        )}
      </div>

      <div ref={scroller} className="relative max-h-[calc(100vh-260px)] overflow-y-auto">
        <div className="grid" style={{ gridTemplateColumns: '56px repeat(7, minmax(0,1fr))' }}>
          <div>
            {Array.from({ length: 24 }, (_, h) => (
              <div
                key={h}
                className="text-muted border-hair relative border-b pr-2 text-right text-[10px]"
                style={{ height: HOUR_H }}
              >
                <span className="absolute -top-1.5 right-2">{h > 0 ? `${pad2(h)}:00` : ''}</span>
              </div>
            ))}
          </div>

          {days.map((d) => {
            const dayEvents = events.filter((e) => !e.allDay && isSameDay(e.start, d))
            const positioned = layoutOverlaps(dayEvents)
            const isToday = isSameDay(d, new Date())

            return (
              <div key={d.toISOString()} className="border-hair relative border-l">
                {Array.from({ length: 24 }, (_, h) => (
                  <div key={h} className="border-hair border-b" style={{ height: HOUR_H }} />
                ))}

                {isToday && (
                  <div
                    className="pointer-events-none absolute right-0 left-0 z-10 border-t border-red-500"
                    style={{ top: ((now.getHours() * 60 + now.getMinutes()) / 60) * HOUR_H }}
                  >
                    <span className="absolute -top-1 -left-1 h-2 w-2 rounded-full bg-red-500" />
                  </div>
                )}

                {positioned.map(({ item: e, left, width }) => {
                  const top = ((e.start.getHours() * 60 + e.start.getMinutes()) / 60) * HOUR_H
                  const height = Math.max((minutesBetween(e.start, e.end) / 60) * HOUR_H, 18)
                  const color = categoryOf(e.categoryId).color
                  return (
                    <button
                      key={e.id}
                      onClick={() => onSelect(e.id)}
                      className="absolute overflow-hidden rounded-md px-1.5 py-0.5 text-left text-[10.5px] leading-tight text-white transition hover:brightness-110"
                      style={{
                        top,
                        height,
                        left: `calc(${left * 100}% + 2px)`,
                        width: `calc(${width * 100}% - 4px)`,
                        background: color,
                        opacity: e.visibility === 'PRIVATE' ? 0.55 : 1,
                      }}
                      title={`${fmtTime(e.start)}~${fmtTime(e.end)} ${e.title}`}
                    >
                      <div className="truncate font-medium">
                        {e.visibility === 'PRIVATE' ? '비공개' : e.title}
                      </div>
                      <div className="truncate opacity-85">{fmtTime(e.start)}</div>
                    </button>
                  )
                })}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function DetailPanel({
  event, onClose, onChange, onDelete,
}: {
  event: DemoEvent
  onClose: () => void
  onChange: (patch: Partial<DemoEvent>) => void
  onDelete: () => void
}) {
  const toTimeValue = (d: Date) => `${pad2(d.getHours())}:${pad2(d.getMinutes())}`
  const setTime = (which: 'start' | 'end', value: string) => {
    const [h, m] = value.split(':').map(Number)
    const base = new Date(event[which])
    base.setHours(h, m, 0, 0)
    onChange({ [which]: base } as Partial<DemoEvent>)
  }

  return (
    <aside className="border-hair surface w-full shrink-0 border-t p-4 lg:w-[320px] lg:border-t-0 lg:border-l">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-[13px] font-semibold">일정 상세</h3>
        <button onClick={onClose} className="text-muted hover:text-brand-500 text-xs">
          닫기 (ESC)
        </button>
      </div>

      <div className="space-y-3">
        <Field label="제목">
          <input
            value={event.title}
            onChange={(e) => onChange({ title: e.target.value })}
            className="border-hair surface-2 w-full rounded-md border px-2 py-1.5 text-[13px] outline-none focus:border-brand-500"
          />
        </Field>

        <div className="grid grid-cols-2 gap-2">
          <Field label="시작">
            <input
              type="time"
              value={toTimeValue(event.start)}
              onChange={(e) => setTime('start', e.target.value)}
              className="border-hair surface-2 w-full rounded-md border px-2 py-1.5 text-[13px] outline-none focus:border-brand-500"
            />
          </Field>
          <Field label="종료">
            <input
              type="time"
              value={toTimeValue(event.end)}
              onChange={(e) => setTime('end', e.target.value)}
              className="border-hair surface-2 w-full rounded-md border px-2 py-1.5 text-[13px] outline-none focus:border-brand-500"
            />
          </Field>
        </div>

        <Field label="카테고리">
          <div className="flex flex-wrap gap-1.5">
            {CATEGORIES.map((c) => (
              <button
                key={c.id}
                onClick={() => onChange({ categoryId: c.id })}
                className={
                  'flex items-center gap-1.5 rounded-md border px-2 py-1 text-[12px] transition ' +
                  (event.categoryId === c.id ? 'border-brand-500' : 'border-hair text-muted')
                }
              >
                <span className="h-2 w-2 rounded-full" style={{ background: c.color }} />
                {c.name}
              </button>
            ))}
          </div>
        </Field>

        <Field label="공개 범위">
          <div className="flex gap-1.5">
            {(['TEAM', 'PRIVATE'] as const).map((v) => (
              <button
                key={v}
                onClick={() => onChange({ visibility: v })}
                className={
                  'rounded-md border px-2.5 py-1 text-[12px] transition ' +
                  (event.visibility === v ? 'border-brand-500' : 'border-hair text-muted')
                }
              >
                {v === 'TEAM' ? '팀 공개' : '비공개'}
              </button>
            ))}
          </div>
          {event.visibility === 'PRIVATE' && (
            <p className="text-muted mt-1.5 text-[11px] leading-5">
              비공개 일정은 팀 캘린더에서 "비공개"로만 보이고, 주간보고 집계에서도 제외된다.
            </p>
          )}
        </Field>

        <div className="border-hair text-muted space-y-1 border-t pt-3 text-[11.5px]">
          <div>소요 시간 · {fmtDuration(minutesBetween(event.start, event.end))}</div>
          <div>
            출처 ·{' '}
            {event.source === 'LOCAL' ? '이 앱에서 생성' : event.source === 'GOOGLE' ? '구글 캘린더' : 'ICS 구독'}
          </div>
        </div>

        <button
          onClick={onDelete}
          className="w-full rounded-md border border-red-500/40 px-3 py-2 text-[13px] text-red-500 transition hover:bg-red-500/10"
        >
          삭제 (되돌리기 가능)
        </button>
      </div>
    </aside>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-muted mb-1 block text-[11px] font-medium">{label}</span>
      {children}
    </label>
  )
}

const dayKey = (d: Date) =>
  `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`

export { dayKey }
