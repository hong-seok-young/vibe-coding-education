import { useMemo, useState } from 'react'
import { addDays, fmtDate, fmtDuration, isoWeek } from '../lib/dates'
import { useCopy } from '../lib/useCopy'
import { aggregate, groupByCategory, summarize, weekRange } from './aggregate'
import { ME } from './data'
import { useDemo } from './store'

interface Item {
  id: string
  key: string
  content: string
  categoryName: string
  color: string
  minutes: number
  edited: boolean
}

type Section = 'DONE' | 'NEXT' | 'ISSUE'

const SECTION_LABEL: Record<Section, string> = {
  DONE: '이번 주 한 일',
  NEXT: '다음 주 계획',
  ISSUE: '이슈 · 리스크',
}

export function WeeklyDemo() {
  const { events } = useDemo()
  const [weekOffset, setWeekOffset] = useState(0)
  const [submitted, setSubmitted] = useState(false)
  const [issues, setIssues] = useState<Item[]>([
    {
      id: 'issue-1',
      key: 'issue-1',
      content: '구글 OAuth 앱 심사가 지연되면 8월 말 배포 일정에 영향',
      categoryName: '이슈',
      color: '#e0793a',
      minutes: 0,
      edited: true,
    },
  ])
  const [overrides, setOverrides] = useState<Record<string, string>>({})
  const [removed, setRemoved] = useState<Set<string>>(new Set())

  const { from, to } = useMemo(() => weekRange(weekOffset), [weekOffset])
  const { year, week } = isoWeek(from)

  const doneRaw = useMemo(() => aggregate(events, from, to), [events, from, to])
  const nextRaw = useMemo(
    () => aggregate(events, addDays(from, 7), addDays(to, 7)),
    [events, from, to],
  )

  const toItems = (raw: typeof doneRaw, section: Section): Item[] =>
    raw
      .filter((r) => !removed.has(section + r.key))
      .map((r) => ({
        id: section + r.key,
        key: r.key,
        content: overrides[section + r.key] ?? r.content,
        categoryName: r.categoryName,
        color: r.color,
        minutes: r.minutes,
        edited: overrides[section + r.key] !== undefined,
      }))

  const done = toItems(doneRaw, 'DONE')
  const next = toItems(nextRaw, 'NEXT')
  const stats = useMemo(() => summarize(doneRaw), [doneRaw])

  const editedCount = Object.keys(overrides).length
  const markdown = useMemo(
    () => buildMarkdown({ year, week, from, to, done, next, issues, stats }),
    [year, week, from, to, done, next, issues, stats],
  )
  const { copied, copy } = useCopy()

  return (
    <div className="mx-auto w-full max-w-5xl px-4 py-6">
      {/* 주 선택 + 상태 */}
      <div className="mb-5 flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1">
          <button
            onClick={() => setWeekOffset((w) => w - 1)}
            className="border-hair hover:border-brand-500/60 rounded-md border px-2.5 py-1.5 text-xs"
          >
            ←
          </button>
          <button
            onClick={() => setWeekOffset(0)}
            className="border-hair hover:border-brand-500/60 rounded-md border px-2.5 py-1.5 text-xs"
          >
            이번 주
          </button>
          <button
            onClick={() => setWeekOffset((w) => w + 1)}
            className="border-hair hover:border-brand-500/60 rounded-md border px-2.5 py-1.5 text-xs"
          >
            →
          </button>
        </div>

        <div>
          <h2 className="text-[15px] font-semibold tracking-tight">
            {year}년 {week}주 · {ME.name}
          </h2>
          <p className="text-muted text-[12px]">
            {fmtDate(from)} ~ {fmtDate(addDays(to, -1))} · 총 {fmtDuration(stats.totalMinutes)}
          </p>
        </div>

        <div className="ml-auto flex items-center gap-2">
          <span
            className={
              'rounded-full px-2.5 py-1 text-[11px] font-semibold ' +
              (submitted ? 'bg-emerald-500/15 text-emerald-500' : 'surface-2 text-muted')
            }
          >
            {submitted ? '제출됨' : '초안'}
          </span>
          <button
            onClick={() => copy(markdown)}
            className="border-hair text-muted hover:text-brand-500 rounded-md border px-2.5 py-1.5 text-xs"
          >
            {copied ? '복사됨 ✓' : '마크다운 복사'}
          </button>
          <button
            onClick={() => setSubmitted((s) => !s)}
            className="bg-brand-500 hover:bg-brand-600 rounded-md px-3 py-1.5 text-xs font-semibold text-white"
          >
            {submitted ? '제출 취소' : '제출'}
          </button>
        </div>
      </div>

      {/* 통계 */}
      <div className="border-hair surface mb-5 rounded-xl border p-4">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-[12px] font-semibold">시간 배분</span>
          <span className="text-muted text-[11.5px]">
            캘린더에서 자동 집계 · 비공개 일정 제외
          </span>
        </div>
        <div className="surface-2 flex h-3 overflow-hidden rounded-full">
          {stats.breakdown.map((b) => (
            <div
              key={b.name}
              style={{ width: b.percent + '%', background: b.color }}
              title={`${b.name} ${b.percent}%`}
            />
          ))}
        </div>
        <div className="mt-2.5 flex flex-wrap gap-x-4 gap-y-1.5">
          {stats.breakdown.map((b) => (
            <span key={b.name} className="flex items-center gap-1.5 text-[12px]">
              <span className="h-2 w-2 rounded-full" style={{ background: b.color }} />
              {b.name} <span className="text-muted">{b.percent}% · {fmtDuration(b.minutes)}</span>
            </span>
          ))}
          {stats.breakdown.length === 0 && (
            <span className="text-muted text-[12px]">이 주에 등록된 일정이 없다</span>
          )}
        </div>
      </div>

      {/* 재생성 안내 */}
      <div className="border-brand-500/40 bg-brand-500/5 mb-5 flex flex-wrap items-center gap-3 rounded-xl border px-4 py-3">
        <span className="text-[13px]">
          초안 재생성 시 <strong>{done.length + next.length - editedCount}개 항목이 갱신</strong>되고{' '}
          <strong>{editedCount}개는 내가 수정한 내용으로 유지</strong>된다.
        </span>
        <button
          onClick={() => {
            setRemoved(new Set())
          }}
          className="border-hair ml-auto rounded-md border px-2.5 py-1.5 text-xs hover:border-brand-500/60"
        >
          초안 재생성
        </button>
        {editedCount > 0 && (
          <button
            onClick={() => setOverrides({})}
            className="text-muted hover:text-brand-500 text-xs underline"
          >
            내 수정 내용 초기화
          </button>
        )}
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <SectionCard
          section="DONE"
          items={done}
          onEdit={(id, content) => setOverrides((o) => ({ ...o, [id]: content }))}
          onRemove={(id) => setRemoved((s) => new Set(s).add(id))}
        />
        <SectionCard
          section="NEXT"
          items={next}
          onEdit={(id, content) => setOverrides((o) => ({ ...o, [id]: content }))}
          onRemove={(id) => setRemoved((s) => new Set(s).add(id))}
        />
      </div>

      <div className="mt-5">
        <IssueCard items={issues} onChange={setIssues} />
      </div>

      <p className="text-muted mt-6 text-[12px] leading-6">
        이 화면의 모든 항목은 <strong>캘린더 데모의 일정에서 자동으로 집계</strong>된 것이다. 캘린더 데모에서
        일정을 추가·수정하고 이 화면으로 돌아오면 즉시 반영된다. 반복되는 일정은 "(N회, N시간)"으로 합쳐지고,
        비공개로 표시한 일정은 집계에서 빠진다.
      </p>
    </div>
  )
}

