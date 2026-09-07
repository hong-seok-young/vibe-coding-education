"""사내 이슈 데일리 리포트 프로그램 — 바이브코딩 실습 완성본 (GUI 버전).

파이썬 버전은 가리지 않는다. 3.13 부터 인증서 검사가 깐깐해져서 사내망(HTTPS를
중간에서 검사하는 환경)에서 통신이 막히는 문제가 있는데, 아래 "사내망 대응"에서
처리하므로 최신 버전으로도 그대로 돌아간다.

더블클릭하면 프로그램 창이 뜨고, 창 안에서 키워드·인증키·받는사람을 입력한 뒤
버튼을 눌러서 뉴스·공시를 모으고 메일을 보낸다. 입력한 값은 같은 폴더의
settings.json에 저장돼서 다음에 열 때도 그대로 남아있다.

사내 네트워크는 외부 SMTP(메일 서버 직접 연결)를 막아두는 경우가 많다.
그래서 이 프로그램은 메일 서버에 직접 붙지 않고, 내 PC에 이미 로그인되어 켜져
있는 **아웃룩(데스크톱 앱)을 원격 조작**해서 보낸다. 그래서 비밀번호를 따로
저장할 필요가 없고, 윈도우 + 클래식 아웃룩에서만 완전 자동 발송이 된다.
"""

from __future__ import annotations

import html
import json
import os
import re
import ssl
import sys
import threading
import tkinter as tk
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from tkinter import scrolledtext, ttk
from urllib.parse import quote

import feedparser
import requests
from requests.adapters import HTTPAdapter

KST = timezone(timedelta(hours=9))
FAR_PAST = datetime(1970, 1, 1, tzinfo=timezone.utc)
MAX_ITEMS = 40

# DART 조회 기간(일). 하루치만 보면 특정 회사는 공시가 없는 날이 훨씬 많아서
# "0건"만 계속 보게 된다. 한 주를 보면 대체로 뭔가 잡힌다.
DAYS_BACK = 7

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")


# ─────────────────────────────────────────────────────────────
# 사내망 대응 — HTTPS 검사 장비(TLS 인스펙션) 뚫고 나가기
# ─────────────────────────────────────────────────────────────
#
# 회사 보안 장비는 인터넷 통신을 중간에서 열어보고, 자기 인증서로 다시 봉인해서
# 넘겨준다. 그 인증서에 파이썬 3.13 부터 새로 요구하는 항목(Authority Key
# Identifier)이 빠져 있어서, 3.13 이상에서는 연결이 이렇게 거부된다:
#
#   SSL: CERTIFICATE_VERIFY_FAILED ... Missing Authority Key Identifier
#
# 파이썬 3.12 까지는 나지 않았다(브라우저와 같은 기준으로 검사했다). 버전을 3.12 로
# 못 박아 피하는 방법도 있지만, 3.12 는 이미 보안 패치만 나오는 단계라 오래 못 쓴다.
# 그래서 버전을 가리지 않고 아래에서 직접 대응한다.

def _make_ssl_context() -> ssl.SSLContext:
    """사내망을 통과할 수 있는 인증서 검사 설정을 만든다.

    두 가지를 같이 해줘야 한다.

    (1) 회사 인증서를 신뢰해야 한다.
        ssl.create_default_context() 는 윈도우에서 윈도우 인증서 저장소(ROOT/CA)를
        함께 읽는다. 회사 보안 장비의 인증서는 이미 거기 등록돼 있으니 이걸 쓰면 된다.
        requests 의 기본값(certifi 묶음)을 쓰면 안 된다 — certifi 를 지정하는 순간
        윈도우 저장소를 덮어써서 회사 인증서를 못 믿게 되고, "발급자를 찾을 수 없다"는
        다른 오류로 바뀐다.

    (2) 3.13 부터 새로 생긴 엄격 검사를 끈다.
        회사 장비가 만든 인증서에는 Authority Key Identifier 항목이 없는데,
        3.13 부터 VERIFY_X509_STRICT 가 기본으로 켜지면서 이 항목을 요구한다.
        (1)로 신뢰까지 해놓고도 이 검사에서 거부되므로 이 플래그만 해제한다.

    인증서 검증 자체는 그대로 켜둔다(verify_mode/check_hostname 을 건드리지 않는다).
    """
    ctx = ssl.create_default_context()
    ctx.verify_flags &= ~getattr(ssl, "VERIFY_X509_STRICT", 0)
    return ctx


