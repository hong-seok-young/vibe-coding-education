import { addDays, minutesBetween, startOfWeek, fmtDuration } from '../lib/dates'
import { categoryOf } from './data'
import type { DemoEvent } from './data'

export interface AggItem {
  key: string
  content: string
  categoryName: string
  color: string
  minutes: number
  count: number
  eventIds: string[]
}

/** 주간 범위 (월요일 00:00 ~ 다음 월요일 00:00) */
export function weekRange(weekOffset: number) {
  const from = addDays(startOfWeek(new Date()), weekOffset * 7)
  return { from, to: addDays(from, 7) }
}

/**
 * 일정 → 주간보고 항목.
 * 순수 함수로 유지한다 (외부 상태·DB 접근 없음). 규칙을 바꿀 때 이 파일만 고친다.
 */
export function aggregate(events: DemoEvent[], from: Date, to: Date): AggItem[] {
  const target = events.filter(
    (e) =>
      e.visibility !== 'PRIVATE' && // 비공개 일정은 보고서에 넣지 않는다
      e.start >= from &&
      e.start < to,
  )

  const groups = new Map<string, AggItem>()
  for (const e of target) {
    const cat = categoryOf(e.categoryId)
    const title = e.title.trim()
    const key = cat.name + '::' + title.toLowerCase()
    const minutes = e.allDay ? 8 * 60 : minutesBetween(e.start, e.end)

    const g = groups.get(key)
    if (g) {
      g.minutes += minutes
      g.count += 1
      g.eventIds.push(e.id)
    } else {
      groups.set(key, {
        key,
        content: title,
        categoryName: cat.name,
        color: cat.color,
        minutes,
        count: 1,
        eventIds: [e.id],
      })
    }
  }

  return [...groups.values()]
    .map((g) => ({
      ...g,
      // 2회 이상 반복된 일정은 한 줄로 합치고 횟수·총 시간을 붙인다
      content: g.count > 1 ? `${g.content} (${g.count}회, ${fmtDuration(g.minutes)})` : g.content,
    }))
    .sort((a, b) => a.categoryName.localeCompare(b.categoryName, 'ko') || b.minutes - a.minutes)
}

export function summarize(items: AggItem[]) {
  const totalMinutes = items.reduce((s, i) => s + i.minutes, 0)
  const map = new Map<string, { minutes: number; color: string }>()
  for (const i of items) {
    const cur = map.get(i.categoryName) ?? { minutes: 0, color: i.color }
    map.set(i.categoryName, { minutes: cur.minutes + i.minutes, color: i.color })
  }
  return {
    totalMinutes,
    breakdown: [...map.entries()]
      .map(([name, v]) => ({
        name,
        minutes: v.minutes,
        color: v.color,
        percent: totalMinutes === 0 ? 0 : Math.round((v.minutes / totalMinutes) * 100),
      }))
      .sort((a, b) => b.minutes - a.minutes),
  }
}

/** 카테고리별로 묶어 화면·마크다운에 쓰기 좋게 만든다 */
export function groupByCategory(items: AggItem[]) {
  const map = new Map<string, { color: string; items: AggItem[] }>()
  for (const i of items) {
    const cur = map.get(i.categoryName) ?? { color: i.color, items: [] }
    cur.items.push(i)
    map.set(i.categoryName, cur)
  }
  return [...map.entries()]
    .map(([name, v]) => ({
      name,
      color: v.color,
      items: v.items,
      minutes: v.items.reduce((s, i) => s + i.minutes, 0),
    }))
    .sort((a, b) => b.minutes - a.minutes)
}