function SectionCard({
  section, items, onEdit, onRemove,
}: {
  section: Section
  items: Item[]
  onEdit: (id: string, content: string) => void
  onRemove: (id: string) => void
}) {
  const groups = useMemo(
    () =>
      groupByCategory(
        items.map((i) => ({
          key: i.key,
          content: i.content,
          categoryName: i.categoryName,
          color: i.color,
          minutes: i.minutes,
          count: 1,
          eventIds: [],
        })),
      ),
    [items],
  )

  return (
    <section className="border-hair surface rounded-xl border">
      <header className="border-hair surface-2 flex items-center justify-between border-b px-4 py-2.5">
        <h3 className="text-[13px] font-semibold">{SECTION_LABEL[section]}</h3>
        <span className="text-muted text-[11px]">{items.length}개 · 자동 생성</span>
      </header>

      <div className="space-y-4 p-4">
        {groups.length === 0 && (
          <p className="text-muted text-[13px]">해당 기간에 집계할 일정이 없다.</p>
        )}
        {groups.map((g) => (
          <div key={g.name}>
            <div className="mb-1.5 flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full" style={{ background: g.color }} />
              <span className="text-[12px] font-semibold">{g.name}</span>
            </div>
            <ul className="space-y-1">
              {g.items.map((gi) => {
                const item = items.find((i) => i.key === gi.key && i.content === gi.content)!
                return (
                  <li key={gi.key} className="group flex items-start gap-2">
                    <span className="text-muted mt-2 text-[10px]">·</span>
                    <EditableLine
                      value={item.content}
                      edited={item.edited}
                      onChange={(v) => onEdit(item.id, v)}
                    />
                    <button
                      onClick={() => onRemove(item.id)}
                      className="text-muted hover:text-red-500 mt-1 shrink-0 text-[11px] opacity-0 transition group-hover:opacity-100"
                      aria-label="항목 제거"
                    >
                      ×
                    </button>
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </div>
    </section>
  )
}

function EditableLine({
  value, edited, onChange,
}: {
  value: string
  edited: boolean
  onChange: (v: string) => void
}) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value)

  if (editing) {
    return (
      <input
        autoFocus
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={() => {
          setEditing(false)
          if (draft.trim() && draft !== value) onChange(draft.trim())
        }}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            setEditing(false)
            if (draft.trim() && draft !== value) onChange(draft.trim())
          } else if (e.key === 'Escape') {
            setDraft(value)
            setEditing(false)
          }
        }}
        className="border-brand-500 surface-2 min-w-0 flex-1 rounded border px-1.5 py-0.5 text-[13.5px] outline-none"
      />
    )
  }

  return (
    <button
      onClick={() => {
        setDraft(value)
        setEditing(true)
      }}
      className="min-w-0 flex-1 rounded px-1 py-0.5 text-left text-[13.5px] leading-6 hover:surface-2"
      title="클릭해서 수정"
    >
      {value}
      {edited && (
        <span className="text-brand-500 ml-1.5 align-middle text-[10px]">수정됨 · 재생성 시 유지</span>
      )}
    </button>
  )
}

function IssueCard({ items, onChange }: { items: Item[]; onChange: (items: Item[]) => void }) {
  const [draft, setDraft] = useState('')

  return (
    <section className="rounded-xl border border-amber-500/40 bg-amber-500/5">
      <header className="flex items-center justify-between border-b border-amber-500/30 px-4 py-2.5">
        <h3 className="text-[13px] font-semibold">이슈 · 리스크</h3>
        <span className="text-muted text-[11px]">자동 생성하지 않는다 — 사람이 직접 쓴다</span>
      </header>
      <div className="p-4">
        <ul className="mb-3 space-y-1">
          {items.map((i) => (
            <li key={i.id} className="group flex items-start gap-2">
              <span className="mt-1.5 text-[11px]">⚠</span>
              <span className="min-w-0 flex-1 text-[13.5px] leading-6">{i.content}</span>
              <button
                onClick={() => onChange(items.filter((x) => x.id !== i.id))}
                className="text-muted hover:text-red-500 mt-1 text-[11px] opacity-0 transition group-hover:opacity-100"
              >
                ×
              </button>
            </li>
          ))}
          {items.length === 0 && <li className="text-muted text-[13px]">등록된 이슈가 없다.</li>}
        </ul>
        <div className="flex gap-2">
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && draft.trim()) {
                onChange([
                  ...items,
                  {
                    id: 'issue-' + Math.random().toString(36).slice(2, 8),
                    key: 'issue',
                    content: draft.trim(),
                    categoryName: '이슈',
                    color: '#e0793a',
                    minutes: 0,
                    edited: true,
                  },
                ])
                setDraft('')
              }
            }}
            placeholder="이슈나 리스크를 직접 입력 (Enter로 추가)"
            className="border-hair surface min-w-0 flex-1 rounded-md border px-2.5 py-1.5 text-[13px] outline-none focus:border-amber-500"
          />
        </div>
      </div>
    </section>
  )
}

