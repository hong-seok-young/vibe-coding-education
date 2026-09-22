"""이슈 리포트 봇 — STEP 4 까지 만든 상태 (실습 정답 코드)

키워드로 구글 뉴스를 모으고, DART 에서 관심 회사 공시를 모아서, 윈도우에 로그인된
아웃룩으로 요약 메일을 보낸다.

    pip install feedparser pywin32
    python main.py

실습 페이지 STEP 4 까지 따라왔을 때 나와야 하는 모습이다. 아직 붙이지 않은
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
    merge(items)
    render(news_box, items, tail=collected_summary("뉴스 %d건" % len(items)))
    log("뉴스 완료: %d건" % len(items))
    return items


# ══════════════════════════════════════════════════════════
# STEP 2. DART 수집 버튼 — 전자공시시스템 (함정 세 겹)
# ══════════════════════════════════════════════════════════

def dart_fetch_all(key, begin, end):
    """그 기간 공시를 마지막 페이지까지 받는다.

    DART 에는 회사 이름으로 찾아달라고 요청하는 기능이 없다. corp_name 을 보내도
    에러 없이 status 000 정상 으로 전체가 온다 (없는 회사 이름을 보내도 그렇다).
    그래서 여기서 다 받고, 고르는 일은 아래에서 직접 한다. 중간에서 끊으면
    뒷페이지에 있던 그 회사 공시를 놓치고 「없다」고 하게 된다.
    """
    collected, page, total_page = [], 1, 1
    while page <= total_page:
        query = urllib.parse.urlencode(dict(crtfc_key=key, bgn_de=begin, end_de=end,
                                            page_no=page, page_count=DART_PAGE_COUNT))
        with urllib.request.urlopen(DART_LIST_API + "?" + query, timeout=25) as res:
            data = json.load(res)
        status = data.get("status")
        if status != "000":
            return collected, status, data.get("message")
        total_page = int(data.get("total_page") or 1)
        collected.extend(data.get("list") or [])
        if page == 1 or page % 10 == 0 or page == total_page:
            log("   공시 목록 %d/%d 페이지 (누적 %d건)" % (page, total_page, len(collected)))
        page += 1
    return collected, "000", "정상"


def collect_dart():
    key = key_entry.get().strip()
    # 뉴스 검색어와 같은 칸을 쓴다 — 실무에서 둘 다 회사명이라 나눠 받을 이유가 없다.
    companies = [c.strip() for c in kw_entry.get().replace(",", " ").split() if c.strip()]
    if not key:
        log("DART 인증키가 없어 건너뜁니다.")
        render(dart_box, [])
        return []

    end_day = date.today()
    begin_day = end_day - timedelta(days=7)
    log("DART 공시를 받아옵니다 (%s ~ %s)" % (begin_day, end_day))
    try:
        raw, status, message = dart_fetch_all(key, begin_day.strftime("%Y%m%d"),
                                              end_day.strftime("%Y%m%d"))
    except Exception as ex:
        log("DART 를 불러오지 못했습니다: %s - %s" % (type(ex).__name__, ex))
        render(dart_box, [])
        return []

    # 0건일 때 이유를 구분해서 알려준다. 그냥 "0건" 은 쓸모가 없다.
    if status == "013":
        log("이 기간에 올라온 공시가 아예 없습니다. (주말·공휴일이면 정상입니다)")
        render(dart_box, [], tail="이 기간에 올라온 공시가 없습니다.")
        return []
    if status in ("010", "011"):
        log("DART 인증키에 문제가 있습니다 - %s %s" % (status, message))
        render(dart_box, [], tail="인증키를 다시 확인해주세요.")
        return []
    if status == "020":
        log("DART 요청 한도를 넘었습니다 - %s %s" % (status, message))
        render(dart_box, [], tail="오늘 요청 한도를 넘었습니다.")
        return []
    if status != "000":
        log("DART 응답이 정상이 아닙니다 - %s %s" % (status, message))
        render(dart_box, [])
        return []

    looked = len(raw)
    if companies:
        picked = [it for it in raw
                  if any(name in it["corp_name"] for name in companies)]
    else:
        picked = raw[:NO_COMPANY_LIMIT]

    items = []
    for it in picked:
        day = it["rcept_dt"]
        shown = (day[4:6] + "/" + day[6:8]) if len(day) == 8 else "-"
        try:
            stamp = datetime(int(day[0:4]), int(day[4:6]), int(day[6:8]),
                             tzinfo=KST).timestamp()
        except (ValueError, IndexError):
            stamp = 0
        items.append(make_item("DART",
                               "[%s] %s" % (it["corp_name"], it["report_nm"].strip()),
                               DART_DOC_URL + it["rcept_no"],
                               shown, stamp, memo=it.get("flr_nm", "")))
        items[-1]["corp"] = it["corp_name"]
    items.sort(key=lambda x: (-x["ts"], x["title"]))

    if companies and not items:
        log("공시 %d건을 살펴봤는데 검색어에 적은 회사 건은 없었습니다." % looked)
        render(dart_box, [],
               tail="공시 %d건을 살펴봤지만 검색어에 적은 회사 건은 없습니다." % looked)
        return []

    if companies:
        by_corp = Counter(x["corp"] for x in items)
        parts = ["%s %d건" % (n, c) for n, c in by_corp.most_common(6)]
        extra = (" (그 외 %d곳)" % (len(by_corp) - 6)) if len(by_corp) > 6 else ""
        tail = "공시 %d건 중 %d건 - %s%s" % (looked, len(items), " / ".join(parts), extra)
    else:
        tail = ("검색어를 안 적으셨으니 전체 %d건 중 최신 %d건만 담았습니다."
                % (looked, len(items)))

    merge(items)
    render(dart_box, items, tail=collected_summary(tail))
    log("DART 완료: %d건. %s" % (len(items), tail))
    return items


# ══════════════════════════════════════════════════════════
# STEP 3. HTML 보고서 만들기 — 정리해서 한 장으로, 파일로 저장해 브라우저로 열기
# ══════════════════════════════════════════════════════════

def merge(new_items):
    """모은 목록에 합치면서 정리한다 — 제목 없는 건 빼고, 제목이 같으면 하나만, 최신순."""
    seen = set(x["title"] for x in COLLECTED)
    for item in new_items:
        title = (item.get("title") or "").strip()
        if not title or title in seen:
            continue
        seen.add(title)
        COLLECTED.append(item)
    COLLECTED.sort(key=lambda x: -x.get("ts", 0))


def collected_summary(prefix):
    counts = Counter(x["src"] for x in COLLECTED)
    body = " / ".join("%s %d건" % (k, v) for k, v in counts.items()) or "0건"
    return "%s   |   지금까지 모은 것: %s" % (prefix, body)


def escape_html(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def build_report_html():
    """모은 항목을 보고서 한 장(HTML)으로 만든다.

    이 결과물을 두 군데에 그대로 쓴다 — 파일로 저장해 브라우저로 열고(STEP 3),
    아웃룩 메일 본문으로도 보낸다(STEP 4). 메일은 별도 디자인 파일을 못 불러오니
    디자인(style)을 본문 안에 직접 넣는다.
    """
    today = datetime.now(KST).strftime("%Y년 %m월 %d일")
    counts = Counter(x["src"] for x in COLLECTED)
    summary = " · ".join("%s %d건" % (k, v) for k, v in counts.items())
    shown = COLLECTED[:REPORT_LIMIT]

    out = ['<div style="font-family:Malgun Gothic,Apple SD Gothic Neo,sans-serif;'
           'max-width:760px;margin:0 auto;color:#222">',
           '<h2 style="margin:0 0 4px">오늘의 이슈 리포트</h2>',
           '<div style="color:#666;font-size:13px;margin-bottom:16px">'
           '%s · 모두 %d건 · %s</div>' % (today, len(COLLECTED), summary)]

    # 출처별로 나눈다. 섞으면 읽기 어렵고, 공시는 시각을 몰라 같은 날 뉴스보다 밀린다.
    for source, label in (("뉴스", "뉴스"), ("DART", "공시 (DART)")):
        group = [x for x in shown if x["src"] == source]
        if not group:
            continue
        out.append('<h3 style="margin:18px 0 6px;padding-bottom:4px;'
                   'border-bottom:2px solid #e5e5e5">%s <span style="color:#888;'
                   'font-weight:normal;font-size:13px">%d건</span></h3>'
                   % (label, len(group)))
        out.append('<table style="border-collapse:collapse;width:100%">')
        for item in group:
            memo = ("  ·  " + escape_html(item["memo"])) if item.get("memo") else ""
            out.append('<tr><td style="padding:7px 0;border-bottom:1px solid #f0f0f0">'
                       '<a href="%s" style="color:#1155cc;text-decoration:none;'
                       'font-size:14px">%s</a>'
                       '<div style="color:#888;font-size:12px;margin-top:2px">%s%s</div>'
                       '</td></tr>'
                       % (escape_html(item["link"]), escape_html(item["title"]),
                          escape_html(item["date"]), memo))
        out.append("</table>")

    if len(COLLECTED) > REPORT_LIMIT:
        out.append('<p style="color:#888;font-size:12px">이 밖에 %d건이 더 있습니다.</p>'
                   % (len(COLLECTED) - REPORT_LIMIT))
    out.append("</div>")
    return "".join(out)


def save_report():
    """보고서를 프로그램과 같은 폴더에 파일로 저장하고 브라우저로 연다."""
    if not COLLECTED:
        log("보고서로 만들 항목이 없습니다. 먼저 수집하세요.")
        return None
    name = "이슈리포트_%s.html" % datetime.now(KST).strftime("%Y%m%d_%H%M")
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    page = ("<!doctype html><html lang=ko><head><meta charset=utf-8>"
            "<title>오늘의 이슈 리포트</title></head>"
            "<body style=\"background:#f6f7f6;padding:24px\">"
            + build_report_html() + "</body></html>")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
    except OSError as ex:
        log("보고서를 저장하지 못했습니다: %s" % ex)
        return None
    log("보고서를 만들었습니다: %s (%d건)" % (name, len(COLLECTED)))
    # 파일 경로를 주소로 바꿀 때는 반드시 as_uri() 를 쓴다. 문자열로 이어붙이면
    # 폴더 이름에 든 # 이나 공백이 주소 문법으로 해석돼 엉뚱한 곳이 열린다
    # (실제로 D:/#. DX/... 폴더에서 D 드라이브 목록이 열렸다).
    webbrowser.open(Path(path).as_uri())
    log("브라우저로 열었습니다. 제목을 누르면 원문으로 갑니다.")
    return path


# ══════════════════════════════════════════════════════════
# STEP 4. 메일 보내기 버튼 — 아웃룩 자동 발송
# ══════════════════════════════════════════════════════════

def send_mail():
    if not COLLECTED:
        log("보낼 항목이 없습니다. 먼저 수집하세요.")
        return
    recipients = [a.strip() for a in to_entry.get().replace(";", ",").split(",")
                  if a.strip()]
    if not recipients:
        log("받는 사람이 비어 있습니다.")
        return
    if os.name != "nt":
        log("아웃룩 자동 발송은 윈도우에서만 됩니다.")
        return
    try:
        import win32com.client as win32
    except ImportError:
        log("아웃룩 조작에 필요한 게 없습니다. 명령창에서 pip install pywin32 하세요.")
        return

    subject = ("[이슈 리포트] %s · %d건"
               % (datetime.now(KST).strftime("%Y-%m-%d"), len(COLLECTED)))
    body = build_report_html()

    # SMTP 로는 못 보낸다 — 포트는 열려 있지만 STARTTLS 단계에서 연결이 끊기고,
    # 애초에 계정 비밀번호를 프로그램에 적어야 한다. 이미 로그인된 아웃룩을 쓴다.
    try:
        outlook = win32.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)          # 0 = 메일
        to_text = "; ".join(recipients)
        mail.To = to_text
        mail.Subject = subject
        mail.HTMLBody = body                  # Body 에 넣으면 링크가 글자로 깨진다
        mail.Send()
        # Send() 뒤에는 이 메일 객체를 다시 건드리면 안 된다. 보낸 편지함으로 옮겨져서
        # mail.To 를 읽기만 해도 "항목이 삭제되었거나 옮겨졌습니다" 오류가 난다.
        # 그러면 실제로는 보내놓고도 실패로 처리돼 메일 창이 또 뜬다.
        log("자동 발송 완료: %s (%d건)" % (to_text, len(COLLECTED)))
        return
    except Exception as ex:
        log("자동 발송이 안 됐습니다 — %s: %s" % (type(ex).__name__, ex))
        log("대신 메일 창을 열어드릴게요.")

    # 「새 아웃룩(New Outlook)」은 위 방식을 지원하지 않는다. 그때는 내용이 채워진
    # 메일 창을 열어서 사람이 [보내기] 만 누르게 한다.
    try:
        outlook = win32.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.To = "; ".join(recipients)
        mail.Subject = subject
        mail.HTMLBody = body
        mail.Display(False)
        log("메일 창 열기 완료 — [보내기] 만 누르시면 됩니다.")
    except Exception as ex:
        log("메일 창도 열리지 않았습니다: %s - %s" % (type(ex).__name__, ex))


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
    ("DART 수집하기", collect_dart),
    ("보고서 만들기", save_report),
    ("메일 보내기", send_mail),
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
