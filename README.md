# 바이브 코딩 교육 프로그램 (웹앱)

프롬프트를 복사해 AI에게 붙여넣으면서 **업무 캘린더 · 주간보고 · 인수인계 웹앱**을 15단계로 만들어 보는
사내 교육 프로그램입니다. dX팀 교육용.

교육 대상이 만드는 결과물은 이런 것입니다.

1. 노션 캘린더 수준의 사용감을 가진 업무 캘린더 (월/주 뷰, 빠른 입력, 드래그 이동)
2. 구글 캘린더 양방향 연동 + 네이버·ICS 등 다른 캘린더를 골라서 추가하는 구조
3. 캘린더 기록을 자동 집계하는 주간보고
4. 주간회의에서 한 명이 화면을 띄워 팀원별 보고를 넘겨보는 발표 모드
5. 부재 시 업무를 넘기고 돌아와서 무슨 일이 있었는지 아는 인수인계
6. RADIUS 로그인 · Coolify 배포 · 사내 웍스 AI 연동

## 이 앱이 제공하는 것

| 화면 | 내용 |
|---|---|
| `/` | 커리큘럼 개요, 진행률 (브라우저에 저장) |
| `/steps/:slug` | 각 단계 — **개요 / 완성 데모 / 프롬프트 / 샘플 결과물 / 원리 설명 / 체크리스트** 탭 |
| `/steps/:slug/demo` | 그 단계에서 만들 결과물의 **동작하는 데모** (해당 단계에만 붙는다) |
| `/prompts` | 전체 프롬프트 30개 검색·복사 |

각 단계는 이렇게 쓰도록 설계했습니다.

- **완성 데모 탭** — 그 단계에서 만들 결과물이 실제로 동작하는 상태로 들어 있다.
  프롬프트를 치기 전에 무엇을 만드는지 눈으로 확인하는 자리다. 데모는 별도 메뉴가 아니라
  **해당 단계 안에만** 붙는다 (목차에서도 그 단계 하위 항목으로 보인다).
- **프롬프트 탭** — 그대로 복사해 AI 대화창(Claude Code / Cursor / 사내 AI)에 붙여넣는다.
- **샘플 결과물 탭** — AI 응답을 기다리기 싫거나 실습 없이 흐름만 보고 싶을 때. 그 프롬프트를 실행하면
  나올 결과(코드·문서·표)를 미리 넣어 두었다. 이 탭만 읽어도 전체 과정을 이해할 수 있다.
- **원리 설명 탭** — dX팀이 대신 만들어 준다 해도 원리는 알아야 하므로, 왜 그렇게 하는지와
  무엇을 결정해야 하는지를 다룬다. (OAuth, 증분 동기화, 권한 검사, 마이그레이션, RADIUS, 컨테이너 배포 등)

데모는 목업 이미지가 아니라 실제로 동작합니다. STEP 05의 캘린더 데모에서 일정을 추가하면 STEP 08의
주간보고 데모와 STEP 09의 발표 모드 데모에 그대로 반영되고, STEP 10의 인수인계 데모에서는
인계자/인수자 시점을 바꿔가며 권한 차이를 직접 확인할 수 있습니다.

데모가 붙어 있는 단계는 다음과 같습니다.

| 단계 | 데모 |
|---|---|
| STEP 01 요구사항 정의 | 캘린더 (앞으로 만들 것의 전체 그림) |
| STEP 04 캘린더 UI · STEP 05 일정 CRUD | 캘린더 |
| STEP 06 구글 캘린더 · STEP 07 다른 캘린더 추가 | 캘린더 연동 설정 |
| STEP 08 주간보고 | 주간보고 |
| STEP 09 발표 모드 | 발표 모드 |
| STEP 10 인수인계 | 인수인계 |

## 실행 방법

### 가장 쉬운 방법 (설치 없음)

배포된 주소를 열면 됩니다. 설치도, 다운로드도, 터미널도 필요 없습니다.

> **https://hong-seok-young.github.io/vibe-coding-education/**

기본 브랜치에 push 하면 GitHub Actions 가 빌드해서 이 주소로 자동 배포합니다.
학습 진행 상황은 각자 브라우저에만 저장되므로 여러 명이 같은 주소를 써도 서로 섞이지 않습니다.

인터넷 없이 쓰거나 사내 위키에 첨부하려면 파일 하나로 묶을 수도 있습니다.

```bash
npm run build:artifact     # → artifact/vibe-coding-education.html (약 570 kB, 자립형)
```

이 파일은 Actions 실행 페이지의 산출물(`single-file-html`)에서도 내려받을 수 있습니다.

### 내 PC에서 개발 모드로 (더블클릭)

