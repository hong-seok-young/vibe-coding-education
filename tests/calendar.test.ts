/**
 * calendar.ts 단위 검증 — 가짜 fetch 로 구글 응답을 흉내내서
 * 요청 파라미터 구성과 오류 처리가 문서대로인지 확인한다.
 * 실행: node --experimental-strip-types calendar.test.ts
 */
import {
  GoogleApiError,
  SyncTokenExpired,
  TokenInvalid,
  deleteEvent,
  insertEvent,
  listEvents,
} from '../src/demo/google/calendar.ts'

let pass = 0
let fail = 0
const calls: Array<{ url: string; init: RequestInit }> = []

function ok(name: string, cond: boolean, detail = '') {
  if (cond) {
    pass++
    console.log('  ✓', name)
  } else {
    fail++
    console.log('  ✗', name, detail)
  }
}

/** 응답을 순서대로 돌려주는 가짜 fetch */
function mockFetch(responses: Array<{ status: number; body?: unknown; headers?: Record<string, string> }>) {
  let i = 0
  globalThis.fetch = (async (url: string, init: RequestInit = {}) => {
    calls.push({ url: String(url), init })
    const r = responses[Math.min(i++, responses.length - 1)]
    return {
      ok: r.status >= 200 && r.status < 300,
      status: r.status,
      headers: { get: (k: string) => r.headers?.[k.toLowerCase()] ?? null },
      json: async () => r.body ?? {},
      text: async () => JSON.stringify(r.body ?? {}),
    }
  }) as unknown as typeof fetch
}

const err = (code: number, reason: string, message = 'x') => ({
  status: code,
  body: { error: { code, message, errors: [{ reason }] } },
})

const TOKEN = 'test-token'
const q = (n = 0) => new URL(calls[n].url).searchParams

console.log('\n[요청 파라미터]')
{
  calls.length = 0
  mockFetch([{ status: 200, body: { items: [], nextSyncToken: 'S1', summary: '내 캘린더', timeZone: 'Asia/Seoul' } }])
  const r = await listEvents(TOKEN, {})
  ok('전체 동기화: timeMin/timeMax/orderBy 전송', !!q().get('timeMin') && !!q().get('timeMax') && q().get('orderBy') === 'startTime')
  ok('전체 동기화: singleEvents=true', q().get('singleEvents') === 'true')
  ok('전체 동기화: syncToken 미전송', q().get('syncToken') === null)
  ok('nextSyncToken 반환', r.nextSyncToken === 'S1')
  ok('mode=full, truncated=false', r.mode === 'full' && r.truncated === false)
  ok('범위 반환(대조 정리용)', !!r.range?.from && !!r.range?.to)
  ok('캘린더 메타 수집', r.meta?.summary === '내 캘린더' && r.meta?.timeZone === 'Asia/Seoul')
}
{
  calls.length = 0
  mockFetch([{ status: 200, body: { items: [], nextSyncToken: 'S2' } }])
  const r = await listEvents(TOKEN, { syncToken: 'PREV' })
  ok('증분: syncToken 전송', q().get('syncToken') === 'PREV')
  ok('증분: 금지 파라미터 미전송 (timeMin/timeMax/orderBy)', !q().get('timeMin') && !q().get('timeMax') && !q().get('orderBy'))
  ok('증분: singleEvents 는 최초와 동일하게 전송', q().get('singleEvents') === 'true')
  ok('증분: showDeleted 를 false 로 보내지 않음', q().get('showDeleted') !== 'false')
  ok('mode=incremental, range 없음', r.mode === 'incremental' && r.range === undefined)
}

console.log('\n[페이지 처리]')
{
  calls.length = 0
  mockFetch([
    { status: 200, body: { items: [], nextPageToken: 'P2' } },
    { status: 200, body: { items: [], nextSyncToken: 'LAST' } },
  ])
  const r = await listEvents(TOKEN, {})
  ok('마지막 페이지까지 읽음 (2회 호출)', calls.length === 2)
  ok('마지막 페이지의 nextSyncToken 저장', r.nextSyncToken === 'LAST' && r.truncated === false)
}
{
  calls.length = 0
  mockFetch([{ status: 200, body: { items: [], nextPageToken: 'MORE' } }])
  const r = await listEvents(TOKEN, { maxPages: 1 })
  ok('상한에 걸리면 truncated=true', r.truncated === true)
  ok('상한에 걸리면 syncToken 저장 안 함', r.nextSyncToken === undefined)
}

