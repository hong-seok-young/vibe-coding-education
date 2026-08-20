/** 데모에서 쓰는 최소한의 날짜 유틸. 외부 의존성 없이 직접 구현했다. */

export const DAY = 86_400_000

export function startOfDay(d: Date) {
  const x = new Date(d)
  x.setHours(0, 0, 0, 0)
  return x
}

export function addDays(d: Date, n: number) {
  const x = new Date(d)
  x.setDate(x.getDate() + n)
  return x
}

export function addMonths(d: Date, n: number) {
  const x = new Date(d)
  x.setDate(1)
  x.setMonth(x.getMonth() + n)
  return x
}

/** 월요일 시작 주의 첫날 */
export function startOfWeek(d: Date) {
  const x = startOfDay(d)
  const day = (x.getDay() + 6) % 7 // 월=0 … 일=6
  return addDays(x, -day)
}

export function startOfMonth(d: Date) {
  const x = startOfDay(d)
  x.setDate(1)
  return x
}

export function isSameDay(a: Date, b: Date) {
  return (
    a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
  )
}

export function isSameMonth(a: Date, b: Date) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth()
}

/** 월 뷰용 42칸(6주). 달마다 높이가 바뀌지 않게 항상 6주로 고정한다. */
export function monthGrid(anchor: Date): Date[] {
  const first = startOfWeek(startOfMonth(anchor))
  return Array.from({ length: 42 }, (_, i) => addDays(first, i))
}

export function weekDays(anchor: Date): Date[] {
  const first = startOfWeek(anchor)
  return Array.from({ length: 7 }, (_, i) => addDays(first, i))
}

export const WEEKDAY_KO = ['월', '화', '수', '목', '금', '토', '일']

export const pad = (n: number) => String(n).padStart(2, '0')

export const fmtTime = (d: Date) => `${pad(d.getHours())}:${pad(d.getMinutes())}`

export const fmtMonthTitle = (d: Date) => `${d.getFullYear()}년 ${d.getMonth() + 1}월`

export const fmtDate = (d: Date) => `${d.getMonth() + 1}/${d.getDate()}`

export const fmtRange = (a: Date, b: Date) =>
  isSameDay(a, b) ? `${fmtDate(a)} ${fmtTime(a)}~${fmtTime(b)}` : `${fmtDate(a)}~${fmtDate(b)}`

/** ISO 8601 주차. 목요일이 포함된 주가 그 해의 1주. */
export function isoWeek(d: Date): { year: number; week: number } {
  const t = startOfDay(d)
  const day = (t.getDay() + 6) % 7
  const thursday = addDays(t, 3 - day)
  const year = thursday.getFullYear()
  const jan1 = new Date(year, 0, 1)
  const week = Math.floor((thursday.getTime() - jan1.getTime()) / (7 * DAY)) + 1
  return { year, week }
}

export function fmtDuration(minutes: number) {
  const h = Math.floor(minutes / 60)
  const m = Math.round(minutes % 60)
  if (h === 0) return `${m}분`
  if (m === 0) return `${h}시간`
  return `${h}시간 ${m}분`
}

export const minutesBetween = (a: Date, b: Date) => Math.max(0, (b.getTime() - a.getTime()) / 60000)