1. **Node.js LTS 설치** — https://nodejs.org (한 번만 하면 됩니다)
2. 이 폴더에서
   - **Windows**: `start.bat` 더블클릭
   - **macOS**: `start.command` 더블클릭
     (처음에 "확인되지 않은 개발자" 경고가 뜨면 파일 우클릭 → 열기)
   - **Linux**: 터미널에서 `bash start.command`
3. 잠시 기다리면 브라우저에 http://localhost:5173 이 자동으로 열립니다

처음 실행할 때만 필요한 패키지를 내려받으므로 2~3분 걸립니다. 그다음부터는 몇 초면 열립니다.
창을 닫거나 `Ctrl+C` 를 누르면 종료됩니다.

### 명령어로 실행

```bash
npm install        # 처음 한 번만
npm run dev        # http://localhost:5173
```

```bash
npm run build      # 타입 검사 + 정적 빌드 → dist/
npm run preview    # 빌드 결과 확인
```

### 소스 받기

git이 없다면 GitHub 저장소에서 브랜치를 고른 뒤 **Code → Download ZIP** 으로 받아 압축을 풀면 됩니다.

```bash
git clone -b claude/vibe-coding-education-program-lgtqes \
  https://github.com/hong-seok-young/vibe-coding-education.git
cd vibe-coding-education
```

> 사내 프록시 환경에서 `npm install` 이 막히는 경우가 있습니다. 그때는 dX팀에 문의하세요.

## 배포

### GitHub Pages (기본 · git push 하면 자동)

`.github/workflows/deploy.yml` 이 기본 브랜치 push 마다 빌드해서 Pages 로 배포합니다.
PR 에서는 배포 없이 빌드·타입검사만 돌아갑니다.

**최초 1회만 저장소 설정이 필요합니다.** Pages 사이트를 만드는 권한은 워크플로 토큰에 없어서
이 부분만 사람이 해야 합니다.

> Settings → Pages → Build and deployment → Source: **GitHub Actions**

설정한 뒤 Actions 탭에서 마지막 실행을 **Re-run jobs** 하면 배포됩니다.
그다음부터는 push 만 하면 자동입니다.

배포 주소: https://hong-seok-young.github.io/vibe-coding-education/

Pages 관련해서 알아둘 것:

- 하위 경로(`/vibe-coding-education/`)로 서빙되므로 빌드 시 `VITE_BASE` 로 그 경로를 넘깁니다.
  라우터도 `BASE_URL` 을 basename 으로 씁니다.
- Pages 에는 SPA 폴백이 없어서 `index.html` 을 `404.html` 로 복사합니다.
  이게 없으면 `/steps/orientation` 직접 진입·새로고침이 404 로 떨어집니다.
- 저장소가 public 이라 Pages 는 무료입니다. private 으로 바꾸면 유료 플랜이 필요합니다.

### Coolify (사내망에 올릴 때)

사내 데이터를 다루는 도구를 사내 서버에서 돌려야 한다면 이쪽입니다.
저장소를 Coolify에 연결하고 빌드 방식을 **Dockerfile**로 지정하면 됩니다.

- 컨테이너 포트: `8080` (root가 아닌 사용자로 실행하므로 80이 아니라 8080을 씁니다)
- 헬스체크 경로: `/healthz`
- SPA 라우팅 폴백은 `nginx.conf`의 `try_files ... /index.html` 이 처리합니다.
  이게 없으면 `/steps/orientation` 을 새로고침할 때 404가 납니다.

로컬에서 컨테이너로 확인하려면:

```bash
docker build -t vibe-edu .
docker run --rm -p 8080:8080 vibe-edu   # http://localhost:8080
```

## 구조

```
src/
├─ content/                교육 콘텐츠 (여기만 고치면 커리큘럼이 바뀐다)
│  ├─ types.ts             Step / Prompt / Block 타입 정의
│  ├─ index.ts             전체 단계 목록과 조회 함수
│  └─ steps/
│     ├─ part0.ts          STEP 00–01  준비 (오리엔테이션, PRD)
│     ├─ part1.ts          STEP 02–05  앱의 뼈대 (셋업, 데이터 모델, 캘린더, CRUD)
│     ├─ part2.ts          STEP 06–07  외부 캘린더 연동 (구글, 네이버·ICS)
│     ├─ part3.ts          STEP 08–10  업무 활용 (주간보고, 발표 모드, 인수인계)
│     └─ part4.ts          STEP 11–14  웍스 AI, RADIUS, Coolify, 운영·요청서
├─ components/             Layout, Blocks 렌더러, PromptCard, CodeBlock
├─ pages/                  HomePage, StepPage, PromptsPage
├─ demo/                   동작하는 완성 결과물 데모 (각 단계의 "완성 데모" 탭에서 렌더링)
│  ├─ registry.tsx         데모 종류 → 컴포넌트 · 조작법 매핑
│  ├─ data.ts              목업 데이터 (실행 시점의 "이번 주" 기준 상대 날짜)
│  ├─ store.tsx            데모 상태 (캘린더 → 주간보고 → 발표 모드 공유)
│  ├─ aggregate.ts         주간보고 집계 로직 (순수 함수)
│  ├─ CalendarDemo.tsx     월/주 뷰, 빠른 입력, 드래그, 상세 편집
│  ├─ WeeklyDemo.tsx       자동 집계 + 수정 보존 + 마크다운 복사
│  ├─ PresentDemo.tsx      발표 모드 (키보드 조작, 타이머, 회의록 복사)
│  ├─ HandoverDemo.tsx     인수인계 (상태 흐름, 권한, 감사 로그)
│  └─ IntegrationsDemo.tsx 프로바이더 능력(capability) 기반 연동 설정
└─ lib/                    날짜 유틸, 겹침 레이아웃, 빠른 입력 파서, 진행률, 테마
```

