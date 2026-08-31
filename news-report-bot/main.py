"""사내 이슈 데일리 리포트 봇 — 바이브코딩 실습 완성본.

파이프라인:
    수집(RSS · 네이버 뉴스 · DART 공시) → Claude API 요약 → Outlook 발송

실행:
    python main.py --dry-run     # 메일 없이 콘솔로만 확인 (처음엔 이걸로)
    python main.py --no-ai       # AI 요약 없이 목록만
    python main.py --login       # 아웃룩(Microsoft) 로그인만 미리 해두기
    python main.py               # 전체 실행 (메일 발송)

설정은 모두 같은 폴더의 .env 파일에서 읽는다. (.env.example 참고)
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import smtplib
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
from urllib.parse import quote

import feedparser
import requests
from dotenv import load_dotenv

load_dotenv()

KST = timezone(timedelta(hours=9))
FAR_PAST = datetime(1970, 1, 1, tzinfo=timezone.utc)


# ─────────────────────────────────────────────────────────────
# 설정 — .env 에서 읽어온다
# ─────────────────────────────────────────────────────────────

def _env_list(name: str) -> list[str]:
    """쉼표로 구분된 환경변수를 리스트로. 빈 값은 버린다."""
    return [v.strip() for v in os.getenv(name, "").split(",") if v.strip()]


KEYWORDS = _env_list("KEYWORDS")                # 모니터링할 키워드
RSS_FEEDS = _env_list("RSS_FEEDS")              # 직접 지정한 RSS 주소
DART_WATCH = _env_list("DART_WATCH")            # 공시를 지켜볼 회사명 (비우면 전체)
DAYS_BACK = int(os.getenv("DAYS_BACK", "1"))    # 며칠치를 볼 것인가 (오늘 포함)
MAX_ITEMS = int(os.getenv("MAX_ITEMS", "40"))   # AI에 넘길 최대 건수

DART_API_KEY = os.getenv("DART_API_KEY", "")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

# ── 아웃룩(Microsoft 365 / Outlook.com) 발송 설정 ──────────
# 보내는 사람이자, MAIL_TO 를 비웠을 때의 기본 수신자.
OUTLOOK_ADDRESS = os.getenv("OUTLOOK_ADDRESS", "")

# 발송 방식: graph(권장) | smtp | auto(기본 — 설정된 쪽을 알아서 고른다)
MAIL_PROVIDER = os.getenv("MAIL_PROVIDER", "auto").strip().lower()

# Graph 방식에 필요한 값. Azure 포털에 등록한 앱의 ID (비밀번호는 필요 없다).
MS_CLIENT_ID = os.getenv("MS_CLIENT_ID", "").strip()
# 회사 계정이면 사내 테넌트 ID, 개인 outlook.com 계정도 섞어 쓰려면 common.
MS_TENANT_ID = os.getenv("MS_TENANT_ID", "common").strip() or "common"
# 로그인 결과(토큰)를 저장해 두는 파일. 두 번째 실행부터는 로그인 창이 안 뜬다.
MS_TOKEN_CACHE = os.getenv("MS_TOKEN_CACHE", ".ms_token_cache.json")

# SMTP 방식(옛 방식)에만 필요. 사내 정책상 막혀 있는 회사가 많다.
OUTLOOK_PASSWORD = os.getenv("OUTLOOK_PASSWORD", "").strip()
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.office365.com").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

MAIL_TO = _env_list("MAIL_TO") or ([OUTLOOK_ADDRESS] if OUTLOOK_ADDRESS else [])


@dataclass
class Item:
    """수집한 항목 하나 (뉴스 기사든 공시든 같은 모양으로 다룬다)."""

    source: str                       # "RSS" | "네이버뉴스" | "DART"
    title: str
    link: str
    dt: datetime | None = None        # 발행 시각 (timezone 포함)
    note: str = field(default="")     # 공시 제출인 등 부가 정보

    @property
    def when(self) -> str:
        return self.dt.astimezone(KST).strftime("%m/%d %H:%M") if self.dt else "-"


def clean_text(raw: str) -> str:
    """HTML 태그와 엔티티를 걷어낸다. (네이버 API 응답은 <b> 태그가 섞여 온다)"""
    return html.unescape(re.sub(r"<[^>]+>", "", raw)).strip()


# ─────────────────────────────────────────────────────────────
# STEP 1. 수집 ① RSS — 키 발급이 필요 없다. 여기서 첫 성공을 만든다.
# ─────────────────────────────────────────────────────────────

def google_news_rss(keyword: str) -> str:
    """구글 뉴스는 키워드 검색 결과를 RSS로 내준다. 키가 필요 없어 실습 시작용으로 좋다."""
    return f"https://news.google.com/rss/search?q={quote(keyword)}&hl=ko&gl=KR&ceid=KR:ko"


def collect_rss(limit_per_feed: int = 10) -> list[Item]:
    feeds = list(RSS_FEEDS) + [google_news_rss(kw) for kw in KEYWORDS]
    items: list[Item] = []

    for url in feeds:
        parsed = feedparser.parse(url)

        # feedparser는 네트워크가 막혀도 예외를 던지지 않고 조용히 빈 결과를 준다.
        # 왜 0건인지 알 수 있도록 여기서 직접 확인한다.
        if parsed.bozo and not parsed.entries:
            print(f"  ! RSS 실패 ({url[:60]}...): {parsed.bozo_exception}")
            continue

        for entry in parsed.entries[:limit_per_feed]:
            dt = None
            if getattr(entry, "published_parsed", None):
                dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            items.append(Item(
                source="RSS",
                title=clean_text(entry.get("title", "")),
                link=entry.get("link", ""),
                dt=dt,
            ))

    return items


# ─────────────────────────────────────────────────────────────
# STEP 2. 수집 ② 네이버 뉴스 검색 API — 헤더로 인증하는 첫 경험
# ─────────────────────────────────────────────────────────────

def collect_naver_news(display: int = 10) -> list[Item]:
    if not (NAVER_CLIENT_ID and NAVER_CLIENT_SECRET):
        print("  - 네이버 키가 없어 건너뜀 (.env의 NAVER_CLIENT_ID / SECRET)")
        return []

    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    items: list[Item] = []

    for keyword in KEYWORDS:
        try:
            resp = requests.get(
                "https://openapi.naver.com/v1/search/news.json",
                headers=headers,
                params={"query": keyword, "display": display, "sort": "date"},
                timeout=10,
            )
            resp.raise_for_status()
        except requests.HTTPError as exc:
            # 401이면 키가 틀린 것, 429면 하루 호출량(25,000회) 초과
            print(f"  ! 네이버 검색 실패 ('{keyword}'): {exc}")
            continue
        except requests.RequestException as exc:
            print(f"  ! 네이버 연결 실패 ('{keyword}'): {exc}")
            continue

        for row in resp.json().get("items", []):
            dt = None
            try:
                dt = parsedate_to_datetime(row.get("pubDate", ""))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=KST)
            except (TypeError, ValueError):
                pass

            items.append(Item(
                source="네이버뉴스",
                title=clean_text(row.get("title", "")),
                link=row.get("originallink") or row.get("link", ""),
                dt=dt,
            ))

    return items


# ─────────────────────────────────────────────────────────────
# STEP 3. 수집 ③ DART 공시 — 파라미터가 가장 많은 API
# ─────────────────────────────────────────────────────────────

def collect_dart(max_pages: int = 5) -> list[Item]:
    if not DART_API_KEY:
        print("  - DART 키가 없어 건너뜀 (.env의 DART_API_KEY)")
        return []

    today = datetime.now(KST).date()
    begin = today - timedelta(days=max(DAYS_BACK - 1, 0))
    items: list[Item] = []

    for page in range(1, max_pages + 1):
        try:
            resp = requests.get(
                "https://opendart.fss.or.kr/api/list.json",
                params={
                    "crtfc_key": DART_API_KEY,
                    "bgn_de": begin.strftime("%Y%m%d"),
                    "end_de": today.strftime("%Y%m%d"),
                    "page_no": page,
                    "page_count": 100,   # 한 페이지 최대 100건
                },
                timeout=10,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"  ! DART 연결 실패: {exc}")
            break

        payload = resp.json()
        status = payload.get("status")

        if status == "013":          # 조회된 데이터 없음 (주말·공휴일이면 정상)
            break
        if status != "000":
            print(f"  ! DART 응답 오류 [{status}] {payload.get('message', '')}")
            break

        for row in payload.get("list", []):
            corp = row.get("corp_name", "")
            # 지켜볼 회사를 지정했으면 그 회사 공시만 남긴다
            if DART_WATCH and not any(name in corp for name in DART_WATCH):
                continue

            dt = None
            try:
                dt = datetime.strptime(row["rcept_dt"], "%Y%m%d").replace(tzinfo=KST)
            except (KeyError, ValueError):
                pass

            items.append(Item(
                source="DART",
                title=f"[{corp}] {row.get('report_nm', '')}".strip(),
                link=f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row.get('rcept_no', '')}",
                dt=dt,
                note=row.get("flr_nm", ""),
            ))

        if page >= int(payload.get("total_page", 1)):
            break

    return items


# ─────────────────────────────────────────────────────────────
# STEP 4. 정리 — 중복 제거 후 최신순
# ─────────────────────────────────────────────────────────────

def dedupe_and_sort(items: list[Item]) -> list[Item]:
    seen: set[str] = set()
    unique: list[Item] = []

    for item in items:
        if not item.title:
            continue
        # 링크가 달라도 제목이 같으면 같은 기사로 본다 (공백·기호 제거 후 비교)
        key = re.sub(r"[^0-9a-z가-힣]", "", item.title.lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    unique.sort(key=lambda i: i.dt or FAR_PAST, reverse=True)
    return unique


# ─────────────────────────────────────────────────────────────
# STEP 5. AI 요약 — Claude API 호출
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """당신은 건설·엔지니어링 회사의 사내 이슈 리포트를 작성하는 담당자입니다.
전달받은 뉴스 기사와 공시 목록을 읽고, 임원이 아침에 30초 만에 훑을 수 있는 리포트를 씁니다.

