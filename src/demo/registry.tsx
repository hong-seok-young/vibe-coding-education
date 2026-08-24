import type { ReactNode } from 'react'
import type { DemoKind } from '../content/types'
import { CalendarDemo } from './CalendarDemo'
import { HandoverDemo } from './HandoverDemo'
import { IntegrationsDemo } from './IntegrationsDemo'
import { PresentDemo } from './PresentDemo'
import { WeeklyDemo } from './WeeklyDemo'

interface DemoMeta {
  title: string
  /** 조작 방법 — 데모 위에 얇게 붙는다 */
  controls?: string
  render: () => ReactNode
}

export const DEMOS: Record<DemoKind, DemoMeta> = {
  calendar: {
    title: '업무 캘린더',
    controls: '단축키 · ← → 이동 · T 오늘 · M/W 월·주 전환 · 날짜 클릭으로 일정 추가 · 일정 드래그로 날짜 이동',
    render: () => <CalendarDemo />,
  },
  weekly: {
    title: '주간보고',
    controls: '항목을 클릭하면 수정된다. 캘린더 데모에서 만든 일정이 이 화면에 그대로 집계된다.',
    render: () => <WeeklyDemo />,
  },
  present: {
    title: '주간회의 발표 모드',
    controls: '→ / Space 다음 사람 · ← 이전 · F 전체화면 · 항목 클릭으로 발표 중 강조',
    render: () => <PresentDemo />,
  },
  handover: {
    title: '인수인계',
    controls: '"지금 보는 사람"을 바꾸면 인계자·인수자 권한 차이를 확인할 수 있다.',
    render: () => <HandoverDemo />,
  },
  integrations: {
    title: '캘린더 연동 설정',
    controls: '동기화 버튼과 토글을 눌러보라. 읽기 전용 캘린더는 내보내기가 잠긴다.',
    render: () => <IntegrationsDemo />,
  },
}

export const DEMO_KINDS = Object.keys(DEMOS) as DemoKind[]
