# 사내 이슈 데일리 리포트 봇

바이브코딩 2시간 실습의 **완성본**. 내 PC에서 `python main.py` 한 번이면 아래가 자동으로 돈다.

```
DART 공시 ─┐
네이버 뉴스 ─┼─→ 중복 제거 → Claude API 요약 → 아웃룩 발송 → 내 메일함
RSS 피드   ─┘
```

사내에서 이미 쓰이는 **키워드 모니터링 메일링**, **경쟁사 동향 수집**, **데일리 뉴스 리포트**가
모두 이 구조다. 키워드와 받는 사람만 바꾸면 팀별 도구가 된다.

---

## 1. 사전 준비 (교육 전에 미리)

### 키 3종 발급

| 키 | 발급처 | 비용 |
|---|---|---|
| DART 인증키 | https://opendart.fss.or.kr → 회원가입 → 인증키 신청 | 무료 (1일 2만건) |
| 네이버 Client ID/Secret | https://developers.naver.com → 애플리케이션 등록 → 검색 API 선택 | 무료 (1일 2.5만회) |
| Claude API Key | https://console.anthropic.com → API Keys | 유료 (아래 비용 참고) |

### 아웃룩 발송 준비 (제일 자주 막히는 단계)

회사 아웃룩(Microsoft 365)은 **아이디 + 비밀번호로 메일을 보내는 옛 방식(SMTP 기본 인증)을
막아 두었다.** 지금 확실하게 되는 길은 **Microsoft Graph API** 이고, 준비물은 앱 ID 하나뿐이다.
비밀번호는 `.env` 에 적지 않는다.

**Azure 앱 등록 (강사가 한 번만 만들어 교육생에게 앱 ID를 나눠줘도 된다)**

1. https://portal.azure.com → **Microsoft Entra ID** → **앱 등록** → **새 등록**
   - 이름: 아무거나 (예: `issue-report-bot`)
   - 지원 계정 유형: 사내 계정만 쓰면 "이 조직 디렉터리의 계정만"
   - 리디렉션 URI: **비워 둔다**
2. 만들어진 앱의 **[개요]** 에서 `애플리케이션(클라이언트) ID` 와 `디렉터리(테넌트) ID` 복사
   → `.env` 의 `MS_CLIENT_ID`, `MS_TENANT_ID`
3. **[인증]** 탭 → 맨 아래 **"퍼블릭 클라이언트 흐름 허용" 을 예(Yes)** 로 (이걸 빼먹으면 로그인이 실패한다)
4. **[API 권한]** → 권한 추가 → **Microsoft Graph** → **위임된 권한** → `Mail.Send` 추가
   (테넌트 설정에 따라 관리자 동의가 필요할 수 있다)

**첫 로그인** — 교육 시작 전에 미리 해두면 실습 중 시간을 벌 수 있다.

```bash
python main.py --login
```

터미널에 뜬 코드를 https://microsoft.com/devicelogin 에 입력하고 회사 계정으로 로그인하면 끝이다.
토큰이 `.ms_token_cache.json` 에 저장되어 다음부터는 로그인 창이 뜨지 않는다.

> **개인 outlook.com 계정**이거나 사내에서 SMTP 인증이 아직 열려 있다면 `MAIL_PROVIDER=smtp` 로
> 두고 `OUTLOOK_ADDRESS` / `OUTLOOK_PASSWORD` 만 채워도 된다. 회사 계정에서 `535` 오류가 나면
> 막힌 것이니 위의 Graph 방식으로 간다.

---

## 2. 설치와 실행

```bash
# 1) 필요한 라이브러리 설치
pip install -r requirements.txt

# 2) 설정 파일 만들기
cp .env.example .env          # Windows PowerShell: copy .env.example .env
#    .env 를 열어 키워드와 키를 채운다

# 3) 아웃룩 로그인 (Graph 방식일 때 한 번만)
python main.py --login

# 4) 먼저 메일 없이 확인 (권장)
python main.py --dry-run

# 5) 진짜 발송
python main.py
```

### 실행 옵션

| 옵션 | 하는 일 |
|---|---|
| `--dry-run` | 메일을 보내지 않고 콘솔에만 출력. 처음엔 이걸로 확인 |
| `--no-ai` | AI 요약을 건너뜀. Claude 키 없이 수집만 테스트할 때 |
| `--login` | 아웃룩 로그인만 미리 해둔다. 수집·발송은 하지 않음 |