class _CorporateTLSAdapter(HTTPAdapter):
    """requests 가 위 설정을 쓰도록 끼워 넣는다."""

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = _make_ssl_context()
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs["ssl_context"] = _make_ssl_context()
        return super().proxy_manager_for(*args, **kwargs)


def _build_session() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (issue-report-bot)"

    # truststore 가 깔려 있으면 그게 가장 깔끔하다 — 검사 자체를 윈도우에 맡기므로
    # 위 두 문제가 한 번에 사라진다. 없어도 아래 설정으로 동작한다.
    try:
        import truststore

        truststore.inject_into_ssl()
    except Exception:
        pass

    session.mount("https://", _CorporateTLSAdapter())
    return session


SESSION = _build_session()


# ─────────────────────────────────────────────────────────────
# STEP 0. 프로그램 창 만들기 — 설정 저장/불러오기
# ─────────────────────────────────────────────────────────────

def load_settings() -> dict:
    """저장된 설정을 불러온다. 파일이 없거나 깨져 있으면 빈 값으로 시작한다."""
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def save_settings(data: dict) -> None:
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@dataclass
class Item:
    """수집한 항목 하나 (뉴스 기사든 공시든 같은 모양으로 다룬다)."""

    source: str                       # "뉴스" | "DART" | 언론사 이름
    title: str
    link: str
    dt: datetime | None = None        # 발행 시각 (timezone 포함)
    note: str = field(default="")     # 공시 제출인 등 부가 정보

    @property
    def when(self) -> str:
        if not self.dt:
            return "-"
        local = self.dt.astimezone(KST)
        # DART 공시는 접수 "날짜"만 알려준다. 그대로 두면 시각이 00:00 으로 채워져서
        # 실제로는 모르는 시각을 아는 것처럼 보이고, 같은 날 뉴스보다 항상 아래로
        # 밀려난다. 자정이면 날짜만 보여준다.
        if (local.hour, local.minute) == (0, 0):
            return local.strftime("%m/%d")
        return local.strftime("%m/%d %H:%M")


def clean_text(raw: str) -> str:
    """HTML 태그와 엔티티를 걷어낸다. (RSS 항목에 간혹 HTML 태그가 섞여 온다)"""
    return html.unescape(re.sub(r"<[^>]+>", "", raw)).strip()


# ─────────────────────────────────────────────────────────────
# STEP 2. 뉴스 수집 버튼 — 구글 뉴스 검색 (인증키 없음)
# ─────────────────────────────────────────────────────────────
#
# 뉴스 수집에 인증키를 쓰지 않는 이유:
#   · NewsAPI.org 는 언어 지정 값에 한국어(ko)가 아예 없다. 받는 값은
#     ar/de/en/es/fr/he/it/nl/no/pt/ru/sv/ud/zh 뿐이고, ko 를 넣으면 400 으로
#     거절당한다. 게다가 한국 매체 수집 자체가 빈약해서 한국어 키워드는 0건이 흔하다.
#   · 네이버 검색은 품질이 가장 좋지만 NAVER API HUB(네이버 클라우드) 계정이 필요하다.
#   · 구글 뉴스는 키워드 검색 결과를 RSS 로 그냥 내준다 — 가입도, 키도, 호출 한도도
#     없고 한국어 키워드가 그대로 통한다. 그래서 이걸 기본으로 쓴다.

def google_news_rss(keyword: str) -> str:
    """구글 뉴스의 키워드 검색 결과 주소. 한국어(hl=ko)·한국(gl=KR) 기준으로 받는다."""
    return f"https://news.google.com/rss/search?q={quote(keyword)}&hl=ko&gl=KR&ceid=KR:ko"