function buildMarkdown({
  year, week, from, to, done, next, issues, stats,
}: {
  year: number
  week: number
  from: Date
  to: Date
  done: Item[]
  next: Item[]
  issues: Item[]
  stats: ReturnType<typeof summarize>
}) {
  const lines: string[] = []
  lines.push(`# ${year}년 ${week}주 주간보고 · ${ME.name} (${ME.dept})`)
  lines.push(`기간: ${fmtDate(from)} ~ ${fmtDate(addDays(to, -1))} · 총 ${fmtDuration(stats.totalMinutes)}`)
  lines.push('')

  const section = (title: string, items: Item[]) => {
    lines.push(`## ${title}`)
    const groups = new Map<string, Item[]>()
    for (const i of items) {
      const list = groups.get(i.categoryName) ?? []
      list.push(i)
      groups.set(i.categoryName, list)
    }
    if (groups.size === 0) lines.push('- (없음)')
    for (const [cat, list] of groups) {
      lines.push(`### ${cat}`)
      for (const i of list) lines.push(`- ${i.content}`)
    }
    lines.push('')
  }

  section('이번 주 한 일', done)
  section('다음 주 계획', next)

  lines.push('## 이슈 · 리스크')
  if (issues.length === 0) lines.push('- 없음')
  for (const i of issues) lines.push(`- ${i.content}`)
  lines.push('')

  lines.push('## 시간 배분')
  lines.push(stats.breakdown.map((b) => `${b.name} ${b.percent}%`).join(' · ') || '-')

  return lines.join('\n')
}
