"""이슈 리포트 봇 — STEP 1 까지 만든 상태 (실습 정답 코드)

키워드로 구글 뉴스를 모으고, DART 에서 관심 회사 공시를 모아서, 윈도우에 로그인된
아웃룩으로 요약 메일을 보낸다.

    pip install feedparser pywin32
    python main.py

실습 페이지 STEP 1 까지 따라왔을 때 나와야 하는 모습이다. 아직 붙이지 않은
버튼은 눌러도 진행 상황 칸에 안내만 나온다. 완성본은 STEP 5 파일이다.

이 프로그램이 왜 이렇게 생겼는지 (프롬프트에서 짚어야 하는 것):
  · 인터넷 접속에 requests 를 쓰지 않는다. 사내 보안장비가 HTTPS 를 중간에서 열어보기
    때문에 requests(certifi 목록만 신뢰)는 첫 접속부터 실패한다. urllib / feedparser 는
    윈도우 인증서 저장소를 보므로 그냥 된다.
  · DART 는 회사 이름으로 검색하는 기능이 없다. 회사명을 보내도 status 000 정상 이라고
    응답이 오면서 전체를 준다. 그래서 기간 전체를 끝까지 받아 직접 골라낸다.
  · 메일은 SMTP 로 못 보낸다. 포트는 열려 있지만 STARTTLS 단계에서 연결이 끊긴다.
    이미 로그인된 아웃룩을 COM 으로 조작하면 비밀번호가 아예 필요 없다.
  · 메일 본문은 HTMLBody 에 넣는다. Body 에 넣으면 링크가 글자로 깨져 눌리지 않는다.
"""

import json
import os
import sys
import threading
import tkinter as tk
import urllib.parse
import urllib.request
import webbrowser
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from tkinter import scrolledtext

import feedparser

KST = timezone(timedelta(hours=9))

# 수집·출력 상한 — 없으면 결과 칸이 수천 줄이 되어 창이 멈춘다.
# 실측: 상한 없이 키워드 1개 108건 -> 326줄, 회사 필터 「삼성」 -> 280줄/18,043자
MAX_PER_KEYWORD = 10      # 키워드당 수집
NO_COMPANY_LIMIT = 50     # 지켜볼 회사를 안 적었을 때 담을 공시
SHOW_LIMIT = 10           # 결과 칸에 보여줄 건수
REPORT_LIMIT = 40         # 보고서·메일에 담을 건수

NEWS_RSS = "https://news.google.com/rss/search"
# 목록을 받는 곳(opendart)과 문서를 여는 곳(dart)이 다르다. 그리고 받은 자료의
# 항목 이름은 rcept_no 지만 주소에 쓸 이름은 rcpNo 다. 틀리면 「거부」 페이지가 열린다.
DART_LIST_API = "https://opendart.fss.or.kr/api/list.json"
DART_DOC_URL = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo="
DART_PAGE_COUNT = 100     # 한 번에 받을 수 있는 최대. 더 크게 요청해도 100건만 온다

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

COLLECTED = []            # 지금까지 모은 항목


# ══════════════════════════════════════════════════════════
# STEP 0. 프로그램 창 만들기 — 설정 저장, 결과 칸 세 개, 클릭되는 제목
# ══════════════════════════════════════════════════════════

def load_settings():
    """창을 닫았다 다시 열어도 입력값이 남아있게 — 프로그램과 같은 폴더에 저장한다."""
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            pass
    return {}


def save_settings():
    data = dict(keywords=kw_entry.get(), mailto=to_entry.get(),
                dart_key=key_entry.get())
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as ex:
        log("설정을 저장하지 못했습니다: %s" % ex)


def log(message):
    """진행 상황과 에러는 전부 여기로. 터미널에만 찍히면 수강생은 볼 수가 없다."""
    def do():
        status_box.config(state="normal")
        status_box.insert("end", message + "\n")
        status_box.see("end")
        status_box.config(state="disabled")
    root.after(0, do)


