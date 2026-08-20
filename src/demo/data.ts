import { addDays, startOfWeek } from '../lib/dates'

export interface Category {
  id: string
  name: string
  color: string
}

export const CATEGORIES: Category[] = [
  { id: 'dev', name: '개발', color: '#4a6ff0' },
  { id: 'meet', name: '회의', color: '#e0793a' },
  { id: 'support', name: '지원', color: '#2fa37a' },
  { id: 'edu', name: '교육', color: '#8b5cf6' },
  { id: 'etc', name: '기타', color: '#78839a' },
]

export const categoryOf = (id: string) => CATEGORIES.find((c) => c.id === id) ?? CATEGORIES[4]

export interface DemoEvent {
  id: string
  title: string
  start: Date
  end: Date
  allDay: boolean
  categoryId: string
  visibility: 'TEAM' | 'PRIVATE'
  source: 'LOCAL' | 'GOOGLE' | 'ICS'
  note?: string
}

export interface DemoUser {
  id: string
  name: string
  dept: string
  role: '팀원' | '팀장'
}

export const USERS: DemoUser[] = [
  { id: 'u1', name: '홍길동', dept: 'dX팀', role: '팀원' },
  { id: 'u2', name: '김철수', dept: 'dX팀', role: '팀원' },
  { id: 'u3', name: '이영희', dept: 'dX팀', role: '팀원' },
  { id: 'u4', name: '박민수', dept: 'dX팀', role: '팀원' },
  { id: 'u5', name: '최지현', dept: 'dX팀', role: '팀장' },
]

export const ME = USERS[0]

/** [요일 오프셋, 시작시각, 소요(분), 제목, 카테고리, 출처, 비공개?] */
type Seed = [number, number, number, string, string, ('LOCAL' | 'GOOGLE' | 'ICS')?, boolean?]

const THIS_WEEK: Seed[] = [
  [0, 9.5, 30, '주간 스크럼', 'meet'],
  [0, 10, 180, '캘린더 월 뷰 구현', 'dev'],
  [0, 14, 120, '캘린더 주 뷰 겹침 레이아웃', 'dev'],
  [0, 16.5, 60, 'dX팀 정기회의', 'meet', 'GOOGLE'],
  [1, 9.5, 30, '주간 스크럼', 'meet'],
  [1, 10, 150, '일정 CRUD 서버 액션', 'dev'],
  [1, 13.5, 90, '캘린더 연동 정책 논의', 'meet'],
  [1, 15.5, 90, '타 팀 데이터 추출 지원', 'support'],
  [2, 9.5, 30, '주간 스크럼', 'meet'],
  [2, 10, 120, '구글 OAuth 토큰 암호화', 'dev'],
  [2, 13, 60, '치과', 'etc', 'LOCAL', true],
  [2, 14.5, 120, '증분 동기화 구현', 'dev'],
  [3, 9.5, 30, '주간 스크럼', 'meet'],
  [3, 10, 120, '동기화 무한루프 디버깅', 'dev'],
  [3, 13.5, 120, '캘린더 연동 정책 논의', 'meet'],
  [3, 16, 60, '사용자 문의 대응', 'support'],
  [4, 9.5, 30, '주간 스크럼', 'meet'],
  [4, 10, 120, '주간보고 집계 로직', 'dev'],
  [4, 13, 120, '사내 보안 교육', 'edu', 'ICS'],
  [4, 15.5, 90, '타 팀 데이터 추출 지원', 'support'],
]

const NEXT_WEEK: Seed[] = [
  [0, 9.5, 30, '주간 스크럼', 'meet'],
  [0, 10, 180, '주간보고 팀 보드 구현', 'dev'],
  [1, 9.5, 30, '주간 스크럼', 'meet'],
  [1, 10, 180, '주간보고 팀 보드 구현', 'dev'],
  [1, 14, 120, '분기 계획 리뷰', 'meet'],
  [2, 9.5, 30, '주간 스크럼', 'meet'],
  [2, 10, 240, '인수인계 화면 착수', 'dev'],
  [3, 9.5, 30, '주간 스크럼', 'meet'],
  [3, 10, 180, '인수인계 화면 착수', 'dev'],
  [3, 14, 90, 'A 고객 정기 점검', 'support'],
  [4, 9.5, 30, '주간 스크럼', 'meet'],
  [4, 10, 120, 'B 서비스 배포 확인', 'dev'],
  [4, 14, 120, '월말 정산 자료 정리', 'etc'],
]