## 콘텐츠 수정하기

교육 내용은 전부 `src/content/steps/*.ts` 에 데이터로 들어 있습니다. 마크다운 파서를 쓰지 않고
블록 타입으로 정의해서, 렌더링이 예측 가능하고 타입 검사가 됩니다.

한 단계는 이런 모양입니다.

```ts
{
  id: '06',
  slug: 'google-calendar',
  part: 'PART 2 · 외부 캘린더 연동',
  title: '구글 캘린더 연동',
  tagline: 'OAuth 로그인 → 일정 읽기 → 내보내기 → 증분 동기화',
  duration: '90분',
  level: '심화',
  goals: [...],           // 학습 목표
  deliverables: [...],    // 끝나면 손에 남는 것
  prompts: [              // 복사해서 AI에 붙여넣는 프롬프트
    { id, label, when, body, tips: [...] },
  ],
  sample: [...],          // 프롬프트 실행 결과 (Block[])
  explain: [...],         // 원리 설명 (Block[])
  checklist: [...],       // 스스로 확인
  dxNote: '...',          // dX팀 지원 포인트
  demo: {                 // 이 단계에 붙는 완성 데모 (없으면 탭도 안 생긴다)
    kind: 'calendar',     // calendar | weekly | present | handover | integrations
    hint: '이 데모에서 무엇을 보라는 것인지 한두 문장',
  },
}
```

`sample` / `explain` 에 쓸 수 있는 블록은 다음과 같습니다 (`src/content/types.ts`).

| 블록 | 용도 |
|---|---|
| `h` / `p` | 소제목 / 문단 |
| `ul` / `ol` | 목록 / 순서 목록 |
| `code` | 코드 블록 (파일명·복사 버튼 포함) |
| `callout` | `info` · `tip` · `warn` · `dx` 강조 상자 |
| `table` | 비교 표 |
| `flow` | 단계 흐름 (A → B → C) |
| `files` | 폴더 구조 트리 |

문단·목록·표 안에서는 `` `코드` ``, `**강조**`, `[링크](url)` 세 가지 인라인 표기를 쓸 수 있습니다.

단계를 추가하려면 해당 `part*.ts` 배열에 객체를 하나 넣으면 됩니다. 사이드바 목차, 홈 화면 커리큘럼,
프롬프트 모음, 진행률은 모두 이 배열에서 자동 생성됩니다.

## 스택

Vite · React 19 · TypeScript · Tailwind CSS 4 · React Router. 외부 API 호출이나 백엔드가 없는
정적 앱이라, 사내망 어디에 올려도 그대로 동작합니다. 학습 진행 상황과 테마는 브라우저
localStorage 에만 저장됩니다.

배포 방식은 세 가지가 있고 같은 소스에서 나옵니다.

| 방식 | 명령 | 쓰는 상황 |
|---|---|---|
| GitHub Pages | git push (Actions 자동) | 기본. 사내망 제한이 없을 때 |
| 컨테이너 | `Dockerfile` | Coolify — 사내 서버에서 돌려야 할 때 |
| 정적 파일 묶음 | `npm run build` | nginx 등 기존 웹서버에 올릴 때 (`dist/`) |
| 단일 HTML 파일 | `npm run build:artifact` | 서버 없이 첨부·오프라인 배포 (해시 라우팅) |

## 참고

교육 콘텐츠에 나오는 외부 서비스 스펙(네이버 캘린더 API 범위, 웍스 AI 실제 엔드포인트, 사내 RADIUS
설정 등)은 **연동 전에 공식 문서와 담당 부서에서 직접 확인해야 합니다.** 해당 단계에도 같은 주의를
적어 두었습니다.
