import { useEffect, useMemo, useRef, useState } from 'react'
import { addDays, fmtDate, fmtDuration, isoWeek } from '../lib/dates'
import { useCopy } from '../lib/useCopy'
import { aggregate, groupByCategory, summarize, weekRange } from './aggregate'
import { ME, TEAM_REPORTS, USERS } from './data'
import { useDemo } from './store'

interface Slide {
  name: string
  dept: string
  submitted: boolean
  totalMinutes: number
  breakdown: { name: string; percent: number; color: string }[]
  done: { category: string; color: string; items: string[] }[]
  next: { category: string; color: string; items: string[] }[]
  issues: string[]
}

export function PresentDemo() {
  const { events } = useDemo()
  const [index, setIndex] = useState(0)
  const [elapsed, setElapsed] = useState(0)
  const [highlight, setHighlight] = useState<string | null>(null)
  const wrapRef = useRef<HTMLDivElement>(null)

  const { from, to } = useMemo(() => weekRange(0), [])
  const { year, week } = isoWeek(from)

  const slides = useMemo<Slide[]>(() => {
    const mine = aggregate(events, from, to)
    const mineNext = aggregate(events, addDays(from, 7), addDays(to, 7))
    const stats = summarize(mine)

    const mySlide: Slide = {
      name: ME.name,
      dept: ME.dept,
      submitted: true,
      totalMinutes: stats.totalMinutes,
      breakdown: stats.breakdown,
      done: groupByCategory(mine).map((g) => ({
        category: g.name,
        color: g.color,
        items: g.items.map((i) => i.content),
      })),
      next: groupByCategory(mineNext).map((g) => ({
        category: g.name,
        color: g.color,
        items: g.items.map((i) => i.content),
      })),
      issues: ['구글 OAuth 앱 심사가 지연되면 8월 말 배포 일정에 영향'],
    }

    const others = TEAM_REPORTS.map((r): Slide => {
      const user = USERS.find((u) => u.id === r.userId)!
      const colorOf = (name: string) => r.breakdown.find((b) => b.name === name)?.color ?? '#78839a'
      return {
        name: user.name,
        dept: user.dept,
        submitted: r.submitted,
        totalMinutes: r.totalMinutes,
        breakdown: r.breakdown,
        done: r.done.map((d) => ({ category: d.category, color: colorOf(d.category), items: d.items })),
        next: r.next.map((d) => ({ category: d.category, color: colorOf(d.category), items: d.items })),
        issues: r.issues,
      }
    })

    return [mySlide, ...others]
  }, [events, from, to])

  const slide = slides[index]
  const nextName = slides[index + 1]?.name

  useEffect(() => {
    setElapsed(0)
    setHighlight(null)
    const t = setInterval(() => setElapsed((e) => e + 1), 1000)
    return () => clearInterval(t)
  }, [index])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement | null)?.tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA') return
      if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault()
        setIndex((i) => Math.min(i + 1, slides.length - 1))
      } else if (e.key === 'ArrowLeft') {
        setIndex((i) => Math.max(i - 1, 0))
      } else if (e.key === 'f' || e.key === 'F') {
        if (document.fullscreenElement) void document.exitFullscreen()
        else void wrapRef.current?.requestFullscreen?.()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [slides.length])

  const minutes = String(Math.floor(elapsed / 60)).padStart(2, '0')
  const seconds = String(elapsed % 60).padStart(2, '0')
  const overTime = elapsed > 120

  const { copied, copy } = useCopy()
  const minutesMd = useMemo(() => buildMinutes(slides, year, week, from, to), [slides, year, week, from, to])

  return (
    <div ref={wrapRef} className="surface flex min-h-0 flex-1 flex-col">
      {/* 상단: 발표자 정보 */}
      <div className="border-hair flex flex-wrap items-center gap-x-6 gap-y-2 border-b px-6 py-4">
        <div>
          <div className="flex items-baseline gap-2">
            <h2 className="text-2xl font-bold tracking-tight md:text-3xl">{slide.name}</h2>
            <span className="text-muted text-sm">{slide.dept}</span>
            {!slide.submitted && (
              <span className="rounded bg-amber-500/15 px-2 py-0.5 text-[11px] font-semibold text-amber-500">
                미제출 · 캘린더 기준 자동 요약
              </span>
            )}
          </div>
          <p className="text-muted mt-0.5 text-sm">
            {year}년 {week}주 · 총 {fmtDuration(slide.totalMinutes)}
          </p>
        </div>

        <div className="min-w-[220px] flex-1">
          <div className="surface-2 flex h-2.5 overflow-hidden rounded-full">
            {slide.breakdown.map((b) => (
              <div key={b.name} style={{ width: b.percent + '%', background: b.color }} />
            ))}
          </div>
          <div className="mt-1.5 flex flex-wrap gap-x-3 gap-y-1">
            {slide.breakdown.map((b) => (
              <span key={b.name} className="flex items-center gap-1 text-[12px]">
                <span className="h-2 w-2 rounded-full" style={{ background: b.color }} />
                {b.name} {b.percent}%
              </span>
            ))}
          </div>
        </div>

        <div
          className={
            'ml-auto rounded-lg px-3 py-1.5 font-mono text-lg tabular-nums ' +
            (overTime ? 'bg-amber-500/15 text-amber-500' : 'surface-2 text-muted')
          }
          title="발표 타이머 · 2분 초과 시 색이 바뀐다 (소리는 내지 않는다)"
        >
          {minutes}:{seconds}
        </div>
      </div>

      {/* 본문 2단 */}
      <div className="grid min-h-0 flex-1 gap-6 overflow-auto px-6 py-5 lg:grid-cols-2">
        <Column
          title="이번 주 한 일"
          groups={slide.done}
          highlight={highlight}
          onHighlight={setHighlight}
        />
        <Column
          title="다음 주 계획"
          groups={slide.next}
          highlight={highlight}
          onHighlight={setHighlight}
        />
      </div>

      {/* 이슈: 있을 때만 */}
      {slide.issues.length > 0 && (
        <div className="border-t border-amber-500/40 bg-amber-500/5 px-6 py-3">
          <div className="mb-1 text-[12px] font-semibold text-amber-500">⚠ 이슈 · 리스크</div>
          <ul className="space-y-0.5">
            {slide.issues.map((i) => (
              <li key={i} className="text-[15px] leading-7 md:text-[17px]">
                {i}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 하단 조작 */}
      <div className="border-hair surface-2 flex flex-wrap items-center gap-3 border-t px-6 py-3">
        <div className="flex items-center gap-1.5">
          {slides.map((s, i) => (
            <button
              key={s.name}
              onClick={() => setIndex(i)}
              title={s.name}
              className={
                'h-2.5 w-2.5 rounded-full transition ' +
                (i === index ? 'bg-brand-500 scale-125' : i < index ? 'bg-brand-500/40' : 'surface border-hair border')
              }
            />
          ))}
        </div>

        <span className="text-muted text-[12px] tabular-nums">
          {index + 1} / {slides.length}
        </span>

        {nextName && <span className="text-muted text-[12px]">다음: {nextName}</span>}

        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => copy(minutesMd)}
            className="border-hair text-muted hover:text-brand-500 rounded-md border px-2.5 py-1.5 text-xs"
          >
            {copied ? '복사됨 ✓' : '회의록 복사'}
          </button>
          <button
            onClick={() => setIndex((i) => Math.max(i - 1, 0))}
            className="border-hair rounded-md border px-2.5 py-1.5 text-xs hover:border-brand-500/60"
          >
            ← 이전
          </button>
          <button
            onClick={() => setIndex((i) => Math.min(i + 1, slides.length - 1))}
            className="bg-brand-500 hover:bg-brand-600 rounded-md px-3 py-1.5 text-xs font-semibold text-white"
          >
            다음 →
          </button>
        </div>
      </div>

      <p className="text-muted border-hair border-t px-6 py-2 text-[11.5px]">
        단축키 · <strong>→ / Space</strong> 다음, <strong>←</strong> 이전, <strong>F</strong> 전체화면 · 항목을
        클릭하면 발표 중 강조 표시된다
      </p>
    </div>
  )
}

function Column({
  title, groups, highlight, onHighlight,
}: {
  title: string
  groups: { category: string; color: string; items: string[] }[]
  highlight: string | null
  onHighlight: (v: string | null) => void
}) {
  return (
    <section>
      <h3 className="text-muted mb-3 text-[13px] font-semibold tracking-wide">{title}</h3>
      <div className="space-y-4">
        {groups.length === 0 && <p className="text-muted text-[15px]">등록된 내용이 없다.</p>}
        {groups.map((g) => (
          <div key={g.category}>
            <div className="mb-1.5 flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full" style={{ background: g.color }} />
              <span className="text-[14px] font-semibold">{g.category}</span>
            </div>
            <ul className="space-y-1">
              {g.items.map((i) => (
                <li key={i}>
                  <button
                    onClick={() => onHighlight(highlight === i ? null : i)}
                    className={
                      'w-full rounded px-2 py-1 text-left text-[16px] leading-8 transition md:text-[18px] ' +
                      (highlight === i ? 'bg-brand-500/15 text-brand-500 font-medium' : 'hover:surface-2')
                    }
                  >
                    {i}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  )
}

function buildMinutes(slides: Slide[], year: number, week: number, from: Date, to: Date) {
  const lines: string[] = []
  lines.push(`# dX팀 주간회의 · ${year}년 ${week}주 (${fmtDate(from)}~${fmtDate(addDays(to, -1))})`)
  lines.push(`참석 ${slides.length}명 / 제출 ${slides.filter((s) => s.submitted).length}명`)
  lines.push('')

  for (const s of slides) {
    lines.push(`## ${s.name} (${fmtDuration(s.totalMinutes)})${s.submitted ? '' : ' · 미제출, 캘린더 기준'}`)
    const top = s.done.flatMap((g) => g.items).slice(0, 3)
    for (const i of top) lines.push(`- ${i}`)
    for (const i of s.issues) lines.push(`- ⚠ ${i}`)
    lines.push('')
  }
  return lines.join('\n')
}
