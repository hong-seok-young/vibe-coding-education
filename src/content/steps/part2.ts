import type { Step } from '../types'

export const part2: Step[] = [
  {
    id: '06',
    slug: 'google-calendar',
    part: 'PART 2 · 외부 캘린더 연동',
    title: '구글 캘린더 연동',
    tagline: 'OAuth 로그인 → 일정 읽기 → 내보내기 → 증분 동기화',
    duration: '90분',
    level: '심화',
    goals: [
      'OAuth 2.0이 "비밀번호를 주지 않고 권한만 빌려주는 방식"임을 이해한다',
      '전체 동기화와 증분 동기화(syncToken)의 차이를 안다',
      '중복 생성·무한 동기화·유령 일정이 왜 생기고 어떻게 막는지 이해한다',
    ],
    deliverables: [
      '구글 계정 연결 버튼과 연결 상태 화면',
      '구글 일정을 캘린더에 겹쳐 보기 (계정별 색상)',
      '우리 일정을 구글로 내보내기',
      '증분 동기화 + 삭제 반영',
    ],
    prompts: [
      {
        id: 'oauth-setup',
        label: '구글 OAuth 설정 안내 받기',
        when: '코드보다 먼저. 구글 클라우드 콘솔에서 해야 할 일을 정리한다.',
        body: `구글 캘린더 연동을 시작합니다. 먼저 코드가 아니라 준비 작업부터 안내해주세요.

알려줄 것:
1. Google Cloud Console 에서 해야 할 일을 순서대로 (클릭 경로 포함)
   - 프로젝트 생성, Calendar API 활성화, OAuth 동의 화면, 사용자 인증 정보(클라이언트 ID) 생성
2. 우리가 필요한 최소 권한(scope)은 정확히 무엇인가?
   - "읽기만"과 "읽기+쓰기" scope의 차이
   - 왜 최소 권한만 요청해야 하는가
3. 리디렉션 URI를 로컬(localhost)과 운영(도메인) 두 개 등록해야 하는 이유
4. OAuth 동의 화면의 "테스트 / 프로덕션" 상태 차이와, 사내 사용자만 쓸 때 주의점
5. 발급받은 클라이언트 ID/시크릿을 어디에 넣고, 절대 하지 말아야 할 것

각 항목마다 "왜 이게 필요한가"를 한 줄씩 붙여주세요. 아직 코드는 필요 없습니다.`,
        tips: [
          '구글 콘솔 UI는 자주 바뀐다. AI가 말한 메뉴 이름이 안 보이면 "지금 화면에 보이는 메뉴는 A, B, C 입니다"라고 알려주고 다시 물어본다.',
          'scope는 나중에 늘리기 어렵다(사용자가 다시 동의해야 함). 처음부터 필요한 범위를 정한다.',
        ],
      },
      {
        id: 'oauth-flow',
        label: 'OAuth 연결 흐름 구현',
        when: '클라이언트 ID/시크릿을 .env 에 넣은 다음.',
        body: `구글 계정 연결 기능을 구현해주세요.

## 화면
- /settings/calendars : 연결된 캘린더 계정 목록
  - "구글 캘린더 연결" 버튼
  - 계정별: 이메일, 색상 선택, 동기화 ON/OFF, 내보내기 허용 ON/OFF, 마지막 동기화 시각, 연결 해제

## 서버
1. GET /api/calendar/google/connect
   - 구글 동의 화면으로 리디렉션
   - CSRF 방지용 state 값 생성·검증 (세션 또는 서명된 쿠키에 저장)
   - access_type=offline, prompt=consent 를 왜 쓰는지 주석으로 설명
2. GET /api/calendar/google/callback
   - code를 토큰으로 교환
   - 사용자 이메일 조회 후 CalendarAccount 저장(upsert)
   - **토큰은 반드시 암호화해서 저장** (AES-256-GCM, 키는 TOKEN_ENC_KEY)
   - 성공/실패 모두 사용자에게 보이는 결과 화면으로 돌려보내기
3. 토큰 갱신 유틸
   - access_token 만료 시 refresh_token 으로 자동 재발급
   - refresh_token 이 무효화된 경우(사용자가 구글에서 권한 철회) 계정을 "재연결 필요" 상태로 표시

## 필수 조건
- 토큰 암호화/복호화 함수는 src/server/crypto.ts 로 분리
- 이 API들은 로그인한 사용자만 호출 가능
- 에러 메시지에 토큰이나 시크릿이 절대 로그로 남지 않게

파일별로 코드를 주고, 마지막에 "연결이 제대로 됐는지 확인하는 방법"을 알려주세요.`,
        tips: [
          '**토큰 암호화를 명시하지 않으면 AI는 평문으로 저장한다.** DB가 유출되면 그 즉시 모든 사용자의 구글 캘린더가 열린다.',
          '`state` 값 검증도 반드시 요청한다. 없으면 CSRF 공격으로 남의 계정을 내 앱에 연결시킬 수 있다.',
        ],
      },
      {
        id: 'sync',
        label: '동기화 구현 (읽기 · 내보내기 · 증분)',
        when: '계정 연결이 성공한 다음. 이 스텝의 핵심.',
        body: `이제 동기화를 구현합니다. PRD 기준: "우리 DB가 원본, 읽기는 가져오기 + 쓰기는 내보내기".

## A. 가져오기 (구글 → 우리)
- 최초 1회: 최근 3개월 ~ 향후 6개월 범위 전체 동기화
- 이후: syncToken 을 사용한 증분 동기화 (변경된 것만)
- syncToken 이 만료(410 Gone)되면 자동으로 전체 동기화로 폴백
- 가져온 일정은 Event(source=GOOGLE) + ExternalEventLink 로 저장
- 구글에서 삭제된 일정(status=cancelled)은 우리 쪽에서도 제거
- 이미 있는 일정은 ExternalEventLink 로 찾아 갱신 (중복 생성 금지)

## B. 내보내기 (우리 → 구글)
- writeEnabled=true 인 계정에만
- 우리 앱에서 만든 일정(source=LOCAL)을 구글에 생성하고 ExternalEventLink 저장
- 수정 시 구글 일정도 갱신, 삭제 시 구글에서도 삭제
- **무한 루프 방지**: 우리가 내보낸 변경이 다음 가져오기에서 "새 변경"으로 잡혀 되돌아오면 안 된다.
  lastSyncedHash 로 내용 지문을 비교해 우리가 만든 변경인지 판단하는 방법으로 구현해주세요

## C. 실행 방식
- 수동: 캘린더 화면의 "동기화" 버튼
- 자동: /api/cron/sync 엔드포인트 (나중에 Coolify 스케줄러가 호출).
  단순 시크릿 헤더로 보호
- 동시 실행 방지: 같은 계정에 대한 동기화가 겹치지 않게 잠금

## D. 결과 보고
- 동기화 결과를 로그로 남기고 화면에 표시: 가져옴 N / 갱신 N / 삭제 N / 실패 N
- 실패한 항목은 건너뛰고 계속 진행 (하나가 죽어서 전체가 멈추지 않게)

먼저 동기화 알고리즘을 의사코드로 보여주고, 그 다음 실제 코드를 주세요.
API 호출 실패, 토큰 만료, 요청 제한(rate limit) 각각의 처리도 포함해주세요.`,
        tips: [
          '이 프롬프트는 이 과정에서 가장 길고 어렵다. 한 번에 안 되면 A → B → C 순서로 잘라서 요청한다.',
          '"무한 루프 방지"를 안 적으면 실제로 무한 루프가 돈다. 우리가 쓰고 → 구글에서 변경 감지 → 우리가 또 쓰고…',
          '`410 Gone` 폴백 처리는 반드시 필요하다. syncToken은 정말로 만료된다.',
        ],
      },
    ],
    sample: [
      { type: 'h', text: 'OAuth 2.0 연결 흐름' },
      {
        type: 'flow',
        title: '사용자가 "구글 캘린더 연결"을 누르면',
        steps: [
          '우리 서버가 state 생성 후 구글 동의 화면으로 보냄',
          '사용자가 구글에서 로그인·동의',
          '구글이 우리 콜백 URL로 `code` 를 보냄',
          '서버가 code + 시크릿 → 토큰 교환',
          '토큰 암호화 후 DB 저장',
          '연결 완료 화면',
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: '여기서 중요한 사실',
        text: '우리 앱은 **사용자의 구글 비밀번호를 절대 보지 않는다.** 사용자는 구글 화면에서 로그인하고, 우리는 "이 앱이 캘린더를 볼 수 있다"는 증표(토큰)만 받는다. 그래서 사용자가 구글 설정에서 언제든 권한을 회수할 수 있다.',
      },
      { type: 'h', text: '필요한 권한(scope)' },
      {
        type: 'table',
        head: ['scope', '할 수 있는 것', '우리에게 필요한가'],
        rows: [
          ['`calendar.readonly`', '일정 읽기만', '읽기 전용 연동이면 이것만'],
          ['`calendar.events`', '일정 읽기 + 만들기/수정/삭제', '내보내기까지 하려면 필요'],
          ['`calendar`', '캘린더 자체 생성/삭제 포함 전체 권한', '**불필요. 요청하지 않는다**'],
          ['`userinfo.email`', '연결한 계정 이메일 확인', '어떤 계정을 연결했는지 표시용'],
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '최소 권한 원칙',
        text: '`calendar` 전체 권한을 요청하면 동의 화면에 "이 앱이 당신의 캘린더를 삭제할 수 있습니다"가 뜬다. 사내 사용자는 그 화면에서 멈춘다. 필요한 것만 요청하는 것은 보안 문제이기도 하고, **사용자가 실제로 동의를 눌러주느냐의 문제**이기도 하다.',
      },
      { type: 'h', text: '토큰 암호화' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/crypto.ts',
        code: `import { createCipheriv, createDecipheriv, randomBytes } from 'node:crypto'

/**
 * 외부 서비스 토큰을 DB에 저장하기 전에 암호화한다.
 * DB 백업 파일이나 덤프가 유출되더라도 토큰 자체는 쓸 수 없게 만드는 것이 목적.
 * 키(TOKEN_ENC_KEY)는 환경변수로만 주입하고, 저장소에 절대 넣지 않는다.
 */
const KEY = Buffer.from(process.env.TOKEN_ENC_KEY!, 'base64') // 32 bytes

export function encryptToken(plain: string): string {
  const iv = randomBytes(12)                        // GCM 권장 12바이트, 매번 새로 생성
  const cipher = createCipheriv('aes-256-gcm', KEY, iv)
  const enc = Buffer.concat([cipher.update(plain, 'utf8'), cipher.final()])
  const tag = cipher.getAuthTag()                   // 위조 여부 검증용
  // iv.tag.ciphertext 를 한 문자열로 합쳐 보관
  return [iv.toString('base64'), tag.toString('base64'), enc.toString('base64')].join('.')
}

export function decryptToken(stored: string): string {
  const [iv, tag, data] = stored.split('.')
  const decipher = createDecipheriv('aes-256-gcm', KEY, Buffer.from(iv, 'base64'))
  decipher.setAuthTag(Buffer.from(tag, 'base64'))
  return Buffer.concat([
    decipher.update(Buffer.from(data, 'base64')),
    decipher.final(),
  ]).toString('utf8')
}`,
      },
      { type: 'h', text: '동기화 알고리즘 (의사코드)' },
      {
        type: 'code',
        lang: 'text',
        filename: '가져오기 동기화',
        code: `syncAccount(account):
  잠금 획득(account.id)  # 같은 계정 동시 동기화 방지, 실패하면 즉시 종료
  try:
    token = 유효한 access_token 확보 (만료면 refresh)

    if account.syncToken 있음:
      pageToken = null
      loop:
        res = GET /calendars/primary/events?syncToken=...&pageToken=...
        if 410 Gone:                      # syncToken 만료
          account.syncToken = null
          전체 동기화로 다시 시작
        각 item 처리
        pageToken = res.nextPageToken
        until pageToken 없음
      account.syncToken = res.nextSyncToken
    else:
      # 전체 동기화: 범위를 반드시 제한한다 (평생 일정을 다 가져오면 안 된다)
      res = GET events?timeMin=3개월전&timeMax=6개월후&singleEvents=true
      각 item 처리
      account.syncToken = res.nextSyncToken

    account.lastSyncedAt = now
  finally:
    잠금 해제


각 item 처리(item):
  link = ExternalEventLink 조회(accountId, item.id)

  if item.status == 'cancelled':          # 구글에서 삭제됨
    if link: 우리 Event 삭제 + link 삭제
    return

  if link 없음:                            # 새 일정
    event = Event 생성(source=GOOGLE, 내용 = item)
    ExternalEventLink 생성(externalId=item.id, etag=item.etag)
    return '가져옴'

  if link.externalEtag == item.etag:      # 내용 변화 없음
    return '건너뜀'

  if hash(item 내용) == link.lastSyncedHash:
    # ★ 무한 루프 차단: 이 변경은 우리가 방금 내보낸 것이 되돌아온 것
    link.externalEtag = item.etag
    return '건너뜀'

  Event 갱신(내용 = item)
  link.externalEtag = item.etag
  return '갱신'`,
      },
      { type: 'h', text: '실제 구현 (핵심 부분)' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/providers/google.ts',
        code: `import { createHash } from 'node:crypto'
import { db } from '@/server/db'
import { decryptToken, encryptToken } from '@/server/crypto'

const API = 'https://www.googleapis.com/calendar/v3'

/** 일정 내용의 지문. 우리가 내보낸 변경이 되돌아온 것인지 판별하는 데 쓴다. */
export function contentHash(e: { title: string; startAt: Date; endAt: Date; description?: string | null }) {
  return createHash('sha256')
    .update([e.title, e.startAt.toISOString(), e.endAt.toISOString(), e.description ?? ''].join('|'))
    .digest('hex')
    .slice(0, 32)
}

/** access_token 이 만료됐으면 refresh_token 으로 갱신한다. */
async function getAccessToken(accountId: string): Promise<string> {
  const acc = await db.calendarAccount.findUniqueOrThrow({ where: { id: accountId } })

  if (acc.expiresAt && acc.expiresAt.getTime() > Date.now() + 60_000) {
    return decryptToken(acc.accessToken)
  }
  if (!acc.refreshToken) throw new ReconnectRequired(accountId)

  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: process.env.GOOGLE_CLIENT_ID!,
      client_secret: process.env.GOOGLE_CLIENT_SECRET!,
      refresh_token: decryptToken(acc.refreshToken),
      grant_type: 'refresh_token',
    }),
  })

  if (!res.ok) {
    // 사용자가 구글에서 권한을 철회한 경우가 대표적. 재연결을 요청해야 한다.
    await db.calendarAccount.update({
      where: { id: accountId },
      data: { syncEnabled: false },
    })
    throw new ReconnectRequired(accountId)
  }

  const json = (await res.json()) as { access_token: string; expires_in: number }
  await db.calendarAccount.update({
    where: { id: accountId },
    data: {
      accessToken: encryptToken(json.access_token),
      expiresAt: new Date(Date.now() + json.expires_in * 1000),
    },
  })
  return json.access_token
}

export class ReconnectRequired extends Error {
  constructor(public accountId: string) {
    super('구글 계정 재연결이 필요합니다')
  }
}

/** 요청 제한(429)과 일시적 서버 오류(5xx)에만 재시도한다. 4xx는 재시도해도 소용없다. */
async function callGoogle(path: string, token: string, init: RequestInit = {}, attempt = 0): Promise<Response> {
  const res = await fetch(API + path, {
    ...init,
    headers: { ...init.headers, Authorization: 'Bearer ' + token },
  })

  if ((res.status === 429 || res.status >= 500) && attempt < 4) {
    const waitMs = 2 ** attempt * 1000 + Math.random() * 500  // 지수 백오프 + 흔들기
    await new Promise((r) => setTimeout(r, waitMs))
    return callGoogle(path, token, init, attempt + 1)
  }
  return res
}`,
      },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/sync/importGoogle.ts',
        code: `export async function importFromGoogle(accountId: string) {
  const stats = { created: 0, updated: 0, deleted: 0, skipped: 0, failed: 0 }
  const acc = await db.calendarAccount.findUniqueOrThrow({ where: { id: accountId } })
  const token = await getAccessToken(accountId)

  let pageToken: string | undefined
  let syncToken = acc.syncToken ?? undefined
  let nextSyncToken: string | undefined

  do {
    const params = new URLSearchParams({ maxResults: '250', singleEvents: 'true' })
    if (syncToken) {
      params.set('syncToken', syncToken)
    } else {
      // 전체 동기화는 반드시 범위를 자른다. 안 자르면 10년치를 끌어온다.
      params.set('timeMin', monthsAgo(3).toISOString())
      params.set('timeMax', monthsAhead(6).toISOString())
    }
    if (pageToken) params.set('pageToken', pageToken)

    const res = await callGoogle('/calendars/primary/events?' + params, token)

    if (res.status === 410) {
      // syncToken 만료 — 증분 동기화 불가. 커서를 버리고 전체 동기화로 다시 시작한다.
      await db.calendarAccount.update({ where: { id: accountId }, data: { syncToken: null } })
      syncToken = undefined
      pageToken = undefined
      continue
    }
    if (!res.ok) throw new Error('구글 API 오류: ' + res.status)

    const page = await res.json()
    for (const item of page.items ?? []) {
      try {
        await applyGoogleItem(acc, item, stats)
      } catch {
        stats.failed++       // 한 건이 실패해도 전체를 멈추지 않는다
      }
    }
    pageToken = page.nextPageToken
    nextSyncToken = page.nextSyncToken ?? nextSyncToken
  } while (pageToken)

  await db.calendarAccount.update({
    where: { id: accountId },
    data: { syncToken: nextSyncToken, lastSyncedAt: new Date() },
  })
  return stats
}`,
      },
      {
        type: 'callout',
        tone: 'tip',
        title: '동기화 결과를 사용자에게 보여줘야 하는 이유',
        text: '"가져옴 12 / 갱신 3 / 삭제 1 / 실패 0" 같은 숫자를 화면에 표시하면, 문제가 생겼을 때 사용자가 먼저 알아차린다. 조용히 실패하는 동기화는 몇 주 뒤 "주간보고에 일정이 하나도 안 잡혀요"라는 문의로 돌아온다.',
      },
    ],
    explain: [
      { type: 'h', text: 'OAuth 2.0을 한 문장으로' },
      {
        type: 'p',
        text: '**"비밀번호를 넘겨주지 않고, 특정 권한만 한시적으로 빌려주는 표준."** 호텔에서 마스터키가 아니라 내 방만 열리는 카드키를 받는 것과 같다. 카드키는 분실 신고로 무효화할 수 있고, 유효기간이 있고, 어느 방을 열 수 있는지가 정해져 있다.',
      },
      {
        type: 'table',
        head: ['용어', '정체', '수명'],
        rows: [
          ['`code` (인가 코드)', '"동의했다"는 일회용 증표. URL로 전달됨', '수 분, 1회용'],
          ['`access_token`', '실제 API를 호출하는 열쇠', '보통 1시간'],
          ['`refresh_token`', 'access_token을 재발급받는 열쇠. **가장 민감하다**', '철회하지 않으면 계속'],
          ['`state`', '요청이 우리 앱에서 시작됐음을 증명하는 난수', '해당 흐름 동안만'],
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'refresh_token 은 사실상 영구 비밀번호다',
        text: '이게 유출되면 공격자는 언제든 새 access_token을 발급받아 캘린더를 읽는다. 그래서 ① 암호화 저장 ② 로그에 절대 남기지 않기 ③ 서버에서만 다루기(브라우저로 절대 보내지 않기) 세 가지가 필수다. AI에게 요청할 때 명시하지 않으면 이 중 아무것도 안 지켜진다.',
      },
      { type: 'h', text: '전체 동기화 vs 증분 동기화' },
      {
        type: 'table',
        head: ['', '전체 동기화', '증분 동기화 (syncToken)'],
        rows: [
          ['가져오는 것', '지정 범위의 모든 일정', '지난번 이후 변경된 것만'],
          ['호출량', '일정 1000개 → 4~5회 페이지 호출', '변경 없으면 1회, 결과 0건'],
          ['언제', '최초 연결, syncToken 만료 시', '평상시 (5~15분마다)'],
          ['위험', '요청 제한에 걸리기 쉬움', '토큰 만료(410) 처리를 잊으면 조용히 멈춤'],
        ],
      },
      {
        type: 'p',
        text: '증분 동기화는 "지난번에 어디까지 봤다"는 책갈피(`syncToken`)를 저장하는 방식이다. 이 책갈피는 구글이 발급하고, 오래 안 쓰거나 서버 사정에 따라 무효가 된다. 그때 `410 Gone` 이 오는데, **이 처리를 빼놓으면 동기화가 영구히 멈춘 채로 아무 에러도 안 보인다.**',
      },
      { type: 'h', text: '동기화의 3대 고질병' },
      {
        type: 'table',
        head: ['증상', '원인', '해법'],
        rows: [
          [
            '**같은 일정이 계속 늘어난다**',
            '외부 일정 ID를 저장하지 않아 매번 새 일정으로 인식',
            '`ExternalEventLink` 에 `@@unique([accountId, externalId])` — DB가 중복을 막는다',
          ],
          [
            '**무한 동기화 (핑퐁)**',
            '우리가 내보낸 변경 → 구글이 "변경됨"으로 리포트 → 우리가 또 갱신 → …',
            '내용 지문(`lastSyncedHash`) 비교. 우리가 만든 변경이면 건너뛴다',
          ],
          [
            '**유령 일정**',
            '구글에서 지운 일정이 우리 DB에 남아 주간보고에 계속 등장',
            '`status=cancelled` 항목을 반드시 처리. 증분 동기화는 삭제도 알려준다',
          ],
        ],
      },
      { type: 'h', text: '"실시간"이 필요하면: Webhook (push notification)' },
      {
        type: 'flow',
        title: '폴링 대신 구글이 알려주게 하기',
        steps: [
          '우리가 `watch` 등록 (콜백 URL + 채널 ID)',
          '구글에서 일정 변경 발생',
          '구글이 우리 콜백 URL로 POST',
          '우리는 해당 계정만 증분 동기화',
        ],
      },
      {
        type: 'p',
        text: '이 방식은 즉시성이 좋고 호출량이 적지만, 대가가 있다. ① 콜백 URL이 **공개 인터넷에서 접근 가능**해야 한다(사내망 전용 서버면 불가). ② 채널은 만료되므로 주기적으로 갱신해야 한다. ③ 알림은 "뭔가 바뀌었다"만 알려주므로 결국 증분 동기화 코드가 있어야 한다. **그래서 MVP는 폴링(5~15분)으로 시작하고, 필요해지면 webhook을 얹는 게 맞다.**',
      },
      {
        type: 'callout',
        tone: 'dx',
        text: '사내 방화벽 안에서 외부 API 호출, 콜백 URL 공개, OAuth 앱 심사(사내 도메인 제한) 같은 부분은 인프라 정책과 얽힙니다. 이 구간은 dX팀과 함께 진행하는 것을 권합니다.',
      },
    ],
    checklist: [
      '구글 계정을 연결하고 /settings/calendars 에 이메일이 표시된다',
      '구글 일정이 캘린더에 겹쳐 보이고 계정 색상이 구분된다',
      '동기화 버튼을 누르면 결과 숫자(가져옴/갱신/삭제)가 보인다',
      '두 번 연속 동기화해도 일정이 중복되지 않는다',
      '구글에서 일정을 지우고 동기화하면 우리 앱에서도 사라진다',
      '우리 앱에서 만든 일정이 구글에 나타난다 (내보내기 허용 시)',
      'DB의 accessToken 컬럼이 암호화된 문자열이다 (평문 아님)',
    ],
    dxNote: 'OAuth 클라이언트 발급과 사내 도메인 제한, 콜백 URL 공개 여부는 dX팀·인프라 협의가 필요합니다.',
    demo: {
      kind: 'integrations',
      hint: '연동이 끝나면 이런 화면이 된다. 계정별 색상, 마지막 동기화 시각, "가져옴/갱신/삭제/실패" 결과 숫자, 토큰이 무효화된 계정의 "재연결 필요" 상태 — 동기화가 조용히 실패하지 않게 만드는 장치들이다.',
    },
  },

  {
    id: '07',
    slug: 'multi-provider',
    part: 'PART 2 · 외부 캘린더 연동',
    title: '네이버 등 다른 캘린더 추가',
    tagline: '한 번 잘 만든 구조에 프로바이더를 끼워 넣기',
    duration: '60분',
    level: '심화',
    goals: [
      '"연동 하나 더 추가"가 쉬워지는 구조(인터페이스 분리)를 이해한다',
      'OAuth · CalDAV · ICS 세 가지 연동 방식의 차이와 한계를 안다',
      '연동을 늘릴 때 늘어나는 진짜 비용이 무엇인지 판단할 수 있다',
    ],
    deliverables: [
      'CalendarProvider 인터페이스와 구글 구현체 리팩터링',
      '네이버(CalDAV) 연동 또는 ICS 구독 연동',
      '"캘린더 추가" 화면에서 종류를 선택하는 UI',
    ],
    prompts: [
      {
        id: 'abstract',
        label: '프로바이더 인터페이스로 리팩터링',
        when: '구글 연동이 동작하는 상태에서. 새 연동을 붙이기 전에 구조를 먼저 정리한다.',
        body: `지금 구글 캘린더 연동 코드가 동작합니다. 이제 다른 캘린더(네이버, Outlook, ICS)를
추가할 수 있는 구조로 리팩터링해주세요.

## 요구사항
1. CalendarProvider 인터페이스 정의 (src/server/providers/types.ts)
   필요한 동작만 최소로:
   - 연결 시작 / 연결 완료 처리
   - 일정 목록 가져오기 (범위 또는 커서 기반)
   - 일정 만들기 / 수정하기 / 삭제하기 (지원하지 않는 프로바이더도 있음 — 이걸 어떻게 표현할지 고민해주세요)
   - 연결 상태 확인
2. 각 프로바이더의 "능력(capability)"을 데이터로 표현
   - 예: { canRead: true, canWrite: false, incrementalSync: true, authKind: 'oauth' | 'caldav' | 'url' }
   - 화면은 이 능력 정보를 보고 버튼을 켜고 끈다 (하드코딩된 if (provider === 'google') 금지)
3. 기존 구글 코드를 이 인터페이스 구현체로 이동 (동작은 그대로)
4. 동기화 엔진(sync)은 프로바이더 종류를 모르고 인터페이스만 호출하게

## 확인
리팩터링 후에도 구글 연동이 그대로 동작하는지 확인하는 방법을 알려주세요.
그리고 "새 프로바이더를 추가하려면 어떤 파일 몇 개를 만들면 되는지" 한 문단으로 정리해주세요.`,
        tips: [
          '**연동을 두 개 붙이기 전에 구조를 잡는 게 핵심이다.** 구글 코드에 if문으로 네이버를 끼워 넣으면 세 번째 연동에서 무너진다.',
          '"지원하지 않는 동작"의 표현 방식을 AI에게 고민하게 하는 것이 이 프롬프트의 포인트다. (예외 던지기 vs capability 플래그)',
        ],
      },
      {
        id: 'naver',
        label: '네이버 캘린더 연동 조사 + 구현',
        when: '인터페이스 리팩터링이 끝난 다음.',
        body: `네이버 캘린더 연동을 추가하려고 합니다. 먼저 조사부터 해주세요.

## 1단계: 조사 (코드 없이)
- 네이버 캘린더에 외부 앱이 접근하는 방법이 현재 어떤 것들이 있는가?
  (네이버 오픈API, CalDAV, iCal(ICS) 내보내기 URL 등)
- 각 방법에 대해: 인증 방식 / 읽기 가능 여부 / 쓰기 가능 여부 / 증분 동기화 가능 여부 / 제약
- **확실하지 않은 부분은 "확인 필요"라고 명시해주세요. 추측을 사실처럼 쓰지 마세요.**
- 공식 문서에서 확인해야 할 항목 체크리스트를 만들어주세요

## 2단계: 안전한 대안 설계
만약 네이버 쓰기 API가 제한적이라면, 우리 앱에서는 이렇게 하고 싶습니다:
- 네이버는 **읽기 전용**으로 연동 (일정을 가져와서 겹쳐 보기만)
- 사용자에게 "이 캘린더는 읽기 전용입니다" 를 UI에 명확히 표시
- 내보내기가 필요하면 구글만 사용

이 정책을 capability 로 표현하고, 화면에서 어떻게 보여줄지 설계해주세요.

## 3단계: 범용 폴백 — ICS 구독
어떤 캘린더든 대응할 수 있는 최후의 수단으로 ICS(iCalendar) URL 구독을 구현해주세요.
- 사용자가 캘린더의 "공개 ICS URL"을 붙여넣으면 주기적으로 읽어와 표시
- ICS 파싱 (VEVENT, DTSTART/DTEND, 타임존, 종일 일정, 반복 규칙은 우선 무시)
- 읽기 전용, 증분 동기화 없음 (매번 전체를 읽고 비교)
- 실패 시(URL 접근 불가, 형식 오류) 사용자에게 원인 표시`,
        tips: [
          '**"확실하지 않으면 확인 필요라고 하라"는 지시는 매우 중요하다.** 외부 API 스펙은 AI가 가장 자주 틀리는 영역이다(문서가 자주 바뀌고, 학습 시점 이후 변경분을 모른다).',
          'AI가 알려준 API 엔드포인트는 **반드시 공식 문서에서 직접 확인한다.** 존재하지 않는 URL을 자신 있게 알려주는 경우가 흔하다.',
          'ICS 구독은 "일단 보이게는 만들 수 있는" 만능 폴백이다. 네이버·아웃룩·사내 그룹웨어 모두 대개 ICS를 지원한다.',
        ],
      },
    ],
    sample: [
      { type: 'h', text: '프로바이더 인터페이스' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/providers/types.ts',
        code: `export type ProviderKind = 'google' | 'naver' | 'outlook' | 'ics'

/**
 * 프로바이더가 "무엇을 할 수 있는지"를 데이터로 표현한다.
 * 화면과 동기화 엔진은 이 값만 보고 동작을 결정한다.
 * (if (provider === 'google') 같은 분기를 코드 전체에 뿌리지 않기 위한 장치)
 */
export interface ProviderCapability {
  kind: ProviderKind
  label: string
  authKind: 'oauth' | 'caldav' | 'url'
  canRead: boolean
  canWrite: boolean          // 우리 일정을 내보낼 수 있는가
  incrementalSync: boolean   // 변경분만 가져올 수 있는가
  supportsDelete: boolean
  notes?: string             // UI에 그대로 보여줄 제약 설명
}

export interface ExternalEvent {
  externalId: string
  etag?: string
  title: string
  description?: string
  startAt: Date
  endAt: Date
  allDay: boolean
  cancelled: boolean         // 원격에서 삭제된 항목
}

export interface FetchResult {
  events: ExternalEvent[]
  nextCursor?: string        // 증분 동기화 커서 (없으면 전체 동기화 방식)
  cursorExpired?: boolean    // 커서가 만료되어 전체 동기화가 필요함
}

export interface CalendarProvider {
  capability: ProviderCapability

  /** 연결 시작 — OAuth면 동의 URL, CalDAV/ICS면 입력 폼 스펙을 돌려준다 */
  beginConnect(userId: string): Promise<{ redirectUrl?: string; formFields?: string[] }>
  completeConnect(userId: string, payload: Record<string, string>): Promise<{ accountId: string }>

  fetchEvents(accountId: string, opts: { cursor?: string; from?: Date; to?: Date }): Promise<FetchResult>

  /** 쓰기를 지원하지 않는 프로바이더는 이 메서드를 구현하지 않는다.
   *  호출부는 capability.canWrite 로 먼저 확인한다. */
  createEvent?(accountId: string, e: Omit<ExternalEvent, 'externalId' | 'cancelled'>): Promise<{ externalId: string; etag?: string }>
  updateEvent?(accountId: string, externalId: string, e: Partial<ExternalEvent>): Promise<{ etag?: string }>
  deleteEvent?(accountId: string, externalId: string): Promise<void>
}`,
      },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/providers/index.ts',
        code: `import { googleProvider } from './google'
import { naverProvider } from './naver'
import { icsProvider } from './ics'
import type { CalendarProvider, ProviderKind } from './types'

/** 프로바이더 등록소. 새 연동을 추가하면 이 맵에 한 줄만 늘어난다. */
const registry: Record<ProviderKind, CalendarProvider | undefined> = {
  google: googleProvider,
  naver: naverProvider,
  ics: icsProvider,
  outlook: undefined,   // 아직 미구현
}

export function getProvider(kind: ProviderKind): CalendarProvider {
  const p = registry[kind]
  if (!p) throw new Error('지원하지 않는 캘린더입니다: ' + kind)
  return p
}

/** "캘린더 추가" 화면은 이 목록만 보고 그려진다 */
export const availableProviders = Object.values(registry)
  .filter((p): p is CalendarProvider => !!p)
  .map((p) => p.capability)`,
      },
      { type: 'h', text: '프로바이더별 능력 비교' },
      {
        type: 'table',
        head: ['프로바이더', '인증', '읽기', '쓰기', '증분', 'UI에 표시할 안내'],
        rows: [
          ['구글 캘린더', 'OAuth 2.0', '✅', '✅', '✅ syncToken', '양방향 연동'],
          ['네이버 캘린더', 'CalDAV 또는 오픈API', '✅', '△ 제한적', '❌', '**읽기 전용으로 연동됩니다**'],
          ['Outlook / M365', 'OAuth 2.0 (Graph)', '✅', '✅', '✅ delta', '양방향 연동 (미구현)'],
          ['ICS URL 구독', 'URL만', '✅', '❌', '❌', '읽기 전용 · 갱신이 최대 1시간 늦을 수 있음'],
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '외부 API 스펙은 반드시 직접 확인한다',
        text: '위 표의 네이버 항목처럼 **"△ 제한적"** 으로 표시된 부분은 실제 연동 전에 공식 문서로 확인해야 한다. AI는 외부 서비스의 API 스펙을 자신 있게 틀리게 말하는 경우가 많다(학습 시점 이후 변경, 유사 서비스와 혼동). 존재하지 않는 엔드포인트를 알려주는 일도 흔하다. **"이 정보의 출처 문서 링크를 알려주세요"** 라고 되묻고, 그 링크를 직접 열어 확인하는 습관이 필요하다.',
      },
      { type: 'h', text: 'ICS 구독 — 만능 폴백' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/providers/ics.ts (발췌)',
        code: `/**
 * ICS(iCalendar) 는 캘린더 데이터의 표준 텍스트 형식이다.
 * 거의 모든 캘린더 서비스가 "공개 URL로 내보내기"를 지원하므로,
 * 정식 API 연동이 막힌 서비스에 대한 최후의 수단이 된다.
 *
 * 한계(사용자에게 반드시 알려야 함):
 *  - 읽기 전용
 *  - 변경이 즉시 반영되지 않는다 (서비스가 캐시를 두는 경우 수십 분 지연)
 *  - URL을 아는 사람은 누구나 일정을 볼 수 있다 → 사내 일정 공유 시 주의
 */
export const icsProvider: CalendarProvider = {
  capability: {
    kind: 'ics',
    label: 'ICS URL 구독',
    authKind: 'url',
    canRead: true,
    canWrite: false,
    incrementalSync: false,
    supportsDelete: false,
    notes: '읽기 전용입니다. 변경 반영이 최대 1시간 늦을 수 있습니다.',
  },

  async beginConnect() {
    return { formFields: ['icsUrl', 'displayName'] }
  },

  async completeConnect(userId, payload) {
    const url = new URL(payload.icsUrl)          // 형식 검증
    if (!['http:', 'https:'].includes(url.protocol)) throw new Error('http(s) URL만 지원합니다')
    // SSRF 방지: 사내망/로컬 주소로 향하는 URL을 차단한다
    assertPublicHost(url.hostname)

    const account = await db.calendarAccount.create({
      data: { userId, provider: 'ICS', accountEmail: url.href, displayName: payload.displayName },
    })
    return { accountId: account.id }
  },

  async fetchEvents(accountId) {
    const acc = await db.calendarAccount.findUniqueOrThrow({ where: { id: accountId } })
    const res = await fetch(acc.accountEmail, { signal: AbortSignal.timeout(15_000) })
    if (!res.ok) throw new Error('ICS를 읽을 수 없습니다 (' + res.status + ')')

    const text = await res.text()
    if (text.length > 5_000_000) throw new Error('ICS 파일이 너무 큽니다')

    return { events: parseIcs(text) }   // 증분 없음 → 매번 전체 비교
  },
}`,
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'SSRF — 사용자가 URL을 입력하는 기능의 함정',
        text: '사용자가 아무 URL이나 넣을 수 있다면, `http://192.168.0.1/admin` 이나 클라우드 메타데이터 주소(`169.254.169.254`)를 넣어 **우리 서버가 대신 사내망을 긁게** 만들 수 있다. 이것이 SSRF다. "사용자가 입력한 URL로 서버가 요청을 보낸다"는 기능을 만들 때는 반드시 사설 IP 대역 차단과 리디렉션 추적 제한을 요청해야 한다. AI는 이 검증을 먼저 넣어주지 않는다.',
      },
    ],
    explain: [
      { type: 'h', text: '연동 하나 추가의 진짜 비용' },
      {
        type: 'p',
        text: '"네이버도 추가해주세요"는 한 문장이지만, 실제로 늘어나는 일은 이렇다.',
      },
      {
        type: 'table',
        head: ['늘어나는 것', '설명'],
        rows: [
          ['인증 방식', 'OAuth/CalDAV/URL마다 연결 흐름과 토큰 저장 방식이 다르다'],
          ['데이터 모양 변환', '각 서비스의 일정 형식 → 우리 Event 로 매핑 (종일 일정·타임존 표현이 서비스마다 다름)'],
          ['능력 차이 대응', '쓰기가 안 되는 서비스는 UI에서 버튼을 숨기고 안내해야 한다'],
          ['오류 처리', '요청 제한, 인증 만료, 서비스 장애를 각각 다르게 처리'],
          ['**테스트 계정**', '연동마다 실제 테스트 계정이 필요하다. 실무에서 이게 제일 오래 걸린다'],
          ['**운영 부담**', '서비스가 API를 바꾸면 우리 코드가 조용히 깨진다. 연동 수 = 유지보수 항목 수'],
        ],
      },
      {
        type: 'callout',
        tone: 'tip',
        title: '그래서 실무 판단은',
        text: '연동은 **필요한 것부터 하나씩** 붙인다. "일단 다 되게" 만들면 모두 얕게 깨진다. 대신 이 스텝에서 만든 **인터페이스와 ICS 폴백**이 있으면, 정식 연동이 없는 서비스도 "보이게는" 만들 수 있다. 실무에서 이 조합이 가장 현실적이다.',
      },
      { type: 'h', text: '왜 인터페이스를 먼저 분리했나' },
      {
        type: 'flow',
        title: '분리하지 않은 경우',
        steps: [
          '구글 코드에 네이버 if문 추가',
          'ICS 때문에 또 분기',
          '동기화 엔진에도 분기',
          'UI에도 분기',
          '한 곳을 고치면 다른 곳이 깨진다',
        ],
      },
      {
        type: 'flow',
        title: '분리한 경우',
        steps: [
          '새 파일 1개 (프로바이더 구현체)',
          '등록소에 한 줄 추가',
          '동기화 엔진·UI는 수정 없음',
        ],
      },
      {
        type: 'p',
        text: '이것이 AI 코딩에서 특히 중요한 이유가 있다. AI는 **눈앞의 요청을 가장 짧은 코드로 해결**하려 한다. "네이버 추가해줘"라고 하면 기존 구글 함수에 if문을 넣는다. 당장은 동작하고, 세 번째 연동에서 무너진다. **구조를 잡는 것은 사람이 지시해야 한다.**',
      },
      { type: 'h', text: 'CalDAV 라는 것' },
      {
        type: 'p',
        text: 'CalDAV는 캘린더를 주고받는 오래된 표준 프로토콜(HTTP 확장)이다. 애플·네이버·많은 그룹웨어가 지원한다. 장점은 표준이라 한 번 구현하면 여러 서비스에 통한다는 것. 단점은 ① OAuth가 아니라 **아이디/비밀번호(또는 앱 비밀번호)를 우리가 보관**해야 하는 경우가 많고 ② XML 기반이라 다루기 번거롭고 ③ 서비스마다 구현 차이가 있어 "표준인데 안 되는" 일이 흔하다.',
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '아이디/비밀번호를 받는 연동의 무게',
        text: 'OAuth는 토큰만 받지만 CalDAV는 계정 비밀번호를 받는 경우가 있다. 이건 **사고 시 피해 범위가 완전히 다르다** — 캘린더만이 아니라 그 계정 전체가 열린다. 가능하면 앱 전용 비밀번호를 쓰게 하고, 그것도 암호화 저장하고, 사내 정책상 허용되는지 먼저 확인해야 한다. 이 판단은 개발 문제가 아니라 보안 정책 문제다.',
      },
      {
        type: 'callout',
        tone: 'dx',
        text: '연동 대상 선정, 사내 그룹웨어 연동, 계정 정보 보관 정책은 dX팀·정보보안 검토가 필요합니다. "어떤 캘린더를 연동할지"만 정해서 요청하시면 됩니다.',
      },
    ],
    checklist: [
      'CalendarProvider 인터페이스로 리팩터링한 뒤에도 구글 연동이 그대로 동작한다',
      '"캘린더 추가" 화면이 registry 목록으로 자동 생성된다 (하드코딩 아님)',
      '읽기 전용 프로바이더는 내보내기 버튼이 비활성화되고 이유가 표시된다',
      'ICS URL 구독으로 외부 캘린더 하나를 가져왔다',
      'ICS URL 입력에 사설 IP 차단(SSRF 방어)이 들어가 있다',
      '새 프로바이더를 추가할 때 손대야 하는 파일이 몇 개인지 말할 수 있다',
    ],
    demo: {
      kind: 'integrations',
      hint: '읽기 전용 캘린더는 내보내기 토글이 잠기고 이유가 표시된다. 화면이 프로바이더의 능력(capability) 값만 보고 그려지기 때문이다. 동기화 버튼을 눌러 결과 숫자가 어떻게 표시되는지도 보라.',
    },
  },
]