console.log('\n[일정 정규화]')
{
  mockFetch([
    {
      status: 200,
      body: {
        items: [
          { id: 'a', etag: 'E1', status: 'confirmed', summary: '팀 회의', start: { dateTime: '2026-08-24T05:00:00Z' }, end: { dateTime: '2026-08-24T06:00:00Z' } },
          { id: 'b', status: 'confirmed', summary: '워크숍', start: { date: '2026-08-25' }, end: { date: '2026-08-26' } },
          { id: 'c', status: 'cancelled' },
          { id: 'd', status: 'confirmed', summary: '', start: { dateTime: '2026-08-24T07:00:00Z' }, end: { dateTime: '2026-08-24T08:00:00Z' } },
        ],
        nextSyncToken: 'S',
      },
    },
  ])
  const r = await listEvents(TOKEN, {})
  const [a, b, c, d] = r.events
  ok('시간 일정: allDay=false, etag 보존', a.allDay === false && a.etag === 'E1')
  ok('종일 일정: date → allDay=true', b.allDay === true && b.title === '워크숍')
  ok('취소된 일정: cancelled=true 로 살아남음', c.cancelled === true && c.externalId === 'c')
  ok('제목 없는 일정 대체 표기', d.title === '(제목 없음)')
}

console.log('\n[오류 처리]')
{
  mockFetch([err(401, 'authError')])
  let caught: unknown
  try { await listEvents(TOKEN, {}) } catch (e) { caught = e }
  ok('401 → TokenInvalid', caught instanceof TokenInvalid)
}
{
  mockFetch([err(410, 'fullSyncRequired')])
  let caught: unknown
  try { await listEvents(TOKEN, { syncToken: 'OLD' }) } catch (e) { caught = e }
  ok('410 fullSyncRequired → SyncTokenExpired', caught instanceof SyncTokenExpired)
}
{
  mockFetch([err(410, 'deleted')])
  let caught: unknown
  try { await deleteEvent(TOKEN, 'gone') } catch (e) { caught = e }
  ok('410 다른 사유 → SyncTokenExpired 아님', caught instanceof GoogleApiError && !(caught instanceof SyncTokenExpired))
}
{
  mockFetch([err(403, 'insufficientPermissions')])
  let caught: GoogleApiError | undefined
  try { await insertEvent(TOKEN, { title: 't', start: new Date(), end: new Date() }) } catch (e) { caught = e as GoogleApiError }
  ok('403 권한 부족 → 재연결 안내', !!caught?.remedy.includes('읽기 + 쓰기'))
}
{
  calls.length = 0
  mockFetch([err(403, 'rateLimitExceeded'), err(403, 'rateLimitExceeded'), { status: 200, body: { items: [], nextSyncToken: 'S' } }])
  const r = await listEvents(TOKEN, {})
  ok('403 속도 제한 → 재시도 후 성공 (3회 호출)', calls.length === 3 && r.nextSyncToken === 'S')
}
{
  calls.length = 0
  const started = Date.now()
  mockFetch([{ ...err(429, 'rateLimitExceeded'), headers: { 'retry-after': '1' } }, { status: 200, body: { items: [] } }])
  await listEvents(TOKEN, {})
  const waited = Date.now() - started
  ok('429 Retry-After 준수 (1초 이상 대기)', waited >= 900, `${waited}ms`)
}
{
  calls.length = 0
  mockFetch([err(400, 'badRequest')])
  let caught: GoogleApiError | undefined
  try { await listEvents(TOKEN, { syncToken: 'X' }) } catch (e) { caught = e as GoogleApiError }
  ok('400 → 재시도하지 않음 (1회 호출)', calls.length === 1 && caught?.status === 400)
}

console.log('\n[쓰기 요청]')
{
  calls.length = 0
  mockFetch([{ status: 200, body: { id: 'new-1', etag: 'E9' } }])
  const start = new Date('2026-08-24T05:00:00Z')
  const end = new Date('2026-08-24T06:00:00Z')
  const r = await insertEvent(TOKEN, { title: '[교육 데모] 내보내기 테스트', start, end })
  const body = JSON.parse(String(calls[0].init.body))
  ok('POST 경로', calls[0].url.endsWith('/calendars/primary/events') && calls[0].init.method === 'POST')
  ok('start/end 를 dateTime 으로 전송', body.start.dateTime === start.toISOString() && body.end.dateTime === end.toISOString())
  ok('생성된 외부 ID 반환', r.externalId === 'new-1' && r.etag === 'E9')
}
{
  calls.length = 0
  mockFetch([{ status: 204 }])
  await deleteEvent(TOKEN, 'evt/1 2')
  ok('DELETE 경로 + ID 인코딩', calls[0].init.method === 'DELETE' && calls[0].url.includes(encodeURIComponent('evt/1 2')))
}

console.log(`\n결과: 통과 ${pass} / 실패 ${fail}`)
process.exit(fail === 0 ? 0 : 1)
