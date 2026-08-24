/** 교육 콘텐츠를 표현하는 블록들. 마크다운 파서 없이 안전하게 렌더링한다. */
export type Block =
  | { type: 'h'; text: string }
  | { type: 'p'; text: string }
  | { type: 'ul'; items: string[] }
  | { type: 'ol'; items: string[] }
  | { type: 'code'; lang?: string; filename?: string; code: string }
  | { type: 'callout'; tone: 'info' | 'tip' | 'warn' | 'dx'; title?: string; text: string }
  | { type: 'table'; head: string[]; rows: string[][] }
  | { type: 'flow'; title?: string; steps: string[] }
  | { type: 'files'; title?: string; tree: string }

/** 단계 안에 붙는 완성 데모 */
export type DemoKind =
  | 'calendar'
  | 'weekly'
  | 'present'
  | 'handover'
  | 'integrations'
  /** 실제 구글 캘린더에 붙어서 동기화를 직접 확인하는 데모 */
  | 'google-live'

export interface StepDemo {
  kind: DemoKind
  /** 데모 탭에 붙는 한 줄 설명 — 이 단계에서 무엇을 보라는 것인지 */
  hint: string
}

/** 학습자가 AI에게 복사·붙여넣기 할 프롬프트 */
export interface Prompt {
  id: string
  label: string
  /** 이 프롬프트를 언제 쓰는지 한 줄 설명 */
  when: string
  body: string
  /** 프롬프트를 쓸 때 조심할 점 */
  tips?: string[]
}

export interface Step {
  /** "00" ~ "14" */
  id: string
  slug: string
  part: string
  title: string
  tagline: string
  /** 예상 소요 시간 */
  duration: string
  level: '입문' | '기본' | '심화'
  /** 학습 목표 */
  goals: string[]
  /** 이 스텝이 끝나면 실제로 손에 남는 결과물 */
  deliverables: string[]
  prompts: Prompt[]
  /** 프롬프트를 실행하면 나오는 예시 결과물 (기다리기 싫은 사람을 위한 미리보기) */
  sample: Block[]
  /** 원리 설명 — dX팀이 대신 해줘도 원리는 알아야 하니까 */
  explain: Block[]
  /** 스스로 확인하는 체크리스트 */
  checklist: string[]
  /** dX팀에 넘겨도 되는 부분 */
  dxNote?: string
  /** 이 단계에서 만들 결과물의 동작하는 데모. 프롬프트를 치기 전에 먼저 본다. */
  demo?: StepDemo
}
