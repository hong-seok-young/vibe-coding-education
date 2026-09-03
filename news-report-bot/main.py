"""사내 이슈 데일리 리포트 프로그램 — 바이브코딩 실습 완성본 (GUI 버전).

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
import sys
import threading
import tkinter as tk
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from tkinter import scrolledtext, ttk
from urllib.parse import quote

import feedparser
import requests

KST = timezone(timedelta(hours=9))
FAR_PAST = datetime(1970, 1, 1, tzinfo=timezone.utc)
MAX_ITEMS = 40
DAYS_BACK = 1

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")


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
        return self.dt.astimezone(KST).strftime("%m/%d %H:%M") if self.dt else "-"


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


def collect_news(keywords: list[str], limit_per_keyword: int = 10) -> tuple[list[Item], list[str]]:
    items: list[Item] = []
    errors: list[str] = []

    if not keywords:
        return items, ["키워드가 없어 건너뜀"]

    for keyword in keywords:
        parsed = feedparser.parse(google_news_rss(keyword))

        # feedparser 는 네트워크가 막혀도 예외를 던지지 않고 조용히 빈 결과를 준다.
        # 그래서 "왜 0건인지"를 직접 구분해서 알려줘야 한다.
        if not parsed.entries:
            reason = getattr(parsed, "bozo_exception", None)
            if reason:
                errors.append(f"'{keyword}' 검색 실패: {reason}")
            else:
                errors.append(f"'{keyword}' 검색 결과 0건")
            continue

        for entry in parsed.entries[:limit_per_keyword]:
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

def collect_dart(watch: list[str], api_key: str, days_back: int = DAYS_BACK, max_pages: int = 5) -> tuple[list[Item], list[str]]:
    items: list[Item] = []
    errors: list[str] = []

    if not api_key:
        return items, ["DART 인증키가 없어 건너뜀"]

    today = datetime.now(KST).date()
    begin = today - timedelta(days=max(days_back - 1, 0))

    for page in range(1, max_pages + 1):
        try:
            resp = requests.get(
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
            break
        if status != "000":
            errors.append(f"DART 응답 오류 [{status}] {payload.get('message', '')}")
            break

        for row in payload.get("list", []):
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

        if page >= int(payload.get("total_page", 1)):
            break

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


# ─────────────────────────────────────────────────────────────
# STEP 5. 메일 조립 — 보기 좋은 이메일 만들기
# ─────────────────────────────────────────────────────────────

def build_html(items: list[Item]) -> str:
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

    <table style="width:100%;border-collapse:collapse;">{''.join(rows)}</table>

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
    import win32com.client  # pywin32 — Windows에만 설치된다 (requirements.txt 참고)

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
        self.collected = dedupe_and_sort(self.collected + new_items)

        def show():
            self.log(f"{label} {len(new_items)}건 수집 (전체 {len(self.collected)}건)")
            for item in self.collected[:10]:
                self.log(f"  · [{item.source}] {item.when}  {item.title}")

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
        parsed = feedparser.parse(url)

        if not parsed.entries:
            reason = getattr(parsed, "bozo_exception", None)
            errors.append(f"{label} 가져오기 실패: {reason}" if reason else f"{label} 0건")
            continue

        for entry in parsed.entries[:limit_per_feed]:
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
