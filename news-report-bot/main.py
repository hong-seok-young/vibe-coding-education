"""사내 이슈 데일리 리포트 봇 — 바이브코딩 실습 완성본.

파이프라인:
    수집(RSS · 네이버 뉴스 · DART 공시) → Claude API 요약 → 아웃룩 발송

사내 네트워크는 외부 SMTP(메일 서버 직접 연결)를 막아두는 경우가 많다.
그래서 이 봇은 메일 서버에 직접 붙지 않고, 내 PC에 이미 로그인되어 켜져 있는
**아웃룩(데스크톱 앱)을 원격 조작**해서 보낸다 — 사람이 아웃룩에서 새 메일을
쓰고 보내기를 누르는 것과 같은 동작을 스크립트가 대신 눌러주는 방식이다.
그래서 비밀번호를 따로 저장할 필요가 없고, 윈도우 + 클래식 아웃룩에서만 된다.

실행:
    python main.py --dry-run     # 메일 없이 콘솔로만 확인 (처음엔 이걸로)
    python main.py --no-ai       # AI 요약 없이 목록만
    python main.py               # 전체 실행 (메일 발송, 아웃룩이 켜져 있어야 함)

설정은 모두 같은 폴더의 .env 파일에서 읽는다. (.env.example 참고)
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
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

MAIL_TO = _env_list("MAIL_TO")   # 받는 사람 (쉼표로 여러 명). 아웃룩 자동화라 반드시 채워야 한다


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
# STEP 6. 메일 발송 — 로컬 아웃룩(데스크톱 앱)을 원격 조작
# ─────────────────────────────────────────────────────────────
# SMTP(메일 서버 직접 발송)가 사내망에서 막혀 있어, 이미 로그인된 아웃룩 앱을
# 대신 조작하는 방식을 쓴다. 아웃룩이 실행 중이어야 하고(꺼져 있으면 자동으로
# 켜진다), "새 아웃룩"이 아니라 클래식 아웃룩이어야 한다. 윈도우 전용이다.

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


def _send_via_classic_outlook(subject: str, html_body: str) -> None:
    """클래식 아웃룩을 COM으로 조작해 완전 자동으로 발송한다.

    '새 아웃룩(New Outlook)'은 애초에 이 COM 인터페이스 자체를 제공하지 않는
    별도 구조의 앱이라, 새 아웃룩만 설치돼 있으면 Dispatch 단계에서 예외가 난다.
    그건 이 함수의 버그가 아니라 새 아웃룩의 설계상 한계이므로, 호출한 쪽에서
    잡아서 _open_draft_mail() 로 넘어간다.
    """
    import win32com.client  # pywin32 — Windows에만 설치된다 (requirements.txt 참고)

    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # 0 = olMailItem
    mail.Subject = subject
    mail.To = "; ".join(MAIL_TO)  # 아웃룩은 세미콜론으로 여러 명을 구분한다
    mail.HTMLBody = html_body
    mail.Send()


def _open_draft_mail(subject: str, plain_body: str) -> None:
    """제목·받는사람·본문을 채운 새 메일 창을 기본 메일 앱으로 연다.

    새 아웃룩은 COM 자동화를 지원하지 않아 완전 자동 발송이 불가능하다.
    대신 mailto: 링크로 초안을 미리 채워서 열어주고, 사람이 [보내기]만
    누르면 되게 한다. (윈도우의 새 아웃룩·구버전 아웃룩 모두 mailto: 의
    기본 처리기로 잡을 수 있다.) mailto 는 길이 제한이 있어 본문은 앞부분만 담는다.
    """
    import webbrowser
    from urllib.parse import quote

    body_limit = 1500
    body = plain_body[:body_limit]
    if len(plain_body) > body_limit:
        body += "\n\n(내용이 길어 일부만 담았습니다. 전체 내용은 위 콘솔 출력을 참고하세요.)"

    mailto = (
        "mailto:" + quote(",".join(MAIL_TO))
        + "?subject=" + quote(subject)
        + "&body=" + quote(body)
    )
    webbrowser.open(mailto)


def send_mail(subject: str, html_body: str, plain_body: str) -> None:
    if not MAIL_TO:
        print("  ! 받는 사람이 없습니다 (.env의 MAIL_TO)")
        return

    if sys.platform != "win32":
        print("  ! 아웃룩 발송은 윈도우에서만 됩니다 (이 스크립트가 로컬 아웃룩 앱을 조작하는 방식이라서).")
        return

    try:
        import win32com.client  # noqa: F401  — 없으면 아래에서 ImportError로 잡는다
    except ImportError:
        print("  ! pywin32 가 설치되어 있지 않습니다. `pip install pywin32` 로 설치하세요.")
        return

    try:
        _send_via_classic_outlook(subject, html_body)
        print(f"  ✓ 메일 발송 완료 (클래식 아웃룩, 자동 발송) → {', '.join(MAIL_TO)}")
        return
    except Exception as exc:
        print(f"  ! 클래식 아웃룩 자동 발송이 안 됩니다: {exc}")
        print("    '새 아웃룩(New Outlook)'만 설치돼 있으면 원래 이렇습니다 — 새 아웃룩은 자동화 자체를 지원하지 않습니다.")

    print("  → 대신 제목·받는사람·내용을 채운 새 메일 창을 엽니다. 뜨는 창에서 [보내기]만 눌러주세요.")
    try:
        _open_draft_mail(subject, plain_body)
        print(f"  ✓ 메일 초안 열기 완료 (수동 발송 필요) → {', '.join(MAIL_TO)}")
    except Exception as exc:
        print(f"  ! 메일 초안도 열지 못했습니다: {exc}")


# ─────────────────────────────────────────────────────────────
# 전체 파이프라인
# ─────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="사내 이슈 데일리 리포트 봇")
    parser.add_argument("--dry-run", action="store_true", help="메일을 보내지 않고 콘솔에만 출력")
    parser.add_argument("--no-ai", action="store_true", help="AI 요약을 건너뜀")
    args = parser.parse_args()

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
