import type { Step } from '../types'

export const part3: Step[] = [
  {
    id: '08',
    slug: 'weekly-report',
    part: 'PART 3 · 업무 활용',
    title: '주간보고 자동 생성',
    tagline: '캘린더에 쌓인 기록이 금요일에 보고서가 되는 구조',
    duration: '60분',
    level: '기본',
    goals: [
      '캘린더 데이터를 주간보고로 집계하는 규칙을 직접 정의한다',
      '"자동 생성"과 "사람의 수정"이 충돌하지 않게 만드는 방법을 배운다',
      '주 단위 계산(ISO 주차)의 함정을 피한다',
    ],
    deliverables: [
      '/weekly 화면 — 주 선택, 자동 초안 생성, 편집, 제출',
      '집계 로직 (카테고리별 묶기, 시간 합계, 비공개 제외)',
      '팀 보드 — 팀원별 제출 현황',
    ],
    prompts: [
      {
        id: 'aggregate',
        label: '주간보고 집계 + 화면',
        when: '캘린더 CRUD가 완성된 다음.',
        body: `주간보고 기능을 만듭니다. PRD의 S-11 스토리를 만족해야 합니다.

## 집계 규칙 (이대로 구현해주세요)
1. 대상 기간: ISO 주차 기준 월요일 00:00 ~ 일요일 24:00 (Asia/Seoul)
2. 대상 일정: 본인의 일정 중
   - visibility = PRIVATE 인 것은 **제외**
   - 취소/삭제된 것 제외
   - 외부 캘린더에서 가져온 일정도 포함 (단 출처를 표시)
3. "이번 주 한 일"(DONE)
   - 카테고리별로 묶는다. 카테고리 없는 것은 "기타"
   - 같은 제목이 여러 번 있으면 하나로 합치고 횟수와 총 시간을 붙인다
     예: "주간 스크럼 (3회, 1시간 30분)"
   - 카테고리 안에서는 총 소요 시간이 긴 것부터
4. "다음 주 계획"(NEXT)
   - 다음 주에 이미 등록된 일정에서 같은 방식으로 생성
5. "이슈·리스크"(ISSUE)
   - 자동 생성하지 않는다. 사람이 직접 쓴다 (빈 항목 1개만 준비)
6. 통계: 총 업무 시간, 카테고리별 비중(%), 회의 시간 비율

## 재생성 규칙 (중요)
- "초안 생성" 버튼은 여러 번 눌릴 수 있다
- edited = true 인 항목은 **절대 덮어쓰지 않는다**
- 사람이 손대지 않은 항목만 새 집계로 교체
- 캘린더에서 사라진 일정에서 만들어진 항목은 (편집되지 않았다면) 제거
- 재생성 전에 "N개 항목이 갱신되고 M개는 유지됩니다" 를 미리 보여준다

## 화면
- 주 선택기 (이전/다음 주, 오늘 주로 이동, "2026년 34주 (8/17~8/23)" 표시)
- 3개 섹션(한 일 / 다음 주 / 이슈), 항목별 인라인 편집, 드래그 순서 변경, 항목 추가·삭제
- 각 항목에 출처 일정 표시 (클릭하면 캘린더로 이동)
- 상단에 통계 요약
- "제출" 버튼 → 상태 SUBMITTED, 제출 후에도 수정 가능하되 "수정됨" 표시

집계 로직은 src/server/report/aggregate.ts 에 **순수 함수**로 분리해주세요
(일정 배열을 넣으면 보고서 항목 배열이 나오는 형태). 테스트하기 쉬워야 합니다.`,
        tips: [
          '**집계 규칙을 이렇게 자세히 적는 것이 이 프롬프트의 핵심이다.** "주간보고 만들어줘"라고 하면 AI는 일정 목록을 그냥 나열한다. 그건 보고서가 아니다.',
          '"같은 제목 합치고 횟수 표시"는 실제 주간보고에서 가장 유용한 기능이다. 주간 스크럼이 5줄로 나오는 보고서는 아무도 안 읽는다.',
          '재생성 규칙(edited 보존)을 빼먹으면 사용자가 두 번째 클릭에서 작업물을 잃는다.',
        ],
      },
      {
        id: 'team-board',
        label: '팀 보드 + 제출 현황',
        when: '개인 주간보고가 동작한 다음.',
        body: `팀 단위 주간보고 보드를 추가해주세요.

## /weekly/team
- 같은 팀 구성원의 해당 주 보고서 제출 현황 (제출 / 초안 / 미작성)
- 팀원 카드: 이름, 상태, 총 업무 시간, "한 일" 항목 수
- 카드 클릭 → 그 사람의 보고서 읽기 전용 보기
- 팀 전체 통계: 카테고리별 시간 합계 (누가 어디에 시간을 쓰는지)
- 팀장/관리자만 접근 (권한은 서버에서 검사)

## 권한 규칙
- 팀원: 같은 팀 사람의 **제출된** 보고서만 읽기 가능
- 초안 상태는 본인만 볼 수 있다 (아직 정리 안 된 내용이 공개되면 아무도 초안을 안 쓴다)
- 팀장: 같은 팀 전체, 초안 여부는 상태로만 표시(내용은 안 보임)

이 권한 규칙을 서버 쿼리 수준에서 강제하는 코드로 만들어주세요.
그리고 권한 검사가 빠진 경로가 없는지 스스로 점검한 결과를 표로 알려주세요.`,
        tips: [
          '"초안은 본인만"이라는 규칙은 사소해 보이지만 **도구가 실제로 쓰이느냐를 결정한다.** 미완성 글이 공개되는 도구에는 아무도 미완성 글을 쓰지 않는다.',
          '권한 규칙은 화면이 아니라 쿼리에 넣어야 한다. 화면에서 숨기는 것은 보안이 아니다.',
        ],
      },
    ],
    sample: [
      { type: 'h', text: '집계 함수 — 이 스텝의 핵심' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/report/aggregate.ts',
        code: `import { differenceInMinutes } from 'date-fns'

export interface AggInput {
  id: string
  title: string
  startAt: Date
  endAt: Date
  allDay: boolean
  visibility: 'TEAM' | 'PRIVATE'
  category?: { id: string; name: string; color: string } | null
  source: string
}

export interface AggItem {
  content: string
  eventIds: string[]
  categoryName: string
  minutes: number
  count: number
}

/**
 * 일정 배열 → 주간보고 항목 배열.
 * 순수 함수(외부 상태·DB 접근 없음)로 유지한다. 그래야 테스트가 쉽고,
 * 규칙을 바꿀 때 화면·DB를 건드리지 않는다.
 */
export function aggregate(events: AggInput[]): AggItem[] {
  // 1) 비공개 일정 제외 — 주간보고는 팀에 공유되는 문서다
  const target = events.filter((e) => e.visibility !== 'PRIVATE')

  // 2) (카테고리, 제목) 조합으로 묶는다. 반복되는 회의를 한 줄로 만드는 핵심.
  const groups = new Map<string, AggItem>()
  for (const e of target) {
    const categoryName = e.category?.name ?? '기타'
    const title = e.title.trim()
    const key = categoryName + '\\u0000' + title.toLowerCase()

    const minutes = e.allDay ? 8 * 60 : Math.max(0, differenceInMinutes(e.endAt, e.startAt))

    const g = groups.get(key)
    if (g) {
      g.minutes += minutes
      g.count += 1
      g.eventIds.push(e.id)
    } else {
      groups.set(key, { content: title, eventIds: [e.id], categoryName, minutes, count: 1 })
    }
  }

  // 3) 표시 문장을 만든다. 2회 이상이면 횟수와 총 시간을 덧붙인다.
  const items = [...groups.values()].map((g) => ({
    ...g,
    content: g.count > 1 ? g.content + ' (' + g.count + '회, ' + fmtDuration(g.minutes) + ')' : g.content,
  }))

  // 4) 카테고리 묶음 유지 + 카테고리 안에서는 시간이 긴 것부터
  return items.sort(
    (a, b) => a.categoryName.localeCompare(b.categoryName, 'ko') || b.minutes - a.minutes,
  )
}

export function fmtDuration(minutes: number): string {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (h === 0) return m + '분'
  if (m === 0) return h + '시간'
  return h + '시간 ' + m + '분'
}

/** 통계: 카테고리별 비중 */
export function summarize(items: AggItem[]) {
  const total = items.reduce((s, i) => s + i.minutes, 0)
  const byCategory = new Map<string, number>()
  for (const i of items) {
    byCategory.set(i.categoryName, (byCategory.get(i.categoryName) ?? 0) + i.minutes)
  }
  return {
    totalMinutes: total,
    breakdown: [...byCategory.entries()]
      .map(([name, minutes]) => ({
        name,
        minutes,
        percent: total === 0 ? 0 : Math.round((minutes / total) * 100),
      }))
      .sort((a, b) => b.minutes - a.minutes),
  }
}`,
      },
      { type: 'h', text: '재생성 — 사람이 고친 것을 지키는 로직' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/report/regenerate.ts',
        code: `/**
 * 초안 재생성.
 * 원칙: 사람이 손댄 것(edited=true)은 신성불가침. 자동 생성 항목만 교체한다.
 */
export async function regenerateDraft(userId: string, isoYear: number, isoWeek: number) {
  const report = await ensureReport(userId, isoYear, isoWeek)
  const { from, to } = isoWeekRange(isoYear, isoWeek)

  const events = await db.event.findMany({
    where: { userId, startAt: { gte: from, lt: to } },
    include: { category: true },
  })
  const fresh = aggregate(events)

  const existing = await db.reportItem.findMany({
    where: { reportId: report.id, section: 'DONE' },
  })
  const kept = existing.filter((i) => i.edited)          // 지킬 것
  const replaceable = existing.filter((i) => !i.edited)  // 버릴 것

  // 사람이 이미 같은 내용을 손봤다면 자동 항목으로 중복 추가하지 않는다
  const keptKeys = new Set(kept.map((i) => normalize(i.content)))
  const toInsert = fresh.filter((f) => !keptKeys.has(normalize(f.content)))

  await db.$transaction([
    db.reportItem.deleteMany({ where: { id: { in: replaceable.map((i) => i.id) } } }),
    db.reportItem.createMany({
      data: toInsert.map((f, idx) => ({
        reportId: report.id,
        section: 'DONE' as const,
        content: f.content,
        eventId: f.eventIds[0],
        edited: false,
        order: kept.length + idx,
      })),
    }),
  ])

  return { replaced: replaceable.length, kept: kept.length, added: toInsert.length }
}

/** 비교용 정규화 — 괄호 안의 "(3회, 1시간)" 같은 자동 생성 꼬리표를 떼고 비교 */
const normalize = (s: string) => s.replace(/\\s*\\([^)]*\\)\\s*$/, '').trim().toLowerCase()`,
      },
      { type: 'h', text: '실제로 생성되는 보고서 모양' },
      {
        type: 'code',
        lang: 'markdown',
        filename: '2026년 34주 (8/17~8/23) · 홍길동',
        code: `## 이번 주 한 일  (총 38시간 30분)

### 개발  (22시간, 57%)
- 캘린더 월/주 뷰 구현 (4회, 12시간)
- 일정 CRUD + 낙관적 갱신 (3회, 7시간)
- 구글 캘린더 토큰 암호화 적용 (3시간)

### 회의  (9시간 30분, 25%)
- 주간 스크럼 (5회, 2시간 30분)
- dX팀 정기회의 (2시간)
- 캘린더 연동 정책 논의 (3회, 5시간)

### 지원  (5시간, 13%)
- 타 팀 데이터 추출 지원 (2회, 3시간)
- 사용자 문의 대응 (2시간)

### 기타  (2시간, 5%)
- 사내 보안 교육 (2시간)

## 다음 주 계획
### 개발
- 주간보고 팀 보드 구현 (예정 8시간)
- 인수인계 화면 착수 (예정 6시간)
### 회의
- 주간 스크럼 (5회 예정)
- 분기 계획 리뷰 (2시간)

## 이슈 · 리스크
- (직접 작성) 구글 OAuth 앱 심사가 지연되면 8월 말 배포 일정에 영향`,
      },
      {
        type: 'callout',
        tone: 'tip',
        title: '"회의 25%"라는 숫자의 힘',
        text: '집계에 카테고리 비중을 넣으면 주간보고가 보고서에서 **관리 도구**로 바뀐다. "이번 달 회의 비중이 40%를 넘었다"는 사실은 캘린더를 눈으로 봐서는 절대 안 보인다. 이 한 줄이 도구를 쓰게 만드는 이유가 되기도 한다.',
      },
    ],
    explain: [
      { type: 'h', text: '이 기능의 본질: 같은 내용을 두 번 쓰지 않게 하기' },
      {
        type: 'flow',
        title: '기존 흐름',
        steps: ['일정을 캘린더에 쓴다', '금요일에 기억을 더듬는다', '주간보고에 다시 쓴다', '빠진 게 생각난다'],
      },
      {
        type: 'flow',
        title: '바뀐 흐름',
        steps: ['일정을 캘린더에 쓴다', '초안 생성 클릭', '문장을 다듬는다', '제출'],
      },
      {
        type: 'p',
        text: '여기서 중요한 것은 **자동 생성이 100% 정확할 필요가 없다는 점**이다. 목표는 "빈 화면에서 시작하지 않게 하는 것"이다. 70% 정확한 초안 + 5분 수정이, 100% 수동 작성 30분보다 압도적으로 낫다.',
      },
      { type: 'h', text: '자동 생성 vs 사람의 수정 — 모든 자동화 기능의 공통 난제' },
      {
        type: 'table',
        head: ['설계', '결과'],
        rows: [
          ['재생성 시 전부 덮어쓰기', '한 번 수정한 사람은 다시 버튼을 안 누른다. 기능이 죽는다'],
          ['재생성 시 전부 추가하기', '같은 항목이 계속 쌓인다. 매주 정리 노동이 생긴다'],
          ['**편집 플래그로 구분 (선택)**', '자동은 갱신, 수동은 보존. 사용자가 버튼을 신뢰하게 된다'],
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '재생성 전에 미리 보여주기',
        text: '"3개 항목이 갱신되고 2개는 유지됩니다"를 버튼 옆에 미리 표시하는 것. 코드 몇 줄이지만 **되돌릴 수 없는 동작에 대한 불안**을 없애준다. 자동화 기능이 실제로 쓰이려면 이 신뢰가 필요하다.',
      },
      { type: 'h', text: 'ISO 주차의 함정' },
      {
        type: 'p',
        text: '"2026년 1주"가 언제인가? 1월 1일이 목요일이면 그 주가 1주다. 1월 1일이 금요일이면 그 주는 **2025년 53주**다. 이걸 직접 계산하려 하면 반드시 연말·연초에 버그가 난다.',
      },
      {
        type: 'code',
        lang: 'typescript',
        code: `import { getISOWeek, getISOWeekYear, startOfISOWeek, endOfISOWeek } from 'date-fns'

// ❌ 직접 계산하지 않는다
// const week = Math.ceil((date.getDate() + firstDay) / 7)

// ✅ 표준 함수를 쓴다. isoYear 와 isoWeek 를 항상 쌍으로 저장한다.
const isoYear = getISOWeekYear(date)   // 2025 가 나올 수 있다 (2026년 1월 날짜인데도)
const isoWeek = getISOWeek(date)`,
      },
      {
        type: 'p',
        text: '스키마에서 `@@unique([userId, isoYear, isoWeek])` 로 못 박은 이유가 이것이다. 주차 계산이 흔들려도 **DB가 같은 주에 보고서 두 개를 못 만들게** 막아준다. 이런 식으로 "코드 실수를 DB 제약으로 막는" 설계가 오래 가는 소프트웨어를 만든다.',
      },
      { type: 'h', text: '순수 함수로 분리하는 이유' },
      {
        type: 'p',
        text: '`aggregate()` 는 DB도, 시간도, 로그인 정보도 모른다. 일정 배열을 넣으면 항목 배열이 나온다. 이렇게 만들면 세 가지가 쉬워진다. ① 테스트: 일정 배열만 만들어 넣으면 된다 ② 규칙 변경: "회의는 따로 묶자"는 요구가 오면 이 파일만 고친다 ③ **AI에게 수정 요청하기**: 파일 하나를 주고 "이 규칙을 이렇게 바꿔줘"라고 하면 되므로 다른 곳을 망가뜨리지 않는다.',
      },
      {
        type: 'callout',
        tone: 'dx',
        text: '보고서 양식은 팀마다 다릅니다. 사내 표준 주간보고 양식·엑셀 내보내기·상위 조직 롤업이 필요하면 dX팀에 요청하세요.',
      },
    ],
    checklist: [
      '/weekly 에서 이번 주 초안이 생성된다',
      '반복 회의가 "(N회, N시간)" 으로 합쳐져 나온다',
      '비공개 일정이 보고서에 나오지 않는다',
      '항목을 수정한 뒤 재생성해도 수정 내용이 남아 있다',
      '재생성 전에 갱신/유지 개수가 미리 표시된다',
      '카테고리별 시간 비중이 표시된다',
      '연말·연초 날짜로 테스트해도 주차가 어긋나지 않는다',
      '다른 사람의 초안 보고서에 접근하면 거부된다',
    ],
    demo: {
      kind: 'weekly',
      hint: '캘린더에 쌓인 일정이 자동으로 집계된 결과다. 반복 회의가 "(5회, 2시간 30분)"으로 합쳐진 것을 보고, 항목을 클릭해 수정한 뒤 "초안 재생성"을 눌러보라 — 내가 고친 문장은 살아남는다.',
    },
  },

  {
    id: '09',
    slug: 'present-mode',
    part: 'PART 3 · 업무 활용',
    title: '주간회의 발표 모드',
    tagline: '한 명이 화면을 띄우면 회의가 굴러가는 화면',
    duration: '40분',
    level: '기본',
    goals: [
      '회의라는 오프라인 상황을 소프트웨어로 지원하는 설계를 해본다',
      '"화면에 띄우는 화면"의 요구사항이 일반 화면과 어떻게 다른지 안다',
      '키보드 조작·전체화면·큰 글씨 같은 발표용 UI 요소를 다룬다',
    ],
    deliverables: [
      '/present 화면 — 팀원별 주간보고를 순서대로 넘겨보는 전체화면 뷰',
      '키보드 내비게이션 + 발표 타이머',
      '회의록용 요약 내보내기',
    ],
    prompts: [
      {
        id: 'present',
        label: '발표 모드 구현',
        when: '팀 주간보고 보드가 동작하는 다음.',
        body: `주간회의용 발표 모드를 만듭니다.
상황: 매주 월요일 오전, 팀장이 회의실 화면에 이 페이지를 띄웁니다.
팀원 5~8명의 주간보고를 순서대로 넘기며 각자 1~2분씩 발표합니다.

## /present?week=2026-W34
- 전체화면 레이아웃, **회의실 뒤에서도 읽히는 큰 글씨**
- 한 화면 = 한 사람의 주간보고
  - 상단: 이름 / 부서 / 이번 주 총 업무 시간 / 카테고리 비중 바
  - 본문 2단: 왼쪽 "이번 주 한 일", 오른쪽 "다음 주 계획"
  - 하단: 이슈·리스크 (있을 때만, 눈에 띄게)
- 하단 진행 표시: "3 / 7" + 팀원 이름 점 표시 (클릭하면 그 사람으로 이동)

## 조작
- → / Space : 다음 사람, ← : 이전 사람
- F : 전체화면 토글, ESC : 나가기
- O : 개요 화면 (팀 전체를 한 눈에 보는 격자)
- 발표 타이머: 사람이 바뀌면 자동으로 0부터 시작, 2분 넘으면 색이 바뀜 (소리 없음)
- 마우스를 3초간 움직이지 않으면 조작 UI가 사라짐

## 데이터
- 해당 주에 제출된 보고서만 표시 (미제출자는 "미제출"로 표시하되 순서에는 포함)
- 팀장/관리자만 접근
- 시작 시 전체 데이터를 한 번에 불러온다 (넘길 때마다 로딩이 걸리면 회의가 끊긴다)

## 추가
- "회의록 복사" 버튼: 이번 주 전체 요약을 마크다운으로 클립보드에 복사
  (사내 위키·메신저에 그대로 붙일 수 있는 형태)

접근성도 고려해주세요: 색만으로 정보를 전달하지 않기, 대비 충분히.`,
        tips: [
          '**"회의실 뒤에서도 읽히는 큰 글씨"** 같은 표현을 쓰면 AI가 폰트 크기를 실제로 키운다. "보기 좋게"라고 하면 평범한 웹 폰트 크기가 나온다.',
          '"넘길 때마다 로딩이 걸리면 회의가 끊긴다"는 이유를 함께 적으면, AI가 데이터 미리 가져오기(prefetch)를 알아서 넣는다. **이유를 적는 것이 요구사항을 적는 것보다 강력하다.**',
          '타이머에 소리를 넣지 않는 것은 의도적이다. 회의실에서 알림 소리는 발표를 끊는다.',
        ],
      },
      {
        id: 'polish',
        label: '실제 회의에서 써보고 다듬기',
        when: '한 번이라도 실제 회의에서 써본 다음. 이 프롬프트가 진짜 개선을 만든다.',
        body: `실제 회의에서 발표 모드를 써봤습니다. 아래 문제들을 고쳐주세요.

1. 팀원 순서가 매주 바뀌어서 다음이 누군지 예측이 안 된다
   → 순서를 고정하고(이름순 또는 지정 순서), 화면에 "다음: 김철수"를 미리 표시
2. 이슈가 없는 사람도 빈 "이슈" 영역이 나와서 화면이 허전하다
   → 내용이 있을 때만 영역을 표시하고, 그 공간은 다른 섹션이 쓰게
3. 발표 중에 특정 항목을 짚으면서 이야기하는데 화면에서 어디를 보는지 모른다
   → 클릭하면 해당 항목이 강조되는 기능 (다음 사람으로 넘어가면 초기화)
4. 미제출자가 있으면 회의가 어색하게 멈춘다
   → 미제출자는 "미제출 · 캘린더 기준 자동 요약"으로 캘린더 집계 결과라도 보여준다
5. 회의 후 회의록 복사를 했는데 너무 길다
   → 각 사람당 "한 일 3줄 + 이슈"만 담은 짧은 버전도 함께 제공

각 항목을 고친 뒤, 실제로 어떻게 달라지는지 한 줄씩 설명해주세요.`,
        tips: [
          '이 프롬프트가 이 스텝의 진짜 교훈이다. **써보기 전에는 4번 문제(미제출자로 회의가 멈춤)를 상상할 수 없다.** 어떤 기획서도 이걸 못 잡는다.',
          '실제 사용 후 피드백을 목록으로 정리해 한 번에 주는 것이, 하나씩 고치는 것보다 결과가 좋다. AI가 항목 간 상충을 함께 고려한다.',
        ],
      },
    ],
    sample: [
      { type: 'h', text: '화면 구성' },
      {
        type: 'code',
        lang: 'text',
        filename: '발표 모드 레이아웃',
        code: `┌────────────────────────────────────────────────────────────┐
│  홍길동 · dX팀                             ⏱ 01:24        │
│  이번 주 38시간 30분                                        │
│  개발 ████████████ 57%  회의 █████ 25%  지원 ██ 13%  기타 ▎5%│
├──────────────────────────────┬─────────────────────────────┤
│  이번 주 한 일                │  다음 주 계획                │
│                              │                             │
│  【개발】                     │  【개발】                    │
│  · 캘린더 월/주 뷰 구현       │  · 주간보고 팀 보드          │
│    (4회, 12시간)              │  · 인수인계 화면 착수        │
│  · 일정 CRUD (3회, 7시간)     │                             │
│  · 토큰 암호화 적용 (3시간)   │  【회의】                    │
│                              │  · 주간 스크럼 (5회)         │
│  【회의】                     │  · 분기 계획 리뷰            │
│  · 주간 스크럼 (5회, 2.5h)    │                             │
│  · 연동 정책 논의 (3회, 5h)   │                             │
├──────────────────────────────┴─────────────────────────────┤
│  ⚠ 이슈 · 리스크                                            │
│  구글 OAuth 앱 심사 지연 시 8월 말 배포 일정 영향            │
├────────────────────────────────────────────────────────────┤
│  ● ● ◉ ○ ○ ○ ○     3 / 7      다음: 김철수    ← → 이동   │
└────────────────────────────────────────────────────────────┘`,
      },
      { type: 'h', text: '키보드 내비게이션' },
      {
        type: 'code',
        lang: 'tsx',
        filename: 'src/app/present/PresentDeck.tsx (발췌)',
        code: `'use client'
import { useEffect, useRef, useState } from 'react'

export function PresentDeck({ slides }: { slides: Slide[] }) {
  const [index, setIndex] = useState(0)
  const [elapsed, setElapsed] = useState(0)
  const [uiVisible, setUiVisible] = useState(true)
  const hideTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  // 사람이 바뀌면 타이머를 0으로. 발표 시간 감각을 주는 것이 목적이므로
  // 소리나 강제 종료는 넣지 않는다 (회의 흐름을 끊기 때문)
  useEffect(() => {
    setElapsed(0)
    const t = setInterval(() => setElapsed((e) => e + 1), 1000)
    return () => clearInterval(t)
  }, [index])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      // 입력창에 타이핑 중이면 단축키를 가로채지 않는다
      const tag = (e.target as HTMLElement)?.tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA') return

      switch (e.key) {
        case 'ArrowRight':
        case ' ':
          e.preventDefault()                       // Space의 기본 스크롤 방지
          setIndex((i) => Math.min(i + 1, slides.length - 1))
          break
        case 'ArrowLeft':
          setIndex((i) => Math.max(i - 1, 0))
          break
        case 'f':
        case 'F':
          document.fullscreenElement
            ? document.exitFullscreen()
            : document.documentElement.requestFullscreen()
          break
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [slides.length])

  // 마우스를 3초간 안 움직이면 조작 UI를 숨긴다 (화면에 내용만 남게)
  useEffect(() => {
    const onMove = () => {
      setUiVisible(true)
      if (hideTimer.current) clearTimeout(hideTimer.current)
      hideTimer.current = setTimeout(() => setUiVisible(false), 3000)
    }
    window.addEventListener('mousemove', onMove)
    onMove()
    return () => {
      window.removeEventListener('mousemove', onMove)
      if (hideTimer.current) clearTimeout(hideTimer.current)
    }
  }, [])

  const slide = slides[index]
  const overTime = elapsed > 120   // 2분 초과 — 색으로만 알린다

  return (
    <div className="flex h-screen flex-col bg-neutral-950 text-neutral-50">
      {/* 실제 렌더링 부분 생략 */}
    </div>
  )
}`,
      },
      { type: 'h', text: '회의록 복사 결과 (짧은 버전)' },
      {
        type: 'code',
        lang: 'markdown',
        filename: '클립보드에 복사되는 내용',
        code: `# dX팀 주간회의 · 2026년 34주 (8/17~8/23)
참석 7명 / 제출 6명

## 홍길동 (38.5h)
- 캘린더 월/주 뷰 구현 (12h)
- 일정 CRUD + 낙관적 갱신 (7h)
- 구글 캘린더 토큰 암호화 (3h)
- ⚠ 구글 OAuth 앱 심사 지연 시 배포 일정 영향

## 김철수 (40h)
- 사내 포털 개편 3차 배포 (16h)
- 데이터 이관 검증 (9h)
- 타 팀 지원 (6h)

## 이영희 (미제출 · 캘린더 기준 자동 요약)
- 고객 대응 (5회, 8h)
- 개발 (14h)

---
## 팀 전체 시간 배분
개발 52% · 회의 21% · 지원 18% · 기타 9%`,
      },
      {
        type: 'callout',
        tone: 'tip',
        title: '"미제출 · 캘린더 기준 자동 요약"',
        text: '이게 실제 회의에서 가장 반응이 좋았던 기능이다. 보고서를 안 쓴 사람도 캘린더만 쓰고 있었다면 회의는 굴러간다. **완벽하지 않은 데이터로도 회의가 멈추지 않게 만드는 것**이 실무 도구의 조건이다.',
      },
    ],
    explain: [
      { type: 'h', text: '"화면에 띄우는 화면"은 다른 규칙을 따른다' },
      {
        type: 'table',
        head: ['', '일반 업무 화면', '발표용 화면'],
        rows: [
          ['보는 거리', '50cm', '3~5m'],
          ['글자 크기', '13~14px', '20~32px 이상'],
          ['정보 밀도', '높게 (한 화면에 많이)', '낮게 (한 화면에 한 사람)'],
          ['조작', '마우스 중심', '키보드 중심 (발표자는 화면 앞에 서 있다)'],
          ['로딩', '스피너 허용', '**허용 안 됨** — 미리 다 불러온다'],
          ['색', '브랜드 색상', '고대비. 프로젝터는 색이 죽는다'],
        ],
      },
      {
        type: 'p',
        text: '이 차이를 프롬프트에 안 적으면 AI는 일반 업무 화면을 만든다. 그리고 그 화면은 실제 회의실에서 **글씨가 안 보여서** 못 쓴다.',
      },
      { type: 'h', text: '기능의 목적을 프롬프트에 적으면 결과가 달라진다' },
      {
        type: 'table',
        head: ['요구사항만 적기', '목적까지 적기'],
        rows: [
          ['"데이터를 미리 불러오세요"', '"넘길 때마다 로딩이 걸리면 회의가 끊긴다" → AI가 prefetch + 캐시 + 낙관적 전환까지 넣는다'],
          ['"타이머를 넣으세요"', '"발표 시간 감각을 주되 발표를 끊지 않아야 한다" → AI가 소리 대신 색 변화를 선택한다'],
          ['"진행 표시를 넣으세요"', '"다음이 누군지 몰라 어색해진다" → AI가 "다음: 김철수" 표시를 추가한다'],
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'AI에게 "왜"를 알려주는 것의 가치',
        text: 'AI는 목적을 알면 요구사항에 없던 것까지 맞게 채운다. 목적을 모르면 요구사항을 문자 그대로만 채운다. 프롬프트에 **"이 기능은 어떤 상황에서 누가 쓴다"** 한 줄을 추가하는 것이, 요구사항을 열 줄 더 쓰는 것보다 효과가 크다.',
      },
      { type: 'h', text: '왜 실시간 동기화(팀장이 넘기면 팀원 화면도 넘어감)를 안 넣었나' },
      {
        type: 'p',
        text: '기술적으로는 WebSocket으로 가능하다. 하지만 우리 상황은 **한 명이 회의실 화면을 띄우는 것**이다. 각자 자기 노트북으로 보는 게 아니다. 실시간 동기화는 서버 상태 관리·재접속 처리·권한 등 상당한 복잡도를 추가하는데, **여기서는 아무 문제도 해결하지 않는다.**',
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '기술적으로 가능한 것 ≠ 지금 필요한 것',
        text: 'AI에게 물어보면 거의 항상 "가능합니다"라고 답하고 코드를 준다. **"이게 지금 어떤 문제를 해결하는가?"는 사람이 물어야 하는 질문이다.** 원격 참여자가 많아지고, 각자 화면으로 보게 되고, 발표자가 매주 바뀌는 상황이 오면 그때 넣으면 된다.',
      },
      {
        type: 'callout',
        tone: 'dx',
        text: '사내 회의실 디스플레이 해상도·화면 공유 환경에 맞춘 최적화, 원격 참여자용 실시간 동기화가 필요하면 dX팀에 요청하세요.',
      },
    ],
    checklist: [
      '/present 에서 팀원 보고서가 한 명씩 전체화면으로 보인다',
      '→ ← Space 로 넘길 수 있고 F로 전체화면이 된다',
      '회의실 화면(또는 노트북을 3m 밖에서) 기준으로 글씨가 읽힌다',
      '사람을 넘길 때 로딩이 발생하지 않는다',
      '미제출자도 캘린더 기준 요약이 보인다',
      '"회의록 복사"로 마크다운이 클립보드에 복사된다',
      '팀원 계정으로 접속하면 접근이 거부된다',
    ],
    demo: {
      kind: 'present',
      hint: '주간회의에서 한 명이 화면에 띄우는 화면이다. →/Space 로 팀원을 넘기고 F로 전체화면. 글씨 크기와 "다음: 김철수" 표시가 왜 필요한지 3m 떨어져서 보면 바로 이해된다.',
    },
  },

  {
    id: '10',
    slug: 'handover',
    part: 'PART 3 · 업무 활용',
    title: '인수인계 기능',
    tagline: '부재 시 업무를 넘기고, 돌아와서 무슨 일이 있었는지 아는 구조',
    duration: '60분',
    level: '기본',
    goals: [
      '"메신저로 구두 인계"의 문제를 데이터 구조로 해결한다',
      '두 사람이 관여하는 기능(요청 → 확인)의 상태 흐름을 설계한다',
      '권한 위임과 감사 로그를 다룬다',
    ],
    deliverables: [
      '/handover 화면 — 부재 등록, 항목 선택, 인수자 지정, 확인',
      '인수자 화면 — 받은 인수인계 확인·항목별 처리',
      '복귀 시 요약 (내가 없는 동안 무슨 일이 있었나)',
    ],
    prompts: [
      {
        id: 'handover-flow',
        label: '인수인계 흐름 구현',
        when: '주간보고까지 완성된 다음.',
        body: `인수인계 기능을 만듭니다.

## 실제 상황
"다음 주 수~금 휴가입니다. 그 사이 A 고객 대응과 B 배포 확인을 김철수님께 부탁드립니다."
지금은 이걸 메신저로 하는데, 휴가 복귀 후에 뭐가 처리됐는지 알 수 없습니다.

## 상태 흐름
REQUESTED (인계자가 만들어 보냄)
  → ACCEPTED (인수자가 확인. 이때부터 인수자에게 보임)
  → DONE (부재 종료 후 인계자가 복귀 확인)

각 상태 전이의 조건과 권한을 명확히 해주세요.

## /handover/new — 인수인계 만들기
1. 부재 기간 선택 (시작~종료, 사유: 휴가/교육/출장/기타)
2. **기간 내 내 일정이 자동으로 목록에 뜬다** — 체크해서 인계 대상 선택
   (이게 캘린더 연동의 진짜 가치다. 뭘 넘겨야 하는지 기억해내지 않아도 된다)
3. 캘린더에 없는 항목은 직접 추가 (예: "월말 정산 마감 체크")
4. 항목별로 인계 메모: 현재 진행 상황 / 연락처 / 주의사항
5. 인수자 선택 (같은 팀 우선, 다른 팀도 가능)
6. 항목마다 다른 인수자를 지정할 수 있어야 한다 (한 사람에게 다 넘기지 않는 경우가 많다)
7. 보내면 인수자에게 알림 (지금은 앱 내 알림만)

## /handover/received — 받은 인수인계
- 항목별 체크: 확인함 / 진행중 / 막힘 / 완료
- 막힘 상태에는 이유를 적게 하고, 인계자에게 표시
- 전체 "확인" 버튼 → ACCEPTED 로 전이. **확인 시각과 사람을 감사 로그에 남긴다**

## 복귀 요약
- 부재 종료 후 인계자가 보는 화면: 항목별 최종 상태, 인수자 메모, 그 기간에 추가된 관련 일정
- "인수인계 완료" 버튼 → DONE

## 필수 조건
- 인계자와 인수자만 해당 인수인계를 볼 수 있다 (팀장은 목록만, 내용은 안 보임 — 정책 선택)
- 부재 기간이 지났는데 ACCEPTED 가 안 된 인수인계는 눈에 띄게 경고
- 항목이 0개인 인수인계는 만들 수 없다
- 인수자를 자기 자신으로 지정할 수 없다
- 모든 상태 전이는 AuditLog 에 기록

먼저 상태 전이 표(현재상태 × 동작 × 누가 × 결과)를 만들고, 그 다음 코드를 주세요.`,
        tips: [
          '**"기간 내 내 일정이 자동으로 목록에 뜬다"** 가 이 기능의 핵심이다. 이것 하나가 캘린더와 인수인계를 연결한다.',
          '"항목마다 다른 인수자" 같은 현실적 요구를 미리 넣으면, 나중에 스키마를 고치지 않아도 된다.',
          '상태 전이 표를 먼저 만들게 하면, AI가 코드를 짤 때 빠지는 경우(권한 없는 사람의 전이 시도 등)가 크게 줄어든다.',
        ],
      },
      {
        id: 'edge-cases',
        label: '예외 상황 점검',
        when: '기본 흐름이 동작한 다음. 두 사람이 관여하는 기능은 예외가 많다.',
        body: `인수인계 기능의 예외 상황을 점검해주세요.
아래 각 상황에서 우리 코드가 어떻게 동작하는지 확인하고, 문제가 있으면 고쳐주세요.

1. 인수자가 확인하기 전에 인계자가 이미 휴가를 떠났다
2. 인수자도 같은 기간에 휴가다 (부재 기간이 겹친다)
3. 인수자가 퇴사/부서이동으로 계정이 비활성화됐다
4. 인계 대상으로 지정한 일정이 그 사이 삭제됐다
5. 인수자가 항목 일부만 확인하고 나머지를 방치했다
6. 같은 기간에 인수인계를 두 번 만들었다 (중복)
7. 부재 기간이 지난 뒤에 새 항목을 추가하려 한다
8. 인수자가 "막힘"으로 표시했는데 인계자가 연락이 안 된다

각 상황에 대해:
- 현재 동작 (문제 있음 / 없음)
- 바람직한 동작
- 수정 코드 (필요한 경우)

그리고 이 중 "코드로 막을 것"과 "화면 안내로 충분한 것"을 구분해주세요.`,
        tips: [
          '**이 프롬프트 형식은 모든 기능에 재사용할 수 있다.** "예외 상황 8개를 나열하고 각각 어떻게 되는지 점검하라"는 요청은 AI가 특히 잘 수행한다.',
          '"코드로 막을 것과 안내로 충분한 것 구분"이 중요하다. 모든 예외를 코드로 막으면 앱이 쓰기 어려워진다.',
          '2번(인수자도 휴가)은 실제로 자주 생기고, 거의 항상 처음 구현에서 빠진다.',
        ],
      },
    ],
    sample: [
      { type: 'h', text: '상태 전이 표' },
      {
        type: 'table',
        head: ['현재', '동작', '누가', '결과', '기록'],
        rows: [
          ['(없음)', '인수인계 생성', '인계자', 'REQUESTED', 'handover.create'],
          ['REQUESTED', '항목 수정/추가', '인계자만', 'REQUESTED 유지', '-'],
          ['REQUESTED', '전체 확인', '**인수자만**', 'ACCEPTED', 'handover.accept (시각·사용자)'],
          ['REQUESTED', '취소', '인계자만', '삭제', 'handover.cancel'],
          ['ACCEPTED', '항목 상태 변경', '인수자', 'ACCEPTED 유지', 'item.status'],
          ['ACCEPTED', '항목 추가', '인계자 (부재 종료 전까지만)', 'ACCEPTED 유지', 'item.add'],
          ['ACCEPTED', '복귀 확인', '**인계자만**', 'DONE', 'handover.done'],
          ['DONE', '모든 변경', '아무도', '거부 (읽기 전용)', '-'],
        ],
      },
      { type: 'h', text: '부재 기간 내 일정 자동 수집' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/handover/collect.ts',
        code: `/**
 * 부재 기간에 걸치는 내 일정을 모은다.
 * "무엇을 인계해야 하는지 기억해내야 하는" 부담을 없애는 것이 이 함수의 목적이다.
 */
export async function collectCandidates(userId: string, from: Date, to: Date) {
  const events = await db.event.findMany({
    // 기간이 "겹치는" 조건. 시작만 비교하면 기간 전에 시작해 걸쳐 있는 일정이 빠진다.
    where: {
      userId,
      startAt: { lt: to },
      endAt: { gt: from },
      visibility: 'TEAM',            // 비공개 일정은 인계 대상으로 제안하지 않는다
    },
    include: { category: true },
    orderBy: { startAt: 'asc' },
  })

  return events.map((e) => ({
    eventId: e.id,
    title: e.title,
    when: formatRange(e.startAt, e.endAt, e.allDay),
    category: e.category?.name ?? '기타',
    // 회의는 대개 "참석 대행"이고, 개발 업무는 "이어받기"다.
    // 인계 메모 템플릿을 미리 채워주면 작성률이 크게 올라간다.
    suggestedNote: e.category?.name === '회의'
      ? '참석 대행 요청. 회의 링크와 안건은 일정 메모 참고'
      : '진행 상황: / 다음 할 일: / 막히면 연락: ',
  }))
}`,
      },
      { type: 'h', text: '상태 전이 — 권한을 코드로 강제' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/handover/transitions.ts',
        code: `'use server'
import { db } from '@/server/db'
import { requireUser } from '@/server/auth'
import { audit } from '@/server/audit'

/** 인수자가 인수인계를 확인한다. 이 동작만이 REQUESTED → ACCEPTED 전이를 만든다. */
export async function acceptHandover(handoverId: string) {
  const me = await requireUser()

  const h = await db.handover.findUnique({
    where: { id: handoverId },
    include: { items: true },
  })
  if (!h) throw new Error('인수인계를 찾을 수 없습니다')

  // ① 권한: 인수자 본인만. 인계자도, 팀장도 대신 확인할 수 없다.
  //    "확인했다"는 기록은 대신할 수 없는 종류의 기록이다.
  if (h.toUserId !== me.id) throw new Error('인수자만 확인할 수 있습니다')

  // ② 상태: REQUESTED 에서만 전이 가능 (중복 확인 방지)
  if (h.status !== 'REQUESTED') throw new Error('이미 처리된 인수인계입니다')

  // ③ 내용: 빈 인수인계를 확인 처리하지 않는다
  if (h.items.length === 0) throw new Error('인계 항목이 없습니다')

  await db.$transaction([
    db.handover.update({
      where: { id: handoverId, status: 'REQUESTED' },  // 경쟁 조건 방지 (조건부 업데이트)
      data: { status: 'ACCEPTED', acceptedAt: new Date() },
    }),
    audit('handover.accept', me.id, handoverId, {
      itemCount: h.items.length,
      fromUserId: h.fromUserId,
    }),
  ])
}

/** 부재 기간이 지났는데 확인되지 않은 인수인계를 찾는다 (경고 표시용) */
export async function findStaleHandovers(userId: string) {
  return db.handover.findMany({
    where: {
      OR: [{ fromUserId: userId }, { toUserId: userId }],
      status: 'REQUESTED',
      absentFrom: { lte: new Date() },   // 이미 부재가 시작됐는데 확인이 안 됨
    },
    include: { toUser: true, fromUser: true },
  })
}`,
      },
      { type: 'h', text: '예외 상황 점검 결과' },
      {
        type: 'table',
        head: ['상황', '바람직한 동작', '구분'],
        rows: [
          [
            '인수자 확인 전에 인계자가 떠남',
            '부재 시작일이 지난 REQUESTED는 양쪽 화면 최상단에 경고. 인수자에게 재알림',
            '코드로 막지 않음 (막을 수 없다) + 강한 안내',
          ],
          [
            '**인수자도 같은 기간 휴가**',
            '인수자 선택 시 그 사람의 부재 기간과 겹치면 경고를 띄우고, 그래도 지정하려면 확인 필요',
            '**코드로 검사** (겹침 조회)',
          ],
          [
            '인수자 계정 비활성화',
            '비활성 사용자는 인수자 목록에 안 나옴. 이미 지정된 건은 "인수자 변경 필요" 표시',
            '**코드로 막음**',
          ],
          [
            '인계 대상 일정이 삭제됨',
            '항목은 남기고 "원본 일정 삭제됨" 표시. 항목 자체를 지우면 인계 내용이 사라진다',
            '**코드로 처리** (onDelete: SetNull)',
          ],
          [
            '일부만 확인하고 방치',
            '항목 단위 상태는 그대로 두고, 부재 종료 시 미처리 항목을 복귀 요약 최상단에 표시',
            '안내로 충분',
          ],
          [
            '같은 기간 중복 생성',
            '기간이 겹치는 REQUESTED/ACCEPTED가 있으면 "기존 것에 추가하시겠습니까?" 제안',
            '**코드로 검사** (막지는 않음)',
          ],
          [
            '부재 종료 후 항목 추가',
            '거부. 종료된 기간의 인계 내용을 바꾸면 기록의 의미가 없어진다',
            '**코드로 막음**',
          ],
          [
            '인수자가 "막힘" 표시했는데 연락 안 됨',
            '막힘 항목은 팀장 화면에도 노출 (내용이 아니라 "막힌 항목 있음"만)',
            '정책 결정 필요 — 조직마다 다름',
          ],
        ],
      },
      {
        type: 'callout',
        tone: 'tip',
        title: '이 표가 왜 중요한가',
        text: '8개 상황 중 **4개는 코드로 막고, 3개는 안내로 처리하고, 1개는 조직 정책 결정**이다. AI에게 "예외를 다 막아줘"라고 하면 8개 전부를 에러로 막는 코드를 만든다. 그러면 사용자는 아무것도 못 한다. **무엇을 막고 무엇을 허용할지는 사람의 판단**이다.',
      },
    ],
    explain: [
      { type: 'h', text: '왜 인수인계가 캘린더 위에 있어야 하는가' },
      {
        type: 'p',
        text: '인수인계 앱을 따로 만들면 "무엇을 인계할지"를 사람이 기억해서 입력해야 한다. 휴가 전날 밤에 하는 그 작업은 항상 누락된다. **캘린더 위에 있으면 "이 기간에 있던 일들" 목록이 자동으로 나온다.** 사람은 고르고 메모만 붙이면 된다.',
      },
      {
        type: 'flow',
        title: '인수인계가 만들어지는 흐름',
        steps: [
          '부재 기간 입력',
          '**기간 내 일정 자동 수집**',
          '체크로 대상 선택',
          '메모 작성 (템플릿 제공)',
          '인수자 지정 → 발송',
        ],
      },
      { type: 'h', text: '두 사람이 관여하는 기능의 설계 원칙' },
      {
        type: 'table',
        head: ['원칙', '이유'],
        rows: [
          ['상태를 명시적으로 정의한다', '"보냈는데 봤는지 모르겠다"가 인수인계 실패의 대부분'],
          ['확인은 대신할 수 없다', '인수자만 ACCEPTED로 만들 수 있다. 대리 확인을 허용하면 기록이 무의미해진다'],
          ['각 전이를 기록한다', '"저는 못 받았습니다"라는 분쟁이 실제로 생긴다. 감사 로그가 답이다'],
          ['막힌 상태를 표현할 수 있게 한다', 'TODO/DONE만 있으면 "못 하고 있음"을 표현할 방법이 없어 침묵한다'],
          ['되돌릴 수 없는 전이를 최소화한다', 'DONE 이후 읽기 전용은 의도적이지만, 그 전 단계는 유연하게'],
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: '"막힘(BLOCKED)" 상태의 가치',
        text: '많은 업무 도구가 TODO / DONE만 제공한다. 그러면 진행이 막힌 사람은 아무 표시도 못 하고 침묵한다. **BLOCKED 상태 하나를 추가하는 것**이 조직의 정보 흐름을 바꾼다. 인계자는 휴가 중에도 "막힌 항목이 있다"는 걸 알 수 있고, 돌아와서 놀라지 않는다.',
      },
      { type: 'h', text: '감사 로그 — 왜 별도 테이블인가' },
      {
        type: 'p',
        text: '"인수인계 확인 여부"는 `Handover.status` 만 봐도 알 수 있다. 그런데 `AuditLog` 를 따로 두는 이유는 **상태는 덮어써지지만 이력은 남아야** 하기 때문이다. 누가 언제 확인했고, 그 전에 몇 번 항목이 바뀌었는지는 상태 컬럼 하나로 표현할 수 없다.',
      },
      {
        type: 'code',
        lang: 'typescript',
        code: `// 상태만 있으면: "확인됨" — 언제? 누가? 그 전에 뭐가 바뀌었나? 알 수 없다
handover.status === 'ACCEPTED'

// 감사 로그가 있으면: 전체 이야기가 남는다
// 08-17 14:02  handover.create   홍길동 → 김철수 (항목 4개)
// 08-17 14:30  item.add          홍길동 (항목 5개)
// 08-18 09:11  handover.accept   김철수
// 08-20 16:40  item.status       김철수 (A고객 대응 → BLOCKED "담당자 연락 안 됨")
// 08-25 10:02  handover.done     홍길동`,
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '개인정보와 감사 로그',
        text: '감사 로그는 "누가 무엇을 했는지"를 남기는 기록이다. 필요한 최소 정보만 남기고(내용 전문이 아니라 항목 수·상태), 보관 기간을 정해야 한다. 사내 개인정보 정책과 충돌하지 않는지 확인이 필요하다 — 이건 개발자가 혼자 결정할 사안이 아니다.',
      },
      {
        type: 'callout',
        tone: 'dx',
        text: '인수인계 정책(승인 필요 여부, 팀장 열람 범위, 기록 보관 기간)은 조직 규정과 연결됩니다. 정책을 정해서 오시면 dX팀에서 구현해 드립니다.',
      },
    ],
    checklist: [
      '부재 기간을 입력하면 그 기간 내 내 일정이 자동으로 목록에 나온다',
      '항목별로 다른 인수자를 지정할 수 있다',
      '인수자로 로그인해서 확인 버튼을 누르면 상태가 ACCEPTED로 바뀐다',
      '인계자가 대신 확인하려 하면 거부된다',
      '항목을 "막힘"으로 표시하면 이유를 적을 수 있고 인계자에게 보인다',
      '부재 기간이 지난 미확인 인수인계에 경고가 표시된다',
      '인수자를 자기 자신으로 지정할 수 없다',
      '상태 전이가 감사 로그에 남는다',
      '예외 상황 8개를 점검하고 4개를 코드로 막았다',
    ],
    demo: {
      kind: 'handover',
      hint: '인계자·인수자 시점을 바꿔가며 같은 인수인계를 보라. 인계자로는 확인 버튼이 없고, 항목을 "막힘"으로 표시하면 사유를 적게 되고, 모든 전이가 감사 로그에 남는다.',
    },
  },
]