const LAST_WEEK: Seed[] = [
  [0, 9.5, 30, '주간 스크럼', 'meet'],
  [0, 10, 240, '요구사항 정의 · PRD 작성', 'etc'],
  [1, 9.5, 30, '주간 스크럼', 'meet'],
  [1, 10, 180, '데이터 모델 설계', 'dev'],
  [1, 14, 120, '스키마 리뷰', 'meet'],
  [2, 9.5, 30, '주간 스크럼', 'meet'],
  [2, 10, 300, '프로젝트 셋업 · 개발환경', 'dev'],
  [3, 9.5, 30, '주간 스크럼', 'meet'],
  [3, 10, 180, '데이터 모델 마이그레이션', 'dev'],
  [3, 15, 90, '타 팀 문의 대응', 'support'],
  [4, 9.5, 30, '주간 스크럼', 'meet'],
  [4, 10, 240, '캘린더 UI 프로토타입', 'dev'],
]

function build(seeds: Seed[], weekOffset: number, prefix: string): DemoEvent[] {
  const base = addDays(startOfWeek(new Date()), weekOffset * 7)
  return seeds.map(([dow, startH, mins, title, categoryId, source = 'LOCAL', priv = false], i) => {
    const start = addDays(base, dow)
    start.setHours(Math.floor(startH), Math.round((startH % 1) * 60), 0, 0)
    const end = new Date(start.getTime() + mins * 60000)
    return {
      id: `${prefix}-${i}`,
      title,
      start,
      end,
      allDay: false,
      categoryId,
      visibility: priv ? ('PRIVATE' as const) : ('TEAM' as const),
      source,
    }
  })
}

/** 데모 초기 일정. 실행 시점의 "이번 주"를 기준으로 만들어진다. */
export function initialEvents(): DemoEvent[] {
  return [
    ...build(LAST_WEEK, -1, 'lw'),
    ...build(THIS_WEEK, 0, 'tw'),
    ...build(NEXT_WEEK, 1, 'nw'),
    // 종일 일정 예시
    (() => {
      const d = addDays(startOfWeek(new Date()), 4)
      d.setHours(0, 0, 0, 0)
      return {
        id: 'allday-1',
        title: '전사 워크숍',
        start: d,
        end: addDays(d, 1),
        allDay: true,
        categoryId: 'etc',
        visibility: 'TEAM' as const,
        source: 'GOOGLE' as const,
      }
    })(),
  ]
}

/** 다른 팀원의 주간보고 (발표 모드 데모용) */
export interface TeamReport {
  userId: string
  submitted: boolean
  done: { category: string; items: string[] }[]
  next: { category: string; items: string[] }[]
  issues: string[]
  totalMinutes: number
  breakdown: { name: string; percent: number; color: string }[]
}