출력 형식 (그 외 문장은 쓰지 마세요):
[핵심 요약]
- 오늘의 흐름을 3줄 이내로. 각 줄은 한 문장.

[주목할 항목]
1. 항목 제목 — 왜 중요한지 한 줄
(최대 5개. 수주·입찰·계약·리스크·규제 관련을 우선합니다.)

HTML 태그나 마크다운 기호(**, ##)는 쓰지 마세요."""


def summarize_with_claude(items: list[Item]) -> str:
    import anthropic  # 요약을 건너뛸 때는 불필요하므로 여기서 임포트

    client = anthropic.Anthropic()  # 키는 .env의 ANTHROPIC_API_KEY 에서 자동으로 읽는다

    lines = [
        f"{n}. [{it.source}] {it.title} ({it.when})"
        for n, it in enumerate(items[:MAX_ITEMS], start=1)
    ]
    user_prompt = (
        f"오늘 수집한 항목 {len(lines)}건입니다. 리포트를 작성해 주세요.\n\n"
        + "\n".join(lines)
    )

    try:
        response = client.beta.messages.create(
            model="claude-opus-5",
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
            # 안전 분류기가 요청을 거절할 경우 자동으로 다른 모델이 이어받게 한다
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError:
        return "(AI 요약 실패: ANTHROPIC_API_KEY가 올바르지 않습니다)"
    except anthropic.RateLimitError:
        return "(AI 요약 실패: 호출 한도를 초과했습니다. 잠시 후 다시 실행하세요)"
    except anthropic.APIError as exc:
        return f"(AI 요약 실패: {exc})"

    if response.stop_reason == "refusal":
        return "(AI가 이 내용에 대한 요약을 거절했습니다)"

    # 응답에는 thinking 블록이 섞여 올 수 있으므로 text 블록만 모은다
    return "".join(b.text for b in response.content if b.type == "text").strip()


# ─────────────────────────────────────────────────────────────
# STEP 6. 메일 발송
# ─────────────────────────────────────────────────────────────

def build_html(summary: str, items: list[Item]) -> str:
    rows = []
    for item in items[:MAX_ITEMS]:
        rows.append(f"""
        <tr>
          <td style="padding:10px 8px;border-bottom:1px solid #eee;white-space:nowrap;
                     color:#888;font-size:12px;vertical-align:top;">{html.escape(item.source)}</td>
          <td style="padding:10px 8px;border-bottom:1px solid #eee;font-size:14px;">
            <a href="{html.escape(item.link)}"
               style="color:#1a1a1a;text-decoration:none;">{html.escape(item.title)}</a>
          </td>
          <td style="padding:10px 8px;border-bottom:1px solid #eee;white-space:nowrap;
                     color:#aaa;font-size:12px;vertical-align:top;">{item.when}</td>
        </tr>""")

    return f"""<!doctype html>
<html><body style="margin:0;padding:24px;background:#f5f6f4;
                   font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;color:#1a2233;">
  <div style="max-width:720px;margin:0 auto;background:#fff;border-radius:12px;padding:28px;">
    <h1 style="font-size:20px;margin:0 0 4px;">오늘의 이슈 리포트</h1>
    <p style="color:#8993a3;font-size:13px;margin:0 0 20px;">
      {datetime.now(KST).strftime('%Y년 %m월 %d일')} · 수집 {len(items)}건
    </p>

    <div style="background:#f0f1ee;border-left:3px solid #e2871f;border-radius:6px;
                padding:16px 18px;font-size:14px;line-height:1.7;white-space:pre-wrap;">
{html.escape(summary)}
    </div>

    <h2 style="font-size:15px;margin:26px 0 6px;">수집 항목</h2>
    <table style="width:100%;border-collapse:collapse;">{''.join(rows)}</table>

    <p style="color:#aaa;font-size:11px;margin-top:24px;">
      바이브코딩 실습 · 내 PC에서 실행된 자동 리포트
    </p>
  </div>
</body></html>"""


# ── 방법 1. Microsoft Graph API (권장) ────────────────────
# 회사 아웃룩(Microsoft 365)은 2025년부터 "아이디 + 비밀번호" 로 메일을 보내는
# 옛 방식(SMTP 기본 인증)을 막았다. 지금 확실하게 되는 길은 Graph API 다.
# 흐름: 화면에 뜬 코드를 브라우저에 입력해 한 번 로그인 → 토큰을 파일에 저장 →
#       다음부터는 자동. 비밀번호를 .env 에 적지 않아도 되니 더 안전하다.

GRAPH_SCOPES = ["Mail.Send"]
GRAPH_SEND_URL = "https://graph.microsoft.com/v1.0/me/sendMail"


def _msal_app():
    """MSAL 앱 객체. 토큰 캐시를 파일에 붙여 둔다."""
    try:
        import msal
    except ImportError:
        print("  ! msal 라이브러리가 없습니다.  pip install -r requirements.txt 를 먼저 실행하세요.")
        return None, None

    cache = msal.SerializableTokenCache()
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), MS_TOKEN_CACHE)
    if os.path.exists(cache_path):
        cache.deserialize(open(cache_path, encoding="utf-8").read())

    app = msal.PublicClientApplication(
        MS_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{MS_TENANT_ID}",
        token_cache=cache,
    )
    return app, cache_path


