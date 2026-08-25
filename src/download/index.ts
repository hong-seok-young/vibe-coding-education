import raw from './app.html?raw'
import type { DemoKind } from '../content/types'

/** 다운로드 파일 안에서 켜지는 화면 */
export type AppTab = 'calendar' | 'weekly' | 'present' | 'handover'

export interface Exercise {
  /** 무엇을 바꾸는 실습인지 */
  label: string
  /** AI에게 그대로 붙여넣을 문장 */
  prompt: string
}

export interface DownloadApp {
  id: string
  title: string
  filename: string
  /** 한 줄 설명 */
  summary: string
  /** 이 파일 안에 들어 있는 기능 */
  contains: string[]
  tabs: AppTab[]
  /** 받아서 AI에게 시켜볼 과제 */
  exercises: Exercise[]
}

/** 어떤 파일에나 붙는 앞머리 — AI가 파일의 성격을 먼저 알게 한다 */
const PREFACE =
  '첨부한 HTML 파일은 파일 하나로 동작하는 업무 관리 웹앱입니다. ' +
  '빌드 도구·서버·외부 라이브러리 없이 순수 HTML·CSS·자바스크립트로만 되어 있고, ' +
  '데이터는 브라우저 localStorage 에 저장됩니다.\n' +
  '아래 요청을 반영해서 **파일 하나짜리 HTML 로 통째로** 다시 주세요. ' +
  '기존 구조(주석으로 나뉜 1~6번 구역)와 한국어 주석은 유지하고, 바꾼 곳에는 무엇을 왜 바꿨는지 주석을 남겨 주세요.\n\n요청:\n'

const ex = (label: string, body: string): Exercise => ({ label, prompt: PREFACE + body })