export const TEAM_REPORTS: TeamReport[] = [
  {
    userId: 'u2',
    submitted: true,
    done: [
      { category: '개발', items: ['사내 포털 개편 3차 배포 (4회, 16시간)', '데이터 이관 검증 (3회, 9시간)'] },
      { category: '회의', items: ['주간 스크럼 (5회, 2시간 30분)', '포털 개편 점검 회의 (2시간)'] },
      { category: '지원', items: ['타 팀 권한 설정 지원 (3회, 6시간)'] },
    ],
    next: [
      { category: '개발', items: ['포털 4차 배포 준비', '이관 잔여 데이터 정리'] },
      { category: '회의', items: ['주간 스크럼 (5회 예정)'] },
    ],
    issues: ['이관 대상 레거시 DB 접근 권한이 아직 안 나옴 — 인프라팀 확인 필요'],
    totalMinutes: 2130,
    breakdown: [
      { name: '개발', percent: 70, color: '#4a6ff0' },
      { name: '회의', percent: 13, color: '#e0793a' },
      { name: '지원', percent: 17, color: '#2fa37a' },
    ],
  },
  {
    userId: 'u3',
    submitted: false,
    done: [
      { category: '지원', items: ['고객 문의 대응 (5회, 8시간)'] },
      { category: '개발', items: ['리포트 화면 개선 (14시간)'] },
      { category: '회의', items: ['주간 스크럼 (5회, 2시간 30분)'] },
    ],
    next: [{ category: '개발', items: ['(미제출 — 캘린더 기준 자동 요약)'] }],
    issues: [],
    totalMinutes: 1470,
    breakdown: [
      { name: '개발', percent: 57, color: '#4a6ff0' },
      { name: '지원', percent: 33, color: '#2fa37a' },
      { name: '회의', percent: 10, color: '#e0793a' },
    ],
  },
  {
    userId: 'u4',
    submitted: true,
    done: [
      { category: '교육', items: ['신입 온보딩 멘토링 (5회, 10시간)'] },
      { category: '개발', items: ['알림 서비스 리팩터링 (18시간)'] },
      { category: '회의', items: ['주간 스크럼 (5회, 2시간 30분)', '알림 정책 검토 (1시간 30분)'] },
    ],
    next: [
      { category: '개발', items: ['알림 서비스 배포', '실패 재전송 큐 적용'] },
      { category: '교육', items: ['온보딩 멘토링 마무리'] },
    ],
    issues: [],
    totalMinutes: 1920,
    breakdown: [
      { name: '개발', percent: 56, color: '#4a6ff0' },
      { name: '교육', percent: 31, color: '#8b5cf6' },
      { name: '회의', percent: 13, color: '#e0793a' },
    ],
  },
  {
    userId: 'u5',
    submitted: true,
    done: [
      { category: '회의', items: ['팀 주간회의 진행 (2시간)', '상위 조직 보고 (3회, 4시간 30분)', '1:1 면담 (4회, 4시간)'] },
      { category: '기타', items: ['하반기 로드맵 정리 (8시간)'] },
      { category: '지원', items: ['채용 면접 (2회, 3시간)'] },
    ],
    next: [
      { category: '회의', items: ['분기 계획 리뷰 주관', '상위 조직 보고'] },
      { category: '기타', items: ['팀 목표 정렬'] },
    ],
    issues: ['캘린더 도구 도입 승인 대기 — 8월 말까지 결론 필요'],
    totalMinutes: 1290,
    breakdown: [
      { name: '회의', percent: 49, color: '#e0793a' },
      { name: '기타', percent: 37, color: '#78839a' },
      { name: '지원', percent: 14, color: '#2fa37a' },
    ],
  },
]

/** 인수인계 데모 */
export interface HandoverItem {
  id: string
  title: string
  detail: string
  status: 'TODO' | 'IN_PROGRESS' | 'BLOCKED' | 'DONE'
  acked: boolean
  blockReason?: string
  fromEvent?: string
}

export interface HandoverDoc {
  id: string
  fromUserId: string
  toUserId: string
  absentFrom: Date
  absentTo: Date
  reason: string
  status: 'REQUESTED' | 'ACCEPTED' | 'DONE'
  items: HandoverItem[]
  log: { at: Date; action: string; actor: string; detail?: string }[]
}

export function initialHandover(): HandoverDoc {
  const base = addDays(startOfWeek(new Date()), 7)
  const created = addDays(new Date(), -1)
  return {
    id: 'h1',
    fromUserId: 'u1',
    toUserId: 'u2',
    absentFrom: addDays(base, 2),
    absentTo: addDays(base, 4),
    reason: '휴가',
    status: 'REQUESTED',
    items: [
      {
        id: 'hi1',
        title: 'A 고객 정기 점검',
        detail: '진행 상황: 8월 점검 항목 정리 완료 / 다음 할 일: 수요일 14시 점검 미팅 참석 대행 / 막히면 연락: 010-0000-0000',
        status: 'TODO',
        acked: false,
        fromEvent: 'A 고객 정기 점검 (수 14:00)',
      },
      {
        id: 'hi2',
        title: 'B 서비스 배포 확인',
        detail: '진행 상황: 스테이징 검증 완료 / 다음 할 일: 금요일 오전 운영 배포 후 헬스체크·에러 로그 확인 / 롤백 절차는 위키 참고',
        status: 'TODO',
        acked: false,
        fromEvent: 'B 서비스 배포 확인 (금 10:00)',
      },
      {
        id: 'hi3',
        title: '월말 정산 자료 정리',
        detail: '진행 상황: 8월분 raw 데이터 수집 완료 / 다음 할 일: 금요일까지 정산 시트 업데이트 / 양식은 공유 드라이브 참고',
        status: 'TODO',
        acked: false,
        fromEvent: '월말 정산 자료 정리 (금 14:00)',
      },
      {
        id: 'hi4',
        title: '주간 스크럼 참석 대행',
        detail: '참석 대행 요청. 진행 중인 캘린더 앱 개발 진척만 공유해주시면 됩니다.',
        status: 'TODO',
        acked: false,
        fromEvent: '주간 스크럼 (매일 09:30)',
      },
    ],
    log: [
      { at: created, action: 'handover.create', actor: '홍길동', detail: '항목 4개 · 인수자 김철수' },
    ],
  }
}