def _fetch_feed(url: str) -> tuple[list, str | None]:
    """뉴스 목록을 받아온다. (항목들, 실패 이유) 를 돌려준다.

    feedparser 에 주소를 그대로 넘기면 feedparser 가 직접 인터넷에 접속하는데,
    그러면 위에서 만든 사내망 대응(SESSION)을 못 타고, 실패해도 예외 없이 조용히
    빈 결과만 준다. 그래서 받아오는 건 우리가 하고, feedparser 에는 받아온 내용만 넘긴다.
    """
    try:
        resp = SESSION.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return [], str(exc)

    return feedparser.parse(resp.content).entries, None


def collect_news(keywords: list[str], limit_per_keyword: int = 10) -> tuple[list[Item], list[str]]:
    items: list[Item] = []
    errors: list[str] = []

    if not keywords:
        return items, ["키워드가 없어 건너뜀"]

    for keyword in keywords:
        entries, reason = _fetch_feed(google_news_rss(keyword))

        if not entries:
            if reason:
                errors.append(f"'{keyword}' 검색 실패: {reason}")
            else:
                errors.append(f"'{keyword}' 검색 결과 0건")
            continue

        for entry in entries[:limit_per_keyword]:
            dt = None
            if getattr(entry, "published_parsed", None):
                dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            items.append(Item(
                source="뉴스",
                title=clean_text(entry.get("title", "")),
                link=entry.get("link", ""),
                dt=dt,
            ))

    return items, errors


# ─────────────────────────────────────────────────────────────
# STEP 3. DART 수집 버튼 — 전자공시시스템 연결
# ─────────────────────────────────────────────────────────────