---

## 3. 자주 나는 에러

| 증상 | 원인과 해결 |
|---|---|
| SMTP `535` 로그인 실패 | 회사가 SMTP 기본 인증을 막은 것이다. 비밀번호 문제가 아니니 재입력해도 소용없다. `MS_CLIENT_ID` 를 채우고 `MAIL_PROVIDER=graph` 로 |
| 로그인 창에서 `AADSTS7000218` | Azure 앱 [인증] 탭의 **"퍼블릭 클라이언트 흐름 허용"** 이 아니오로 되어 있다 |
| Graph 발송 `403` | 앱 [API 권한] 에 **위임된** `Mail.Send` 가 없거나 관리자 동의가 안 된 상태 |
| Graph 발송 `401` | 토큰 만료. `.ms_token_cache.json` 을 지우고 `python main.py --login` 다시 |
| `AADSTS50020` / 계정을 찾을 수 없음 | `MS_TENANT_ID` 가 내 계정의 테넌트와 다르다. 회사 계정이면 사내 테넌트 ID로 |
| `RSS 실패 ... Forbidden` | 회사 네트워크가 그 사이트를 막는 경우. 다른 RSS 주소로 바꾸거나 개인 네트워크에서 실행 |
| 네이버 `401` | Client ID/Secret 오타, 또는 애플리케이션에 **검색 API**를 추가하지 않음 |
| DART `[013]` | 오류가 아니다. 그 기간에 공시가 없다는 뜻 (주말·공휴일이면 정상) |
| DART `[020]` | 하루 호출 한도 초과. 내일 다시 |
| `수집 0건` | `.env` 의 `KEYWORDS` 가 비었거나, 키워드가 너무 좁다. 넓은 단어로 먼저 시험 |

막히면 **에러 메시지 전문을 그대로 복사해서 Claude에게 붙여넣는 것**이 가장 빠르다.

---

## 4. 매일 자동으로 실행하기

교육에서는 수동 실행까지만 한다. 자동화는 이 단계를 추가하면 된다.

**Windows — 작업 스케줄러**
1. `작업 스케줄러` → `기본 작업 만들기` → 트리거: 매일 오전 8시
2. 동작: `프로그램 시작` → 프로그램에 `python.exe` 경로, 인수에 `main.py`,
   시작 위치에 이 폴더 경로

**macOS / Linux — cron**
```bash
crontab -e
# 매일 오전 8시
0 8 * * * cd /경로/news-report-bot && /usr/bin/python3 main.py
```

> PC가 꺼져 있으면 실행되지 않는다. 24시간 돌리려면 서버가 필요하다.

---

## 5. 비용

Claude API는 요약 1회에 대략 수집 항목 40건 기준 **50~100원** 수준이다
(매일 1회 실행 시 월 2~3천원). 정확한 단가는 https://claude.com/pricing 참고.

더 줄이고 싶으면 `main.py` 의 `summarize_with_claude()` 에서
`output_config={"effort": "low"}` 를 추가하거나 `model` 을 `claude-sonnet-5` 로 바꾼다.

---

## 6. 보안 — 꼭 지킬 것

- **`.env` 와 `.ms_token_cache.json` 은 절대 공유하지 않는다.** 메신저·메일·깃허브에 올리는
  순간 키가 유출된다. 특히 `.ms_token_cache.json` 에는 **내 아웃룩 계정으로 메일을 보낼 수 있는
  토큰**이 들어 있다 (이 폴더의 `.gitignore` 가 두 파일을 이미 제외하도록 되어 있다).
- 크롤링 대상은 **공개된 뉴스·공시·RSS만** 쓴다. 로그인이 필요한 사이트, 유료 콘텐츠,
  사내망 시스템은 대상으로 삼지 않는다.
- 사내 기밀·개인정보를 프롬프트에 넣지 않는다. 이 스크립트가 다루는 것은 전부 공개 정보다.

---

## 파일 구성

| 파일 | 내용 |
|---|---|
| `main.py` | 전체 파이프라인. 실습 단계별로 주석이 나뉘어 있다 |
| `.env.example` | 설정 템플릿. 복사해서 `.env` 로 쓴다 |
| `requirements.txt` | 필요한 라이브러리 5개 |
