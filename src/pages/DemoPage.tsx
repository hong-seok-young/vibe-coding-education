import { Link, NavLink, useParams } from 'react-router-dom'
import { CalendarDemo } from '../demo/CalendarDemo'
import { HandoverDemo } from '../demo/HandoverDemo'
import { IntegrationsDemo } from '../demo/IntegrationsDemo'
import { PresentDemo } from '../demo/PresentDemo'
import { WeeklyDemo } from '../demo/WeeklyDemo'

const TABS = [
  { key: 'calendar', label: '캘린더', step: '04–05', stepSlug: 'calendar-ui' },
  { key: 'weekly', label: '주간보고', step: '08', stepSlug: 'weekly-report' },
  { key: 'present', label: '발표 모드', step: '09', stepSlug: 'present-mode' },
  { key: 'handover', label: '인수인계', step: '10', stepSlug: 'handover' },
  { key: 'integrations', label: '캘린더 연동', step: '06–07', stepSlug: 'google-calendar' },
] as const

const NOTE: Record<string, string> = {
  calendar:
    '날짜를 클릭해 "14시 팀 회의"처럼 입력해 보라. 일정을 드래그해 다른 날로 옮기고, 클릭해서 카테고리·공개범위를 바꿀 수 있다. 단축키 ← → · T(오늘) · M/W(월·주 전환).',
  weekly:
    '캘린더 데모에서 만든 일정이 그대로 집계된다. 항목을 클릭해 수정하면 "수정됨"으로 표시되고, 재생성해도 그 내용은 유지된다.',
  present:
    '주간회의에서 한 명이 화면을 띄우는 화면이다. → / Space 로 사람을 넘기고, F로 전체화면. 첫 번째 슬라이드는 캘린더 데모 데이터로 만들어진다.',
  handover:
    '인계자와 인수자 시점을 전환해가며 같은 인수인계를 볼 수 있다. 확인은 인수자만, 복귀 확인은 인계자만 가능하다.',
  integrations:
    '프로바이더의 능력(읽기/쓰기/증분)에 따라 화면이 달라진다. 읽기 전용 캘린더는 내보내기 토글이 잠긴다.',
}

export function DemoPage() {
  const { section = 'calendar' } = useParams()
  const active = TABS.find((t) => t.key === section) ?? TABS[0]

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="border-hair surface border-b px-4 pt-3">
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <span className="bg-brand-500/15 text-brand-500 rounded px-2 py-0.5 text-[10.5px] font-semibold">
            완성 결과물 데모
          </span>
          <span className="text-muted text-[11.5px]">
            15단계를 끝내면 만들어지는 화면들. 실제로 동작하니 직접 만져볼 수 있다.
          </span>
          <Link
            to={`/steps/${active.stepSlug}`}
            className="text-brand-500 ml-auto text-[12px] hover:underline"
          >
            STEP {active.step} 설명 보기 →
          </Link>
        </div>

        <div className="scrollbar-none -mb-px flex gap-1 overflow-x-auto">
          {TABS.map((t) => (
            <NavLink
              key={t.key}
              to={`/demo/${t.key}`}
              className={({ isActive }) =>
                'shrink-0 border-b-2 px-3 py-2 text-[13px] font-medium transition ' +
                (isActive
                  ? 'border-brand-500 text-brand-500'
                  : 'text-muted hover:text-brand-500 border-transparent')
              }
            >
              {t.label}
              <span className="text-muted ml-1.5 font-mono text-[9.5px]">{t.step}</span>
            </NavLink>
          ))}
        </div>
      </div>

      <p className="text-muted border-hair surface-2 border-b px-4 py-2 text-[12px] leading-6">
        {NOTE[active.key]}
      </p>

      {active.key === 'calendar' && <CalendarDemo />}
      {active.key === 'weekly' && <WeeklyDemo />}
      {active.key === 'present' && <PresentDemo />}
      {active.key === 'handover' && <HandoverDemo />}
      {active.key === 'integrations' && <IntegrationsDemo />}
    </div>
  )
}