def render(target, items, tail=""):
    """방금 가져온 것만, 앞에서 SHOW_LIMIT 건까지. 제목을 누르면 원문이 열린다."""
    def do():
        target.config(state="normal")
        target.delete("1.0", "end")
        for i, item in enumerate(items[:SHOW_LIMIT]):
            tag = "link%d_%d" % (id(target), i)
            target.insert("end", "%d. " % (i + 1))
            target.insert("end", item["title"] + "\n", tag)
            memo = ("  ·  " + item["memo"]) if item.get("memo") else ""
            target.insert("end", "     " + item["date"] + memo + "\n")
            target.tag_config(tag, foreground="#1155cc", underline=True)
            target.tag_bind(tag, "<Button-1>",
                            lambda ev, u=item["link"]: webbrowser.open(u))
            target.tag_bind(tag, "<Enter>", lambda ev, t=target: t.config(cursor="hand2"))
            target.tag_bind(tag, "<Leave>", lambda ev, t=target: t.config(cursor=""))
        if len(items) > SHOW_LIMIT:
            target.insert("end", "\n... 이 밖에 %d건이 더 있습니다.\n"
                          % (len(items) - SHOW_LIMIT))
        if tail:
            target.insert("end", "\n" + tail + "\n")
        target.config(state="disabled")
    root.after(0, do)


def make_item(source, title, link, shown_date, timestamp, memo=""):
    """기사·공시 한 건을 담는 형태. 시각을 모르면 날짜만 보여준다."""
    return dict(src=source, title=title, link=link, date=shown_date,
                ts=timestamp, memo=memo)


# ══════════════════════════════════════════════════════════
# STEP 1. 뉴스 수집 버튼 — 구글 뉴스 (인증키 없음)
# ══════════════════════════════════════════════════════════

def collect_news():
    raw = kw_entry.get().strip()
    if not raw:
        log("검색어가 없어 뉴스는 건너뜁니다.")
        render(news_box, [])
        return []

    keywords = [k.strip() for k in raw.replace(",", " ").split() if k.strip()]
    items = []
    for keyword in keywords:
        query = urllib.parse.urlencode(dict(q=keyword, hl="ko", gl="KR", ceid="KR:ko"))
        # feedparser 는 내부에서 urllib 를 쓴다 -> 윈도우 인증서 저장소를 보므로
        # 사내 보안장비 환경에서도 그냥 된다. requests 로 바꾸면 첫 접속부터 실패한다.
        try:
            feed = feedparser.parse(NEWS_RSS + "?" + query)
        except Exception as ex:
            log("[%s] 가져오는 중 문제가 생겼습니다: %s - %s"
                % (keyword, type(ex).__name__, ex))
            continue

        if not feed.entries:
            # "네트워크가 막아서 못 받아온 것" 과 "받아왔는데 기사가 없는 것" 을 구분한다.
            why = getattr(feed, "bozo_exception", None)
            if why:
                log("[%s] 못 받아왔습니다 - %s" % (keyword, why))
            else:
                log("[%s] 받아왔지만 이 키워드로 걸리는 기사가 없습니다." % keyword)
            continue

        for entry in feed.entries[:MAX_PER_KEYWORD]:
            try:
                when = parsedate_to_datetime(entry.published).astimezone(KST)
                shown, stamp = when.strftime("%m/%d %H:%M"), when.timestamp()
            except Exception:
                shown, stamp = "-", 0
            items.append(make_item("뉴스", entry.title, entry.link, shown, stamp))

        log("[%s] %d건 (검색결과 %d건 중)"
            % (keyword, min(len(feed.entries), MAX_PER_KEYWORD), len(feed.entries)))

    items.sort(key=lambda x: -x["ts"])
    render(news_box, items, tail="뉴스 %d건 가져왔습니다." % len(items))
    log("뉴스 완료: %d건" % len(items))
    return items


# ══════════════════════════════════════════════════════════
# STEP 2. DART 수집 버튼 — 전자공시시스템 (함정 세 겹)
# ══════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════
# STEP 3. HTML 보고서 만들기 — 정리해서 한 장으로, 파일로 저장해 브라우저로 열기
# ══════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════
# STEP 4. 메일 보내기 버튼 — 아웃룩 자동 발송
# ══════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════
# STEP 5. 전체 실행 — 수집에서 발송까지 한 번에
# ══════════════════════════════════════════════════════════

BUSY = threading.Lock()