def collect_dart(watch: list[str], api_key: str, days_back: int = DAYS_BACK, max_pages: int = 30) -> tuple[list[Item], list[str]]:
    """DART 공시를 가져온다. 회사 이름을 지정했으면 그 회사 것만 남긴다.

    주의할 점이 두 가지 있다.

    · DART 의 목록 조회는 **회사 이름으로 검색할 수 없다.** 기간 안의 공시를 전부
      받아온 뒤 우리가 직접 골라내야 한다. 그래서 기간 안의 페이지를 끝까지 받아야
      한다 — 중간에 끊으면 뒷페이지에 있던 그 회사 공시를 놓쳐서 "0건"이 된다.
    · 하루치만 보면 특정 회사는 공시가 없는 날이 훨씬 많다. 그래서 기본 기간을
      넉넉하게 잡는다(DAYS_BACK).

    0건일 때 왜 0건인지 알 수 있도록, 기간 안의 전체 공시 수와 걸러낸 결과를
    함께 돌려준다.
    """
    items: list[Item] = []
    errors: list[str] = []

    if not api_key:
        return items, ["DART 인증키가 없어 건너뜀"]

    today = datetime.now(KST).date()
    begin = today - timedelta(days=max(days_back - 1, 0))
    period = f"{begin:%Y-%m-%d}~{today:%Y-%m-%d}"

    total_seen = 0        # 기간 안의 전체 공시 수 (걸러내기 전)
    truncated = False

    page = 1
    while page <= max_pages:
        try:
            resp = SESSION.get(
                "https://opendart.fss.or.kr/api/list.json",
                params={
                    "crtfc_key": api_key,
                    "bgn_de": begin.strftime("%Y%m%d"),
                    "end_de": today.strftime("%Y%m%d"),
                    "page_no": page,
                    "page_count": 100,
                },
                timeout=10,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            errors.append(f"DART 연결 실패: {exc}")
            break

        payload = resp.json()
        status = payload.get("status")

        if status == "013":          # 조회된 데이터 없음 (주말·공휴일이면 정상)
            errors.append(f"DART: {period} 기간에 공시가 없습니다 (주말·공휴일이면 정상)")
            break
        if status != "000":
            errors.append(f"DART 응답 오류 [{status}] {payload.get('message', '')}")
            break

        rows = payload.get("list", [])
        total_seen += len(rows)

        for row in rows:
            corp = row.get("corp_name", "")
            if watch and not any(name in corp for name in watch):
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

        total_page = int(payload.get("total_page", 1) or 1)
        if page >= total_page:
            break
        page += 1
    else:
        truncated = True

    # 0건일 때 원인을 알 수 있게 설명을 남긴다.
    if total_seen:
        if watch and not items:
            errors.append(
                f"DART: {period} 공시 {total_seen}건을 살펴봤지만 "
                f"'{', '.join(watch)}' 이(가) 이름에 들어간 회사는 없었습니다. "
                f"회사 이름을 짧게(예: 삼성) 적었는지, 기간을 늘릴지 확인해보세요."
            )
        elif watch:
            errors.append(f"DART: {period} 공시 {total_seen}건 중 {len(items)}건이 '{', '.join(watch)}' 관련")

    if truncated:
        errors.append(
            f"DART: 기간 안의 공시가 너무 많아 앞부분 {total_seen}건까지만 확인했습니다. "
            f"기간을 줄이면 빠짐없이 볼 수 있습니다."
        )

    return items, errors


# ─────────────────────────────────────────────────────────────
# STEP 4. 정리 — 중복 제거 후 최신순 (수집 버튼들이 공통으로 쓴다)
# ─────────────────────────────────────────────────────────────

def dedupe_and_sort(items: list[Item]) -> list[Item]:
    seen: set[str] = set()
    unique: list[Item] = []

    for item in items:
        if not item.title:
            continue
        key = re.sub(r"[^0-9a-z가-힣]", "", item.title.lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    unique.sort(key=lambda i: i.dt or FAR_PAST, reverse=True)
    return unique


def group_by_source(items: list[Item]) -> list[tuple[str, list[Item]]]:
    """출처별로 묶어서 (출처, 항목들) 목록으로 돌려준다. 각 묶음은 최신순.

    한 목록에 뉴스와 공시를 시간순으로 섞어두면 읽기가 어렵다. 특히 공시는 시각을
    모르니 같은 날 뉴스보다 늘 아래로 밀려서 뒤죽박죽으로 보인다. 그래서 보여줄 때는
    출처별로 나눈다. (중복 제거와 최신순 정렬은 이미 끝난 상태로 들어온다)
    """
    groups: dict[str, list[Item]] = {}
    for item in items:
        groups.setdefault(item.source, []).append(item)

    # 뉴스를 먼저, DART를 그다음, 나머지(언론사)는 뒤에
    def order(source: str) -> tuple[int, str]:
        return ({"뉴스": 0, "DART": 1}.get(source, 2), source)

    return sorted(groups.items(), key=lambda kv: order(kv[0]))


# ─────────────────────────────────────────────────────────────
# STEP 5. 메일 조립 — 보기 좋은 이메일 만들기
# ─────────────────────────────────────────────────────────────

def build_html(items: list[Item]) -> str:
    """메일 본문을 만든다. 출처별로 섹션을 나눠서, 뉴스와 공시가 섞이지 않게 한다."""
    sections = []
    shown = 0

    for source, group in group_by_source(items):
        if shown >= MAX_ITEMS:
            break

        rows = []
        for item in group[: MAX_ITEMS - shown]:
            rows.append(f"""
        <tr>
          <td style="padding:9px 8px;border-bottom:1px solid #eee;font-size:14px;">
            <a href="{html.escape(item.link)}"
               style="color:#1a1a1a;text-decoration:none;">{html.escape(item.title)}</a>
          </td>
          <td style="padding:9px 8px;border-bottom:1px solid #eee;white-space:nowrap;
                     color:#aaa;font-size:12px;vertical-align:top;">{item.when}</td>
        </tr>""")
        shown += len(rows)

        sections.append(f"""
    <h2 style="font-size:14px;margin:24px 0 6px;padding-bottom:6px;
               border-bottom:2px solid #1a2233;">{html.escape(source)}
      <span style="color:#8993a3;font-weight:normal;font-size:12px;">{len(group)}건</span>
    </h2>
    <table style="width:100%;border-collapse:collapse;">{''.join(rows)}</table>""")

    omitted = len(items) - shown
    more = (f"""
    <p style="color:#aaa;font-size:12px;margin-top:16px;">
      이 밖에 {omitted}건이 더 있습니다.
    </p>""" if omitted > 0 else "")

    summary = " · ".join(f"{source} {len(group)}건" for source, group in group_by_source(items))

    return f"""<!doctype html>
<html><body style="margin:0;padding:24px;background:#f5f6f4;
                   font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;color:#1a2233;">
  <div style="max-width:720px;margin:0 auto;background:#fff;border-radius:12px;padding:28px;">
    <h1 style="font-size:20px;margin:0 0 4px;">오늘의 이슈 리포트</h1>
    <p style="color:#8993a3;font-size:13px;margin:0 0 4px;">
      {datetime.now(KST).strftime('%Y년 %m월 %d일')} · 수집 {len(items)}건
    </p>
    <p style="color:#8993a3;font-size:12px;margin:0;">{html.escape(summary)}</p>
{''.join(sections)}{more}

    <p style="color:#aaa;font-size:11px;margin-top:24px;">
      바이브코딩 실습 · 내 PC에서 실행된 자동 리포트
    </p>
  </div>
</body></html>"""


# ─────────────────────────────────────────────────────────────
# STEP 6. 메일 보내기 버튼 — 아웃룩 자동 발송
# ─────────────────────────────────────────────────────────────

def _send_via_classic_outlook(subject: str, html_body: str, mail_to: list[str]) -> None:
    """클래식 아웃룩을 COM으로 조작해 완전 자동으로 발송한다.

    '새 아웃룩(New Outlook)'은 애초에 이 COM 인터페이스 자체를 제공하지 않는
    별도 구조의 앱이라, 새 아웃룩만 설치돼 있으면 Dispatch 단계에서 예외가 난다.
    그건 이 함수의 버그가 아니라 새 아웃룩의 설계상 한계이므로, 호출한 쪽에서
    잡아서 _open_draft_mail() 로 넘어간다.
    """
    import win32com.client  # pywin32 (requirements.txt 참고)

    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # 0 = olMailItem
    mail.Subject = subject
    mail.To = "; ".join(mail_to)  # 아웃룩은 세미콜론으로 여러 명을 구분한다
    mail.HTMLBody = html_body
    mail.Send()


# ─────────────────────────────────────────────────────────────
# STEP 7. 새 아웃룩 대응 + 메일 보내기 마무리
# ─────────────────────────────────────────────────────────────

def _open_draft_mail(subject: str, plain_body: str, mail_to: list[str]) -> None:
    """제목·받는사람·본문을 채운 새 메일 창을 기본 메일 앱으로 연다.

    새 아웃룩은 COM 자동화를 지원하지 않아 완전 자동 발송이 불가능하다.
    대신 mailto: 링크로 초안을 미리 채워서 열어주고, 사람이 [보내기]만
    누르면 되게 한다.
    """
    import webbrowser

    body_limit = 1500
    body = plain_body[:body_limit]
    if len(plain_body) > body_limit:
        body += "\n\n(내용이 길어 일부만 담았습니다.)"

    mailto = (
        "mailto:" + quote(",".join(mail_to))
        + "?subject=" + quote(subject)
        + "&body=" + quote(body)
    )
    webbrowser.open(mailto)


def send_mail(subject: str, html_body: str, plain_body: str, mail_to: list[str], log) -> None:
    if not mail_to:
        log("! 받는 사람이 없습니다.")
        return

    if sys.platform != "win32":
        log("! 아웃룩 발송은 윈도우에서만 됩니다.")
        return

    try:
        import win32com.client  # noqa: F401  — 없으면 아래에서 ImportError로 잡는다
    except ImportError:
        log("! pywin32 가 설치되어 있지 않습니다. `pip install pywin32` 로 설치하세요.")
        return

    try:
        _send_via_classic_outlook(subject, html_body, mail_to)
        log(f"✓ 메일 발송 완료 (자동 발송) → {', '.join(mail_to)}")
        return
    except Exception as exc:
        log(f"! 자동 발송이 안 됩니다: {exc}")
        log("  '새 아웃룩(New Outlook)'만 설치돼 있으면 원래 이렇습니다.")

    log("→ 대신 제목·받는사람·내용을 채운 새 메일 창을 엽니다. 뜨는 창에서 [보내기]만 눌러주세요.")
    try:
        _open_draft_mail(subject, plain_body, mail_to)
        log("✓ 메일 초안 열기 완료 (수동 발송 필요)")
    except Exception as exc:
        log(f"! 메일 초안도 열지 못했습니다: {exc}")


# ─────────────────────────────────────────────────────────────
# STEP 8. 전체 완성 — 창 조립, 버튼 연결, 전체 실행
# ─────────────────────────────────────────────────────────────

FIELDS = [
    ("keywords", "키워드 (쉼표로 구분)"),
    ("dart_watch", "지켜볼 회사 (쉼표로 구분, 비워도 됨)"),
    ("mail_to", "메일 받을 사람 (쉼표로 구분)"),
    ("dart_key", "DART 인증키"),
]


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("DART·뉴스 정보 크롤링 및 메일발송 프로그램")
        self.settings = load_settings()
        self.collected: list[Item] = []

        form = ttk.Frame(root, padding=10)
        form.pack(fill="x")

        self.vars: dict[str, tk.StringVar] = {}
        for key, label in FIELDS:
            row = ttk.Frame(form)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=28).pack(side="left")
            var = tk.StringVar(value=self.settings.get(key, ""))
            var.trace_add("write", lambda *_: self._save_settings())
            ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)
            self.vars[key] = var

        btns = ttk.Frame(root, padding=10)
        btns.pack(fill="x")
        self.buttons = [
            ttk.Button(btns, text="뉴스 수집하기", command=self.on_collect_news),
            ttk.Button(btns, text="DART 수집하기", command=self.on_collect_dart),
            ttk.Button(btns, text="메일 보내기", command=self.on_send_mail),
            ttk.Button(btns, text="전체 실행", command=self.on_run_all),
        ]
        for b in self.buttons:
            b.pack(side="left", padx=4)

        self.log_box = scrolledtext.ScrolledText(root, width=76, height=20, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

        self._log_python_version()

    def _log_python_version(self) -> None:
        """어떤 파이썬으로 돌고 있는지 맨 처음에 한 줄로 보여준다.

        문제가 생겼을 때 강사에게 알려주기 쉽게 하려는 목적이다. 버전에 따라
        동작이 달라지지는 않는다.
        """
        major, minor = sys.version_info[:2]
        self.log(f"파이썬 {major}.{minor} 로 실행 중")

    def _save_settings(self) -> None:
        save_settings({k: v.get() for k, v in self.vars.items()})

    def log(self, message: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _list_field(self, key: str) -> list[str]:
        return [v.strip() for v in self.vars[key].get().split(",") if v.strip()]

    def _set_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for b in self.buttons:
            b.configure(state=state)

    def _run_in_background(self, task) -> None:
        """버튼을 눌렀을 때 창이 멈춘 것처럼 보이지 않도록, 실제 작업은 별도
        스레드에서 진행하고 끝나면 버튼을 다시 눌러쓸 수 있게 되돌린다."""
        self._set_buttons_enabled(False)

        def wrapper():
            try:
                task()
            finally:
                self.root.after(0, lambda: self._set_buttons_enabled(True))

        threading.Thread(target=wrapper, daemon=True).start()

    def _merge(self, new_items: list[Item], label: str) -> None:
        before = len(self.collected)
        self.collected = dedupe_and_sort(self.collected + new_items)
        added = len(self.collected) - before

        def show():
            # 방금 누른 버튼이 무엇을 가져왔는지만 보여준다. 전체 목록을 매번 다시
            # 늘어놓으면 앞서 모은 것과 뒤섞여 보여서 뭐가 새로 온 건지 알 수 없다.
            self.log(f"{label} {len(new_items)}건 가져옴 (새로 추가 {added}건)")
            for item in dedupe_and_sort(new_items)[:10]:
                self.log(f"    {item.when}  {item.title}")
            if len(new_items) > 10:
                self.log(f"    ... 외 {len(new_items) - 10}건")

            # 지금까지 모은 것을 출처별로 한 줄 요약
            summary = " · ".join(
                f"{source} {len(group)}건" for source, group in group_by_source(self.collected)
            )
            self.log(f"  = 지금까지 모은 것: {summary}  (전체 {len(self.collected)}건)")
            self.log("")

        self.root.after(0, show)

    def on_collect_news(self) -> None:
        def task():
            self.root.after(0, lambda: self.log("뉴스 수집 중..."))
            items, errors = collect_news(self._list_field("keywords"))
            for e in errors:
                self.root.after(0, lambda e=e: self.log(f"  ! {e}"))
            self._merge(items, "뉴스")
        self._run_in_background(task)

    def on_collect_dart(self) -> None:
        def task():
            self.root.after(0, lambda: self.log("DART 수집 중..."))
            items, errors = collect_dart(self._list_field("dart_watch"), self.vars["dart_key"].get())
            for e in errors:
                self.root.after(0, lambda e=e: self.log(f"  ! {e}"))
            self._merge(items, "DART")
        self._run_in_background(task)

    def on_send_mail(self) -> None:
        def task():
            if not self.collected:
                self.root.after(0, lambda: self.log("! 보낼 항목이 없습니다. 먼저 수집하세요."))
                return
            subject = f"[이슈 리포트] {datetime.now(KST).strftime('%m/%d')} · {len(self.collected)}건"
            plain_body = "\n".join(f"- [{i.source}] {i.title}\n  {i.link}" for i in self.collected)
            html_body = build_html(self.collected)
            send_mail(subject, html_body, plain_body, self._list_field("mail_to"),
                      lambda m: self.root.after(0, lambda: self.log(m)))
        self._run_in_background(task)

    def on_run_all(self) -> None:
        def task():
            self.root.after(0, lambda: self.log("전체 실행 시작..."))

            self.root.after(0, lambda: self.log("뉴스 수집 중..."))
            news_items, news_errors = collect_news(self._list_field("keywords"))
            for e in news_errors:
                self.root.after(0, lambda e=e: self.log(f"  ! {e}"))
            self._merge(news_items, "뉴스")

            self.root.after(0, lambda: self.log("DART 수집 중..."))
            dart_items, dart_errors = collect_dart(self._list_field("dart_watch"), self.vars["dart_key"].get())
            for e in dart_errors:
                self.root.after(0, lambda e=e: self.log(f"  ! {e}"))
            self._merge(dart_items, "DART")

            if not self.collected:
                self.root.after(0, lambda: self.log("! 수집된 항목이 없어 메일은 보내지 않습니다."))
                return

            subject = f"[이슈 리포트] {datetime.now(KST).strftime('%m/%d')} · {len(self.collected)}건"
            plain_body = "\n".join(f"- [{i.source}] {i.title}\n  {i.link}" for i in self.collected)
            html_body = build_html(self.collected)
            send_mail(subject, html_body, plain_body, self._list_field("mail_to"),
                      lambda m: self.root.after(0, lambda: self.log(m)))
        self._run_in_background(task)


# ─────────────────────────────────────────────────────────────
# STEP 9. 추가실습(보너스) — 언론사 RSS 추가로 붙이기
# ─────────────────────────────────────────────────────────────
#
# 구글 뉴스는 "키워드로 검색"이지만, 언론사 RSS는 "그 언론사 해당 분야 최신 기사"가
# 통째로 온다. 키워드에 안 걸리는 기사까지 훑을 수 있어서 같이 쓰면 사각지대가 줄어든다.
# 이것도 인증키가 필요 없다.

PRESS_FEEDS = [
    ("연합뉴스 경제", "https://www.yna.co.kr/rss/economy.xml"),
    ("한국경제", "https://rss.hankyung.com/feed/economy.xml"),
    ("매일경제", "https://www.mk.co.kr/rss/30100041/"),
]


def collect_press_rss(feeds=PRESS_FEEDS, limit_per_feed: int = 10) -> tuple[list[Item], list[str]]:
    items: list[Item] = []
    errors: list[str] = []

    for label, url in feeds:
        entries, reason = _fetch_feed(url)

        if not entries:
            errors.append(f"{label} 가져오기 실패: {reason}" if reason else f"{label} 0건")
            continue

        for entry in entries[:limit_per_feed]:
            dt = None
            if getattr(entry, "published_parsed", None):
                dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            items.append(Item(
                source=label,
                title=clean_text(entry.get("title", "")),
                link=entry.get("link", ""),
                dt=dt,
            ))

    return items, errors


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
