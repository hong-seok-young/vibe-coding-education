import { useCallback, useEffect, useMemo, useState } from 'react'
import { ScriptBlocked } from '../../lib/loadScript'
import { useDemo } from '../store'
import {
  GoogleApiError,
  SyncTokenExpired,
  TokenInvalid,
  deleteEvent,
  insertEvent,
  listEvents,
  probeCalendar,
} from './calendar'
import { GoogleAuthError, revokeToken, requestToken } from './gis'
import type { GrantedToken } from './gis'

const KEY_CLIENT_ID = 'vibe-edu:google-client-id'
const KEY_SYNC_TOKEN = 'vibe-edu:google-sync-token'
const KEY_CREATED = 'vibe-edu:google-created-ids'

export interface SyncLog {
  at: Date
  mode: 'full' | 'incremental'
  /** 구글이 돌려준 변경 항목 수 */
  fetched: number
  created: number
  updated: number
  skipped: number
  deleted: number
  pages: number
  ms: number
  note?: string
}

export type Phase = 'need-client-id' | 'disconnected' | 'connecting' | 'connected'

const read = (k: string) => {
  try {
    return localStorage.getItem(k)
  } catch {
    return null
  }
}
const write = (k: string, v: string | null) => {
  try {
    v === null ? localStorage.removeItem(k) : localStorage.setItem(k, v)
  } catch {
    /* 프라이빗 모드 등 — 저장 실패는 기능을 막지 않는다 */
  }
}

/**
 * 실제 구글 캘린더에 붙어서 동기화를 시연하는 상태 훅.
 *
 * 액세스 토큰은 메모리에만 둔다. localStorage 에 저장하지 않는다 —
 * 브라우저 저장소에 남은 토큰은 다른 스크립트가 읽어갈 수 있고,
 * 이 데모는 "토큰을 어떻게 다뤄야 하는가"도 같이 가르치는 화면이기 때문이다.
 * 그래서 새로고침하면 다시 연결해야 한다. 그 불편이 곧 서버가 필요한 이유다.
 */
