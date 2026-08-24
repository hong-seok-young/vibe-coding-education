/**
 * Google Calendar API v3 호출 (브라우저에서 직접)
 *
 * 이 파일이 STEP 06 의 `src/server/providers/google.ts` 에 대응한다.
 * 실제 앱에서는 이 코드가 서버에 있어야 한다 — 여기서는 서버가 없어서 브라우저에 두고,
 * 그 대가(리프레시 토큰 없음, 토큰이 화면 수명만큼만 유지됨)를 화면에 밝혀둔다.
 */
const BASE = 'https://www.googleapis.com/calendar/v3'

export class GoogleApiError extends Error {
  constructor(
    public status: number,
    message: string,
    /** 사용자에게 보여줄 다음 행동 */
    public remedy: string,
  ) {
    super(message)
  }
}

/** syncToken 이 만료된 경우. 전체 동기화로 폴백해야 한다 (STEP 06 의 핵심 함정) */
export class SyncTokenExpired extends GoogleApiError {
  constructor() {
    super(410, 'syncToken 이 만료되었습니다', '전체 동기화로 다시 시작합니다')
  }
}

/** 토큰이 만료됐거나 취소됨 → 다시 연결해야 한다 */
export class TokenInvalid extends GoogleApiError {
  constructor() {
    super(401, '토큰이 만료되었거나 취소되었습니다', '"다시 연결"을 눌러 권한을 새로 받아주세요')
  }
}

export interface RawGoogleEvent {
  id: string
  etag?: string
  status?: 'confirmed' | 'tentative' | 'cancelled'
  summary?: string
  updated?: string
  start?: { dateTime?: string; date?: string; timeZone?: string }
  end?: { dateTime?: string; date?: string; timeZone?: string }
}

export interface NormalizedEvent {
  externalId: string
  etag?: string
  title: string
  start: Date
  end: Date
  allDay: boolean
  cancelled: boolean
  updatedAt?: Date
}

/** 구글 오류 응답에서 사유(reason)를 꺼낸다. 403·410 은 사유에 따라 처리가 완전히 달라진다. */
async function readError(res: Response): Promise<{ reason: string; message: string }> {
  try {
    const json = (await res.json()) as {
      error?: { message?: string; errors?: Array<{ reason?: string }> }
    }
    return { reason: json.error?.errors?.[0]?.reason ?? '', message: json.error?.message ?? '' }
  } catch {
    return { reason: '', message: '' }
  }
}

/** 재시도해도 되는 사유 — 일시적인 속도 제한이다 */
const RETRYABLE = new Set(['rateLimitExceeded', 'userRateLimitExceeded', 'quotaExceeded', 'backendError'])

async function call(
  path: string,
  token: string,
  init: RequestInit = {},
  attempt = 0,
): Promise<Response> {
  const res = await fetch(BASE + path, {
    ...init,
    headers: {
      ...(init.headers ?? {}),
      Authorization: 'Bearer ' + token,
      ...(init.body ? { 'Content-Type': 'application/json' } : {}),
    },
  })

  if (res.ok) return res

  const { reason, message } = await readError(res)

  // 속도 제한과 일시적 서버 오류만 재시도한다. 나머지 4xx 는 다시 보내도 같은 결과다.
  // 429 뿐 아니라 403 도 사유가 속도 제한이면 재시도 대상이다 (구글은 둘 다로 보낸다).
  if ((res.status === 429 || res.status >= 500 || RETRYABLE.has(reason)) && attempt < 2) {
    // 서버가 "언제 다시 오라"고 알려주면 그 값을 우선한다
    const retryAfter = Number(res.headers.get('Retry-After'))
    const waitMs =
      Number.isFinite(retryAfter) && retryAfter > 0
        ? retryAfter * 1000
        : 2 ** attempt * 700 + Math.random() * 300
    await new Promise((r) => setTimeout(r, Math.min(waitMs, 8000)))
    return call(path, token, init, attempt + 1)
  }

  if (res.status === 401) throw new TokenInvalid()

  if (res.status === 410) {
    // 410 은 원인이 여러 갈래다. syncToken 만료일 때만 전체 동기화로 폴백해야 한다.
    if (!reason || reason === 'fullSyncRequired' || /sync token/i.test(message)) {
      throw new SyncTokenExpired()
    }
    throw new GoogleApiError(410, '대상이 이미 삭제되었습니다', '동기화를 한 번 더 눌러 상태를 맞춰주세요')
  }

  if (res.status === 403) {
    // 사용자가 할 수 있는 일이 사유마다 다르므로 구분해서 알려준다.
    const remedy =
      reason === 'insufficientPermissions'
        ? '읽기 전용으로 연결된 상태다. 쓰기 실습을 하려면 "읽기 + 쓰기"로 다시 연결해야 한다.'
        : RETRYABLE.has(reason)
          ? '요청 한도를 넘었다. 잠시 뒤 다시 시도해주세요.'
          : 'Google Calendar API 가 활성화돼 있는지, 동의 화면의 테스트 사용자에 이 계정이 있는지 확인해주세요.'
    throw new GoogleApiError(403, '권한이 없거나 한도를 넘었습니다' + (reason ? ` (${reason})` : ''), remedy)
  }

  if (res.status === 404) {
    throw new GoogleApiError(404, '대상을 찾을 수 없습니다', '이미 삭제된 일정일 수 있습니다')
  }

  if (res.status === 400) {
    // 증분 동기화에 금지된 파라미터를 함께 보내면 여기로 온다. 재시도 대상이 아니라 코드 버그다.
    throw new GoogleApiError(
      400,
      '잘못된 요청입니다' + (reason ? ` (${reason})` : ''),
      message || '요청 조건을 확인해주세요',
    )
  }

  throw new GoogleApiError(res.status, `구글 API 오류 (${res.status})`, message || '잠시 뒤 다시 시도해주세요')
}

