import type { Step } from '../types'

export const part4: Step[] = [
  {
    id: '11',
    slug: 'works-ai',
    part: 'PART 4 · AI · 인증 · 배포',
    title: '웍스 AI API 연동',
    tagline: '주간보고 요약과 자연어 일정 입력을 AI에게',
    duration: '60분',
    level: '심화',
    goals: [
      'API 키를 안전하게 다루는 구조(서버 프록시)를 만든다',
      'AI 기능을 "실패해도 앱이 멈추지 않게" 설계한다',
      '어떤 기능에 AI를 쓰고 어떤 기능에 쓰지 말아야 하는지 판단한다',
    ],
    deliverables: [
      '/api/ai/* 서버 프록시 (키는 서버에만)',
      '주간보고 요약 생성 버튼',
      '자연어 일정 입력 (정규식으로 못 잡는 문장 처리)',
      '실패·지연·비용에 대한 방어 코드',
    ],
    prompts: [
      {
        id: 'ai-proxy',
        label: 'AI 프록시 계층 만들기',
        when: 'AI 기능을 붙이기 전에 반드시 이것부터.',
        body: `사내에서 제공하는 "웍스 AI" API 키가 있습니다. 이걸 앱에 연동합니다.
아직 정확한 API 스펙은 확인 중이므로, **OpenAI 호환 형태(/chat/completions)를 가정**하고
나중에 실제 스펙에 맞게 한 파일만 고치면 되는 구조로 만들어주세요.

## 절대 조건
1. API 키는 **서버에서만** 사용한다. 브라우저로 절대 전달되지 않는다
2. 클라이언트는 우리 서버의 /api/ai/* 만 호출한다 (외부 API를 직접 호출하지 않는다)
3. 로그에 프롬프트 전문과 사용자 데이터를 남기지 않는다 (토큰 수·소요시간·성공여부만)

## 구현
1. src/server/ai/client.ts — 외부 API 호출을 감싸는 유일한 지점
   - baseUrl / apiKey / model 은 환경변수에서
   - 타임아웃 (기본 20초), 재시도 (429·5xx만, 최대 2회, 지수 백오프)
   - 응답 형식 검증 (기대한 모양이 아니면 에러)
   - 실제 스펙이 다를 경우 여기만 고치면 되게 어댑터 형태로
2. src/server/ai/prompts.ts — 프롬프트 템플릿을 코드가 아니라 데이터로 분리
   - 주간보고 요약 / 이슈 추출 / 자연어 일정 파싱
3. /api/ai/[task]/route.ts — 인증된 사용자만, 작업별 요청 제한(rate limit)
   - 같은 사용자가 1분에 10회 초과 호출하면 거부
4. 사용량 기록: 사용자별·기능별 호출 수와 토큰 수를 DB에 기록 (비용 추적)

## 방어 설계
- AI 호출이 실패하면 → 기능은 "요약 없이" 정상 동작한다. 앱 전체가 멈추지 않는다
- AI 호출이 느리면 → 화면에 진행 표시, 취소 가능
- AI 응답이 형식에 안 맞으면 → 사람이 쓴 것처럼 그대로 넣지 않고, 실패로 처리

먼저 이 구조를 그림으로 설명하고(어떤 요청이 어디를 지나는지), 그 다음 코드를 주세요.`,
        tips: [
          '**"실제 스펙은 확인 중"이라고 솔직히 말하는 것이 좋은 프롬프트다.** AI가 어댑터 구조로 만들어주고, 나중에 파일 하나만 고치면 된다.',
          '"API 키는 서버에만"을 명시하지 않으면, AI는 종종 클라이언트에서 직접 호출하는 코드를 만든다. 그러면 **키가 브라우저에 노출된다.**',
          '요청 제한(rate limit)은 처음부터 넣는다. 없으면 실수 한 번으로 하루치 비용이 날아갈 수 있다.',
        ],
      },
      {
        id: 'ai-features',
        label: 'AI 기능 3개 구현',
        when: '프록시 계층이 동작한 다음.',
        body: `프록시 위에 실제 기능을 만들어주세요.

## 기능 1: 주간보고 요약
- 입력: 이번 주 보고 항목들 (한 일 / 다음 주 / 이슈)
- 출력: 3~4문장 요약. 팀장이 먼저 읽는 문장
- 규칙:
  - 항목에 없는 내용을 새로 만들어내지 않는다 (없으면 "해당 없음")
  - 숫자(시간·건수)는 입력값 그대로만 사용
  - 존댓말 없는 보고체 ("~함", "~예정")
- 결과는 사용자가 수정 가능하고, 수정하면 다시 생성해도 덮어쓰지 않는다

## 기능 2: 자연어 일정 입력
- 입력: "다음주 화요일 오후 2시부터 4시까지 김부장님과 3분기 계획 리뷰"
- 출력: JSON — { title, startAt, endAt, allDay, categoryHint }
- 규칙:
  - **응답을 반드시 JSON 스키마로 검증** (zod). 검증 실패 시 정규식 파서로 폴백
  - 오늘 날짜와 타임존을 프롬프트에 함께 전달 ("다음주 화요일"을 계산할 수 있게)
  - 사용자에게 결과를 **저장 전에 보여주고 확인받는다** (AI가 날짜를 틀릴 수 있다)

## 기능 3: 인수인계 메모 초안
- 입력: 일정 제목 + 카테고리 + 최근 관련 일정들
- 출력: "진행 상황 / 다음 할 일 / 주의사항" 형태의 초안
- 규칙: 사실을 만들어내지 말고, 정보가 부족하면 빈 항목으로 남긴다

## 공통
- 각 기능마다 프롬프트 전문을 src/server/ai/prompts.ts 에 상수로
- 개인정보·고객명이 프롬프트에 들어가는 경우를 검토하고, 필요하면 마스킹 옵션 제공
- 각 기능이 실패했을 때 사용자에게 보이는 화면을 정의`,
        tips: [
          '**"응답을 JSON 스키마로 검증"은 타협 불가다.** AI는 때때로 설명 문장을 섞어 보내거나 필드를 빼먹는다. 검증 없이 DB에 넣으면 데이터가 오염된다.',
          '"저장 전에 사용자 확인"도 필수다. AI가 "다음주 화요일"을 잘못 계산해 일정이 엉뚱한 날에 잡히면, 그 신뢰는 회복이 안 된다.',
          '기능 1의 "없는 내용을 만들어내지 않는다"는 지시는 넣어도 100% 지켜지지 않는다. 그래서 사람이 수정 가능해야 한다.',
        ],
      },
    ],
    sample: [
      { type: 'h', text: '요청이 지나가는 길' },
      {
        type: 'flow',
        steps: [
          '브라우저',
          '**우리 서버** `/api/ai/summarize`',
          '인증·요청제한 확인',
          '프롬프트 조립 (템플릿 + 데이터)',
          '웍스 AI API (키는 여기서만 사용)',
          '응답 검증 (zod)',
          '브라우저로 결과만 반환',
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '브라우저에서 직접 호출하면 안 되는 이유',
        text: '브라우저 코드에 API 키를 넣으면, 개발자 도구의 네트워크 탭이나 소스 파일에서 **누구나 키를 꺼낼 수 있다.** 그 키로 외부에서 무제한 호출이 가능해지고, 비용은 우리 회사가 낸다. "환경변수에 넣었으니 안전하다"는 착각이 흔하다 — `NEXT_PUBLIC_` 이 붙은 환경변수는 브라우저로 그대로 나간다.',
      },
      { type: 'h', text: 'AI 클라이언트 (유일한 외부 호출 지점)' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/ai/client.ts',
        code: `import { z } from 'zod'

const BASE = process.env.WORKS_AI_BASE_URL!
const KEY = process.env.WORKS_AI_API_KEY!
const MODEL = process.env.WORKS_AI_MODEL ?? 'default'

/**
 * 웍스 AI 호출을 감싸는 유일한 지점.
 * 실제 API 스펙이 OpenAI 호환이 아니라면 이 파일만 고치면 된다.
 */
const ResponseShape = z.object({
  choices: z.array(z.object({ message: z.object({ content: z.string() }) })).min(1),
  usage: z.object({ prompt_tokens: z.number(), completion_tokens: z.number() }).optional(),
})

export interface AiResult {
  text: string
  promptTokens: number
  completionTokens: number
  ms: number
}

export async function callAi(
  system: string,
  user: string,
  opts: { maxTokens?: number; temperature?: number; timeoutMs?: number } = {},
): Promise<AiResult> {
  const started = Date.now()
  const timeoutMs = opts.timeoutMs ?? 20_000

  for (let attempt = 0; attempt <= 2; attempt++) {
    let res: Response
    try {
      res = await fetch(BASE + '/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer ' + KEY,     // 키는 이 줄에서만 등장한다
        },
        body: JSON.stringify({
          model: MODEL,
          messages: [
            { role: 'system', content: system },
            { role: 'user', content: user },
          ],
          max_tokens: opts.maxTokens ?? 800,
          temperature: opts.temperature ?? 0.2,   // 업무 문서는 낮게 — 매번 다른 문장이 나오면 안 된다
        }),
        signal: AbortSignal.timeout(timeoutMs),
      })
    } catch {
      // 타임아웃·네트워크 오류. 마지막 시도였으면 포기한다.
      if (attempt === 2) throw new AiUnavailable('AI 서버에 연결할 수 없습니다')
      await sleep(2 ** attempt * 800)
      continue
    }

    if (res.status === 429 || res.status >= 500) {
      if (attempt === 2) throw new AiUnavailable('AI 서버가 응답하지 않습니다')
      await sleep(2 ** attempt * 800)
      continue
    }
    if (!res.ok) {
      // 4xx는 재시도해도 같은 결과다. 단, 본문에 키가 섞여 나올 수 있으니 그대로 로그에 남기지 않는다.
      throw new AiUnavailable('AI 요청이 거부되었습니다 (' + res.status + ')')
    }

    const parsed = ResponseShape.safeParse(await res.json())
    if (!parsed.success) throw new AiUnavailable('AI 응답 형식이 올바르지 않습니다')

    return {
      text: parsed.data.choices[0].message.content.trim(),
      promptTokens: parsed.data.usage?.prompt_tokens ?? 0,
      completionTokens: parsed.data.usage?.completion_tokens ?? 0,
      ms: Date.now() - started,
    }
  }
  throw new AiUnavailable('AI 호출 실패')
}

/** AI를 못 쓰는 상황을 명시적인 타입으로 만든다. 호출부가 "없으면 없는 대로" 처리할 수 있게. */
export class AiUnavailable extends Error {}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))`,
      },
      { type: 'h', text: '프롬프트를 코드가 아니라 데이터로' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/ai/prompts.ts',
        code: `export const WEEKLY_SUMMARY_SYSTEM = [
  '당신은 사내 업무 주간보고를 요약하는 도구입니다.',
  '',
  '규칙:',
  '1. 입력에 없는 사실을 절대 추가하지 않는다. 정보가 없으면 해당 항목을 생략한다.',
  '2. 숫자(시간, 건수)는 입력에 있는 값만 그대로 사용한다. 계산하거나 추정하지 않는다.',
  '3. 3~4문장. 보고체("~함", "~예정")를 쓰고 존댓말과 인사말은 쓰지 않는다.',
  '4. 이슈가 있으면 마지막 문장에 반드시 포함한다.',
  '5. 출력은 요약 문장만. 제목·머리말·설명을 붙이지 않는다.',
].join('\\n')

/** 자연어 일정 파싱. 반드시 JSON만 반환하도록 강제하고, 결과는 zod로 검증한다. */
export const EVENT_PARSE_SYSTEM = [
  '당신은 한국어 문장에서 일정 정보를 추출하는 파서입니다.',
  'JSON 객체 하나만 출력하고, 그 외 어떤 문자도 출력하지 않습니다.',
  '',
  '스키마:',
  '{ "title": string, "startAt": ISO8601, "endAt": ISO8601, "allDay": boolean,',
  '  "categoryHint": "개발"|"회의"|"지원"|"교육"|"기타", "confidence": 0~1 }',
  '',
  '규칙:',
  '1. 상대 날짜("다음주 화요일")는 주어진 기준 시각과 타임존으로 계산한다.',
  '2. 시간이 없으면 allDay=true.',
  '3. 종료 시각이 없으면 회의는 1시간, 그 외는 2시간으로 둔다.',
  '4. title 에서 날짜·시간 표현은 제거하고 사람 이름과 업무 내용만 남긴다.',
  '5. 확실하지 않으면 confidence 를 낮게 준다. 추측으로 값을 채우지 않는다.',
].join('\\n')

export function eventParseUser(input: string, nowIso: string, tz: string) {
  return [
    '기준 시각: ' + nowIso,
    '타임존: ' + tz,
    '입력 문장: ' + input,
  ].join('\\n')
}`,
      },
      { type: 'h', text: 'AI 응답을 신뢰하지 않는 방법' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/ai/parseEvent.ts',
        code: `import { z } from 'zod'
import { callAi, AiUnavailable } from './client'
import { EVENT_PARSE_SYSTEM, eventParseUser } from './prompts'
import { parseQuickInput } from '@/lib/parseQuickInput'   // STEP 05의 정규식 파서

const Parsed = z.object({
  title: z.string().min(1).max(200),
  startAt: z.coerce.date(),
  endAt: z.coerce.date(),
  allDay: z.boolean(),
  categoryHint: z.enum(['개발', '회의', '지원', '교육', '기타']),
  confidence: z.number().min(0).max(1),
})

/**
 * 자연어 → 일정. 3단 방어:
 *  ① AI 응답이 JSON이 아니거나 스키마에 안 맞으면 → 정규식 파서로 폴백
 *  ② 날짜가 비상식적이면(과거 1년 이전, 미래 2년 이후) → 폴백
 *  ③ confidence 가 낮으면 → 결과를 쓰되 화면에 "확인 필요" 표시
 */
export async function parseEventText(input: string, tz = 'Asia/Seoul') {
  try {
    const res = await callAi(
      EVENT_PARSE_SYSTEM,
      eventParseUser(input, new Date().toISOString(), tz),
      { maxTokens: 300, temperature: 0 },
    )

    // AI가 코드블록으로 감싸 보내는 경우가 흔하다. 관대하게 벗겨낸다.
    const json = res.text.replace(/^\\u0060{3}(?:json)?/i, '').replace(/\\u0060{3}$/,'').trim()
    const parsed = Parsed.safeParse(JSON.parse(json))
    if (!parsed.success) return fallback(input, 'schema')

    const { startAt, endAt } = parsed.data
    const yearMs = 365 * 24 * 3600 * 1000
    if (
      endAt <= startAt ||
      startAt.getTime() < Date.now() - yearMs ||
      startAt.getTime() > Date.now() + 2 * yearMs
    ) {
      return fallback(input, 'sanity')          // 날짜가 말이 안 된다
    }

    return {
      ...parsed.data,
      source: 'ai' as const,
      needsConfirm: parsed.data.confidence < 0.7,
    }
  } catch (e) {
    if (e instanceof AiUnavailable) return fallback(input, 'unavailable')
    return fallback(input, 'error')
  }
}

function fallback(input: string, reason: string) {
  const q = parseQuickInput(input)
  return { ...toEvent(q), source: 'regex' as const, needsConfirm: true, fallbackReason: reason }
}`,
      },
      {
        type: 'callout',
        tone: 'tip',
        title: '이 코드의 핵심은 AI 호출이 아니라 폴백이다',
        text: '실제 코드에서 AI 호출은 5줄이고, 나머지 30줄은 **AI를 믿지 않는 코드**다. 이게 AI 기능을 실무에 넣는 일의 실체다. "AI가 알아서 해줄 것"이라는 가정 위에 만든 기능은 반드시 어느 날 조용히 망가진다.',
      },
      { type: 'h', text: '생성된 요약 예시' },
      {
        type: 'code',
        lang: 'text',
        filename: 'AI 요약 결과',
        code: `이번 주 캘린더 앱 개발에 22시간을 투입해 월/주 뷰와 일정 CRUD를 완료함.
구글 캘린더 연동은 토큰 암호화까지 적용했고 동기화 검증이 남음.
회의는 9시간 30분(전체 25%)으로 연동 정책 논의가 비중을 차지함.
구글 OAuth 앱 심사 지연 시 8월 말 배포 일정에 영향이 있어 확인이 필요함.`,
      },
    ],
    explain: [
      { type: 'h', text: 'AI를 써야 하는 기능과 쓰면 안 되는 기능' },
      {
        type: 'table',
        head: ['기능', 'AI 적합도', '이유'],
        rows: [
          ['주간보고 요약 문장 만들기', '✅ 적합', '정답이 하나가 아니고, 틀려도 사람이 고치면 된다'],
          ['자연어 일정 입력', '✅ 적합 (확인 절차 필수)', '규칙으로 못 잡는 표현이 많다. 단 결과를 사람이 확인'],
          ['인수인계 메모 초안', '✅ 적합', '빈 화면보다 초안이 낫다'],
          ['업무 시간 집계', '❌ 부적합', '**계산은 코드로 한다.** AI에게 더하기를 시키면 틀린다'],
          ['권한 판단 (이 사람이 볼 수 있나)', '❌ 부적합', '보안 결정을 확률적 모델에 맡기지 않는다'],
          ['일정 중복 검사', '❌ 부적합', '규칙이 명확하면 코드가 더 빠르고 정확하고 무료다'],
          ['인사평가용 업무 분석', '⚠️ 위험', '사람에 대한 판단을 AI가 하면 안 된다. 조직 신뢰 문제'],
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '집계는 코드로',
        text: '"이번 주 총 업무 시간"을 AI에게 계산하게 하면 안 된다. 언어 모델은 산수를 잘 못하고, 틀렸는지 확인할 방법도 없다. **숫자는 코드가 계산해서 AI에게 넘겨주고, AI는 그 숫자로 문장만 만든다.** 이 경계가 흐려지면 보고서 숫자를 믿을 수 없게 된다.',
      },
      { type: 'h', text: '사내 AI를 쓰는 이유' },
      {
        type: 'table',
        head: ['', '외부 공개 AI 서비스', '사내 웍스 AI'],
        rows: [
          ['업무 데이터 전송', '외부 사업자 서버로 나간다', '사내 통제 범위'],
          ['보안 검토', '개별 승인 필요, 거절되는 경우 많음', '이미 검토된 경로'],
          ['비용', '개인 카드 / 부서별 산발적 결제', '사내 계약·정산'],
          ['접근 통제', '키 관리가 개인에게 맡겨짐', '발급·회수 절차 존재'],
        ],
      },
      {
        type: 'p',
        text: '이것이 이 스텝에서 사내 API를 쓰는 이유다. 코드 구조는 동일하다 — `client.ts` 한 파일만 바꾸면 어떤 AI 서비스든 붙는다. **어댑터 구조로 만들어두는 것**이 나중에 서비스를 바꿀 자유를 준다.',
      },
      { type: 'h', text: '비용과 지연을 설계에 넣기' },
      {
        type: 'ul',
        items: [
          '**캐시**: 같은 보고서에 대한 요약을 매번 새로 만들지 않는다. 내용이 안 바뀌면 저장된 요약을 쓴다',
          '**요청 제한**: 사용자당 분당 호출 수 제한. 버튼 연타로 100번 호출되는 것을 막는다',
          '**작업 크기 제한**: 프롬프트에 넣는 데이터 양에 상한을 둔다 (일정 500개를 다 넣지 않는다)',
          '**사용량 기록**: 누가 어떤 기능을 얼마나 쓰는지 기록. 비용이 왜 늘었는지 나중에 알 수 있다',
          '**비동기 처리**: 오래 걸리는 작업(팀 전체 요약)은 즉시 응답하지 않고 백그라운드로 돌린다',
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: '개인정보와 프롬프트',
        text: '주간보고에는 고객명·담당자명·계약 내용이 들어갈 수 있다. 이 데이터가 AI 프롬프트에 담겨 전송된다는 사실을 **사용자가 알아야 한다.** ① 어떤 데이터가 AI로 가는지 화면에 명시 ② 민감 항목 제외 옵션 제공 ③ 사내 정책상 허용 범위 확인. 이건 기술 문제가 아니라 신뢰 문제다.',
      },
      {
        type: 'callout',
        tone: 'dx',
        text: '웍스 AI의 실제 API 스펙, 키 발급, 사용량 한도, 사내 AI 이용 정책은 dX팀에 문의하세요. `client.ts` 어댑터만 교체하면 되는 구조로 만들어 두었으니 연동 자체는 짧습니다.',
      },
    ],
    checklist: [
      '브라우저 개발자 도구 네트워크 탭에서 API 키가 보이지 않는다',
      '주간보고 "AI 요약" 버튼이 동작한다',
      'AI 서버를 일부러 막아도(잘못된 URL) 주간보고 기능 자체는 정상 동작한다',
      '자연어 입력 결과가 저장 전에 확인 화면으로 표시된다',
      'AI가 이상한 JSON을 보내도 정규식 파서로 폴백된다',
      '같은 사용자가 짧은 시간에 반복 호출하면 요청 제한에 걸린다',
      '사용량(호출 수·토큰)이 DB에 기록된다',
    ],
  },

  {
    id: '12',
    slug: 'radius-auth',
    guides: ['dx-request'],
    part: 'PART 4 · AI · 인증 · 배포',
    title: 'RADIUS 로그인 연동',
    tagline: '사내 계정으로 로그인하게 만들기',
    duration: '60분',
    level: '심화',
    goals: [
      'RADIUS가 무엇이고 웹앱 인증에 어떻게 끼워 넣는지 이해한다',
      '인증(누구인가)과 세션(로그인 유지)이 다른 문제임을 안다',
      '로그인 기능에서 반드시 필요한 방어(잠금·로깅·전송 보안)를 챙긴다',
    ],
    deliverables: [
      '사번/비밀번호 로그인 화면',
      'RADIUS 인증 → 세션 발급 흐름',
      '최초 로그인 시 사용자 프로필 생성',
      '실패 잠금 · 감사 로그',
    ],
    prompts: [
      {
        id: 'radius-design',
        label: 'RADIUS 인증 설계 (코드 전)',
        when: '인증을 붙이기 전. 구조를 먼저 이해하고 확인할 것을 정리한다.',
        body: `사내 RADIUS 인증 서버로 로그인을 구현하려고 합니다. 먼저 설계와 확인 사항부터 알려주세요.

## 알려줄 것
1. RADIUS가 무엇인지 3줄 설명. 웹앱 로그인에 쓸 때의 위치 (브라우저 → 우리 서버 → RADIUS)
2. 인증 방식(PAP / CHAP / MSCHAPv2)의 차이와, 우리가 어떤 것을 쓸지 판단 기준
3. Node.js에서 RADIUS로 인증 요청을 보내는 방법과 필요한 정보 목록
   (호스트, 포트, shared secret, NAS-Identifier 등 각각이 무엇인지)
4. RADIUS는 인증만 해줍니다. 그렇다면:
   - 로그인 상태 유지(세션)는 어떻게 하는가?
   - 사용자 이름·부서 같은 정보는 어디서 얻는가?
   - 권한(팀원/팀장/관리자)은 어디서 관리하는가?
5. 이 구조에서 **보안상 반드시 지켜야 할 것** 목록
6. 사내 인프라 담당자에게 물어봐야 할 것 체크리스트
   (우리 앱 서버 IP를 RADIUS 클라이언트로 등록해야 하는지 등)

## 주의
- RADIUS 관련 정보는 환경마다 크게 다릅니다. 확실하지 않은 것은 "확인 필요"로 표시해주세요
- 아직 코드는 필요 없습니다. 구조 이해가 목적입니다`,
        tips: [
          '**이 프롬프트의 목적은 "인프라 담당자에게 물어볼 질문 목록"을 얻는 것이다.** RADIUS는 사내 설정에 따라 크게 다르므로, 코드보다 확인이 먼저다.',
          '4번이 핵심 질문이다. "RADIUS는 인증만 한다"는 사실을 이해하면 나머지 설계가 자연스럽게 풀린다.',
        ],
      },
      {
        id: 'radius-impl',
        label: '로그인 구현',
        when: 'RADIUS 접속 정보(호스트·시크릿)를 확보한 다음.',
        body: `RADIUS 로그인을 구현해주세요.

## 구조
브라우저 (사번 + 비밀번호)
  → 우리 서버 (POST /api/auth/login)
  → RADIUS 인증 요청
  → 성공 시: User 조회 또는 생성 → 세션 쿠키 발급
  → 실패 시: 실패 기록 + 일반적인 오류 메시지

## 구현
1. src/server/auth/radius.ts — RADIUS 인증 함수
   - 타임아웃 5초 (RADIUS가 응답 없으면 로그인 시도가 무한정 매달리지 않게)
   - 성공/실패/서버오류를 **구분해서** 반환 (사용자에게는 구분해서 보여주지 않음)
2. 세션: 서명된 HttpOnly · Secure · SameSite=Lax 쿠키. 만료 12시간
   - Auth.js(next-auth) Credentials Provider를 쓰거나, 직접 구현 중 무엇이 나은지 판단해서 추천해주세요
3. 최초 로그인 사용자
   - User 레코드가 없으면 생성 (사번은 RADIUS 응답 기준)
   - 이름·부서 입력 화면으로 유도, 역할은 기본 MEMBER
4. 보호
   - 같은 사번에 대해 5회 연속 실패 시 10분 잠금 (IP 기준도 별도로)
   - 로그인 성공·실패를 감사 로그에 기록 (**비밀번호는 절대 기록하지 않는다**)
   - 오류 메시지는 "사번 또는 비밀번호가 올바르지 않습니다" 하나로 통일
     (사번이 존재하는지 알려주지 않는다)
5. 모든 페이지 보호: 미들웨어로 비로그인 접근을 로그인 화면으로
   - 로그인 후 원래 가려던 페이지로 복귀
6. 로그아웃

## 절대 지켜야 할 것
- 비밀번호는 어디에도 저장하지 않는다 (DB·로그·캐시·에러 메시지)
- 비밀번호는 메모리에서 인증 직후 참조를 놓는다
- HTTPS가 아닌 환경에서는 로그인을 막거나 경고한다

마지막에 "RADIUS 서버 없이 로컬에서 개발·테스트하는 방법"도 알려주세요.`,
        tips: [
          '**"RADIUS 서버 없이 개발하는 방법"을 꼭 물어본다.** 없으면 로컬 개발이 완전히 막힌다. 보통 개발용 스텁(가짜 인증)을 만들고 환경변수로 전환한다.',
          '오류 메시지 통일은 사소해 보이지만 중요하다. "존재하지 않는 사번입니다"는 공격자에게 사번 목록을 알려주는 기능이 된다.',
          '잠금 기능을 안 넣으면 비밀번호 무한 시도가 가능하다. AI는 요청하지 않으면 이걸 넣지 않는다.',
        ],
      },
    ],
    sample: [
      { type: 'h', text: 'RADIUS의 위치' },
      {
        type: 'flow',
        steps: [
          '브라우저: 사번 + 비밀번호',
          '**우리 서버** (HTTPS로 받음)',
          'RADIUS 서버로 Access-Request',
          'Access-Accept / Access-Reject',
          '성공 → 세션 쿠키 발급',
          '이후 요청은 쿠키로 인증',
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'RADIUS는 인증만 한다',
        text: 'RADIUS는 "이 사번과 비밀번호가 맞나?"에 예/아니오만 답한다. 그 뒤의 일은 전부 우리 몫이다 — **로그인 상태 유지(세션), 사용자 정보(이름·부서), 권한(팀원/팀장)**. 그래서 우리 DB의 `User` 테이블이 여전히 필요하고, 거기에 비밀번호 컬럼만 없는 것이다.',
      },
      { type: 'h', text: 'RADIUS 인증 함수' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/auth/radius.ts',
        code: `import radius from 'radius'
import { createSocket } from 'node:dgram'

export type AuthOutcome =
  | { ok: true; username: string; attributes: Record<string, string> }
  | { ok: false; reason: 'rejected' }
  | { ok: false; reason: 'unavailable' }   // 서버 무응답 — 사용자에게는 구분해 보여주지 않지만
                                            // 운영 로그에서는 반드시 구분해야 한다

/**
 * RADIUS Access-Request 를 보내 인증을 확인한다.
 * RADIUS는 UDP 기반이라 "응답이 없음"이 흔한 실패 모드다. 타임아웃을 반드시 둔다.
 */
export async function authenticate(username: string, password: string): Promise<AuthOutcome> {
  const secret = process.env.RADIUS_SECRET!
  const host = process.env.RADIUS_HOST!
  const port = Number(process.env.RADIUS_PORT ?? 1812)

  const packet = radius.encode({
    code: 'Access-Request',
    secret,
    attributes: [
      ['User-Name', username],
      ['User-Password', password],                              // PAP: 시크릿으로 난독화되어 전송
      ['NAS-Identifier', process.env.RADIUS_NAS_IDENTIFIER!],   // "어느 앱이 묻는지" 식별
    ],
  })

  return new Promise<AuthOutcome>((resolve) => {
    const socket = createSocket('udp4')
    let settled = false

    const finish = (out: AuthOutcome) => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      socket.close()
      resolve(out)
    }

    const timer = setTimeout(() => finish({ ok: false, reason: 'unavailable' }), 5000)

    socket.on('message', (msg) => {
      try {
        const res = radius.decode({ packet: msg, secret })
        if (res.code === 'Access-Accept') {
          finish({ ok: true, username, attributes: flatten(res.attributes) })
        } else {
          finish({ ok: false, reason: 'rejected' })
        }
      } catch {
        finish({ ok: false, reason: 'unavailable' })
      }
    })

    socket.on('error', () => finish({ ok: false, reason: 'unavailable' }))
    socket.send(packet, 0, packet.length, port, host, (err) => {
      if (err) finish({ ok: false, reason: 'unavailable' })
    })
  })
  // 이 함수는 password 를 어디에도 저장하지 않고, 반환값에도 포함하지 않는다.
}`,
      },
      { type: 'h', text: '로그인 라우트 — 방어가 대부분' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/app/api/auth/login/route.ts',
        code: `import { z } from 'zod'
import { authenticate } from '@/server/auth/radius'
import { createSession } from '@/server/auth/session'
import { checkLockout, recordFailure, clearFailures } from '@/server/auth/lockout'
import { audit } from '@/server/audit'

const Body = z.object({
  employeeNo: z.string().trim().min(1).max(32),
  password: z.string().min(1).max(256),
})

export async function POST(req: Request) {
  const ip = req.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ?? 'unknown'

  const parsed = Body.safeParse(await req.json())
  if (!parsed.success) return fail()

  const { employeeNo, password } = parsed.data

  // ① 잠금 확인 — 무한 시도를 막는다. 사번 기준과 IP 기준을 따로 센다.
  const lock = await checkLockout(employeeNo, ip)
  if (lock.locked) {
    await audit('auth.locked', null, employeeNo, { ip, until: lock.until })
    return Response.json(
      { error: '로그인 시도가 많습니다. ' + lock.minutesLeft + '분 후 다시 시도해주세요.' },
      { status: 429 },
    )
  }

  // ② RADIUS 인증
  const result = await authenticate(employeeNo, password)

  if (!result.ok) {
    await recordFailure(employeeNo, ip)
    // 운영 로그에는 원인을 구분해 남긴다 (RADIUS 장애와 비밀번호 오류는 완전히 다른 사건)
    await audit('auth.fail', null, employeeNo, { ip, reason: result.reason })
    // 사용자에게는 구분하지 않는다
    return fail()
  }

  await clearFailures(employeeNo, ip)

  // ③ 사용자 레코드 확보. RADIUS는 인증만 하므로 프로필은 우리가 관리한다.
  const user = await db.user.upsert({
    where: { employeeNo },
    update: {},                                   // 기존 사용자는 아무것도 덮어쓰지 않는다
    create: { employeeNo, name: employeeNo },     // 이름은 최초 로그인 후 본인이 입력
  })

  // ④ 세션 발급
  await createSession(user.id)
  await audit('auth.success', user.id, user.id, { ip })

  return Response.json({ ok: true, needsProfile: user.name === user.employeeNo })
}

/** 실패 응답은 항상 동일하게. 사번 존재 여부를 알려주지 않는다. */
const fail = () =>
  Response.json({ error: '사번 또는 비밀번호가 올바르지 않습니다.' }, { status: 401 })`,
      },
      { type: 'h', text: '로컬 개발용 스텁' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/auth/index.ts',
        code: `import { authenticate as radiusAuth } from './radius'

/**
 * RADIUS 서버는 사내망에서만 접근된다. 로컬 개발에서는 스텁을 쓴다.
 * AUTH_MODE=stub 일 때만 동작하고, 운영 빌드에서는 아예 켜지지 않도록 막는다.
 */
export const authenticate =
  process.env.AUTH_MODE === 'stub' && process.env.NODE_ENV !== 'production'
    ? stubAuthenticate
    : radiusAuth

async function stubAuthenticate(username: string, password: string) {
  console.warn('[auth] 스텁 인증 모드입니다. 운영에서 절대 사용하지 마세요.')
  await new Promise((r) => setTimeout(r, 300))   // 실제 지연을 흉내내야 UI 문제를 발견한다
  if (password === 'devpass') {
    return { ok: true as const, username, attributes: {} }
  }
  return { ok: false as const, reason: 'rejected' as const }
}`,
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '스텁이 운영에 켜지지 않게 하는 이중 잠금',
        text: '`AUTH_MODE=stub` **그리고** `NODE_ENV !== production` 두 조건을 모두 확인한다. 환경변수 하나에만 의존하면, 배포 설정 실수 한 번으로 **누구나 devpass로 로그인 가능한 서버**가 인터넷에 열린다. 이런 종류의 이중 안전장치는 AI에게 명시적으로 요청해야 한다.',
      },
    ],
    explain: [
      { type: 'h', text: '인증 · 세션 · 인가는 다른 문제다' },
      {
        type: 'table',
        head: ['단계', '질문', '담당', '우리 코드에서'],
        rows: [
          ['인증 (Authentication)', '당신이 정말 그 사람인가?', 'RADIUS', '로그인 시 1회'],
          ['세션 (Session)', '방금 로그인한 그 사람인가?', '우리 앱 (쿠키)', '모든 요청'],
          ['인가 (Authorization)', '이걸 할 권한이 있는가?', '우리 앱 (DB의 role)', '모든 데이터 접근'],
        ],
      },
      {
        type: 'p',
        text: '이 셋을 구분하지 못하면 "RADIUS 붙였으니 보안 끝"이라고 착각한다. 실제로는 **인증은 시작일 뿐**이고, 앞선 스텝들에서 계속 강조한 "권한 검사를 서버에서" 부분이 인가에 해당한다. 로그인한 사용자가 남의 일정을 수정할 수 있다면, RADIUS는 아무 도움이 안 된다.',
      },
      { type: 'h', text: 'PAP / CHAP / MSCHAPv2' },
      {
        type: 'table',
        head: ['방식', '비밀번호 전송', '주의'],
        rows: [
          ['PAP', 'shared secret으로 난독화되어 전송', '가장 단순. RADIUS 서버가 원문 비밀번호를 알 수 있어야 함. **앱↔RADIUS 구간이 신뢰된 사내망이어야 한다**'],
          ['CHAP', '챌린지-응답 (비밀번호 자체는 전송 안 함)', '서버가 원문 비밀번호를 보관해야 하는 구조라 요즘 잘 안 씀'],
          ['MSCHAPv2', '해시 기반 챌린지-응답', 'AD 연동 환경에서 흔함. 구현 복잡도 높음'],
        ],
      },
      {
        type: 'p',
        text: '어느 것을 쓸지는 **사내 RADIUS 서버 설정이 결정한다.** 우리가 고르는 게 아니다. 그래서 첫 프롬프트가 "인프라 담당자에게 물어볼 목록"을 만드는 것이었다.',
      },
      { type: 'h', text: '왜 세션을 직접 만들지 말고 검증된 방식을 쓰는가' },
      {
        type: 'ul',
        items: [
          '**쿠키 속성**: `HttpOnly`(자바스크립트에서 못 읽음), `Secure`(HTTPS에서만), `SameSite`(다른 사이트에서의 요청 제한) — 하나만 빠져도 세션 탈취 경로가 열린다',
          '**서명**: 쿠키 내용을 사용자가 고쳐서 다른 사람이 될 수 없어야 한다',
          '**만료와 갱신**: 12시간 만료, 활동 중이면 연장. 로그아웃 시 확실히 무효화',
          '**CSRF**: 다른 사이트가 우리 앱에 요청을 보내게 만드는 공격에 대한 방어',
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '인증 코드는 AI에게 맡기고 사람이 검증해야 하는 대표 영역',
        text: 'AI는 동작하는 로그인 코드를 잘 만든다. 그런데 위 항목 중 몇 개는 조용히 빠진다 — **동작에는 영향이 없기 때문이다.** 로그인이 되니까 다 된 것처럼 보인다. 인증 코드는 반드시 사람이(또는 dX팀이) 검토해야 하는 부분이다.',
      },
      { type: 'h', text: '반드시 챙길 목록' },
      {
        type: 'table',
        head: ['항목', '안 하면'],
        rows: [
          ['HTTPS 강제', '사내망이라도 비밀번호가 평문으로 흐른다'],
          ['실패 잠금', '비밀번호 무한 시도 가능'],
          ['오류 메시지 통일', '사번 존재 여부가 노출된다'],
          ['비밀번호 로깅 금지', '로그 파일이 비밀번호 목록이 된다'],
          ['RADIUS 타임아웃', '인증 서버 장애 시 앱 전체가 매달린다'],
          ['감사 로그', '이상 로그인을 사후에 확인할 수 없다'],
          ['스텁 이중 잠금', '설정 실수로 인증 없는 서버가 열린다'],
        ],
      },
      {
        type: 'callout',
        tone: 'dx',
        text: 'RADIUS 접속 정보, 클라이언트 IP 등록, 인증 방식(PAP/MSCHAPv2) 결정, 인증 코드 보안 검토는 **dX팀·인프라팀과 함께 진행하세요.** 이 스텝은 원리 이해가 목적이고, 실제 연동은 사내 환경 정보 없이는 진행할 수 없습니다.',
      },
    ],
    checklist: [
      '스텁 모드로 로그인·로그아웃이 동작한다',
      '비로그인 상태로 /calendar 에 접근하면 로그인 화면으로 이동한다',
      '로그인 후 원래 가려던 페이지로 돌아온다',
      '5회 실패 후 잠금이 걸린다',
      '틀린 사번과 틀린 비밀번호의 오류 메시지가 동일하다',
      '로그에 비밀번호가 남지 않는다 (직접 검색해서 확인)',
      '인프라 담당자에게 물어볼 항목 목록을 만들었다',
      '스텁 모드가 운영 환경에서 켜지지 않는 것을 코드로 확인했다',
    ],
    dxNote: '이 스텝은 사내 인프라 정보가 필요합니다. RADIUS 연동은 dX팀에 요청하시는 것을 권장합니다.',
  },

  {
    id: '13',
    slug: 'coolify-deploy',
    guides: ['github-pages', 'dx-request'],
    part: 'PART 4 · AI · 인증 · 배포',
    title: 'Coolify 배포',
    tagline: '내 컴퓨터에서만 되던 것을 팀이 쓰게 만들기',
    duration: '60분',
    level: '심화',
    goals: [
      '컨테이너로 앱을 포장하고 서버에서 실행하는 흐름을 이해한다',
      '환경변수·마이그레이션·백업 같은 운영 필수 항목을 챙긴다',
      '배포가 실패했을 때 되돌리는 방법을 안다',
    ],
    deliverables: [
      'Dockerfile (멀티스테이지 빌드)',
      'Coolify 배포 설정 (환경변수, 도메인, 헬스체크)',
      '자동 마이그레이션 + 백업 계획',
    ],
    prompts: [
      {
        id: 'dockerfile',
        label: 'Dockerfile 작성',
        when: '로컬에서 앱이 정상 동작하는 상태에서.',
        body: `이 Next.js 앱을 Coolify로 배포하려고 합니다. 먼저 컨테이너 이미지를 만들어주세요.

## Dockerfile 요구사항
1. 멀티스테이지 빌드 (빌드 도구가 최종 이미지에 남지 않게)
2. Next.js standalone 출력 사용 (이미지 크기 최소화)
3. node_modules 캐시를 활용해 재빌드가 빠르게
4. **root가 아닌 사용자로 실행**
5. Prisma Client 생성 단계 포함
6. 컨테이너 시작 시 DB 마이그레이션 자동 실행 (실패하면 앱을 띄우지 않는다)
7. 헬스체크 엔드포인트 (/api/health) — DB 연결까지 확인
8. .dockerignore (node_modules, .next, .env, .git 제외)

## 함께 알려줄 것
- next.config.js 에 필요한 설정
- 이미지 빌드·로컬 실행 테스트 명령어
- 최종 이미지 크기 예상치
- 각 단계가 왜 필요한지 주석

그리고 "빌드 시점 환경변수"와 "실행 시점 환경변수"의 차이를 설명해주세요.
Next.js에서 이걸 혼동하면 어떤 문제가 생기는지 구체적으로.`,
        tips: [
          '**"root가 아닌 사용자로 실행"을 안 적으면 AI는 root로 돌리는 Dockerfile을 만든다.** 컨테이너가 뚫렸을 때 피해 범위가 달라진다.',
          '"마이그레이션 실패 시 앱을 띄우지 않는다"는 중요하다. 구조가 안 맞는 DB에 앱이 붙으면 데이터가 깨진다.',
          '빌드/실행 시점 환경변수 구분은 Next.js에서 가장 흔한 배포 사고 원인이다.',
        ],
      },
      {
        id: 'coolify',
        label: 'Coolify 배포 설정',
        when: 'Dockerfile로 로컬 컨테이너 실행이 확인된 다음.',
        body: `Coolify에 배포하는 절차를 알려주세요. Coolify는 self-hosted PaaS입니다.

## 알려줄 것
1. Coolify에서 이 앱을 배포하는 순서
   - 프로젝트/리소스 생성, git 저장소 연결, 빌드 방식(Dockerfile) 지정
   - PostgreSQL 데이터베이스 리소스 추가
   - 앱과 DB를 연결하는 방법 (내부 네트워크 주소 사용)
2. 환경변수 설정
   - 어떤 값들을 넣어야 하는지 목록 (우리 .env.example 기준)
   - 로컬 값과 달라져야 하는 것들 (DATABASE_URL, AUTH_URL, 리디렉션 URI 등)
   - 비밀값을 Coolify에서 관리하는 방법
3. 도메인과 HTTPS
   - 도메인 연결, 인증서 자동 발급
   - 사내 전용으로만 접근시키려면 어떤 선택지가 있는지
4. 배포 후 확인 절차 (헬스체크, 로그 확인, 첫 로그인 테스트)
5. **되돌리기**: 배포가 잘못됐을 때 이전 버전으로 돌아가는 방법
6. DB 백업: 주기적 백업 설정과, 복구를 실제로 테스트하는 방법
7. 주기 작업: 캘린더 동기화를 정기 실행하는 방법 (Coolify 스케줄러 또는 cron)

## 배포 후 반드시 확인할 체크리스트도 만들어주세요
특히 "구글 OAuth 리디렉션 URI를 운영 도메인으로 추가"처럼 잊기 쉬운 것들.`,
        tips: [
          '**리디렉션 URI 추가를 잊는 것이 배포 후 1번 사고다.** 로컬에서는 되던 구글 로그인이 운영에서 안 된다.',
          '백업은 "설정했다"가 아니라 **"복구를 해봤다"**가 완료 기준이다. 복구 안 되는 백업은 백업이 아니다.',
          '되돌리기 방법을 배포 전에 알아둔다. 문제가 생긴 뒤에 찾으면 이미 늦다.',
        ],
      },
    ],
    sample: [
      {
        type: 'code',
        lang: 'dockerfile',
        filename: 'Dockerfile',
        code: `# ── 1단계: 의존성만 설치 (캐시 최대 활용) ──────────────
FROM node:22-alpine AS deps
WORKDIR /app
# package 파일만 먼저 복사 → 소스가 바뀌어도 이 레이어는 재사용된다
COPY package.json package-lock.json ./
RUN npm ci

# ── 2단계: 빌드 ────────────────────────────────────────
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Prisma Client 생성 — 스키마에 맞는 타입·쿼리 코드를 만든다
RUN npx prisma generate
# NEXT_PUBLIC_* 은 이 시점에 코드에 박힌다. 런타임에 바꿀 수 없다.
RUN npm run build

# ── 3단계: 실행 (빌드 도구 없는 최소 이미지) ────────────
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# root로 실행하지 않는다. 컨테이너가 뚫려도 권한을 최소화한다.
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

# standalone 출력만 복사 → 이미지가 1GB대에서 200MB대로 줄어든다
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
# 마이그레이션 실행에 필요한 것들
COPY --from=builder --chown=nextjs:nodejs /app/prisma ./prisma
COPY --from=builder --chown=nextjs:nodejs /app/node_modules/.prisma ./node_modules/.prisma
COPY --from=builder --chown=nextjs:nodejs /app/node_modules/prisma ./node_modules/prisma
COPY --from=builder --chown=nextjs:nodejs /app/node_modules/@prisma ./node_modules/@prisma

COPY --chown=nextjs:nodejs docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

USER nextjs
EXPOSE 3000
ENV PORT=3000 HOSTNAME=0.0.0.0

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \\
  CMD node -e "fetch('http://127.0.0.1:3000/api/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

ENTRYPOINT ["./docker-entrypoint.sh"]`,
      },
      {
        type: 'code',
        lang: 'bash',
        filename: 'docker-entrypoint.sh',
        code: `#!/bin/sh
set -e   # 어느 명령이든 실패하면 즉시 종료

echo "[entrypoint] DB 마이그레이션 적용..."
# migrate deploy: 이미 만들어진 마이그레이션만 적용한다.
# (migrate dev 는 개발용이며 데이터를 지울 수 있다 — 운영에서 절대 쓰지 않는다)
npx prisma migrate deploy

# 마이그레이션이 실패하면 set -e 로 여기서 멈춘다.
# 구조가 안 맞는 DB에 앱이 붙어 데이터를 깨뜨리는 것보다, 안 뜨는 게 낫다.

echo "[entrypoint] 서버 시작"
exec node server.js`,
      },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/app/api/health/route.ts',
        code: `import { db } from '@/server/db'

/**
 * 헬스체크. "프로세스가 살아 있다"가 아니라 "요청을 처리할 수 있다"를 확인해야 한다.
 * DB 연결이 끊긴 앱은 살아 있어도 아무 일도 못 한다.
 */
export async function GET() {
  try {
    await db.$queryRaw\`SELECT 1\`
    return Response.json({ ok: true, ts: new Date().toISOString() })
  } catch {
    // 실패 원인을 외부에 노출하지 않는다 (DB 호스트명 등이 새어나갈 수 있다)
    return Response.json({ ok: false }, { status: 503 })
  }
}`,
      },
      { type: 'h', text: '운영 환경변수 — 로컬과 달라지는 것들' },
      {
        type: 'table',
        head: ['변수', '로컬', '운영 (Coolify)'],
        rows: [
          ['`DATABASE_URL`', 'localhost:5432', 'Coolify 내부 DB 주소 (컨테이너 간 네트워크)'],
          ['`AUTH_URL`', 'http://localhost:3000', 'https://calendar.ourcompany.com'],
          ['`GOOGLE_REDIRECT_URI`', 'localhost 콜백', '운영 도메인 콜백 — **구글 콘솔에도 등록해야 한다**'],
          ['`AUTH_SECRET`', '아무 값', '새로 생성한 강한 값 (로컬 값 재사용 금지)'],
          ['`TOKEN_ENC_KEY`', '아무 값', '**한 번 정하면 절대 바꾸지 않는다** — 바꾸면 저장된 토큰을 못 읽는다'],
          ['`AUTH_MODE`', 'stub', '설정하지 않음 (실제 RADIUS 사용)'],
          ['`NODE_ENV`', 'development', 'production'],
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '빌드 시점 vs 실행 시점 환경변수',
        text: 'Next.js에서 `NEXT_PUBLIC_` 으로 시작하는 변수는 **빌드할 때 코드에 박힌다.** Coolify에서 값을 바꿔도 재빌드하지 않으면 반영되지 않는다. 반대로 서버 전용 변수(`DATABASE_URL` 등)는 실행 시점에 읽으므로 재시작만 하면 된다. 이 차이를 모르면 "환경변수를 바꿨는데 왜 그대로냐"로 몇 시간을 태운다.',
      },
      { type: 'h', text: '배포 후 체크리스트' },
      {
        type: 'ol',
        items: [
          '`/api/health` 가 200을 반환한다',
          'Coolify 로그에 `prisma migrate deploy` 성공 메시지가 있다',
          'HTTPS로 접속되고 인증서가 유효하다',
          '**구글 클라우드 콘솔에 운영 리디렉션 URI를 추가했다** (가장 흔한 누락)',
          '운영 도메인에서 구글 캘린더 연결이 실제로 성공한다',
          'RADIUS 로그인이 동작한다 (스텁 모드가 꺼져 있는지 확인)',
          'DB 백업이 실제로 생성되고 있다',
          '**백업으로 복구를 한 번 해봤다** (다른 DB에 복원 테스트)',
          '캘린더 동기화 스케줄러가 실제로 실행된다 (로그 확인)',
          '이전 버전으로 되돌리는 방법을 확인했다',
        ],
      },
      {
        type: 'code',
        lang: 'bash',
        filename: '백업 · 복구 (검증까지)',
        code: `# 백업 (Coolify 스케줄러에 등록하거나 서버 cron)
docker exec work-calendar-db pg_dump -U app -Fc work_calendar \\
  > /backups/wc-$(date +%Y%m%d-%H%M).dump

# ★ 복구 테스트 — 백업은 이걸 해봐야 백업이다.
#   운영 DB가 아니라 임시 DB에 복원해서 확인한다.
createdb -U app wc_restore_test
pg_restore -U app -d wc_restore_test /backups/wc-20260820-0300.dump
psql -U app -d wc_restore_test -c "SELECT count(*) FROM \\"Event\\";"
dropdb -U app wc_restore_test`,
      },
    ],
    explain: [
      { type: 'h', text: '왜 컨테이너인가' },
      {
        type: 'p',
        text: '"내 컴퓨터에서는 되는데"의 원인은 대개 환경 차이다 — Node 버전, 설치된 패키지, OS 라이브러리. 컨테이너는 **앱과 그 실행 환경을 하나로 포장**한다. 그래서 내 노트북에서 돌던 이미지가 서버에서도 똑같이 돈다.',
      },
      {
        type: 'flow',
        title: 'Coolify 배포 흐름',
        steps: [
          'git push',
          'Coolify가 감지',
          'Dockerfile로 이미지 빌드',
          '새 컨테이너 시작 (마이그레이션 → 앱)',
          '헬스체크 통과',
          '트래픽 전환',
        ],
      },
      {
        type: 'p',
        text: '헬스체크가 통과하지 못하면 트래픽이 전환되지 않고 이전 버전이 계속 돈다. 그래서 **헬스체크를 제대로 만드는 것**이 무중단 배포의 핵심이다. "프로세스가 떴다"만 확인하는 헬스체크는 DB가 끊긴 앱을 정상으로 판정한다.',
      },
      { type: 'h', text: 'Coolify를 쓰는 이유' },
      {
        type: 'table',
        head: ['', '직접 서버 운영', 'Coolify', '외부 클라우드 PaaS'],
        rows: [
          ['배포', 'ssh 접속 후 수동', 'git push 자동', 'git push 자동'],
          ['HTTPS 인증서', '직접 발급·갱신', '자동', '자동'],
          ['데이터 위치', '우리 서버', '**우리 서버**', '외부 사업자'],
          ['비용', '서버 비용만', '서버 비용만', '사용량 과금'],
          ['사내망 전용 운영', '가능', '**가능**', '어려움'],
        ],
      },
      {
        type: 'p',
        text: '사내 업무 데이터를 다루는 앱에서 "데이터가 우리 서버에 있다"는 점이 결정적이다. Coolify는 그 조건을 지키면서 외부 PaaS의 편의성을 가져온다.',
      },
      { type: 'h', text: '마이그레이션을 배포에 넣는 이유와 그 위험' },
      {
        type: 'p',
        text: '컨테이너 시작 시 `prisma migrate deploy` 를 실행하면, 코드와 DB 구조가 항상 같이 움직인다. 사람이 잊을 수 없다. 다만 알아야 할 위험이 있다.',
      },
      {
        type: 'ul',
        items: [
          '**컨테이너가 여러 개면** 동시에 마이그레이션을 시도한다. Prisma는 잠금으로 방어하지만, 인스턴스를 늘릴 때는 별도 마이그레이션 단계로 분리하는 것이 안전하다',
          '**컬럼 삭제·이름 변경은 되돌릴 수 없다.** 앱을 이전 버전으로 롤백해도 DB는 안 돌아간다. 그래서 "컬럼 추가 → 코드 배포 → 나중에 옛 컬럼 삭제" 처럼 두 번에 나눠 하는 방식(확장 후 수축)을 쓴다',
          '**큰 테이블에 인덱스를 추가하면** 그 동안 앱이 멈출 수 있다. 데이터가 커지면 별도 작업으로 분리',
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '롤백은 코드만 되돌린다',
        text: '배포 실패 시 이전 버전으로 되돌리면 코드는 돌아가지만 **DB 구조 변경은 그대로 남는다.** 그래서 "이전 코드가 새 DB 구조에서도 동작하는가"를 생각해야 한다. 컬럼을 지우는 마이그레이션이 특히 위험하다. 이 원리를 알면 왜 실무에서 마이그레이션을 조심스럽게 다루는지 이해된다.',
      },
      { type: 'h', text: '배포 = 끝이 아니라 시작' },
      {
        type: 'table',
        head: ['항목', '없으면 벌어지는 일'],
        rows: [
          ['백업 + **복구 테스트**', '사고 시 데이터가 사라진다. 복구 안 되는 백업은 아주 흔하다'],
          ['로그 확인 경로', '"동기화가 안 돼요"에 아무 답을 못 한다'],
          ['헬스체크 + 알림', '앱이 죽어 있는 걸 사용자가 먼저 알려준다'],
          ['에러 추적', '재현 안 되는 버그를 영원히 못 잡는다'],
          ['되돌리기 절차', '문제 발생 시 몇 시간을 태운다'],
        ],
      },
      {
        type: 'callout',
        tone: 'dx',
        text: 'Coolify 인스턴스 준비, 도메인·인증서, 사내망 접근 제어, 백업 정책, 모니터링 연동은 **dX팀에서 지원합니다.** 이 스텝은 "무엇이 필요한지 알고 요청할 수 있게" 하는 것이 목적입니다.',
      },
    ],
    checklist: [
      '로컬에서 docker build && docker run 으로 컨테이너가 뜬다',
      '컨테이너 실행 시 마이그레이션이 자동 적용된다',
      '/api/health 가 DB 연결까지 확인한다',
      'Coolify에 배포되어 운영 도메인으로 접속된다',
      'HTTPS 인증서가 유효하다',
      '구글 OAuth 리디렉션 URI를 운영 도메인으로 추가했다',
      '운영에서 구글 캘린더 연결이 성공한다',
      'DB 백업이 생성되고, 복구를 실제로 테스트했다',
      '이전 버전으로 되돌리는 방법을 확인했다',
      '컨테이너가 root가 아닌 사용자로 실행된다',
    ],
    dxNote: 'Coolify 인스턴스·도메인·백업 정책은 dX팀에서 세팅해 드립니다.',
  },

  {
    id: '14',
    slug: 'operate-and-next',
    guides: ['dx-request'],
    part: 'PART 4 · AI · 인증 · 배포',
    title: '운영, 그리고 dX팀에 넘기기',
    tagline: '만든 것을 계속 쓰이게 만드는 일 + 잘 요청하는 방법',
    duration: '30분',
    level: '기본',
    goals: [
      '배포 후에 실제로 필요한 운영 항목을 파악한다',
      '내가 만든 것과 dX팀에 맡길 것을 구분한다',
      'dX팀에 제대로 요청하는 문서를 작성한다',
    ],
    deliverables: [
      '운영 점검 목록',
      '다음 기능 우선순위',
      'dX팀 개발 요청서 (이 과정의 최종 산출물)',
    ],
    prompts: [
      {
        id: 'ops',
        label: '운영 준비 점검',
        when: '배포가 끝난 다음.',
        body: `배포까지 끝났습니다. 이제 팀이 실제로 쓰기 시작하면 무엇이 필요한지 점검해주세요.

## 점검 항목
1. 로그: 무엇을 남기고 있고, 무엇이 부족한가? 어디서 확인하는가?
2. 오류 추적: 사용자가 겪은 에러를 개발자가 알 수 있는가?
3. 모니터링: 앱이 죽었을 때, DB가 꽉 찼을 때 누가 어떻게 아는가?
4. 백업: 주기, 보관 기간, 복구 소요 시간
5. 성능: 일정이 사용자당 5,000개가 되면 어디가 먼저 느려지는가?
   구체적으로 어떤 쿼리·화면인지 짚어주세요
6. 보안: 지금까지 놓친 것이 있는지 전체 점검
   (권한, 입력 검증, 비밀값, 의존성 취약점)
7. 사용자 지원: 문의가 들어왔을 때 데이터를 어떻게 확인하는가? (관리자 화면 필요성)
8. 의존성 관리: 패키지 업데이트를 언제 어떻게 하는가?

각 항목마다 "지금 상태 / 필요한 것 / 우선순위(높음·중간·낮음)"로 정리해주세요.
그리고 **가장 먼저 해야 할 3가지**를 짚어주세요.`,
        tips: [
          '5번(성능)을 구체적 숫자로 물어보는 것이 중요하다. "일정 5,000개"처럼 실제 규모를 주면 AI가 구체적인 병목을 짚어준다.',
          '이 프롬프트는 배포 후 한 달 뒤에 다시 돌려보면 좋다. 실제 사용 데이터가 쌓인 뒤의 답이 다르다.',
        ],
      },
      {
        id: 'request-doc',
        label: 'dX팀 개발 요청서 만들기',
        when: '이 과정의 마지막. 실제로 dX팀에 요청할 때 쓴다.',
        body: `지금까지 만든 것과 만들지 못한 것을 정리해서, dX팀에 전달할 개발 요청서를 작성해주세요.

## 포함할 것
1. 배경 — 왜 이 도구가 필요한가 (현재 업무 방식의 문제, 영향받는 사람 수)
2. 이미 검증된 것 — 내가 직접 만들어 동작을 확인한 기능 목록
   (프로토타입 저장소 링크, 화면 캡처)
3. 요청 사항 — 우선순위 순으로, 각각:
   - 무엇을 (기능)
   - 왜 (해결하는 문제)
   - 완료 기준 (어떻게 확인할 것인가)
4. 사내 환경 의존 항목 — 내가 진행할 수 없어 dX팀이 필요한 것
   (RADIUS 연동, Coolify 인스턴스, 웍스 AI 실제 스펙, 도메인, 백업 정책)
5. 결정이 필요한 정책 — 조직 차원의 판단이 필요한 것
   (일정 열람 범위, 인수인계 승인 절차, 감사 로그 보관 기간, 개인정보 처리)
6. 이미 알고 있는 위험·한계
   (반복 일정 미지원, 양방향 동기화 제한, 모바일 미지원)
7. 기대 효과 — 가능하면 숫자로 (주간보고 작성 시간, 회의 시간)

## 형식
마크다운, 3~4페이지 분량. 읽는 사람이 개발자라고 가정하고,
"알아서 잘 만들어주세요"가 아니라 판단에 필요한 정보를 주는 문서로.`,
        tips: [
          '**2번(이미 검증된 것)이 이 문서의 힘이다.** 동작하는 프로토타입이 있는 요청과 없는 요청은 완전히 다르게 취급된다.',
          '5번(정책 결정)을 명시하면 "이건 우리가 정해줘야 하는구나"를 상대가 바로 안다. 이게 빠지면 프로젝트가 중간에 멈춘다.',
          '6번(알고 있는 한계)을 솔직히 쓰면 신뢰가 올라간다. 숨기면 나중에 문제가 된다.',
        ],
      },
    ],
    sample: [
      { type: 'h', text: '운영 점검 결과 (예시)' },
      {
        type: 'table',
        head: ['항목', '지금 상태', '필요한 것', '우선순위'],
        rows: [
          ['로그', 'console.log 만. 컨테이너 재시작 시 소실', '구조화 로그 + 외부 수집. 최소 7일 보관', '**높음**'],
          ['오류 추적', '없음. 사용자가 말해줘야 안다', 'Sentry 류 도구 또는 서버 에러 로그 알림', '**높음**'],
          ['백업 복구 테스트', '백업만 있고 복구는 안 해봄', '월 1회 복구 리허설', '**높음**'],
          ['모니터링', '헬스체크만 있고 알림이 없다', '실패 시 메신저 알림', '중간'],
          ['성능', '시드 데이터 25건으로만 테스트', '아래 병목 항목 참고', '중간'],
          ['관리자 화면', '없음. DB를 직접 봐야 한다', '사용자·연동 상태 조회 화면', '중간'],
          ['의존성 취약점', '확인 안 함', 'npm audit 정기 실행', '중간'],
          ['접근 통제', '로그인만. 사내망 제한 없음', 'IP 제한 또는 VPN 경유', '**정책 확인 필요**'],
        ],
      },
      { type: 'h', text: '성능: 데이터가 늘면 먼저 느려지는 곳' },
      {
        type: 'table',
        head: ['화면 / 작업', '병목', '대응'],
        rows: [
          [
            '월 캘린더 (일정 5,000개)',
            '한 달치만 조회하므로 문제 없음. 단 `@@index([userId, startAt])` 가 없으면 전체 스캔',
            '인덱스 확인 (이미 넣었다)',
          ],
          [
            '팀 캘린더 (10명 × 5,000개)',
            '팀원 전체 일정을 한 번에 조회 → 응답 커짐',
            '기간 제한 + 필요 필드만 select',
          ],
          [
            '주간보고 초안 생성',
            '일정 조회 후 메모리 집계 — 주 단위라 데이터가 작다. 안전',
            '없음',
          ],
          [
            '**팀 전체 통계 (분기·연간)**',
            '수만 건을 앱에서 집계 → 여기가 첫 병목',
            'DB 집계 쿼리(GROUP BY)로 이동, 또는 주 단위 집계 테이블 캐시',
          ],
          [
            '**캘린더 동기화**',
            '계정 20개 × 증분 동기화. 순차 실행이면 오래 걸리고, 병렬이면 요청 제한',
            '계정별 큐 + 동시 실행 수 제한',
          ],
          [
            '발표 모드',
            '전체 미리 불러오기 → 팀이 20명이 되면 초기 로딩 증가',
            '현재 + 다음 2명만 미리, 나머지는 지연 로딩',
          ],
        ],
      },
      {
        type: 'callout',
        tone: 'tip',
        title: '성능 최적화는 측정 후에',
        text: '위 표에서 실제 문제가 될 것은 굵게 표시한 2개뿐이다. 나머지를 미리 최적화하면 코드만 복잡해진다. **"느려질 것 같다"가 아니라 "느리다"를 확인한 다음에 고친다.** AI에게 "최적화해줘"라고 하면 필요 없는 곳까지 다 손대므로, 병목을 지정해서 요청해야 한다.',
      },
      { type: 'h', text: 'dX팀 개발 요청서 (발췌)' },
      {
        type: 'code',
        lang: 'markdown',
        filename: 'docs/REQUEST-dX.md',
        code: `# 개발 요청: 업무 캘린더 기반 주간보고 · 인수인계 도구

## 1. 배경
- 대상: dX팀 외 3개 팀, 약 34명
- 현재: 일정은 구글 캘린더, 주간보고는 매주 금요일 수동 작성(1인당 약 40분),
  주간회의 때 각자 화면 공유(5~7분 낭비), 휴가 인계는 메신저 구두
- 문제: 같은 내용 이중 입력, 팀 현황 미가시, 인계 누락으로 인한 후속 대응 지연

## 2. 이미 검증한 것 (프로토타입)
저장소: git.internal/hong/work-calendar (브랜치 main)
직접 만들어 동작을 확인한 기능:
| 기능 | 상태 | 확인 방법 |
|---|---|---|
| 캘린더 월/주 뷰, 일정 CRUD, 드래그 이동 | 동작 | 로컬 + 스테이징 |
| 구글 캘린더 연동 (읽기 + 내보내기, 증분 동기화) | 동작 | 테스트 계정 2개로 검증 |
| 주간보고 자동 초안 (카테고리 집계, 편집 보존) | 동작 | 4주치 실데이터로 확인 |
| 발표 모드 (키보드 내비, 회의록 복사) | 동작 | 실제 주간회의 2회 사용 |
| 인수인계 (요청→확인→완료, 감사 로그) | 동작 | 팀원 2명과 시나리오 테스트 |
| RADIUS 로그인 | **미완** | 구조만. 스텁 모드로 개발 중 |
| Coolify 배포 | **미완** | Dockerfile 작성 완료, 인스턴스 없음 |

## 3. 요청 사항 (우선순위 순)
### P1. RADIUS 인증 연동
- 왜: 사내 계정 로그인이 없으면 실사용 배포 불가
- 완료 기준: 사번/비밀번호로 로그인, 5회 실패 잠금, 감사 로그 기록
- 필요: RADIUS 접속 정보, 앱 서버 IP를 클라이언트로 등록, 인증 방식 확정

### P2. Coolify 배포 및 운영 환경
- 왜: 팀이 접속할 수 있는 주소가 필요
- 완료 기준: 사내 도메인 HTTPS 접속, 자동 배포, 일 1회 백업 + 복구 검증
- 필요: Coolify 인스턴스, 도메인, 백업 저장소, 사내망 접근 정책

### P3. 인증·권한 코드 보안 검토
- 왜: 프로토타입은 제가 만들었고 보안 검토를 받지 못했습니다
- 완료 기준: 권한 우회·입력 검증·비밀값 관리 점검 결과 및 수정
- 참고: 자체 점검으로 발견해 수정한 항목 목록 첨부 (docs/SECURITY-SELFCHECK.md)

### P4. 웍스 AI 실제 스펙 연동
- 왜: 현재 OpenAI 호환 형태로 가정하고 어댑터 구조로 구현
- 완료 기준: src/server/ai/client.ts 교체 후 요약 기능 정상 동작
- 필요: 실제 API 스펙, 키 발급, 사용량 한도

### P5. 로그·오류 추적
- 왜: 지금은 문의가 오면 원인을 확인할 방법이 없습니다
- 완료 기준: 서버 오류 발생 시 알림, 최소 7일 로그 조회

## 4. 정책 결정 요청 (조직 판단 필요)
| 항목 | 선택지 | 영향 |
|---|---|---|
| 일정 열람 범위 | 같은 팀 제목까지 / 바쁨만 / 상위 조직 포함 | 팀 캘린더·주간보고 공개 범위 |
| 인수인계 승인 | 인수자 확인만 / 팀장 승인 필요 | 상태 흐름에 단계 추가 여부 |
| 감사 로그 보관 | 3개월 / 1년 / 3년 | 개인정보 정책 |
| AI 전송 데이터 | 전체 / 고객명 마스킹 / AI 미사용 옵션 | 요약 기능 품질 |
| 접근 제어 | 사내망만 / VPN / 인터넷 공개 | 외부 근무 시 사용 가능 여부 |

## 5. 알고 있는 한계
- 반복 일정(매주 회의) 미지원 — 개별 일정으로 등록해야 함
- 구글 연동은 "읽기 + 내보내기". 구글에서 수정한 내용은 다음 동기화 때 우리 쪽 사본만 갱신
- 네이버 캘린더는 읽기 전용 (ICS 구독) 으로만 검증
- 모바일 전용 화면 없음 (반응형까지만)
- 동시 사용자 50명 이상 규모는 테스트하지 않음

## 6. 기대 효과
- 주간보고 작성: 1인당 약 40분 → 약 10분 (34명 × 4주 = 월 68시간 절감 추정)
- 주간회의: 화면 공유 전환 시간 제거로 회의당 약 7분 단축
- 인수인계 누락으로 인한 후속 대응 건수 감소 (현재 월 2~3건)`,
      },
      {
        type: 'callout',
        tone: 'tip',
        title: '이 문서가 이 교육의 최종 산출물이다',
        text: '15단계를 다 따라오지 않았더라도, **이 형식의 요청서를 쓸 수 있게 되는 것**이 이 과정의 목표다. "캘린더 만들어주세요"와 이 문서는 결과물의 품질과 소요 기간에서 완전히 다른 차이를 만든다.',
      },
    ],
    explain: [
      { type: 'h', text: '15단계를 지나온 뒤 남는 것' },
      {
        type: 'table',
        head: ['배운 것', '왜 중요한가'],
        rows: [
          ['요구사항을 검증 가능하게 쓰는 법', 'AI에게든 사람에게든 통하는 유일한 언어'],
          ['한 번에 하나씩 만들고 확인하는 리듬', '큰 요청은 반드시 어긋난다'],
          ['AI가 만든 코드를 의심하는 지점', '권한 검사, 입력 검증, 실패 처리는 조용히 빠진다'],
          ['외부 연동의 실제 난이도', '"연동해주세요" 한 문장의 무게를 알게 된다'],
          ['운영이 개발보다 길다는 사실', '배포는 시작점이다'],
          ['무엇을 맡기고 무엇을 판단할지', 'AI·dX팀에 맡길 것과 내가 결정할 것의 경계'],
        ],
      },
      { type: 'h', text: '바이브 코딩의 현실적인 위치' },
      {
        type: 'table',
        head: ['잘 되는 것', '한계'],
        rows: [
          ['**아이디어를 실제로 만져보게 만드는 것**', '한 사람이 유지보수까지 감당하기는 어렵다'],
          ['화면·CRUD·연동 초안을 빠르게 뽑는 것', '보안·성능·안정성은 별도 검토가 필요하다'],
          ['"이게 될까?"를 며칠 안에 확인하는 것', '조직 정책·인프라 결정은 여전히 사람의 일'],
          ['요구사항을 스스로 정리하게 되는 것', '코드를 읽지 못하면 어디까지 믿을지 판단이 어렵다'],
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: '이 과정의 진짜 목표',
        text: '**혼자 다 만들 수 있게 되는 것이 아니다.** 무엇을 원하는지 정확히 말할 수 있게 되고, 그게 왜 쉽거나 어려운지 이해하고, 만들어진 것을 검증할 수 있게 되는 것이다. 프로토타입을 직접 만들어본 사람의 요청은 완전히 다른 요청이 된다.',
      },
      { type: 'h', text: '다음에 붙일 만한 것들' },
      {
        type: 'ul',
        items: [
          '**알림** — 인수인계 요청, 미제출 주간보고, 동기화 실패를 메신저로 (사내 메신저 웹훅)',
          '**반복 일정** — RRULE 지원. 예외 처리(하나만 수정)까지 하면 난이도가 크게 오른다',
          '**엑셀 내보내기** — 상위 보고용. 실무에서 요청이 가장 많이 들어온다',
          '**조직 롤업** — 팀 → 부문 → 전사 단위 집계',
          '**모바일 화면** — 최소한 일정 등록과 인수인계 확인만이라도',
          '**업무 태그 자동 분류** — 제목으로 카테고리를 추천 (AI 활용 여지)',
        ],
      },
      {
        type: 'callout',
        tone: 'dx',
        title: 'dX팀에 요청할 때',
        text: '이 교육을 끝까지 따라오지 않아도 됩니다. 필요한 것은 **① 무엇을 원하는지 ② 왜 필요한지 ③ 어떻게 확인할지** 이 세 가지입니다. 위 요청서 형식이 그 틀입니다. 프로토타입까지 만들어 오셨다면 더 좋고, 없어도 PRD(01단계) 하나만 써 오시면 바로 시작할 수 있습니다.',
      },
    ],
    checklist: [
      '운영 점검 목록을 만들고 우선순위를 정했다',
      '가장 먼저 해야 할 3가지를 확인했다',
      '데이터가 늘면 어디가 먼저 느려지는지 안다',
      'dX팀 개발 요청서를 작성했다',
      '조직 차원의 정책 결정이 필요한 항목을 목록으로 뽑았다',
      '내가 만든 것의 한계를 솔직하게 문서화했다',
    ],
  },
]