def _save_cache(cache, cache_path: str) -> None:
    if cache.has_state_changed:
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(cache.serialize())


def graph_access_token(interactive: bool = True) -> str:
    """액세스 토큰을 얻는다. 저장된 토큰이 있으면 조용히 갱신하고, 없으면 로그인 안내를 띄운다."""
    if not MS_CLIENT_ID:
        print("  ! .env 의 MS_CLIENT_ID 가 비어 있습니다 (Azure 앱 등록 후 받은 값).")
        return ""

    app, cache_path = _msal_app()
    if app is None:
        return ""

    result = None
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(GRAPH_SCOPES, account=accounts[0])

    if not result:
        if not interactive:
            print("  ! 저장된 로그인이 없습니다.  python main.py --login 을 먼저 실행하세요.")
            return ""
        flow = app.initiate_device_flow(scopes=GRAPH_SCOPES)
        if "user_code" not in flow:
            print(f"  ! 로그인 시작 실패: {flow.get('error_description', flow)}")
            return ""
        print()
        print("  ┌─ 아웃룩 로그인 ─────────────────────────────")
        print(f"  │ 1) 브라우저에서 {flow['verification_uri']} 열기")
        print(f"  │ 2) 코드 입력: {flow['user_code']}")
        print("  │ 3) 회사 아웃룩 계정으로 로그인 후 [수락]")
        print("  └───────────────────────────────────────────")
        print("  (로그인을 마칠 때까지 여기서 기다립니다)")
        result = app.acquire_token_by_device_flow(flow)

    _save_cache(app.token_cache, cache_path)

    if "access_token" not in result:
        print(f"  ! 로그인 실패: {result.get('error_description', result)}")
        return ""
    return result["access_token"]


