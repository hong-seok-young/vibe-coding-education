import type { Step } from '../types'

export const part1: Step[] = [
  {
    id: '02',
    slug: 'project-setup',
    part: 'PART 1 · 앱의 뼈대',
    title: '프로젝트 셋업',
    tagline: '빈 폴더에서 "localhost에 화면이 뜬다"까지',
    duration: '30분',
    level: '기본',
    goals: [
      'Next.js + TypeScript + Tailwind + PostgreSQL 개발 환경을 만든다',
      '환경변수(.env)와 비밀값을 코드에서 분리하는 습관을 잡는다',
      'AI가 매번 헤매지 않게 프로젝트 규칙 파일을 심어둔다',
    ],
    deliverables: [
      '실행되는 Next.js 프로젝트 (localhost:3000)',
      'Docker로 띄운 로컬 PostgreSQL',
      'CLAUDE.md (또는 .cursorrules) — AI에게 주는 상시 규칙',
    ],
    prompts: [
      {
        id: 'scaffold',
        label: '프로젝트 생성',
        when: 'PRD를 확정한 다음. 실제로 파일이 만들어지기 시작하는 첫 프롬프트.',
        body: `이제 프로젝트를 만듭니다.

기술 스택을 아래로 확정합니다.
- Next.js 최신 안정 버전, App Router, TypeScript
- Tailwind CSS
- PostgreSQL + Prisma
- 패키지 매니저: pnpm (없으면 npm)

요청:
1. 프로젝트를 생성하는 명령어를 순서대로 알려주세요. 각 명령어가 무엇을 하는지 한 줄 설명 포함
2. 로컬 개발용 PostgreSQL을 Docker로 띄우는 docker-compose.yml 을 만들어주세요.
   - 컨테이너 이름/DB 이름은 이 프로젝트 이름을 반영
   - 데이터가 컨테이너를 지워도 남도록 볼륨 설정
3. .env.example 파일을 만들어주세요. 앞으로 필요할 값들을 미리 주석과 함께 넣어주세요
   (DB 연결, 세션 시크릿, 구글 OAuth, RADIUS, 웍스 AI — 지금은 값이 비어 있어도 됩니다)
4. 최종 폴더 구조를 트리로 보여주세요. 앞으로 어떤 폴더에 무엇이 들어갈지 주석 포함
5. 마지막에 "여기까지 제대로 됐는지 확인하는 방법"을 알려주세요

주의: .env 파일은 절대 git에 커밋되지 않아야 합니다. .gitignore 확인도 해주세요.`,
        tips: [
          '명령어는 한 번에 다 붙여넣지 말고 하나씩 실행한다. 중간에 에러가 나면 **에러 전문을 그대로 복사해서** AI에게 준다.',
          '`npx create-next-app` 이 물어보는 질문(App Router? Tailwind?)에 AI가 알려준 대로 답한다.',
          'Docker가 없다면 "Docker 없이 진행할 방법"을 물어본다. (예: 로컬 Postgres 설치 또는 SQLite로 시작)',
        ],
      },
      {
        id: 'rules-file',
        label: 'AI 상시 규칙 파일 만들기',
        when: '프로젝트 폴더가 생긴 직후. 이걸 해두면 이후 스텝에서 컨텍스트를 매번 설명하지 않아도 된다.',
        body: `프로젝트 루트에 AI 코딩 도구가 항상 참고할 규칙 파일을 만들어주세요.
(Claude Code면 CLAUDE.md, Cursor면 .cursor/rules, 둘 다 만들어도 됩니다)

내용에 포함할 것:
1. 이 프로젝트가 무엇인지 3줄 요약
2. 기술 스택과 버전
3. 폴더 구조 규칙 (어떤 코드를 어디에 두는지)
4. 코딩 규칙
   - 서버에서만 쓰는 코드와 브라우저 코드를 섞지 않는다
   - DB 접근은 특정 폴더(예: src/server/)를 통해서만 한다
   - 비밀값은 process.env 로만 읽고, 클라이언트 컴포넌트에서 참조하지 않는다
   - 사용자 입력은 zod 로 검증한다
   - 권한 검사는 화면이 아니라 서버에서 한다
5. 작업 방식
   - 한 번에 한 기능씩
   - 파일을 수정할 때는 전체 경로를 먼저 밝힌다
   - 새 패키지를 추가하기 전에 나에게 먼저 물어본다
6. 자주 쓰는 명령어 목록 (개발 서버, DB 마이그레이션, 빌드)

파일 전문을 출력해주세요.`,
        tips: [
          '이 파일은 **프로젝트의 헌법**이다. 나중에 AI가 규칙을 어기면 "CLAUDE.md 4번 규칙 위반"이라고 지적하면 된다.',
          '"새 패키지 추가 전에 물어보기" 규칙은 꼭 넣는다. 이게 없으면 의존성이 조용히 불어난다.',
        ],
      },
    ],
    sample: [
      { type: 'h', text: '1. 생성 명령어' },
      {
        type: 'code',
        lang: 'bash',
        filename: 'terminal',
        code: `# Next.js 프로젝트 생성 (App Router + TS + Tailwind)
npx create-next-app@latest work-calendar --typescript --tailwind --app --eslint
cd work-calendar

# Prisma: DB 스키마를 코드로 관리하는 도구
npm i -D prisma && npm i @prisma/client
npx prisma init

# 입력 검증 + 날짜 처리
npm i zod date-fns

# 로컬 DB 띄우기
docker compose up -d

# 개발 서버
npm run dev   # http://localhost:3000`,
      },
      { type: 'h', text: '2. 로컬 DB' },
      {
        type: 'code',
        lang: 'yaml',
        filename: 'docker-compose.yml',
        code: `services:
  db:
    image: postgres:16-alpine
    container_name: work-calendar-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: devpassword     # 로컬 전용. 운영에서는 절대 이렇게 쓰지 않는다
      POSTGRES_DB: work_calendar
    ports:
      - "5432:5432"
    volumes:
      - db-data:/var/lib/postgresql/data  # 컨테이너를 지워도 데이터는 남는다
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d work_calendar"]
      interval: 10s
      retries: 5

volumes:
  db-data:`,
      },
      { type: 'h', text: '3. 환경변수 틀' },
      {
        type: 'code',
        lang: 'ini',
        filename: '.env.example',
        code: `# ── 데이터베이스 ─────────────────────────────
DATABASE_URL="postgresql://app:devpassword@localhost:5432/work_calendar?schema=public"

# ── 세션/인증 ────────────────────────────────
# openssl rand -base64 32 로 생성
AUTH_SECRET=""
AUTH_URL="http://localhost:3000"

# ── 구글 캘린더 (STEP 06) ────────────────────
GOOGLE_CLIENT_ID=""
GOOGLE_CLIENT_SECRET=""
GOOGLE_REDIRECT_URI="http://localhost:3000/api/calendar/google/callback"

# ── RADIUS 인증 (STEP 12) ────────────────────
RADIUS_HOST=""
RADIUS_PORT="1812"
RADIUS_SECRET=""
RADIUS_NAS_IDENTIFIER="work-calendar"

# ── 웍스 AI (STEP 11) ────────────────────────
WORKS_AI_BASE_URL=""
WORKS_AI_API_KEY=""
WORKS_AI_MODEL=""

# ── 외부 캘린더 토큰 암호화 키 (STEP 06) ─────
# 32바이트 base64. 절대 재생성하지 않는다(기존 토큰 복호화 불가)
TOKEN_ENC_KEY=""`,
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '.env 와 .env.example',
        text: '`.env.example` 은 **키 이름만** 담아 git에 커밋한다. 실제 값이 든 `.env` 는 절대 커밋하지 않는다. 한 번 커밋된 비밀값은 되돌려도 git 이력에 남는다 — 그때는 키를 폐기하고 새로 발급하는 것이 유일한 해결책이다.',
      },
      { type: 'h', text: '4. 폴더 구조' },
      {
        type: 'files',
        tree: `work-calendar/
├─ prisma/
│  └─ schema.prisma          # DB 구조 정의 (STEP 03)
├─ src/
│  ├─ app/                   # 화면(라우트). 폴더 = URL 경로
│  │  ├─ (app)/
│  │  │  ├─ calendar/        # 캘린더 화면 (STEP 04~05)
│  │  │  ├─ weekly/          # 주간보고 (STEP 08)
│  │  │  ├─ present/         # 발표 모드 (STEP 09)
│  │  │  └─ handover/        # 인수인계 (STEP 10)
│  │  └─ api/                # 서버 API
│  │     ├─ events/
│  │     ├─ calendar/google/ # OAuth 콜백·동기화 (STEP 06)
│  │     └─ ai/              # 웍스 AI 프록시 (STEP 11)
│  ├─ components/            # 재사용 UI (버튼, 캘린더 그리드 등)
│  ├─ server/                # ★ 서버 전용 코드. DB·외부 API·비밀값
│  │  ├─ db.ts               # Prisma 클라이언트
│  │  ├─ auth.ts             # 세션·권한 (STEP 12)
│  │  └─ providers/          # 캘린더 연동 구현체 (STEP 07)
│  └─ lib/                   # 순수 함수 (날짜 계산, 포맷) — 서버·클라이언트 공용
├─ docs/
│  ├─ PRD.md
│  └─ ROADMAP.md
├─ docker-compose.yml
├─ .env.example
└─ CLAUDE.md                 # AI 상시 규칙`,
      },
      { type: 'h', text: '5. 확인 방법' },
      {
        type: 'ol',
        items: [
          '`docker compose ps` → db 컨테이너가 `healthy` 상태',
          '`npm run dev` → 브라우저에서 http://localhost:3000 에 기본 페이지가 뜬다',
          '`npx prisma db pull` 이 에러 없이 끝난다 → DB 연결 성공',
          '`git status` 에 `.env` 가 보이지 않는다 → .gitignore 정상',
        ],
      },
    ],
    explain: [
      { type: 'h', text: '왜 이 스택인가' },
      {
        type: 'table',
        head: ['선택', '역할', '이게 없으면'],
        rows: [
          ['Next.js', '화면과 서버 API를 한 프로젝트에서 만들고 Docker 하나로 배포', '프론트/백엔드 저장소 2개, 배포 2개, CORS 설정'],
          ['TypeScript', '데이터 모양이 안 맞으면 실행 전에 잡아준다', 'AI가 만든 코드의 오타·필드명 실수를 런타임에서 발견'],
          ['Tailwind', '클래스 이름으로 스타일 지정. 캘린더처럼 촘촘한 UI에 유리', 'CSS 파일이 늘어나고 AI가 만든 스타일이 서로 충돌'],
          ['PostgreSQL', '일정·보고·인수인계 관계를 다루는 표준 관계형 DB', '엑셀/JSON 파일 관리 → 동시 수정 시 데이터 손상'],
          ['Prisma', 'DB 구조를 코드로 정의하고 변경 이력을 마이그레이션으로 관리', '운영 DB에 손으로 ALTER TABLE → 되돌릴 수 없는 사고'],
        ],
      },
      { type: 'h', text: '환경변수: 코드와 비밀값을 분리하는 이유' },
      {
        type: 'flow',
        title: '같은 코드, 다른 값',
        steps: [
          '코드 (git 저장소)',
          '+ 환경변수 (서버마다 다름)',
          '= 로컬 / 스테이징 / 운영',
        ],
      },
      {
        type: 'p',
        text: '코드에 `password = "abc123"` 을 적으면 세 가지가 동시에 망가진다. ① 저장소를 볼 수 있는 모든 사람이 비밀값을 본다. ② 운영 값을 바꾸려면 코드를 다시 배포해야 한다. ③ 로컬과 운영이 같은 DB를 가리켜 실수로 실데이터를 지운다. 13단계(Coolify 배포)에서 이 환경변수들을 서버 쪽에 넣는다.',
      },
      { type: 'h', text: '"서버 전용 폴더"를 따로 두는 이유' },
      {
        type: 'p',
        text: 'Next.js는 서버 코드와 브라우저 코드가 같은 프로젝트에 섞여 있다. 실수로 브라우저에서 실행되는 파일에 API 키를 import 하면, **그 키가 브라우저로 전송되는 자바스크립트 파일 안에 그대로 담긴다.** 개발자 도구만 열면 누구나 볼 수 있다. 그래서 `src/server/` 를 정해두고 "이 폴더는 클라이언트 컴포넌트에서 절대 import 하지 않는다"는 규칙을 CLAUDE.md에 박아둔다.',
      },
      {
        type: 'callout',
        tone: 'tip',
        title: '규칙 파일(CLAUDE.md)의 위력',
        text: 'AI 코딩에서 같은 지시를 반복하고 있다면, 그건 규칙 파일에 넣어야 한다는 신호다. "매번 파일 경로를 먼저 써라", "패키지 추가 전에 물어봐라" 같은 규칙 5~10줄이 이후 수십 번의 되돌리기를 막는다.',
      },
      {
        type: 'callout',
        tone: 'dx',
        text: '사내 표준 프로젝트 템플릿(로깅·인증·CI 포함)이 필요하면 dX팀에 요청하세요. 셋업 단계를 건너뛰고 4단계부터 시작할 수 있습니다.',
      },
    ],
    checklist: [
      'localhost:3000 에서 페이지가 뜬다',
      'docker compose ps 에서 DB가 healthy 다',
      '.env 를 만들고 .gitignore 에 포함돼 있음을 확인했다',
      'CLAUDE.md (또는 규칙 파일)를 만들었다',
      '첫 커밋을 했다 (git add . && git commit -m "chore: 프로젝트 셋업")',
    ],
    dxNote: '사내 프록시·인증서 환경에서 npm/Docker가 막히는 경우가 있습니다. 네트워크 이슈는 dX팀 문의.',
  },

  {
    id: '03',
    slug: 'data-model',
    part: 'PART 1 · 앱의 뼈대',
    title: '데이터 모델 설계',
    tagline: '일정 · 주간보고 · 인수인계를 담을 그릇 만들기',
    duration: '40분',
    level: '기본',
    goals: [
      '앞으로 만들 모든 기능의 데이터 구조를 한 번에 설계한다',
      '외부 캘린더 연동과 인수인계를 나중에 붙일 수 있게 미리 자리를 만들어둔다',
      '마이그레이션(DB 구조 변경 이력)의 개념을 이해한다',
    ],
    deliverables: [
      'prisma/schema.prisma — 전체 데이터 모델',
      '적용된 첫 마이그레이션',
      'Prisma Studio에서 눈으로 확인 가능한 테이블',
    ],
    prompts: [
      {
        id: 'schema',
        label: '데이터 모델 설계 요청',
        when: '프로젝트 셋업이 끝난 직후. PRD를 근거로 스키마를 만든다.',
        body: `docs/PRD.md 를 근거로 Prisma 스키마를 설계해주세요.

담아야 할 개념:
1. User — RADIUS로 인증되므로 비밀번호는 저장하지 않는다. 사번/이름/부서/역할(팀원·팀장·관리자)
2. Team — 사용자는 하나의 팀에 속한다
3. Event — 업무 일정. 제목, 시작/종료(종일 여부 포함), 메모, 카테고리, 공개범위(팀공개/비공개), 작성자
4. Category — 업무 카테고리(예: 개발, 회의, 지원, 교육). 색상 포함. 주간보고에서 묶는 기준
5. CalendarAccount — 사용자가 연결한 외부 캘린더 계정 (google | naver | outlook | ics).
   액세스/리프레시 토큰은 암호화해서 저장, 동기화 상태(syncToken, 마지막 동기화 시각)도 보관
6. ExternalEventLink — 우리 Event 와 외부 캘린더 일정의 짝. 외부 일정 ID, ETag, 마지막 동기화 시각.
   같은 일정이 중복 생성되는 것을 막는 역할
7. WeeklyReport — 사용자 × 주(ISO 주차) 단위. 상태(초안·제출), 제출 시각
8. ReportSection / ReportItem — 주간보고 안의 "이번 주 한 일 / 다음 주 계획 / 이슈"와 그 항목들.
   각 항목은 어떤 Event 에서 생성됐는지 연결될 수 있고, 사람이 수정하면 편집됨 표시
9. Handover — 인수인계 묶음. 부재 기간(시작·종료), 인계자, 인수자, 상태(요청·확인·완료), 메모
10. HandoverItem — 인수인계 대상 개별 항목. 연결된 Event 또는 자유 텍스트, 현재 상태, 인수자 확인 여부
11. AuditLog — 인수인계 확인, 외부 캘린더 연동 변경 등 중요 행위 기록

요청:
- schema.prisma 전문
- 각 모델 위에 이 모델이 왜 필요한지 한 줄 주석
- 자주 조회하는 조건에 대한 인덱스 (예: 사용자 + 기간으로 일정 조회)
- 마이그레이션 실행 명령어
- 이 설계에서 나중에 문제가 될 수 있는 지점 3가지와 그 이유

주의: 지금 단계에서 화면 코드는 만들지 마세요. 스키마만.`,
        tips: [
          '**"나중에 문제가 될 지점 3가지"를 꼭 물어본다.** AI가 스스로 설계의 약점을 말하게 하는 장치다. 반복 일정(매주 회의)과 타임존이 자주 언급될 것이다.',
          '스키마가 너무 크게 느껴지면 "MVP에 꼭 필요한 것만 남기고 나머지는 주석으로"라고 요청한다.',
        ],
      },
      {
        id: 'seed',
        label: '샘플 데이터 넣기',
        when: '마이그레이션이 성공한 다음. 화면을 만들 때 빈 화면을 보지 않으려면 반드시 필요하다.',
        body: `테스트용 시드 데이터 스크립트를 만들어주세요. (prisma/seed.ts)

내용:
- 팀 1개 ("dX팀"), 사용자 4명 (팀장 1, 팀원 3)
- 카테고리 5개: 개발/회의/지원/교육/기타 (각각 색상)
- 이번 주와 지난 주에 걸쳐 사용자별 일정 총 25개 정도
  (회의·개발·지원이 섞이고, 종일 일정 2개, 비공개 일정 2개 포함)
- 지난 주 주간보고 1건 (제출 상태), 이번 주 주간보고 1건 (초안 상태)
- 인수인계 1건 (요청 상태)

조건:
- 여러 번 실행해도 데이터가 중복되지 않게 (upsert 또는 초기화 후 삽입)
- 날짜는 실행 시점의 "이번 주"를 기준으로 상대적으로 계산 (하드코딩된 날짜 금지)
- package.json 에 실행 스크립트 추가 방법도 알려주세요`,
        tips: [
          '"실행 시점 기준 상대 날짜"는 중요하다. 날짜를 고정해두면 다음 주에 화면이 텅 빈다.',
          '시드 데이터의 품질이 곧 화면 개발 속도다. 일정 25개 정도는 있어야 캘린더 레이아웃 문제가 드러난다.',
        ],
      },
    ],
    sample: [
      {
        type: 'code',
        lang: 'prisma',
        filename: 'prisma/schema.prisma (발췌)',
        code: `generator client { provider = "prisma-client-js" }
datasource db { provider = "postgresql"; url = env("DATABASE_URL") }

/// 사내 구성원. RADIUS가 인증을 담당하므로 비밀번호는 저장하지 않는다.
model User {
  id           String   @id @default(cuid())
  employeeNo   String   @unique          // 사번 = RADIUS 로그인 ID
  name         String
  department   String?
  role         Role     @default(MEMBER)
  teamId       String?
  team         Team?    @relation(fields: [teamId], references: [id])
  events       Event[]
  reports      WeeklyReport[]
  handoversOut Handover[] @relation("from")
  handoversIn  Handover[] @relation("to")
  accounts     CalendarAccount[]
  createdAt    DateTime @default(now())
}

enum Role { MEMBER LEADER ADMIN }

/// 업무 일정. 이 앱의 중심 데이터. 주간보고와 인수인계 모두 여기서 파생된다.
model Event {
  id          String    @id @default(cuid())
  userId      String
  user        User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  title       String
  description String?
  startAt     DateTime                    // 항상 UTC로 저장
  endAt       DateTime
  allDay      Boolean   @default(false)
  timeZone    String    @default("Asia/Seoul")
  categoryId  String?
  category    Category? @relation(fields: [categoryId], references: [id])
  visibility  Visibility @default(TEAM)   // PRIVATE 이면 주간보고·팀뷰에서 제외
  source      EventSource @default(LOCAL) // 우리 앱에서 만든 것인지, 외부에서 읽어온 것인지
  externalLink ExternalEventLink?
  reportItems  ReportItem[]
  handoverItems HandoverItem[]
  updatedAt   DateTime  @updatedAt
  createdAt   DateTime  @default(now())

  @@index([userId, startAt])              // "이 사람의 이 기간 일정" 조회가 가장 빈번하다
  @@index([startAt, endAt])
}

enum Visibility { TEAM PRIVATE }
enum EventSource { LOCAL GOOGLE NAVER OUTLOOK ICS }

/// 사용자가 연결한 외부 캘린더 계정. 프로바이더가 늘어나도 이 테이블 하나로 관리한다.
model CalendarAccount {
  id            String   @id @default(cuid())
  userId        String
  user          User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  provider      EventSource
  accountEmail  String
  displayName   String?
  color         String   @default("#4a6ff0")
  accessToken   String   @db.Text          // 암호화해서 저장 (평문 금지)
  refreshToken  String?  @db.Text          // 암호화해서 저장
  expiresAt     DateTime?
  syncToken     String?                    // 증분 동기화 커서 (STEP 06)
  lastSyncedAt  DateTime?
  syncEnabled   Boolean  @default(true)
  writeEnabled  Boolean  @default(false)   // 이 계정으로 내보내기를 허용할지
  createdAt     DateTime @default(now())

  @@unique([userId, provider, accountEmail])
}

/// 우리 Event ↔ 외부 캘린더 일정의 1:1 짝. 중복 생성과 무한 동기화를 막는 핵심 테이블.
model ExternalEventLink {
  id             String   @id @default(cuid())
  eventId        String   @unique
  event          Event    @relation(fields: [eventId], references: [id], onDelete: Cascade)
  accountId      String
  externalId     String                    // 구글의 event.id 등
  externalEtag   String?                   // 변경 여부를 값 비교 없이 판단
  lastSyncedAt   DateTime @default(now())
  lastSyncedHash String?                   // 우리 쪽 내용 지문. 우리가 만든 변경인지 구분

  @@unique([accountId, externalId])        // 같은 외부 일정이 두 번 들어오지 않는다
}

/// 사용자 × 주차 단위 주간보고.
model WeeklyReport {
  id          String   @id @default(cuid())
  userId      String
  user        User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  isoYear     Int
  isoWeek     Int                          // ISO 주차 (연말·연초 경계를 안전하게 처리)
  status      ReportStatus @default(DRAFT)
  summary     String?  @db.Text            // AI 요약 (STEP 11)
  submittedAt DateTime?
  items       ReportItem[]
  updatedAt   DateTime @updatedAt

  @@unique([userId, isoYear, isoWeek])     // 한 사람의 한 주는 보고서 하나
}

enum ReportStatus { DRAFT SUBMITTED }
enum ReportSection { DONE NEXT ISSUE }

model ReportItem {
  id         String   @id @default(cuid())
  reportId   String
  report     WeeklyReport @relation(fields: [reportId], references: [id], onDelete: Cascade)
  section    ReportSection
  content    String   @db.Text
  eventId    String?                       // 어느 일정에서 만들어졌는지
  event      Event?   @relation(fields: [eventId], references: [id], onDelete: SetNull)
  edited     Boolean  @default(false)      // 사람이 고친 항목은 재생성 시 보존
  order      Int      @default(0)
}

/// 부재 기간 단위 인수인계 묶음.
model Handover {
  id         String   @id @default(cuid())
  fromUserId String
  fromUser   User     @relation("from", fields: [fromUserId], references: [id])
  toUserId   String
  toUser     User     @relation("to", fields: [toUserId], references: [id])
  absentFrom DateTime
  absentTo   DateTime
  reason     String?                       // 휴가, 교육, 출장 등
  note       String?  @db.Text
  status     HandoverStatus @default(REQUESTED)
  acceptedAt DateTime?
  items      HandoverItem[]
  createdAt  DateTime @default(now())

  @@index([toUserId, status])
}

enum HandoverStatus { REQUESTED ACCEPTED DONE }
enum ItemStatus { TODO IN_PROGRESS BLOCKED DONE }

model HandoverItem {
  id         String   @id @default(cuid())
  handoverId String
  handover   Handover @relation(fields: [handoverId], references: [id], onDelete: Cascade)
  title      String
  detail     String?  @db.Text             // 진행 상황, 연락처, 주의사항
  eventId    String?
  event      Event?   @relation(fields: [eventId], references: [id], onDelete: SetNull)
  status     ItemStatus @default(TODO)
  acked      Boolean  @default(false)      // 인수자가 항목별로 확인
}

/// 감사 로그. "누가 언제 인수인계를 확인했는가"는 반드시 남긴다.
model AuditLog {
  id        String   @id @default(cuid())
  actorId   String?
  action    String                          // "handover.accept", "calendar.connect" ...
  targetId  String?
  meta      Json?
  createdAt DateTime @default(now())

  @@index([action, createdAt])
}`,
      },
      {
        type: 'code',
        lang: 'bash',
        filename: 'terminal',
        code: `# 스키마를 실제 DB에 반영 (변경 이력이 prisma/migrations/ 에 파일로 남는다)
npx prisma migrate dev --name init

# 시드 데이터 넣기
npx prisma db seed

# 브라우저로 DB 내용 확인
npx prisma studio   # http://localhost:5555`,
      },
      { type: 'h', text: 'AI가 짚어준 "나중에 문제가 될 지점"' },
      {
        type: 'table',
        head: ['지점', '무엇이 문제인가', '지금의 대응'],
        rows: [
          [
            '반복 일정 (매주 월요일 회의)',
            '반복 규칙(RRULE)을 저장할 곳이 없다. 1년치를 개별 일정으로 펼치면 데이터가 폭증하고, 하나만 수정하는 예외 처리가 불가능',
            'MVP 제외. 스키마에 `recurrenceRule` 필드 자리만 주석으로 남긴다',
          ],
          [
            '타임존',
            '한국만 쓸 것 같지만, 해외 참석자·서머타임·종일 일정 경계에서 하루가 밀린다',
            'DB는 UTC로만 저장, 표시할 때만 `timeZone` 으로 변환. 종일 일정은 별도 규칙',
          ],
          [
            '외부에서 삭제된 일정',
            '구글에서 지운 일정을 우리가 계속 갖고 있으면 유령 일정이 남는다',
            '`ExternalEventLink` 로 짝을 추적하고, 동기화 때 사라진 항목은 소프트 삭제 처리 (STEP 06)',
          ],
        ],
      },
    ],
    explain: [
      { type: 'h', text: '마이그레이션이 뭐고 왜 중요한가' },
      {
        type: 'p',
        text: '마이그레이션은 **DB 구조를 바꾼 이력을 파일로 남기는 것**이다. `prisma/migrations/` 폴더에 "이 시점에 이 컬럼을 추가했다"는 SQL이 순서대로 쌓인다.',
      },
      {
        type: 'flow',
        title: '같은 구조가 모든 환경에 재현되는 방법',
        steps: [
          'schema.prisma 수정',
          '`migrate dev` → 마이그레이션 파일 생성',
          'git 커밋 (동료도 같은 구조를 얻는다)',
          '배포 시 `migrate deploy` → 운영 DB에 같은 순서로 적용',
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '운영 DB에 손으로 테이블 고치기 금지',
        text: '운영 DB만 손으로 고치면 코드가 기대하는 구조와 실제 구조가 갈라진다. 이건 며칠 뒤 "로컬에서는 되는데 서버에서만 터지는" 버그로 돌아온다. 13단계 배포 파이프라인에서 `prisma migrate deploy` 를 자동으로 실행하도록 넣는다.',
      },
      { type: 'h', text: '이 스키마의 핵심 설계 결정 3가지' },
      {
        type: 'ol',
        items: [
          '**Event가 중심이고 나머지는 파생이다.** 주간보고 항목(ReportItem)과 인수인계 항목(HandoverItem)이 모두 `eventId` 를 옵션으로 갖는다. 일정에서 자동 생성될 수도, 손으로 추가될 수도 있게 만든 것. 이 한 줄 설계로 "캘린더에 쓰면 주간보고가 된다"는 핵심 가치가 성립한다.',
          '**ExternalEventLink 를 분리했다.** 외부 일정 ID를 Event 테이블에 컬럼으로 박으면, 같은 일정을 구글과 네이버에 동시에 내보낼 수 없다. 별도 테이블로 빼면 하나의 일정이 여러 외부 캘린더와 짝을 지을 수 있다.',
          '**보고 항목에 `edited` 플래그가 있다.** "자동 생성"과 "사람이 수정"이 충돌하는 지점이다. 이 불리언 하나가 "재생성을 눌렀더니 내가 쓴 문장이 날아갔다"는 최악의 사용자 경험을 막는다.',
        ],
      },
      { type: 'h', text: 'ISO 주차를 쓰는 이유' },
      {
        type: 'p',
        text: '"2026년 1월 1주"는 사람마다 다르게 센다. 주간보고는 주 단위로 딱 하나여야 하는데, 주차 계산이 흔들리면 같은 주에 보고서가 두 개 생긴다. ISO 8601 주차는 "월요일 시작, 목요일이 포함된 주가 그 해의 1주"라는 국제 규칙으로 이 모호함을 없앤다. `date-fns` 의 `getISOWeek`, `getISOWeekYear` 를 쓴다.',
      },
      {
        type: 'callout',
        tone: 'tip',
        title: '스키마 설계는 AI와 사람의 협업이 가장 잘 먹히는 지점',
        text: 'AI는 표준적인 테이블 구조와 인덱스, 관계 설정을 아주 잘 뽑는다. 사람이 할 일은 **"우리 회사에서는 인수인계가 부재 단위인가 업무 단위인가"** 같은 도메인 판단이다. 이 판단이 틀리면 코드가 아무리 좋아도 못 쓴다.',
      },
      {
        type: 'callout',
        tone: 'dx',
        text: '실제 운영에서는 조직도·인사 정보 연동, 권한 정책, 개인정보 보관 기간 같은 판단이 필요합니다. 스키마 리뷰는 dX팀에 요청하세요 — 나중에 데이터 이관하는 비용이 훨씬 큽니다.',
      },
    ],
    checklist: [
      'npx prisma migrate dev 가 성공했다',
      'prisma/migrations/ 폴더에 마이그레이션 파일이 생겼다',
      'Prisma Studio에서 테이블과 시드 데이터를 눈으로 확인했다',
      'Event / WeeklyReport / Handover 가 어떻게 연결되는지 말로 설명할 수 있다',
      '반복 일정과 타임존이 왜 어려운지 이해했다',
    ],
  },

  {
    id: '04',
    slug: 'calendar-ui',
    part: 'PART 1 · 앱의 뼈대',
    title: '캘린더 UI 만들기',
    tagline: '노션 캘린더 같은 월·주 뷰를 처음부터',
    duration: '60분',
    level: '기본',
    goals: [
      '월/주 뷰 캘린더를 직접 만들면서 날짜 그리드 계산 원리를 이해한다',
      '"노션 캘린더 같다"는 느낌이 어떤 구체적 동작들의 합인지 분해한다',
      '라이브러리를 쓸지 직접 만들지 판단하는 기준을 얻는다',
    ],
    deliverables: [
      '/calendar 화면 — 월 뷰 + 주 뷰 전환, 오늘 강조, 시드 일정 표시',
      '날짜 계산 유틸 (src/lib/date.ts)',
    ],
    prompts: [
      {
        id: 'calendar-shell',
        label: '캘린더 월 뷰 만들기',
        when: '시드 데이터가 DB에 있는 상태에서.',
        body: `캘린더 화면을 만듭니다. 목표는 "노션 캘린더 수준의 사용감"입니다.

## 1단계: 월 뷰만
경로: /calendar
- 월 그리드 (6주 × 7일 고정 높이 — 월이 바뀌어도 레이아웃이 흔들리지 않게)
- 주 시작은 월요일
- 이번 달이 아닌 날짜는 흐리게
- 오늘 날짜는 숫자에 강조 표시
- 상단 툴바: 이전/다음/오늘 버튼, "2026년 8월" 표시, 월·주 뷰 전환 탭
- 각 날짜 칸에 그 날의 일정을 최대 3개까지 표시하고, 넘치면 "+2개 더"
- 일정 칩은 카테고리 색상의 점 + 시간 + 제목 (종일 일정은 배경색 막대)
- 데이터는 서버 컴포넌트에서 Prisma로 조회 (해당 월 범위 + 앞뒤 여백 주간 포함)

## 설계 조건
- 날짜 계산 로직은 src/lib/date.ts 에 순수 함수로 분리하고, UI 컴포넌트는 계산하지 않는다
- 시간대: DB는 UTC, 화면은 Asia/Seoul. 변환 지점을 한 곳으로 모은다
- 키보드: ←/→ 로 주 이동, T 로 오늘, M/W 로 뷰 전환
- 반응형: 좁은 화면에서는 월 뷰 대신 목록 뷰로 대체

먼저 파일 목록과 각 파일의 역할을 알려주고, 그 다음 코드를 파일별로 주세요.
date-fns 를 사용하고, 캘린더 라이브러리는 쓰지 마세요 (원리를 이해하는 것이 목적).`,
        tips: [
          '"6주 고정"을 명시하지 않으면 달마다 그리드 높이가 달라져 화면이 덜컹거린다. 이런 디테일이 "노션 같음"의 정체다.',
          '한 번에 월 뷰 + 주 뷰를 다 요청하지 않는다. 월 뷰가 확실히 동작한 뒤 주 뷰를 요청한다.',
          '결과 화면이 어색하면 스크린샷을 찍어 붙이고 "이 부분 간격이 넓다"처럼 구체적으로 지적한다.',
        ],
      },
      {
        id: 'week-view',
        label: '주 뷰 + 겹침 처리',
        when: '월 뷰가 정상 동작한 다음.',
        body: `이제 주 뷰를 추가해주세요.

- 세로축 = 시간 (0~24시), 가로축 = 월~일 7일
- 현재 시각에 빨간 선 표시 (1분마다 갱신)
- 기본 스크롤 위치는 오전 8시
- 시간 겹치는 일정은 나란히 폭을 나눠 표시 (겹침 그룹 계산)
- 종일 일정은 그리드 위쪽 별도 영역에 가로 막대로
- 30분 단위 격자, 시간 눈금은 왼쪽에 고정

특히 "시간이 겹치는 일정을 나란히 배치하는 알고리즘"을 순수 함수로 분리하고,
그 함수가 어떻게 동작하는지 주석으로 설명해주세요. (이게 캘린더 UI의 핵심 로직입니다)`,
        tips: [
          '겹침 레이아웃은 캘린더에서 가장 까다로운 부분이다. 여기서 만든 함수는 나중에 발표 모드에서도 재사용된다.',
          '"현재 시각 선"은 1분마다 리렌더링되므로, 캘린더 전체가 아니라 그 선만 갱신되게 요청한다.',
        ],
      },
    ],
    sample: [
      {
        type: 'callout',
        tone: 'info',
        title: '완성 결과를 먼저 보기',
        text: '이 스텝의 결과물은 이 교육 프로그램 안에 **실제로 동작하는 데모**로 들어 있다. 아래 코드를 읽기 전에 데모를 먼저 만져보면 "무엇을 만드는지"가 훨씬 빨리 잡힌다.',
      },
      { type: 'h', text: '날짜 계산 유틸' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/lib/date.ts',
        code: `import {
  startOfMonth, endOfMonth, startOfWeek, endOfWeek,
  addDays, isSameDay, isSameMonth, format,
} from 'date-fns'
import { ko } from 'date-fns/locale'

/**
 * 월 뷰에 그릴 날짜 42개(6주 x 7일)를 만든다.
 * 6주로 고정하는 이유: 달마다 5주/6주로 바뀌면 그리드 높이가 달라져 화면이 덜컹거린다.
 */
export function buildMonthGrid(anchor: Date): Date[] {
  const first = startOfWeek(startOfMonth(anchor), { weekStartsOn: 1 }) // 1 = 월요일
  return Array.from({ length: 42 }, (_, i) => addDays(first, i))
}

/** 화면에 보이는 범위 전체 (DB 조회 조건으로 그대로 사용) */
export function monthRange(anchor: Date) {
  const grid = buildMonthGrid(anchor)
  return { from: grid[0], to: addDays(grid[41], 1) }
}

export function weekRange(anchor: Date) {
  return {
    from: startOfWeek(anchor, { weekStartsOn: 1 }),
    to: addDays(endOfWeek(anchor, { weekStartsOn: 1 }), 1),
  }
}

export const isToday = (d: Date) => isSameDay(d, new Date())
export const inMonth = (d: Date, anchor: Date) => isSameMonth(d, anchor)
export const dayLabel = (d: Date) => format(d, 'd')
export const monthTitle = (d: Date) => format(d, 'yyyy년 M월', { locale: ko })

/** 캘린더 조회는 항상 "범위가 겹치는" 조건이다. 시작만 비교하면 걸친 일정이 누락된다. */
export function overlaps(a: { startAt: Date; endAt: Date }, from: Date, to: Date) {
  return a.startAt < to && a.endAt > from
}`,
      },
      { type: 'h', text: '겹침 레이아웃 — 캘린더 UI의 핵심 알고리즘' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/lib/overlap.ts',
        code: `export interface Positioned<T> {
  item: T
  /** 0~1 사이 비율. 왼쪽 위치와 폭 */
  left: number
  width: number
}

/**
 * 시간이 겹치는 일정들을 나란히 배치한다.
 *
 * 알고리즘:
 *  1) 시작 시각 순으로 정렬
 *  2) 앞에서부터 훑으며, 지금까지의 그룹 최대 종료시각보다 늦게 시작하면 그룹을 끊는다
 *     (= 서로 겹치지 않는 일정 묶음의 경계)
 *  3) 한 그룹 안에서 "칼럼(열)"을 배정한다.
 *     각 열의 마지막 일정이 끝난 뒤에 시작하는 일정은 그 열을 재사용할 수 있다
 *  4) 그룹의 열 개수로 폭을 나눈다 (열 3개면 각 33%)
 *
 * 이 방식이면 09:00-10:00, 09:30-11:00, 10:30-12:00 세 개가
 * [0], [1], [0] 열에 들어가 폭 50%씩 두 열로 정리된다.
 */
export function layoutOverlaps<T extends { startAt: Date; endAt: Date }>(
  items: T[],
): Positioned<T>[] {
  const sorted = [...items].sort(
    (a, b) => a.startAt.getTime() - b.startAt.getTime() || b.endAt.getTime() - a.endAt.getTime(),
  )

  const result: Positioned<T>[] = []
  let group: T[] = []
  let groupEnd = -Infinity

  const flush = () => {
    if (group.length === 0) return
    const columns: T[][] = []
    for (const it of group) {
      // 이 일정이 들어갈 수 있는 첫 번째 열을 찾는다
      let col = columns.findIndex((c) => c[c.length - 1].endAt <= it.startAt)
      if (col === -1) {
        columns.push([it])
        col = columns.length - 1
      } else {
        columns[col].push(it)
      }
      result.push({ item: it, left: col, width: 1 }) // 폭은 아래에서 정규화
    }
    const n = columns.length
    // 이 그룹에 속한 결과들의 left/width를 비율로 환산
    for (let i = result.length - group.length; i < result.length; i++) {
      result[i].width = 1 / n
      result[i].left = result[i].left / n
    }
    group = []
    groupEnd = -Infinity
  }

  for (const it of sorted) {
    if (it.startAt.getTime() >= groupEnd) flush()   // 겹치지 않음 → 새 그룹
    group.push(it)
    groupEnd = Math.max(groupEnd, it.endAt.getTime())
  }
  flush()
  return result
}`,
      },
      { type: 'h', text: '월 뷰 컴포넌트 (핵심 부분)' },
      {
        type: 'code',
        lang: 'tsx',
        filename: 'src/components/calendar/MonthGrid.tsx',
        code: `'use client'
import { buildMonthGrid, inMonth, isToday, dayLabel } from '@/lib/date'
import type { EventDTO } from '@/lib/types'

const WEEKDAYS = ['월', '화', '수', '목', '금', '토', '일']

export function MonthGrid({
  anchor, events, onPickDay,
}: { anchor: Date; events: EventDTO[]; onPickDay: (d: Date) => void }) {
  const days = buildMonthGrid(anchor)

  // 날짜별로 일정을 미리 묶어둔다 (42칸마다 전체 배열을 훑지 않도록)
  const byDay = new Map<string, EventDTO[]>()
  for (const e of events) {
    const key = e.startAt.slice(0, 10)
    const list = byDay.get(key) ?? []
    list.push(e)
    byDay.set(key, list)
  }

  return (
    <div className="grid grid-cols-7 border-t border-l">
      {WEEKDAYS.map((w) => (
        <div key={w} className="border-r border-b px-2 py-1.5 text-xs text-neutral-500">
          {w}
        </div>
      ))}

      {days.map((d) => {
        const key = d.toISOString().slice(0, 10)
        const list = (byDay.get(key) ?? []).slice(0, 3)
        const more = (byDay.get(key)?.length ?? 0) - list.length

        return (
          <button
            key={key}
            onClick={() => onPickDay(d)}
            className={
              'h-28 border-r border-b p-1.5 text-left align-top transition hover:bg-neutral-50 ' +
              (inMonth(d, anchor) ? '' : 'text-neutral-400 bg-neutral-50/50')
            }
          >
            <span
              className={
                'inline-flex h-6 w-6 items-center justify-center rounded-full text-xs ' +
                (isToday(d) ? 'bg-blue-600 font-semibold text-white' : '')
              }
            >
              {dayLabel(d)}
            </span>

            <ul className="mt-1 space-y-0.5">
              {list.map((e) => (
                <li key={e.id} className="flex items-center gap-1 truncate text-[11px]">
                  <span
                    className="h-1.5 w-1.5 shrink-0 rounded-full"
                    style={{ background: e.color }}
                  />
                  <span className="truncate">{e.title}</span>
                </li>
              ))}
              {more > 0 && <li className="text-[11px] text-neutral-500">+{more}개 더</li>}
            </ul>
          </button>
        )
      })}
    </div>
  )
}`,
      },
      {
        type: 'callout',
        tone: 'tip',
        title: '이 코드에서 배울 습관',
        text: '`byDay` 맵을 미리 만드는 부분을 보라. 42개 칸마다 전체 일정 배열을 훑으면 일정이 500개일 때 21,000번 비교한다. 미리 한 번 묶어두면 500번이면 끝난다. **AI가 만든 코드에서 반복문 안의 반복문을 발견하면 한 번 의심해보는 습관**이 쌓이면 성능 문제 대부분이 예방된다.',
      },
    ],
    explain: [
      { type: 'h', text: '"노션 캘린더 같다"를 분해하면' },
      {
        type: 'p',
        text: '"편하다"는 느낌은 정체가 있다. 아래 항목들을 프롬프트에 명시하면 결과물이 달라진다.',
      },
      {
        type: 'table',
        head: ['느낌', '실제 구현 요소'],
        rows: [
          ['빠르다', '낙관적 갱신(서버 응답을 기다리지 않고 화면 먼저 반영), 뷰 전환 시 데이터 재사용'],
          ['안정적이다', '6주 고정 그리드, 스크롤 위치 보존, 뷰를 바꿔도 보던 날짜 유지'],
          ['키보드로 다 된다', '←/→ 이동, T=오늘, M/W 뷰 전환, N=새 일정, ESC=닫기'],
          ['입력이 안 끊긴다', '날짜 클릭 → 인라인 입력 → Enter 저장 후 입력창 유지 (모달을 다시 열지 않음)'],
          ['정보 밀도가 높다', '작은 폰트, 색 점, 좁은 여백, "+N개 더" 축약'],
        ],
      },
      { type: 'h', text: '왜 캘린더 라이브러리를 쓰지 않았나' },
      {
        type: 'p',
        text: 'FullCalendar 같은 라이브러리를 쓰면 30분에 끝난다. 여기서 직접 만든 이유는 **교육 목적**이다. 다만 실무 판단 기준은 이렇다.',
      },
      {
        type: 'table',
        head: ['상황', '판단'],
        rows: [
          ['표준 캘린더 기능이면 충분하다', '라이브러리 사용. 반복 일정·드래그·리사이즈가 이미 검증돼 있다'],
          ['우리 업무 속성(카테고리·보고 연동)이 UI에 깊게 들어간다', '직접 구현. 라이브러리의 데이터 모델과 싸우는 시간이 더 크다'],
          ['디자인을 사내 표준에 정확히 맞춰야 한다', '직접 구현 또는 headless 라이브러리만'],
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'AI에게 "캘린더 만들어줘"라고만 하면',
        text: '거의 항상 라이브러리를 설치하고, 그 라이브러리의 예제를 붙여넣는다. 그 결과 우리 데이터 모델과 안 맞아서 다음 스텝이 전부 막힌다. **라이브러리를 쓸지 말지는 사람이 먼저 결정하고 프롬프트에 명시해야 한다.**',
      },
      { type: 'h', text: '타임존: 반드시 한 번은 데는 곳' },
      {
        type: 'flow',
        title: '변환 지점을 한 곳으로 모으는 규칙',
        steps: [
          'DB 저장: 항상 UTC',
          '서버 → 클라이언트: ISO 문자열',
          '화면 표시 직전에만 Asia/Seoul 변환',
          '사용자 입력: 로컬 시각 → UTC 변환 후 저장',
        ],
      },
      {
        type: 'p',
        text: '이 규칙이 흔들리면 "종일 일정이 하루 밀려 보인다", "밤 11시 일정이 다음날로 잡힌다" 같은 버그가 생긴다. 특히 **종일 일정**은 시각이 아니라 "날짜" 개념이므로, 타임존 변환을 하지 않는 것이 정답이다. 이걸 프롬프트에 미리 못 박아둬야 한다.',
      },
      {
        type: 'callout',
        tone: 'dx',
        text: '캘린더 UI는 겉보기보다 공수가 큽니다(겹침 레이아웃, 드래그, 반복 일정, 타임존). 사내 표준 캘린더 컴포넌트가 필요하면 dX팀에 요청하세요.',
      },
    ],
    checklist: [
      '/calendar 에서 월 그리드가 뜨고 시드 일정이 보인다',
      '이전/다음/오늘 버튼이 동작한다',
      '주 뷰로 전환되고 현재 시각 선이 보인다',
      '시간이 겹치는 일정이 나란히 표시된다',
      '월이 바뀌어도 그리드 높이가 변하지 않는다',
    ],
    demo: {
      kind: 'calendar',
      hint: '이 단계의 목표물이다. 월/주 뷰를 전환하고(M·W), 6주 고정 그리드라 달을 넘겨도 높이가 흔들리지 않는 것, 겹치는 일정이 나란히 배치되는 것을 확인해보라.',
    },
  },

  {
    id: '05',
    slug: 'event-crud',
    part: 'PART 1 · 앱의 뼈대',
    title: '일정 등록·수정·삭제',
    tagline: '읽기만 되는 캘린더를 실제로 쓸 수 있는 도구로',
    duration: '50분',
    level: '기본',
    goals: [
      '서버에 데이터를 쓰는 전체 경로(입력 → 검증 → 저장 → 화면 갱신)를 이해한다',
      '입력 검증과 권한 검사를 왜 서버에서 하는지 체감한다',
      '낙관적 갱신으로 "빠른 느낌"을 만든다',
    ],
    deliverables: [
      '날짜 클릭 → 인라인 입력 → Enter 저장',
      '일정 상세 편집 패널 (제목·시간·카테고리·공개범위·메모)',
      '드래그로 일정 날짜 이동',
      'zod 검증 + 서버 권한 검사',
    ],
    prompts: [
      {
        id: 'quick-add',
        label: '빠른 입력 + 저장 경로',
        when: '캘린더 월 뷰가 동작하는 상태에서.',
        body: `일정 생성·수정·삭제를 구현해주세요. 사용자 스토리 S-04(빠른 일정 입력)를 만족해야 합니다.

## 요구사항
1. 월 뷰에서 날짜 칸 클릭 → 그 칸 안에 인라인 입력창
   - Enter 저장, ESC 취소
   - 저장 후 입력창은 그대로 유지되어 연속 입력 가능
   - 제목만 입력하면 그 날 09:00~10:00 기본값
2. 자연어 파싱: 제목에 시간 표현이 있으면 뽑아낸다
   - "14시 팀 회의" → 14:00~15:00, 제목 "팀 회의"
   - "3-5pm 고객 미팅", "10:30 스크럼 30분" 같은 패턴도 처리
   - 파싱 실패해도 절대 에러를 내지 않고 제목 전체로 저장
3. 일정 클릭 → 오른쪽 상세 패널에서 편집 (제목/시간/종일/카테고리/공개범위/메모)
4. 삭제는 확인 절차 없이 실행하고 "되돌리기" 토스트를 5초간 보여준다
5. 드래그로 다른 날짜에 놓으면 날짜만 변경 (시간은 유지)

## 구현 조건
- 서버 액션(또는 /api/events 라우트)에서 zod로 입력 검증
- **권한 검사는 반드시 서버에서**: 본인 일정만 수정/삭제 가능
- 낙관적 갱신: 화면을 먼저 바꾸고, 실패하면 되돌리고 오류 토스트
- 자연어 파싱 함수는 src/lib/parseQuickInput.ts 에 순수 함수로 분리 + 테스트 케이스 표로 정리

먼저 데이터 흐름을 4~5줄로 설명하고, 그 다음 파일별 코드를 주세요.`,
        tips: [
          '"삭제 확인 창 없이 되돌리기 제공"은 의도된 선택이다. 확인 창은 사용자를 느리게 만들고, 실수는 되돌리기로 해결하는 게 낫다.',
          '자연어 파싱은 완벽할 필요가 없다. **실패해도 안전하게** 동작하는 게 훨씬 중요하다.',
          '드래그는 마지막에 요청한다. 먼저 저장이 확실히 되는지 확인.',
        ],
      },
      {
        id: 'validation-review',
        label: '보안·검증 점검 요청',
        when: 'CRUD가 동작한 다음. AI에게 자기 코드를 감사하게 만든다.',
        body: `방금 만든 일정 CRUD 코드를 보안 관점에서 점검해주세요.

체크할 것:
1. 다른 사람의 일정 ID를 직접 넣어 요청하면 수정/삭제가 되는가? (권한 우회)
2. 서버가 클라이언트에서 온 userId 를 신뢰하고 있지는 않은가?
3. 검증되지 않은 입력이 DB로 들어갈 경로가 있는가? (제목 길이, 종료 < 시작, 잘못된 날짜)
4. 응답에 필요 이상의 정보가 담기지 않는가? (다른 사용자 정보, 내부 ID)
5. 비공개(PRIVATE) 일정이 팀 조회 API에 섞여 나오지 않는가?

발견한 문제를 위험도(높음/중간/낮음)와 함께 표로 정리하고,
가장 위험한 것부터 수정 코드를 주세요.
그리고 이런 실수를 앞으로 반복하지 않도록 CLAUDE.md 에 추가할 규칙도 제안해주세요.`,
        tips: [
          '**이 프롬프트는 모든 기능 구현 뒤에 재사용한다.** 특히 3번(권한 우회)은 AI가 만든 코드에서 가장 자주 나오는 실수다.',
          'AI가 "문제 없습니다"라고 하면 의심한다. "userId를 어디서 가져오는지 그 코드 줄을 보여주세요"라고 구체적으로 되묻는다.',
        ],
      },
    ],
    sample: [
      { type: 'h', text: '데이터 흐름' },
      {
        type: 'flow',
        steps: [
          '사용자 입력 (인라인 창)',
          '낙관적 갱신 — 화면 먼저 반영',
          '서버 액션 호출',
          'zod 검증 + 세션에서 userId 확보',
          'Prisma 저장',
          '성공: 확정 / 실패: 롤백 + 토스트',
        ],
      },
      { type: 'h', text: '자연어 빠른 입력 파서' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/lib/parseQuickInput.ts',
        code: `export interface QuickParsed {
  title: string
  startMinutes: number  // 자정 기준 분
  endMinutes: number
  matched: boolean      // 시간 표현을 찾았는지
}

const DEFAULT_START = 9 * 60
const DEFAULT_DURATION = 60

/**
 * "14시 팀 회의", "3-5pm 고객 미팅", "10:30 스크럼 30분" 같은 입력에서 시간을 뽑는다.
 * 설계 원칙: 못 알아들으면 조용히 기본값을 쓴다. 사용자에게 에러를 던지지 않는다.
 */
export function parseQuickInput(raw: string): QuickParsed {
  const input = raw.trim()
  const fallback: QuickParsed = {
    title: input,
    startMinutes: DEFAULT_START,
    endMinutes: DEFAULT_START + DEFAULT_DURATION,
    matched: false,
  }
  if (!input) return fallback

  // 1) 범위형: "3-5pm", "14:00-15:30", "9시-11시"
  const range = input.match(
    /(\\d{1,2})(?::(\\d{2}))?\\s*(?:시)?\\s*[-~]\\s*(\\d{1,2})(?::(\\d{2}))?\\s*(?:시)?\\s*(am|pm|오전|오후)?/i,
  )
  if (range) {
    const mer = range[5]?.toLowerCase()
    const start = toMinutes(+range[1], +(range[2] ?? 0), mer)
    const end = toMinutes(+range[3], +(range[4] ?? 0), mer)
    return {
      title: strip(input, range[0]),
      startMinutes: start,
      endMinutes: end > start ? end : start + DEFAULT_DURATION,
      matched: true,
    }
  }

  // 2) 시작 + 소요시간: "10:30 스크럼 30분", "14시 회의 2시간"
  const single = input.match(/(\\d{1,2})(?::(\\d{2}))?\\s*(?:시)?\\s*(am|pm|오전|오후)?/i)
  if (single) {
    const start = toMinutes(+single[1], +(single[2] ?? 0), single[3]?.toLowerCase())
    const dur = input.match(/(\\d{1,3})\\s*분/) ? +input.match(/(\\d{1,3})\\s*분/)![1]
      : input.match(/(\\d{1,2})\\s*시간/) ? +input.match(/(\\d{1,2})\\s*시간/)![1] * 60
      : DEFAULT_DURATION
    const title = strip(strip(input, single[0]), input.match(/(\\d{1,3})\\s*(분|시간)/)?.[0] ?? '')
    // 시간처럼 보이는 숫자만 있고 제목이 사라졌으면 원문을 제목으로
    return {
      title: title || input,
      startMinutes: start,
      endMinutes: start + dur,
      matched: true,
    }
  }

  return fallback
}

function toMinutes(h: number, m: number, meridiem?: string) {
  let hour = h
  if (meridiem === 'pm' || meridiem === '오후') hour = h === 12 ? 12 : h + 12
  if (meridiem === 'am' || meridiem === '오전') hour = h === 12 ? 0 : h
  // 오전/오후 표시 없이 1~7이면 업무시간대로 해석 (3시 = 15시)
  if (!meridiem && h >= 1 && h <= 7) hour = h + 12
  return Math.min(hour, 23) * 60 + Math.min(m, 59)
}

const strip = (s: string, part: string) => (part ? s.replace(part, '').trim() : s.trim())`,
      },
      {
        type: 'table',
        head: ['입력', '제목', '시간', '비고'],
        rows: [
          ['`14시 팀 회의`', '팀 회의', '14:00~15:00', '기본 1시간'],
          ['`3-5pm 고객 미팅`', '고객 미팅', '15:00~17:00', '범위 인식'],
          ['`10:30 스크럼 30분`', '스크럼', '10:30~11:00', '소요시간 인식'],
          ['`3시 리뷰`', '리뷰', '15:00~16:00', '오전/오후 없으면 업무시간 추정'],
          ['`분기 계획 정리`', '분기 계획 정리', '09:00~10:00', '시간 없음 → 기본값, 에러 없음'],
        ],
      },
      { type: 'h', text: '서버 액션 — 검증과 권한' },
      {
        type: 'code',
        lang: 'typescript',
        filename: 'src/server/actions/events.ts',
        code: `'use server'
import { z } from 'zod'
import { revalidatePath } from 'next/cache'
import { db } from '@/server/db'
import { requireUser } from '@/server/auth'

const CreateEvent = z
  .object({
    title: z.string().trim().min(1, '제목을 입력하세요').max(200),
    startAt: z.coerce.date(),
    endAt: z.coerce.date(),
    allDay: z.boolean().default(false),
    categoryId: z.string().cuid().optional(),
    visibility: z.enum(['TEAM', 'PRIVATE']).default('TEAM'),
    description: z.string().max(5000).optional(),
  })
  .refine((v) => v.endAt > v.startAt, {
    message: '종료 시각이 시작 시각보다 빨라요',
    path: ['endAt'],
  })

export async function createEvent(input: unknown) {
  // ① 세션에서 사용자를 가져온다. 클라이언트가 보낸 userId는 절대 믿지 않는다.
  const user = await requireUser()

  // ② 입력 검증. 통과한 값만 DB로 간다.
  const data = CreateEvent.parse(input)

  const event = await db.event.create({
    data: { ...data, userId: user.id },   // ③ userId는 서버가 붙인다
    include: { category: true },
  })

  revalidatePath('/calendar')
  return event
}

export async function updateEvent(id: string, input: unknown) {
  const user = await requireUser()
  const data = CreateEvent.partial().parse(input)

  // ④ 권한 검사: "내 것"이라는 조건을 WHERE 절에 넣는다.
  //    먼저 조회해서 비교하는 방식보다 안전하다 (경쟁 조건 없음)
  const result = await db.event.updateMany({
    where: { id, userId: user.id },
    data,
  })
  if (result.count === 0) throw new Error('일정을 찾을 수 없거나 권한이 없습니다')

  revalidatePath('/calendar')
}

export async function deleteEvent(id: string) {
  const user = await requireUser()
  const result = await db.event.deleteMany({ where: { id, userId: user.id } })
  if (result.count === 0) throw new Error('일정을 찾을 수 없거나 권한이 없습니다')
  revalidatePath('/calendar')
}`,
      },
      { type: 'h', text: '보안 점검 프롬프트 결과 (예시)' },
      {
        type: 'table',
        head: ['위험도', '발견', '수정'],
        rows: [
          [
            '**높음**',
            '`updateEvent` 초기 버전이 `db.event.update({ where: { id } })` 였다 → 남의 일정 ID를 넣으면 수정 가능',
            '`updateMany` + `where: { id, userId }` 로 변경'],
          [
            '**높음**',
            '팀 캘린더 조회 API가 `visibility: PRIVATE` 일정의 제목까지 반환',
            '조회 시 `visibility: TEAM` 필터, 비공개는 "바쁨"으로 치환해서 반환'],
          [
            '중간',
            '클라이언트가 보낸 `userId` 를 그대로 저장 → 다른 사람 이름으로 일정 생성 가능',
            '요청 본문에서 `userId` 필드를 아예 제거하고 세션에서만 가져옴'],
          ['중간', '제목 길이 제한 없음 → 10만 자 입력 시 화면 깨짐', 'zod `max(200)`'],
          ['낮음', '응답에 사용자 이메일·내부 팀 ID 포함', '필요한 필드만 select'],
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: '이 표가 이 스텝의 진짜 결과물이다',
        text: '1·3번 항목은 AI가 만든 코드에서 **매우 흔하게** 나온다. AI는 "동작하는 코드"를 만들도록 학습됐고, 권한 검사는 동작에 영향을 주지 않기 때문이다. 기능이 하나 끝날 때마다 위 점검 프롬프트를 돌리는 습관을 들여야 한다.',
      },
    ],
    explain: [
      { type: 'h', text: '왜 검증을 서버에서 또 하는가' },
      {
        type: 'p',
        text: '화면에서 이미 "제목은 필수"라고 막았는데 서버에서 또 검사하는 게 낭비처럼 보인다. 하지만 **화면 검증은 사용자 편의고, 서버 검증은 보안이다.** 브라우저 개발자 도구나 curl 한 줄로 화면을 건너뛰고 서버에 직접 요청을 보낼 수 있다.',
      },
      {
        type: 'code',
        lang: 'bash',
        code: `# 화면을 전혀 거치지 않고 서버에 직접 요청 — 누구나 할 수 있다
curl -X POST https://ourapp.com/api/events \\
  -H "Content-Type: application/json" \\
  -d '{"title":"","userId":"other-person-id","startAt":"2026-13-45"}'`,
      },
      {
        type: 'p',
        text: '그래서 원칙은 하나다. **"클라이언트에서 온 것은 전부 거짓일 수 있다."** 누가 요청했는지는 세션(쿠키)에서만 가져오고, 무엇을 요청했는지는 검증한 뒤에만 쓴다.',
      },
      { type: 'h', text: '낙관적 갱신 (Optimistic Update)' },
      {
        type: 'table',
        head: ['방식', '사용자 체감', '위험'],
        rows: [
          ['서버 응답 후 화면 갱신', '클릭 후 200~500ms 멈춤. 연속 입력 시 답답', '없음'],
          ['**낙관적 갱신**', '즉시 반영. "빠르다"는 느낌의 정체', '실패 시 되돌리는 코드를 반드시 써야 한다'],
        ],
      },
      {
        type: 'p',
        text: '낙관적 갱신의 함정은 **실패 처리를 잊는 것**이다. AI에게 요청할 때 "실패하면 되돌리고 오류를 알려준다"를 반드시 같이 적어야 한다. 안 적으면 저장 실패한 일정이 화면에만 남아 있다가 새로고침하면 사라지는, 최악의 버그가 생긴다.',
      },
      { type: 'h', text: '자연어 입력을 "실패해도 안전하게" 만드는 설계' },
      {
        type: 'p',
        text: '`parseQuickInput` 이 가장 잘한 부분은 파싱 정확도가 아니라 **어떤 입력에도 예외를 던지지 않는다**는 점이다. "분기 계획 정리"처럼 시간이 없으면 기본값을 쓰고 제목을 그대로 보존한다. 사용자는 파서가 있다는 사실조차 모르는 게 좋다.',
      },
      {
        type: 'callout',
        tone: 'tip',
        title: '11단계 예고',
        text: '정규식 파서로는 "다음주 화요일 오후에 김부장님과 미팅" 같은 문장을 못 다룬다. 11단계에서 웍스 AI를 붙이면 이런 문장도 일정으로 바꿀 수 있다. **다만 정규식 파서를 먼저 만드는 이유는, AI 호출은 느리고 비용이 들고 실패할 수 있기 때문이다.** 흔한 패턴은 규칙으로 즉시 처리하고, 애매한 것만 AI에게 넘기는 게 좋은 설계다.',
      },
      {
        type: 'callout',
        tone: 'dx',
        text: '권한 모델(팀 간 열람 범위, 팀장 대리 수정, 관리자 감사)은 조직 정책에 따라 달라집니다. 정책 설계와 코드 감사는 dX팀에 요청하세요.',
      },
    ],
    checklist: [
      '날짜를 클릭해 제목만 입력하고 Enter로 저장된다',
      '"14시 팀 회의" 처럼 입력하면 시간이 잡힌다',
      '일정을 클릭해 시간·카테고리·공개범위를 수정할 수 있다',
      '삭제 후 되돌리기가 동작한다',
      '드래그로 다른 날짜로 옮길 수 있다',
      '보안 점검 프롬프트를 돌려 발견된 문제를 고쳤다',
      '남의 일정 ID로 수정 요청을 보내면 거부된다',
    ],
    demo: {
      kind: 'calendar',
      hint: '날짜를 클릭해 "14시 팀 회의"처럼 입력해보라. Enter 후 입력창이 유지돼 연속 입력이 되는 것, 일정을 드래그해 날짜를 옮기는 것, 삭제 후 되돌리기가 뜨는 것 — 이 세 가지가 이 단계에서 만들 동작이다.',
    },
  },
]
