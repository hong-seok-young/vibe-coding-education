export interface QuickParsed {
  title: string
  startMinutes: number
  endMinutes: number
  matched: boolean
}

const DEFAULT_START = 9 * 60
const DEFAULT_DURATION = 60

const RANGE =
  /(\d{1,2})(?::(\d{2}))?\s*(?:시)?\s*[-~]\s*(\d{1,2})(?::(\d{2}))?\s*(?:시)?\s*(am|pm|오전|오후)?/i
const SINGLE = /(\d{1,2})(?::(\d{2}))?\s*(?:시|am|pm|오전|오후)/i
const DUR_MIN = /(\d{1,3})\s*분/
const DUR_HOUR = /(\d{1,2})\s*시간/

/**
 * "14시 팀 회의", "3-5pm 고객 미팅", "10:30 스크럼 30분" 에서 시간을 뽑는다.
 * 설계 원칙: 못 알아들으면 조용히 기본값을 쓴다. 절대 예외를 던지지 않는다.
 */
export function parseQuickInput(raw: string): QuickParsed {
  const input = raw.trim()
  const fallback: QuickParsed = {
    title: input,
    startMinutes: DEFAULT_START,
    endMinutes: DEFAULT_START + DEFAULT_DURATION,
    matched: false,
  }
  if (!input) return fallback

  const range = input.match(RANGE)
  if (range) {
    const mer = range[5]?.toLowerCase()
    const start = toMinutes(+range[1], +(range[2] ?? 0), mer)
    const end = toMinutes(+range[3], +(range[4] ?? 0), mer)
    const title = strip(input, range[0])
    return {
      title: title || input,
      startMinutes: start,
      endMinutes: end > start ? end : start + DEFAULT_DURATION,
      matched: true,
    }
  }

  const single = input.match(SINGLE)
  if (single) {
    const mer = /am|오전/i.test(single[0]) ? '오전' : /pm|오후/i.test(single[0]) ? '오후' : undefined
    const start = toMinutes(+single[1], +(single[2] ?? 0), mer)
    const durMin = input.match(DUR_MIN)
    const durHour = input.match(DUR_HOUR)
    const dur = durMin ? +durMin[1] : durHour ? +durHour[1] * 60 : DEFAULT_DURATION
    const title = strip(strip(input, single[0]), durMin?.[0] ?? durHour?.[0] ?? '')
    return {
      title: title || input,
      startMinutes: start,
      endMinutes: Math.min(start + dur, 24 * 60),
      matched: true,
    }
  }

  return fallback
}

function toMinutes(h: number, m: number, meridiem?: string) {
  let hour = h
  if (meridiem === 'pm' || meridiem === '오후') hour = h === 12 ? 12 : h + 12
  else if (meridiem === 'am' || meridiem === '오전') hour = h === 12 ? 0 : h
  // 오전/오후 표시가 없고 1~7시면 업무시간대로 해석한다 (3시 → 15시)
  else if (h >= 1 && h <= 7) hour = h + 12
  return Math.min(hour, 23) * 60 + Math.min(m, 59)
}

const strip = (s: string, part: string) => (part ? s.replace(part, ' ').replace(/\s+/g, ' ').trim() : s.trim())