def run_in_background(work):
    """버튼을 누른 동안 창이 멈추지 않게. 작업 중에는 버튼도 잠시 안 눌린다.

    앞에서 쓰던 방식대로 그냥 실행하면 DART 는 28페이지라 15초 동안 창이 먹통이 되고,
    수강생은 프로그램이 죽은 줄 알고 강제 종료한다.
    """
    if not BUSY.acquire(blocking=False):
        log("아직 앞의 작업이 끝나지 않았습니다.")
        return
    for button in ALL_BUTTONS:
        button.config(state="disabled")

    def go():
        # 아웃룩 조작(COM)은 그 일을 하는 스레드마다 먼저 초기화를 해줘야 한다.
        # 빠뜨리면 자동 발송이 com_error (-2147221008, CoInitialize 가 호출되지
        # 않았습니다) 로 실패한다. 창이 멈추지 않게 뒤에서 작업하는 구조라 반드시 필요하다.
        com_ready = False
        try:
            import pythoncom
            pythoncom.CoInitialize()
            com_ready = True
        except ImportError:
            pass
        try:
            save_settings()
            work()
        except Exception as ex:                    # 어떤 경우에도 조용히 죽지 않게
            log("예상 못 한 문제가 생겼습니다: %s - %s" % (type(ex).__name__, ex))
        finally:
            if com_ready:
                try:
                    import pythoncom
                    pythoncom.CoUninitialize()
                except Exception:
                    pass
            BUSY.release()
            root.after(0, lambda: [b.config(state="normal") for b in ALL_BUTTONS])

    threading.Thread(target=go, daemon=True).start()


def not_ready():
    """아직 연결하지 않은 버튼. 다음 단계에서 실제 동작을 붙인다."""
    log("이 버튼은 아직 준비 중입니다. 다음 단계에서 연결합니다.")


# ── 창 조립 ────────────────────────────────────────────────
root = tk.Tk()
root.title("이슈 리포트 봇")
root.geometry("940x820")

saved = load_settings()
form = tk.Frame(root)
form.pack(fill="x", padx=10, pady=8)
FIELDS = (("검색어 (회사명, 쉼표로 여러 개):", "keywords"),
          ("메일 받을 사람:", "mailto"),
          ("DART 인증키:", "dart_key"))
entries = []
for row, (label, field) in enumerate(FIELDS):
    tk.Label(form, text=label).grid(row=row, column=0, sticky="e", pady=2)
    entry = tk.Entry(form, width=58)
    entry.grid(row=row, column=1, padx=4, pady=2)
    entry.insert(0, saved.get(field, ""))
    entries.append(entry)
kw_entry, to_entry, key_entry = entries

buttons = tk.Frame(root)
buttons.pack(fill="x", padx=10)
BUTTON_SPECS = [
    ("뉴스 수집하기", collect_news),
    ("DART 수집하기", not_ready),
    ("보고서 만들기", not_ready),
    ("메일 보내기", not_ready),
    ("전체 실행", not_ready),
]
ALL_BUTTONS = []
for label, action in BUTTON_SPECS:
    button = tk.Button(buttons, text=label,
                       command=lambda fn=action: run_in_background(fn))
    button.pack(side="left", padx=(0, 6))
    ALL_BUTTONS.append(button)

tk.Label(root, text="뉴스 수집 결과", anchor="w").pack(fill="x", padx=10, pady=(8, 0))
news_box = scrolledtext.ScrolledText(root, height=12, wrap="word", state="disabled")
news_box.pack(fill="both", expand=True, padx=10)

tk.Label(root, text="DART 수집 결과", anchor="w").pack(fill="x", padx=10, pady=(8, 0))
dart_box = scrolledtext.ScrolledText(root, height=12, wrap="word", state="disabled")
dart_box.pack(fill="both", expand=True, padx=10)

tk.Label(root, text="진행 상황", anchor="w").pack(fill="x", padx=10, pady=(8, 0))
status_box = scrolledtext.ScrolledText(root, height=8, wrap="word", state="disabled")
status_box.pack(fill="x", padx=10, pady=(0, 10))


def on_close():
    save_settings()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)
log("파이썬 %s 로 실행 중입니다." % sys.version.split()[0])
root.mainloop()
