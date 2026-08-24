import { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { CATEGORIES, initialEvents, initialHandover } from './data'
import type { DemoEvent, HandoverDoc, HandoverItem } from './data'

/** 외부 캘린더에서 가져온 일정 (구글 실연동 데모가 넘겨주는 모양) */
export interface ExternalEventInput {
  externalId: string
  etag?: string
  title: string
  start: Date
  end: Date
  allDay: boolean
  source: 'GOOGLE' | 'ICS'
}

interface Store {
  events: DemoEvent[]
  addEvent: (e: Omit<DemoEvent, 'id'>) => void
  updateEvent: (id: string, patch: Partial<DemoEvent>) => void
  deleteEvent: (id: string) => void
  undoDelete: () => void
  pendingUndo: DemoEvent | null
  reset: () => void

  handover: HandoverDoc
  acceptHandover: () => void
  setItemStatus: (id: string, status: HandoverItem['status'], reason?: string) => void
  addHandoverItem: (title: string, detail: string) => void
  finishHandover: () => void
  resetHandover: () => void

  /** 주간보고에서 사람이 직접 수정한 항목 (재생성 시 보존) */
  editedItems: Record<string, string>
  setEditedItem: (key: string, content: string) => void
  clearEdited: () => void

  /**
   * 외부 캘린더(구글 등)에서 가져온 일정을 우리 캘린더에 반영한다.
   * externalId 로 짝을 찾아 upsert 하므로, 같은 일정을 여러 번 가져와도 중복되지 않는다.
   * STEP 06 의 "같은 일정이 계속 늘어난다" 고질병을 막는 장치를 축약한 것.
   */
  mergeExternalEvents: (items: ExternalEventInput[]) => {
    created: number
    updated: number
    skipped: number
  }
  /** 원격에서 삭제된 일정을 우리 쪽에서도 제거한다 (유령 일정 방지) */
  removeExternalEvents: (externalIds: string[]) => number
  /**
   * 전체 동기화 결과와 우리 쪽 상태를 대조해, 결과에 없는 일정을 지운다.
   *
   * 전체 동기화는 "삭제됨"을 알려주지 않는다(취소된 항목은 응답에서 빠진다).
   * 그래서 전체 동기화만 반복하면 원격에서 지운 일정이 우리 쪽에 영원히 남는다.
   * 이 대조가 그 유령 일정을 걷어낸다. 동기화가 훑지 않은 기간의 일정은 건드리지 않는다.
   */
  pruneExternalEvents: (
    source: 'GOOGLE' | 'ICS',
    keepExternalIds: string[],
    range: { from: Date; to: Date },
  ) => number
  /** 연결 해제 시 외부에서 가져온 일정만 걷어낸다 */
  clearExternalEvents: (source: 'GOOGLE' | 'ICS') => number
  externalCount: (source: 'GOOGLE' | 'ICS') => number
}

const Ctx = createContext<Store | null>(null)

/** 외부에서 온 일정에 카테고리를 추정해 붙인다. 주간보고 집계가 카테고리 단위이기 때문. */
function guessCategoryId(title: string) {
  if (/회의|미팅|스크럼|리뷰|논의|면담|sync|standup/i.test(title)) return 'meet'
  if (/지원|문의|대응|점검|support/i.test(title)) return 'support'
  if (/교육|워크숍|세미나|학습|training/i.test(title)) return 'edu'
  if (/개발|구현|배포|디버깅|리팩터|설계|dev|deploy/i.test(title)) return 'dev'
  return 'etc'
}

export function DemoProvider({ children }: { children: ReactNode }) {
  const [events, setEvents] = useState<DemoEvent[]>(() => initialEvents())
  const [pendingUndo, setPendingUndo] = useState<DemoEvent | null>(null)
  const [handover, setHandover] = useState<HandoverDoc>(() => initialHandover())
  const [editedItems, setEditedItems] = useState<Record<string, string>>({})

  /**
   * 동기화 함수들은 "몇 건이 새로 생기고 몇 건이 갱신됐는지"를 즉시 돌려줘야 한다.
   * 그 계산을 setEvents(updater) 안에서 하면 두 가지가 깨진다.
   *   ① updater 는 나중에(렌더 중에) 실행되므로 호출한 쪽은 항상 0 을 받는다
   *   ② StrictMode 는 updater 를 두 번 실행하므로 카운트가 배로 튄다
   * 그래서 현재 목록을 ref 로 들고, 계산은 동기적으로 하고, 결과 배열을 그대로 넣는다.
   */
  const eventsRef = useRef(events)
  eventsRef.current = events

  const commit = useCallback((next: DemoEvent[]) => {
    eventsRef.current = next
    setEvents(next)
  }, [])

  const addEvent = useCallback(
    (e: Omit<DemoEvent, 'id'>) => {
      commit([...eventsRef.current, { ...e, id: 'new-' + Math.random().toString(36).slice(2, 9) }])
    },
    [commit],
  )

  const updateEvent = useCallback(
    (id: string, patch: Partial<DemoEvent>) => {
      commit(eventsRef.current.map((e) => (e.id === id ? { ...e, ...patch } : e)))
    },
    [commit],
  )

  const deleteEvent = useCallback(
    (id: string) => {
      const target = eventsRef.current.find((e) => e.id === id) ?? null
      setPendingUndo(target)
      commit(eventsRef.current.filter((e) => e.id !== id))
    },
    [commit],
  )

  const undoDelete = useCallback(() => {
    setPendingUndo((cur) => {
      if (cur) commit([...eventsRef.current, cur])
      return null
    })
  }, [commit])

  const reset = useCallback(() => {
    commit(initialEvents())
    setPendingUndo(null)
    setEditedItems({})
  }, [commit])

  const mergeExternalEvents = useCallback<Store['mergeExternalEvents']>(
    (items) => {
      const result = { created: 0, updated: 0, skipped: 0 }
      const prev = eventsRef.current

      // externalId → 우리 일정. 이 맵이 곧 "짝(link)" 이고 중복 생성을 막는 장치다.
      const byExternal = new Map(prev.filter((e) => e.externalId).map((e) => [e.externalId!, e]))
      const patched = new Map<string, DemoEvent>()
      const added: DemoEvent[] = []

      for (const item of items) {
        const mine = byExternal.get(item.externalId)

        if (!mine) {
          added.push({
            id: 'ext-' + item.externalId,
            title: item.title,
            start: item.start,
            end: item.end,
            allDay: item.allDay,
            categoryId: guessCategoryId(item.title),
            visibility: 'TEAM',
            source: item.source,
            externalId: item.externalId,
            etag: item.etag,
          })
          result.created++
          continue
        }

        // etag 가 같으면 내용이 안 바뀐 것 → 건너뛴다 (불필요한 갱신을 만들지 않는다)
        if (item.etag && mine.etag === item.etag) {
          result.skipped++
          continue
        }

        patched.set(mine.id, {
          ...mine,
          title: item.title,
          start: item.start,
          end: item.end,
          allDay: item.allDay,
          etag: item.etag,
        })
        result.updated++
      }

      if (result.created || result.updated) {
        commit([...prev.map((e) => patched.get(e.id) ?? e), ...added])
      }
      return result
    },
    [commit],
  )

  const removeExternalEvents = useCallback(
    (externalIds: string[]) => {
      const targets = new Set(externalIds)
      const prev = eventsRef.current
      const next = prev.filter((e) => !(e.externalId && targets.has(e.externalId)))
      if (next.length !== prev.length) commit(next)
      return prev.length - next.length
    },
    [commit],
  )

  const pruneExternalEvents = useCallback<Store['pruneExternalEvents']>(
    (source, keepExternalIds, range) => {
      const keep = new Set(keepExternalIds)
      const prev = eventsRef.current
      const next = prev.filter((e) => {
        if (e.source !== source || !e.externalId) return true
        // 이번 동기화가 훑은 기간 밖이면 판단 근거가 없으므로 남긴다
        if (e.start < range.from || e.start >= range.to) return true
        return keep.has(e.externalId)
      })
      if (next.length !== prev.length) commit(next)
      return prev.length - next.length
    },
    [commit],
  )

  const clearExternalEvents = useCallback(
    (source: 'GOOGLE' | 'ICS') => {
      const prev = eventsRef.current
      const next = prev.filter((e) => !(e.source === source && e.externalId))
      if (next.length !== prev.length) commit(next)
      return prev.length - next.length
    },
    [commit],
  )

  const externalCount = useCallback(
    (source: 'GOOGLE' | 'ICS') => events.filter((e) => e.source === source && !!e.externalId).length,
    [events],
  )

  const acceptHandover = useCallback(() => {
    setHandover((h) =>
      h.status !== 'REQUESTED'
        ? h
        : {
            ...h,
            status: 'ACCEPTED',
            items: h.items.map((i) => ({ ...i, acked: true })),
            log: [...h.log, { at: new Date(), action: 'handover.accept', actor: '김철수' }],
          },
    )
  }, [])

  const setItemStatus = useCallback((id: string, status: HandoverItem['status'], reason?: string) => {
    setHandover((h) => ({
      ...h,
      items: h.items.map((i) => (i.id === id ? { ...i, status, blockReason: reason } : i)),
      log: [
        ...h.log,
        {
          at: new Date(),
          action: 'item.status',
          actor: '김철수',
          detail:
            (h.items.find((i) => i.id === id)?.title ?? '') +
            ' → ' +
            status +
            (reason ? ' (' + reason + ')' : ''),
        },
      ],
    }))
  }, [])

  const addHandoverItem = useCallback((title: string, detail: string) => {
    setHandover((h) => ({
      ...h,
      items: [
        ...h.items,
        { id: 'hi-' + Math.random().toString(36).slice(2, 8), title, detail, status: 'TODO', acked: false },
      ],
      log: [...h.log, { at: new Date(), action: 'item.add', actor: '홍길동', detail: title }],
    }))
  }, [])

  const finishHandover = useCallback(() => {
    setHandover((h) =>
      h.status !== 'ACCEPTED'
        ? h
        : { ...h, status: 'DONE', log: [...h.log, { at: new Date(), action: 'handover.done', actor: '홍길동' }] },
    )
  }, [])

  const resetHandover = useCallback(() => setHandover(initialHandover()), [])

  const setEditedItem = useCallback((key: string, content: string) => {
    setEditedItems((prev) => ({ ...prev, [key]: content }))
  }, [])

  const clearEdited = useCallback(() => setEditedItems({}), [])

  const value = useMemo<Store>(
    () => ({
      events,
      addEvent,
      updateEvent,
      deleteEvent,
      undoDelete,
      pendingUndo,
      reset,
      handover,
      acceptHandover,
      setItemStatus,
      addHandoverItem,
      finishHandover,
      resetHandover,
      editedItems,
      setEditedItem,
      clearEdited,
      mergeExternalEvents,
      removeExternalEvents,
      pruneExternalEvents,
      clearExternalEvents,
      externalCount,
    }),
    [
      events, addEvent, updateEvent, deleteEvent, undoDelete, pendingUndo, reset,
      handover, acceptHandover, setItemStatus, addHandoverItem, finishHandover, resetHandover,
      editedItems, setEditedItem, clearEdited,
      mergeExternalEvents, removeExternalEvents, pruneExternalEvents, clearExternalEvents, externalCount,
    ],
  )

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useDemo() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('DemoProvider 안에서만 사용할 수 있습니다')
  return ctx
}

export { CATEGORIES }