def send_via_graph(subject: str, html_body: str) -> bool:
    token = graph_access_token()
    if not token:
        return False

    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "toRecipients": [{"emailAddress": {"address": a}} for a in MAIL_TO],
        },
        "saveToSentItems": True,
    }
    res = requests.post(
        GRAPH_SEND_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30,
    )
    if res.status_code == 202:           # 202 Accepted 가 정상 (본문은 비어 있다)
        return True

    print(f"  ! Graph 발송 실패 [{res.status_code}] {res.text[:300]}")
    if res.status_code == 403:
        print("    → 앱에 Mail.Send 권한이 없거나 관리자 동의가 안 된 상태입니다.")
    return False


# ── 방법 2. SMTP (옛 방식) ────────────────────────────────
# 사내 정책이 아직 허용하거나, 개인 outlook.com 계정을 쓸 때만 된다.
# 회사 계정에서 535 오류가 나면 막힌 것이니 위의 Graph 방식으로 간다.

def send_via_smtp(subject: str, html_body: str, plain_body: str) -> bool:
    if not (OUTLOOK_ADDRESS and OUTLOOK_PASSWORD):
        print("  ! .env 의 OUTLOOK_ADDRESS / OUTLOOK_PASSWORD 가 비어 있습니다.")
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = OUTLOOK_ADDRESS
    message["To"] = ", ".join(MAIL_TO)
    message.set_content(plain_body)                       # 텍스트만 보는 메일 앱을 위한 대체본
    message.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
            smtp.starttls()                               # 587 포트는 접속 후 암호화로 전환한다
            smtp.login(OUTLOOK_ADDRESS, OUTLOOK_PASSWORD)
            smtp.send_message(message)
    except smtplib.SMTPAuthenticationError as e:
        print(f"  ! 로그인 실패 — {e.smtp_code} {e.smtp_error!r}")
        print("    회사 아웃룩은 SMTP 기본 인증이 막혀 있는 경우가 대부분입니다.")
        print("    .env 에 MS_CLIENT_ID 를 채우고 Graph 방식(MAIL_PROVIDER=graph)으로 보내세요.")
        return False
    except OSError as e:
        print(f"  ! SMTP 접속 실패 — {e}")
        print("    사내 방화벽이 587 포트를 막았을 수 있습니다.")
        return False
    return True


