import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { CATEGORIES, initialEvents, initialHandover } from './data'
import type { DemoEvent, HandoverDoc, HandoverItem } from './data'

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
}

const Ctx = createContext<Store | null>(null)

export function DemoProvider({ children }: { children: ReactNode }) {
  const [events, setEvents] = useState<DemoEvent[]>(() => initialEvents())
  const [pendingUndo, setPendingUndo] = useState<DemoEvent | null>(null)
  const [handover, setHandover] = useState<HandoverDoc>(() => initialHandover())
  const [editedItems, setEditedItems] = useState<Record<string, string>>({})

  const addEvent = useCallback((e: Omit<DemoEvent, 'id'>) => {
    setEvents((prev) => [...prev, { ...e, id: 'new-' + Math.random().toString(36).slice(2, 9) }])
  }, [])

  const updateEvent = useCallback((id: string, patch: Partial<DemoEvent>) => {
    setEvents((prev) => prev.map((e) => (e.id === id ? { ...e, ...patch } : e)))
  }, [])

  const deleteEvent = useCallback((id: string) => {
    setEvents((prev) => {
      const target = prev.find((e) => e.id === id) ?? null
      setPendingUndo(target)
      return prev.filter((e) => e.id !== id)
    })
  }, [])

  const undoDelete = useCallback(() => {
    setPendingUndo((cur) => {
      if (cur) setEvents((prev) => [...prev, cur])
      return null
    })
  }, [])

  const reset = useCallback(() => {
    setEvents(initialEvents())
    setPendingUndo(null)
    setEditedItems({})
  }, [])

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
          detail: (h.items.find((i) => i.id === id)?.title ?? '') + ' → ' + status + (reason ? ' (' + reason + ')' : ''),
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
    }),
    [
      events, addEvent, updateEvent, deleteEvent, undoDelete, pendingUndo, reset,
      handover, acceptHandover, setItemStatus, addHandoverItem, finishHandover, resetHandover,
      editedItems, setEditedItem, clearEdited,
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