export interface CalendarMeta {
  summary: string
  timeZone?: string
  /** owner / writer / reader … 읽기 전용 권한으로 붙었는지 확인용 */
  accessRole?: string
}

/**
 * 연결된 캘린더가 무엇인지 확인한다.
 *
 * calendars.get 을 쓰면 캘린더 자체를 읽는 더 넓은 권한(calendar.readonly)이 필요하다.
 * 우리는 일정 목록만 필요하므로, events.list 응답 최상단에 함께 오는 캘린더 정보를 쓴다.
 * 이렇게 하면 calendar.events.readonly 만으로 끝난다 — 최소 권한.
 */
export async function probeCalendar(token: string): Promise<CalendarMeta> {
  const params = new URLSearchParams({ maxResults: '1', singleEvents: 'true' })
  const res = await call('/calendars/primary/events?' + params.toString(), token)
  const json = (await res.json()) as { summary?: string; timeZone?: string; accessRole?: string }
  return {
    summary: json.summary ?? '기본 캘린더',
    timeZone: json.timeZone,
    accessRole: json.accessRole,
  }
}

export interface ListResult {
  events: NormalizedEvent[]
  nextSyncToken?: string
  /** 이번 호출이 전체 동기화였는지 증분이었는지 */
  mode: 'full' | 'incremental'
  /** 페이지 수 — 증분 동기화가 왜 싼지 눈으로 보여주기 위해 기록한다 */
  pages: number
  /** 페이지 상한에 걸려 중간에 멈췄는지. 이때는 syncToken 이 발급되지 않는다 */
  truncated: boolean
  meta?: CalendarMeta
  /** 이번 전체 동기화가 훑은 범위. 증분 동기화에서는 없다 */
  range?: { from: Date; to: Date }
}

interface ListOptions {
  /** 있으면 증분 동기화 */
  syncToken?: string
  /** 전체 동기화 범위 */
  from?: Date
  to?: Date
  /** 안전장치: 데모에서 수천 건을 끌어오지 않도록 */
  maxPages?: number
}

/**
 * 일정 목록을 가져온다.
 *
 * - syncToken 이 있으면 "지난번 이후 변경분만" 가져온다 (증분 동기화)
 * - syncToken 이 없으면 지정 범위 전체를 가져온다 (전체 동기화)
 * - syncToken 이 만료되면 구글이 410 을 준다 → SyncTokenExpired 로 올려서 호출부가 폴백하게 한다
 *
 * 주의: syncToken 을 쓸 때는 범위(timeMin/timeMax)나 정렬 같은 조건을 함께 보낼 수 없다.
 * 첫 동기화에 쓴 조건이 그 토큰에 이미 박혀 있기 때문이다.
 */