def send_mail(subject: str, html_body: str, plain_body: str) -> None:
    if not MAIL_TO:
        print("  ! 받는 사람이 없습니다 (.env의 MAIL_TO 또는 OUTLOOK_ADDRESS)")
        return

    provider = MAIL_PROVIDER
    if provider == "auto":
        provider = "graph" if MS_CLIENT_ID else "smtp"

    if provider == "graph":
        ok = send_via_graph(subject, html_body)
    else:
        ok = send_via_smtp(subject, html_body, plain_body)

    if ok:
        print(f"  ✓ 메일 발송 완료 ({provider}) → {', '.join(MAIL_TO)}")


# ─────────────────────────────────────────────────────────────
# 전체 파이프라인
# ─────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="사내 이슈 데일리 리포트 봇")
    parser.add_argument("--dry-run", action="store_true", help="메일을 보내지 않고 콘솔에만 출력")
    parser.add_argument("--no-ai", action="store_true", help="AI 요약을 건너뜀")
    parser.add_argument("--login", action="store_true",
                        help="아웃룩(Microsoft) 로그인만 미리 해둔다. 수집·발송은 하지 않음")
    args = parser.parse_args()

    if args.login:
        print("아웃룩 로그인을 시작합니다.")
        if graph_access_token():
            print(f"  ✓ 로그인 완료. 토큰을 {MS_TOKEN_CACHE} 에 저장했습니다.")
            print("    이제 python main.py 로 바로 발송할 수 있습니다.")
            return 0
        return 1

    if not KEYWORDS and not RSS_FEEDS and not DART_WATCH:
        print("설정된 키워드가 없습니다. .env 파일의 KEYWORDS를 채워주세요.")
        return 1

    print(f"키워드: {', '.join(KEYWORDS) or '(없음)'}")

    print("\n[1/4] 수집 중...")
    collected: list[Item] = []
    for label, collector in (("RSS", collect_rss),
                             ("네이버뉴스", collect_naver_news),
                             ("DART", collect_dart)):
        found = collector()
        print(f"  · {label}: {len(found)}건")
        collected.extend(found)

    items = dedupe_and_sort(collected)
    print(f"  → 중복 제거 후 {len(items)}건")

    print("\n[2/4] 요약 중...")
    if not items:
        summary = "오늘 수집된 항목이 없습니다."
        print("  - 수집 결과가 없어 AI 호출을 건너뜁니다")
    elif args.no_ai:
        summary = "(AI 요약 생략 — --no-ai 옵션)"
        print("  - 건너뜀")
    else:
        summary = summarize_with_claude(items)
        print("  ✓ 요약 완료")

    print("\n[3/4] 메일 조립 중...")
    subject = f"[이슈 리포트] {datetime.now(KST).strftime('%m/%d')} · {len(items)}건"
    plain_body = summary + "\n\n" + "\n".join(
        f"- [{i.source}] {i.title}\n  {i.link}" for i in items[:MAX_ITEMS]
    )
    html_body = build_html(summary, items)

    print("\n[4/4] 발송...")
    if args.dry_run:
        print("  - --dry-run 이라 보내지 않습니다. 아래는 메일에 들어갈 내용입니다.\n")
        print("=" * 60)
        print(subject)
        print("=" * 60)
        print(plain_body[:2000])
    else:
        send_mail(subject, html_body, plain_body)

    return 0


if __name__ == "__main__":
    sys.exit(main())