export const DOWNLOADS: DownloadApp[] = [
  {
    id: 'workspace',
    title: '업무 관리 앱 (전체)',
    filename: 'work-manager.html',
    summary: '캘린더 · 주간보고 · 발표 모드 · 인수인계가 모두 들어간 파일 하나.',
    contains: [
      '업무 캘린더 — 월·주 보기, 일정 추가·수정·삭제, 분류별 색, 비공개 일정',
      '주간보고 — 캘린더 일정을 자동 집계, 다음 주 계획·이슈 작성, 마크다운 복사',
      '발표 모드 — 팀원별 보고를 한 명씩 넘기며 보여주기',
      '인수인계 — 항목별 상태·확인 체크, 진행률, 마크다운 복사',
      '브라우저 저장소에 자동 저장 · 다크 모드 자동 전환',
    ],
    tabs: ['calendar', 'weekly', 'present', 'handover'],
    exercises: [
      ex('분류 추가하기', '일정 분류에 "출장"을 색 #c2410c 로 추가해 주세요. 캘린더 색과 주간보고 집계에도 자동으로 반영되어야 합니다.'),
      ex('검색 넣기', '캘린더 화면 위에 검색창을 넣어 주세요. 글자를 치면 제목에 그 글자가 들어간 일정만 남고, 지우면 다시 전부 보여야 합니다.'),
      ex('집계 규칙 바꾸기', '주간보고에서 30분 이하로 짧은 일정은 목록에 넣지 말고, 대신 맨 아래에 "짧은 일정 N건 (총 M분)" 한 줄로만 보여 주세요.'),
      ex('내보내기 추가', '주간보고 화면에 "CSV로 내려받기" 버튼을 넣어 주세요. 분류, 내용, 소요시간(분) 세 칸짜리 CSV 파일이 받아져야 하고 엑셀에서 한글이 깨지지 않아야 합니다.'),
    ],
  },
  {
    id: 'calendar',
    title: '업무 캘린더',
    filename: 'work-calendar.html',
    summary: '캘린더 화면만 켜 둔 파일. 일정 추가·수정·삭제를 손보는 실습에 쓴다.',
    contains: [
      '월 보기 · 주 보기 전환 (단축키 M · W)',
      '빈 칸 클릭으로 일정 추가, 일정 클릭으로 수정·삭제',
      '분류별 색, 팀 공개 / 비공개 구분',
      '주 보기에서 겹치는 일정 좌우 분할',
    ],
    tabs: ['calendar'],
    exercises: [
      ex('종일 일정', '일정 편집 창에 "종일" 체크박스를 넣어 주세요. 체크하면 시작·종료 시간 칸이 사라지고, 월 보기에서는 시간 없이 제목만 보여야 합니다.'),
      ex('반복 일정', '"매주 반복" 체크박스를 넣어 주세요. 체크하고 저장하면 같은 요일·같은 시간으로 4주치 일정이 한 번에 만들어지게 해 주세요.'),
      ex('일 보기 추가', '월·주 보기 옆에 "일" 보기를 추가해 주세요. 하루치 시간표를 크게 보여주고, 단축키는 D 로 해 주세요.'),
    ],
  },
  {
    id: 'weekly',
    title: '주간보고 · 발표 모드',
    filename: 'weekly-report.html',
    summary: '일정이 보고서로 바뀌는 규칙과 회의용 발표 화면만 켜 둔 파일.',
    contains: [
      '주 단위 이동, 분류별 시간 비율 막대',
      '같은 제목 자동 합치기 · 비공개 일정 제외',
      '다음 주 계획 · 이슈 작성 후 자동 저장',
      '마크다운 복사 · 발표 모드(← → 로 사람 넘기기, 전체화면)',
    ],
    tabs: ['weekly', 'present'],
    exercises: [
      ex('보고서 서식 바꾸기', '마크다운 복사 내용을 우리 회사 양식에 맞춰 주세요. 맨 위에 "부서 / 이름 / 기간" 표를 넣고, 한 일은 표(분류·내용·시간) 형태로 바꿔 주세요.'),
      ex('지난주와 비교', '주간보고 위에 지난주 대비 총 업무시간이 몇 % 늘었는지 줄었는지 한 줄로 보여 주세요.'),
      ex('발표 타이머', '발표 모드에 사람당 3분 타이머를 넣어 주세요. 남은 시간이 30초 아래로 내려가면 숫자가 빨간색으로 바뀌게 해 주세요.'),
    ],
  },
  {
    id: 'handover',
    title: '인수인계',
    filename: 'handover.html',
    summary: '부재 기간 업무를 넘겨주고 받았는지 확인하는 화면만 켜 둔 파일.',
    contains: [
      '부재 기간 · 사유 · 인수자 지정',
      '항목별 상태(대기·진행중·막힘·완료)와 인수 확인 체크',
      '확인 진행률 막대',
      '인수인계서 마크다운 복사',
    ],
    tabs: ['handover'],
    exercises: [
      ex('항목 추가 기능', '인수인계 항목을 화면에서 직접 추가·삭제할 수 있게 해 주세요. "+ 항목 추가" 버튼과 제목·상세 입력 칸이 필요합니다.'),
      ex('막힘 사유 받기', '상태를 "막힘"으로 바꾸면 사유를 반드시 적게 하고, 적은 사유를 항목 아래에 빨간 글씨로 보여 주세요.'),
      ex('기록 남기기', '누가 언제 무엇을 바꿨는지 화면 아래에 기록으로 쌓아 주세요. 상태 변경과 확인 체크가 모두 기록에 남아야 합니다.'),
    ],
  },
]

export const findDownload = (id: string) => DOWNLOADS.find((d) => d.id === id)

/** 각 단계의 데모 아래에 어떤 파일을 붙일지 */
const BY_DEMO: Partial<Record<DemoKind, string>> = {
  calendar: 'calendar',
  weekly: 'weekly',
  present: 'weekly',
  handover: 'handover',
  integrations: 'workspace',
}

export const downloadForDemo = (kind: DemoKind) => {
  const id = BY_DEMO[kind]
  return id ? findDownload(id) : undefined
}

/** 템플릿에 화면 구성과 제목을 채워 완성된 HTML 문자열을 만든다 */
export function buildHtml(app: DownloadApp): string {
  return raw.replaceAll('__TABS__', JSON.stringify(app.tabs)).replaceAll('__TITLE__', app.title)
}

/** 브라우저에 파일로 내려준다 */
export function saveHtml(app: DownloadApp) {
  const blob = new Blob([buildHtml(app)], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = app.filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  // 즉시 지우면 사파리에서 저장이 취소되는 경우가 있어 조금 뒤에 정리한다
  setTimeout(() => URL.revokeObjectURL(url), 4000)
}

/** 받기 전에 동작을 확인할 수 있게 새 탭에서 열어 준다 */
export function previewHtml(app: DownloadApp) {
  const blob = new Blob([buildHtml(app)], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  window.open(url, '_blank', 'noopener')
  setTimeout(() => URL.revokeObjectURL(url), 60000)
}

/** 파일 크기를 "24 kB" 처럼 */
export function sizeOf(app: DownloadApp): string {
  return Math.round(new Blob([buildHtml(app)]).size / 1024) + ' kB'
}