export function useGoogleLive() {
  const { mergeExternalEvents, removeExternalEvents, pruneExternalEvents, clearExternalEvents, externalCount } =
    useDemo()

  const envClientId = (import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined) ?? ''
  const [clientId, setClientIdState] = useState(() => read(KEY_CLIENT_ID) ?? envClientId)
  const [token, setToken] = useState<GrantedToken | null>(null)
  const [account, setAccount] = useState<{ summary: string; timeZone?: string; accessRole?: string } | null>(
    null,
  )
  const [syncToken, setSyncTokenState] = useState<string | null>(() => read(KEY_SYNC_TOKEN))
  const [createdIds, setCreatedIds] = useState<string[]>(() => {
    try {
      return JSON.parse(read(KEY_CREATED) ?? '[]') as string[]
    } catch {
      return []
    }
  })
  const [busy, setBusy] = useState<string | null>(null)
  const [error, setError] = useState<{ message: string; remedy?: string } | null>(null)
  const [scriptBlocked, setScriptBlocked] = useState(false)
  const [log, setLog] = useState<SyncLog[]>([])
  const [now, setNow] = useState(() => Date.now())

  // 토큰 남은 시간을 화면에 보여주기 위해 1초마다 갱신 (짧은 수명이 이 흐름의 특징이다)
  useEffect(() => {
    if (!token) return
    const t = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(t)
  }, [token])

  const expired = !!token && token.expiresAt <= now
  const phase: Phase = !clientId.trim()
    ? 'need-client-id'
    : busy === 'connect'
      ? 'connecting'
      : token && !expired
        ? 'connected'
        : 'disconnected'

  const setClientId = useCallback((v: string) => {
    setClientIdState(v)
    write(KEY_CLIENT_ID, v.trim() || null)
    setError(null)
  }, [])

  const setSyncToken = useCallback((v: string | null) => {
    setSyncTokenState(v)
    write(KEY_SYNC_TOKEN, v)
  }, [])

  const rememberCreated = useCallback((ids: string[]) => {
    setCreatedIds(ids)
    write(KEY_CREATED, JSON.stringify(ids))
  }, [])

  const fail = useCallback((e: unknown) => {
    if (e instanceof ScriptBlocked) {
      setScriptBlocked(true)
      setError({
        message: '구글 인증 스크립트를 불러올 수 없는 환경입니다',
        remedy: '이 화면은 외부 스크립트를 허용하는 환경에서만 실제 연동을 시연할 수 있습니다.',
      })
      return
    }
    if (e instanceof GoogleAuthError) {
      setError({ message: e.message })
      return
    }
    if (e instanceof GoogleApiError) {
      setError({ message: e.message, remedy: e.remedy })
      return
    }
    setError({ message: e instanceof Error ? e.message : '알 수 없는 오류' })
  }, [])

  const connect = useCallback(
    async (wantWrite: boolean) => {
      setBusy('connect')
      setError(null)
      try {
        // 이미 한 번 연결했던 사용자라면(토큰 만료 후 재연결) 계정 선택 화면을 건너뛴다
        const granted = await requestToken(clientId.trim(), wantWrite, account !== null)
        setToken(granted)
        setAccount(await probeCalendar(granted.accessToken))
      } catch (e) {
        fail(e)
        setToken(null)
      } finally {
        setBusy(null)
      }
    },
    [clientId, account, fail],
  )

  const disconnect = useCallback(async () => {
    setBusy('disconnect')
    try {
      if (token) await revokeToken(token.accessToken).catch(() => undefined)
    } finally {
      setToken(null)
      setAccount(null)
      setSyncToken(null)
      const removed = clearExternalEvents('GOOGLE')
      setLog((l) => [
        {
          at: new Date(),
          mode: 'full',
          fetched: 0,
          created: 0,
          updated: 0,
          skipped: 0,
          deleted: removed,
          pages: 0,
          ms: 0,
          note: '연결 해제 — 권한을 회수하고 가져온 일정을 정리했다',
        },
        ...l,
      ])
      setBusy(null)
    }
  }, [token, clearExternalEvents, setSyncToken])

  /** 동기화 1회. syncToken 이 있으면 증분, 없으면 전체. 410 이면 전체로 폴백한다. */
  const sync = useCallback(
    async (opts: { forceFull?: boolean } = {}) => {
      if (!token) return
      setBusy('sync')
      setError(null)
      const started = Date.now()

      const useToken = opts.forceFull ? undefined : (syncToken ?? undefined)
      let note: string | undefined

      try {
        let result
        try {
          result = await listEvents(token.accessToken, { syncToken: useToken })
        } catch (e) {
          if (e instanceof SyncTokenExpired) {
            // 이 폴백이 없으면 동기화가 조용히 영구 정지한다 (STEP 06 의 함정).
            // 문서가 요구하는 대로 커서를 버리고 전체 동기화로 다시 시작한다.
            // 아래 전체 동기화의 대조(prune)가 그 사이 원격에서 지워진 일정을 정리해준다.
            note = 'syncToken 이 만료되어 전체 동기화로 다시 시작했다'
            setSyncToken(null)
            result = await listEvents(token.accessToken, {})
          } else {
            throw e
          }
        }

        const cancelled = result.events.filter((e) => e.cancelled)
        const alive = result.events.filter((e) => !e.cancelled)

        const merged = mergeExternalEvents(
          alive.map((e) => ({
            externalId: e.externalId,
            etag: e.etag,
            title: e.title,
            start: e.start,
            end: e.end,
            allDay: e.allDay,
            source: 'GOOGLE' as const,
          })),
        )
        let deleted = removeExternalEvents(cancelled.map((e) => e.externalId))

        // 전체 동기화는 "삭제됨"을 알려주지 않는다. 취소된 일정은 아예 응답에서 빠진다.
        // 그래서 결과에 없는 일정을 우리 쪽에서 걷어내야 한다 — 이게 없으면 유령 일정이 남는다.
        // (증분 동기화는 삭제 항목을 직접 보내주므로 이 대조가 필요 없다)
        if (result.mode === 'full' && result.range && !result.truncated) {
          deleted += pruneExternalEvents('GOOGLE', alive.map((e) => e.externalId), result.range)
        }

        if (result.nextSyncToken) setSyncToken(result.nextSyncToken)
        if (result.truncated) {
          note =
            (note ? note + ' / ' : '') +
            '페이지 상한에 걸려 일부만 가져왔다 — 이럴 때는 syncToken 을 저장하지 않는다(빠뜨린 구간을 영구히 놓치게 되므로)'
        }

        setLog((l) => [
          {
            at: new Date(),
            mode: result.mode,
            fetched: result.events.length,
            created: merged.created,
            updated: merged.updated,
            skipped: merged.skipped,
            deleted,
            pages: result.pages,
            ms: Date.now() - started,
            note,
          },
          ...l,
        ])
      } catch (e) {
        if (e instanceof TokenInvalid) setToken(null)
        fail(e)
      } finally {
        setBusy(null)
      }
    },
    [token, syncToken, mergeExternalEvents, removeExternalEvents, pruneExternalEvents, setSyncToken, fail],
  )

  /** 내보내기 테스트 — 구글 캘린더에 실제 일정을 하나 만든다 */
  const exportTest = useCallback(async () => {
    if (!token?.canWrite) return
    setBusy('export')
    setError(null)
    try {
      const start = new Date()
      start.setMinutes(0, 0, 0)
      start.setHours(start.getHours() + 2)
      const end = new Date(start.getTime() + 60 * 60 * 1000)

      const { externalId } = await insertEvent(token.accessToken, {
        title: '[교육 데모] 내보내기 테스트',
        start,
        end,
        description:
          '바이브 코딩 교육 프로그램의 STEP 06 데모가 만든 일정입니다. 화면의 "만든 일정 정리" 버튼으로 지울 수 있습니다.',
      })

      if (externalId) rememberCreated([...createdIds, externalId])
      setLog((l) => [
        {
          at: new Date(),
          mode: 'incremental',
          fetched: 0,
          created: 1,
          updated: 0,
          skipped: 0,
          deleted: 0,
          pages: 0,
          ms: 0,
          note: '구글 캘린더에 일정을 만들었다 — 이제 동기화를 눌러보면 그 일정이 되돌아온다',
        },
        ...l,
      ])
    } catch (e) {
      if (e instanceof TokenInvalid) setToken(null)
      fail(e)
    } finally {
      setBusy(null)
    }
  }, [token, createdIds, rememberCreated, fail])

  /** 데모가 만든 일정을 모두 지운다. 남의 실제 캘린더를 어지럽히지 않기 위한 정리 버튼. */
  const cleanupCreated = useCallback(async () => {
    if (!token?.canWrite || createdIds.length === 0) return
    setBusy('cleanup')
    setError(null)
    const remaining: string[] = []
    let removed = 0

    for (const id of createdIds) {
      try {
        await deleteEvent(token.accessToken, id)
        removed++
      } catch (e) {
        // 이미 지워진 것(404)은 성공으로 본다. 그 외는 남겨두고 다시 시도할 수 있게 한다.
        if (e instanceof GoogleApiError && e.status === 404) removed++
        else remaining.push(id)
      }
    }

    rememberCreated(remaining)
    removeExternalEvents(createdIds)
    setLog((l) => [
      {
        at: new Date(),
        mode: 'incremental',
        fetched: 0,
        created: 0,
        updated: 0,
        skipped: 0,
        deleted: removed,
        pages: 0,
        ms: 0,
        note:
          remaining.length > 0
            ? `정리 완료 ${removed}건, 실패 ${remaining.length}건`
            : '데모가 만든 일정을 모두 정리했다',
      },
      ...l,
    ])
    setBusy(null)
  }, [token, createdIds, rememberCreated, removeExternalEvents])

  const secondsLeft = token ? Math.max(0, Math.floor((token.expiresAt - now) / 1000)) : 0

  return useMemo(
    () => ({
      phase,
      clientId,
      setClientId,
      clientIdFromEnv: !!envClientId && clientId === envClientId,
      account,
      canWrite: !!token?.canWrite,
      secondsLeft,
      expired,
      syncToken,
      googleEventCount: externalCount('GOOGLE'),
      createdCount: createdIds.length,
      busy,
      error,
      scriptBlocked,
      log,
      connect,
      disconnect,
      sync,
      exportTest,
      cleanupCreated,
      resetSyncToken: () => setSyncToken(null),
    }),
    [
      phase, clientId, setClientId, envClientId, account, token, secondsLeft, expired, syncToken,
      externalCount, createdIds.length, busy, error, scriptBlocked, log,
      connect, disconnect, sync, exportTest, cleanupCreated, setSyncToken,
    ],
  )
}