export async function listEvents(token: string, opts: ListOptions = {}): Promise<ListResult> {
  const maxPages = opts.maxPages ?? 5
  const from = opts.from ?? monthsFromNow(-1)
  const to = opts.to ?? monthsFromNow(2)
  const events: NormalizedEvent[] = []
  let pageToken: string | undefined
  let nextSyncToken: string | undefined
  let meta: CalendarMeta | undefined
  let pages = 0

  do {
    // singleEvents 는 증분 동기화에도 같은 값을 보내야 한다.
    // 문서: syncToken 과 함께 못 보내는 것은 timeMin/timeMax/orderBy/updatedMin/q 등이고,
    //      "그 외 파라미터는 최초 동기화와 동일해야 한다(다르면 동작이 정의되지 않음)".
    const params = new URLSearchParams({ maxResults: '250', singleEvents: 'true' })

    if (opts.syncToken) {
      params.set('syncToken', opts.syncToken)
      // syncToken 을 쓸 때는 삭제된 항목이 항상 함께 온다 (showDeleted 를 false 로 둘 수 없다).
      // 그래서 삭제 반영이 증분 동기화에서 자동으로 된다.
    } else {
      // 전체 동기화는 반드시 범위를 자른다. 안 자르면 평생 일정을 다 끌어온다.
      params.set('timeMin', from.toISOString())
      params.set('timeMax', to.toISOString())
      params.set('orderBy', 'startTime')
    }
    if (pageToken) params.set('pageToken', pageToken)

    const res = await call('/calendars/primary/events?' + params.toString(), token)
    const json = (await res.json()) as {
      items?: RawGoogleEvent[]
      nextPageToken?: string
      nextSyncToken?: string
      summary?: string
      timeZone?: string
      accessRole?: string
    }

    if (!meta) {
      meta = { summary: json.summary ?? '기본 캘린더', timeZone: json.timeZone, accessRole: json.accessRole }
    }

    for (const item of json.items ?? []) {
      const norm = normalize(item)
      if (norm) events.push(norm)
    }

    pageToken = json.nextPageToken
    // nextSyncToken 은 마지막 페이지에만 온다. 중간 페이지에는 nextPageToken 이 대신 온다.
    nextSyncToken = json.nextSyncToken ?? nextSyncToken
    pages++
  } while (pageToken && pages < maxPages)

  return {
    events,
    // 페이지를 다 못 읽었으면 커서를 저장하지 않는다. 반쪽 상태에 책갈피를 꽂으면
    // 다음 증분 동기화가 빠뜨린 구간을 영구히 놓친다.
    nextSyncToken: pageToken ? undefined : nextSyncToken,
    mode: opts.syncToken ? 'incremental' : 'full',
    pages,
    truncated: !!pageToken,
    meta,
    range: opts.syncToken ? undefined : { from, to },
  }
}

/** 우리 일정을 구글로 내보낸다 (쓰기 권한 필요) */
export async function insertEvent(
  token: string,
  e: { title: string; start: Date; end: Date; description?: string },
) {
  const res = await call('/calendars/primary/events', token, {
    method: 'POST',
    body: JSON.stringify({
      summary: e.title,
      description: e.description,
      start: { dateTime: e.start.toISOString() },
      end: { dateTime: e.end.toISOString() },
    }),
  })
  const json = (await res.json()) as RawGoogleEvent
  return { externalId: json.id, etag: json.etag }
}

/** 내보낸 일정을 지운다 (데모가 만든 일정을 정리하는 용도) */
export async function deleteEvent(token: string, externalId: string) {
  await call('/calendars/primary/events/' + encodeURIComponent(externalId), token, {
    method: 'DELETE',
  })
}

/** 구글의 일정 표현을 우리 모양으로 바꾼다. 종일 일정은 시각이 아니라 날짜다. */
function normalize(item: RawGoogleEvent): NormalizedEvent | null {
  if (!item.id) return null

  const cancelled = item.status === 'cancelled'
  const startRaw = item.start?.dateTime ?? item.start?.date
  const endRaw = item.end?.dateTime ?? item.end?.date

  // 삭제된 항목은 내용 없이 id 만 오는 경우가 있다. 그래도 "삭제됨" 정보는 살려야 한다.
  if (!startRaw || !endRaw) {
    return cancelled
      ? {
          externalId: item.id,
          etag: item.etag,
          title: item.summary ?? '(삭제된 일정)',
          start: new Date(0),
          end: new Date(0),
          allDay: false,
          cancelled: true,
        }
      : null
  }

  const allDay = !item.start?.dateTime
  return {
    externalId: item.id,
    etag: item.etag,
    title: item.summary?.trim() || '(제목 없음)',
    start: new Date(startRaw),
    end: new Date(endRaw),
    allDay,
    cancelled,
    updatedAt: item.updated ? new Date(item.updated) : undefined,
  }
}

function monthsFromNow(n: number) {
  const d = new Date()
  d.setMonth(d.getMonth() + n)
  return d
}
