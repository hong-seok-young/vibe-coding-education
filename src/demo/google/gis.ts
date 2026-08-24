/**
 * 구글 로그인·권한 요청 (브라우저 전용 흐름)
 *
 * 이 앱은 서버가 없는 정적 사이트다. 그래서 STEP 06 이 가르치는 정식 흐름
 * (서버가 클라이언트 시크릿으로 code 를 토큰으로 교환하고 refresh_token 을 암호화 저장)을
 * 그대로 쓸 수 없다. 대신 구글이 자바스크립트 앱을 위해 제공하는 토큰 흐름을 쓴다.
 *
 * 두 방식의 차이는 그대로 교육 소재다.
 *
 *   서버 흐름 (실제 앱)          | 브라우저 흐름 (이 데모)
 *   ---------------------------- | ----------------------------
 *   클라이언트 시크릿 사용       | 시크릿 없음 (클라이언트 ID만)
 *   refresh_token 받음           | refresh_token 없음
 *   서버가 백그라운드 동기화     | 사용자가 화면을 열고 있을 때만
 *   토큰을 서버에 암호화 저장    | 메모리에만 두고 새로고침하면 사라짐
 *
 * 그래서 이 데모로는 "연결 → 동기화 → 내보내기" 를 실제로 해볼 수 있지만,
 * 자동 주기 동기화는 원리상 불가능하다. 그 사실 자체를 화면에 밝혀둔다.
 */
import { loadScript } from '../../lib/loadScript'

export const GIS_SCRIPT = 'https://accounts.google.com/gsi/client'

/**
 * 일정 목록 읽기만. `calendar.readonly` 보다 좁다.
 * (calendar.readonly 는 캘린더 자체 정보까지 읽을 수 있어서, 목록만 필요한 우리에게는 과하다)
 * 최소 권한 원칙 — STEP 06 이 가르치는 규칙을 이 데모 자신에게도 적용한 것.
 */
export const SCOPE_READONLY = 'https://www.googleapis.com/auth/calendar.events.readonly'
/** 일정 만들기/수정/삭제까지. 내보내기 실습에만 필요하다 */
export const SCOPE_EVENTS = 'https://www.googleapis.com/auth/calendar.events'

export interface GrantedToken {
  accessToken: string
  /** 만료 시각 (ms). 브라우저 흐름의 토큰은 수명이 짧다. */
  expiresAt: number
  scope: string
  canWrite: boolean
}

interface TokenResponse {
  access_token?: string
  expires_in?: number
  scope?: string
  error?: string
  error_description?: string
}

interface TokenClient {
  requestAccessToken: (overrides?: { prompt?: string; hint?: string }) => void
}

interface GoogleOAuth2 {
  initTokenClient: (config: {
    client_id: string
    scope: string
    prompt?: string
    callback: (res: TokenResponse) => void
    error_callback?: (err: { type?: string; message?: string }) => void
  }) => TokenClient
  revoke: (token: string, done?: (res: { successful?: boolean }) => void) => void
  hasGrantedAllScopes?: (res: TokenResponse, ...scopes: string[]) => boolean
}

declare global {
  interface Window {
    google?: { accounts?: { oauth2?: GoogleOAuth2 } }
  }
}

export class GoogleAuthError extends Error {
  constructor(
    message: string,
    /** 사용자가 창을 닫은 것인지(정상 취소) 실제 오류인지 구분 */
    public cancelled = false,
  ) {
    super(message)
  }
}

async function oauth2(): Promise<GoogleOAuth2> {
  await loadScript(GIS_SCRIPT)
  const api = window.google?.accounts?.oauth2
  if (!api) throw new GoogleAuthError('구글 로그인 스크립트를 초기화할 수 없습니다')
  return api
}

/**
 * 권한을 요청한다. 사용자가 구글 화면에서 로그인·동의하면 액세스 토큰이 돌아온다.
 * 우리 앱은 사용자의 구글 비밀번호를 보지 않는다 — 이것이 OAuth 의 요점이다.
 */
export async function requestToken(
  clientId: string,
  wantWrite: boolean,
  /** 이미 동의한 사용자의 토큰을 다시 받는 경우. 계정 선택 화면을 건너뛴다 */
  renew = false,
): Promise<GrantedToken> {
  const api = await oauth2()
  const scope = wantWrite ? `${SCOPE_READONLY} ${SCOPE_EVENTS}` : SCOPE_READONLY

  return new Promise<GrantedToken>((resolve, reject) => {
    const client = api.initTokenClient({
      client_id: clientId,
      scope,
      // 값을 주지 않으면 라이브러리가 select_account 를 강제한다.
      // 재발급은 빈 문자열로 두어 불필요한 계정 선택을 건너뛴다.
      ...(renew ? { prompt: '' } : {}),
      callback: (res) => {
        if (res.error) {
          reject(
            new GoogleAuthError(
              describeAuthError(res.error, res.error_description),
              res.error === 'access_denied',
            ),
          )
          return
        }
        if (!res.access_token) {
          reject(new GoogleAuthError('토큰을 받지 못했습니다'))
          return
        }

        const granted = res.scope ?? scope

        // 사용자는 동의 화면에서 권한을 하나씩 체크 해제할 수 있다(세분화 동의).
        // 그래서 "요청했으니 받았을 것"이라고 가정하지 않고, 구글이 알려주는 실제 허용 범위로 판단한다.
        const canWrite =
          api.hasGrantedAllScopes?.(res, SCOPE_EVENTS) ?? granted.split(' ').includes(SCOPE_EVENTS)

        resolve({
          accessToken: res.access_token,
          // 토큰 수명은 구글이 정한다. 1시간으로 못 박지 않고 응답값을 쓴다.
          expiresAt: Date.now() + (res.expires_in ?? 3600) * 1000,
          scope: granted,
          canWrite,
        })
      },
      // error_callback 을 지정하지 않으면 라이브러리가 "팝업이 닫혔다"를 감지하는 타이머 자체를
      // 시작하지 않는다. 즉 사용자가 창을 닫아도 아무 일도 일어나지 않는 화면이 된다.
      error_callback: (err) => {
        const cancelled = err.type === 'popup_closed' || err.type === 'popup_failed_to_open'
        reject(
          new GoogleAuthError(
            cancelled
              ? '구글 창이 닫혔습니다. 팝업 차단을 해제하고 다시 시도해주세요.'
              : (err.message ?? '구글 인증에 실패했습니다'),
            cancelled,
          ),
        )
      },
    })

    client.requestAccessToken()
  })
}

/** 권한 회수. 사용자가 구글 계정 설정에서 하는 것과 같은 일을 우리 화면에서 해준다. */
export async function revokeToken(accessToken: string): Promise<boolean> {
  const api = await oauth2()
  return new Promise<boolean>((resolve) =>
    api.revoke(accessToken, (res) => resolve(res?.successful !== false)),
  )
}

function describeAuthError(error: string, description?: string) {
  switch (error) {
    case 'access_denied':
      return '동의를 취소했습니다. 캘린더를 읽으려면 권한이 필요합니다.'
    case 'idpiframe_initialization_failed':
      return '브라우저가 구글 인증 프레임을 차단했습니다. 서드파티 쿠키 차단 설정을 확인해주세요.'
    case 'invalid_client':
      return '클라이언트 ID가 올바르지 않습니다. 구글 클라우드 콘솔의 값과 대조해주세요.'
    default:
      return description ? `${error}: ${description}` : `구글 인증 오류 (${error})`
  }
}
