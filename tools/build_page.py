"""실습 HTML 을 만든다 — 저장소 루트의 페이지 하나를 통째로 다시 쓴다.

    python3 tools/build_page.py

단계별 내용은 steps.py, 사전 준비 페이지는 prep.html 에 있다. 페이지의
"정답 코드 파일 받기" 버튼용으로 news-report-bot/main.py 를 base64 로 박아 넣기
때문에, main.py 를 고친 뒤에도 이걸 다시 실행해야 페이지에 반영된다.

만든 뒤 확인할 것 — 태그 짝, 체크박스 수, <script> 안의 문법(node --check),
그리고 브라우저로 열어서 페이지 이동이 되는지.
"""

import os
import re
import html as h

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

from steps import STEPS

# 사내 AI 툴은 파일/폴더를 직접 만들거나 읽지 못하는 대화형 도구라 (프롬프트를 넣으면
# 그에 맞는 .py 파일을 다운로드해 주는 방식), 매 단계마다 "앞에서 만든 것에 이걸 더해서
# 전체를 통째로 다시 파일로 달라"는 요청을 프롬프트 끝에 붙인다. (그래야 학생이 어디에
# 뭘 끼워 넣을지 고민하지 않고, 매 단계마다 완성된 파일 하나만 들고 갈 수 있다.)
#
# 프롬프트에는 "내가 받아서 덮어쓸 거야" 같은 말을 넣지 않는다. AI는 파일을 내려주기만
# 하고, 같은 이름으로 또 받으면 브라우저가 "main (2).py" 처럼 번호를 붙여 저장하기 때문에
# 학생 입장에서 "덮어쓰기"가 실제로 일어나지 않는다. 그래서 요청은 어디까지나 "앞에 것에
# 더해서 전체를 다시 달라"로만 하고, 받은 파일을 어떻게 다루는지는 아래 안내문에서 따로
# 설명한다.
#
# 단, STEP 0 은 AI를 처음 쓰기 시작하는 단계라 아직 내 PC에 아무 파일도 없다. 앞 단계가
# 없으니 "앞에 것에 더해서"라는 말도 성립하지 않아, 첫 단계만 "새로 만들어주고 + 저장·실행
# 방법도 알려달라"로 따로 쓴다. (사전 준비는 파이썬 설치뿐이고 폴더/파일을 미리 주지 않는다.)
_NO_BACKSLASH = (
    " 그리고 코드에 역슬래시 문자는 쓰지 말아줘. 받은 파일에서 역슬래시가 사라져서 프로그램이 "
    "안 열린 적이 있어 — 줄바꿈이 필요하면 chr(10) 을 쓰면 된다고 들었어."
)
_FIRST_FILE_SUFFIX = (
    "\n\n코드는 채팅창에 쓰지 말고 .py 파일로 첨부해줘. 파일을 어디에 어떤 이름으로 저장하고 "
    "어떻게 실행하면 창이 뜨는지도 순서대로 알려줘." + _NO_BACKSLASH
)
_FULL_FILE_SUFFIX = (
    "\n\n코드는 채팅창에 쓰지 말고, 앞에 만들어준 것에 이걸 더해서 전체를 통째로 .py 파일로 "
    "다시 첨부해줘. 되던 기능은 하나도 빼지 말고, 바뀐 부분만 잘라서 주지 말고 항상 전체를." + _NO_BACKSLASH
)
for _step in STEPS:
    _step["prompt"] = _step["prompt"] + (
        _FIRST_FILE_SUFFIX if _step["id"] == "s0" else _FULL_FILE_SUFFIX
    )


LINEBREAK = chr(10)


def esc(s):
    return h.escape(s)


# ── prep.html 에서 섹션 A~D 와 콜아웃 추출 ──────────────────
prep_src = open(f"{HERE}/prep.html", encoding="utf-8").read()


def between(text, start_marker, end_marker, start_from=0):
    i = text.index(start_marker, start_from)
    j = text.index(end_marker, i + len(start_marker))
    return text[i:j], i, j


sections_prep, _, _ = between(
    prep_src,
    '  <section class="group">\n    <div class="group-head">\n      <span class="num">A</span>',
    '\n\n  <div class="callout">',
)

# 파이썬 설치.bat 은 페이지 안에 내장하지도, 깃허브 링크로 받게 하지도 않는다.
# base64로 박아넣고 Blob 으로 강제 다운로드시키는 방식은 "HTML smuggling"과 패턴이
# 같아 회사 PC 보안 소프트웨어가 다운로드 자체를 막았고(실제 확인됨), 깃허브 링크로
# 바꿔도 사용자 입장에서 낯선 화면으로 튄다는 문제가 있었다. 그래서 이 파일은 실습
# 폴더 안에 이미 들어있는 로컬 파일로 취급하고(더블클릭만 안내), 이 페이지 하나만
# 따로 받은 예외적인 경우에만 파이썬 공식 사이트 링크로 안내한다.

# 설치 파일 더블클릭이 회사 정책에 막히는 경우를 위한 대안. 본문(체크리스트)에는
# 명령 프롬프트를 시키지 않는다 — 사전 준비는 "더블클릭 한 번"으로 끝나야 한다.
# 여기는 진짜 막힌 사람만 펼쳐보는 자리다.
callout_prep = '''
  <div class="callout">
    <p><strong>설치 파일이 회사 정책에 막히면</strong> — 아래 순서로 대신 준비한다.
      여기까지 왔으면 강사에게 알려주는 것이 가장 빠르다.</p>
    <ol style="margin:8px 0 0; padding-left:20px;">
      <li><a href="https://www.python.org/ftp/python/pymanager/python-manager-26.3.msix">파이썬 설치 관리자</a>를
        받아 더블클릭해 설치한 뒤, 명령 프롬프트(cmd)에서 <code>py install 3</code></li>
      <li>이어서 <code>pip install feedparser pywin32</code>
        (인증서 오류가 나면 <code>pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org feedparser pywin32</code>)</li>
    </ol>
  </div>'''


PART_LABELS = {1: "실습 1 · 수집", 2: "실습 2 · 보고서", 3: "실습 3 · 메일 발송"}

# ── STEP 카드 렌더링 (한 STEP = 한 페이지) ──────────────────

# STEP 0 페이지에 넣는 완성 창 그림. tools/program-window.png 을 base64 로 박아
# 넣어서 HTML 파일 하나만 있어도 그림이 보이게 한다 (이미지 파일을 따로 들고 다니지
# 않아도 된다). 그림은 _lab/capture.py 로 main.py 를 실제로 띄워 찍는다 —
# 화면을 긁으면 사내 보안 워터마크가 같이 찍히므로 PrintWindow 방식을 쓴다.
import base64 as _b64

with open(f"{HERE}/program-window.png", "rb") as _f:
    SHOT_B64 = _b64.b64encode(_f.read()).decode("ascii")

SHOT_HTML = f'''
    <figure class="shot">
      <img src="data:image/png;base64,{SHOT_B64}"
           alt="완성된 프로그램 창 — 입력 칸 세 개, 버튼 다섯 개, 결과 칸 세 개">
    </figure>
'''


def render_step_page(step, index, total):
    lib_html = ""
    if step["need_install"]:
        lib_html = f'''
      <div class="cmd-box">
        <span class="cmd-label">터미널에 먼저 입력 — 사전 준비에서 이미 받아뒀으면 넘어가기</span>
        <code class="cmd-text" id="cmd-{step['id']}">{esc(step['need_install'])}</code>
        <button class="copy-btn" data-copy="cmd-{step['id']}">복사</button>
      </div>'''

    criteria_html = "\n".join(f'          <li>{esc(c)}</li>' for c in step["criteria"])

    # 이 단계에서 만들 것을 줄글 대신 번호 목록으로 보여준다 (todo 가 있는 단계만).
    if step.get("todo"):
        items = LINEBREAK.join(f'        <li>{esc(t)}</li>' for t in step["todo"])
        todo_html = f'<ol class="step-todo">{LINEBREAK}{items}{LINEBREAK}      </ol>'
    else:
        todo_html = "<p class=" + chr(34) + "step-desc" + chr(34) + ">" + esc(step["desc"]) + "</p>"
    intro = SHOT_HTML if step["id"] == "s0" else ""

    trouble_html = ""
    if step.get("trouble"):
        t = step["trouble"]
        trouble_html = f'''
    <details class="answer-details">
      <summary>{esc(t['summary'])}</summary>
      <p class="tiny" style="margin-top: 4px;">{t['body']}</p>
      <div class="prompt-box" style="margin-top: 10px;">
        <div class="prompt-box-head">
          <span class="prompt-label">이 프롬프트를 이어서 넣기</span>
          <button class="copy-btn" data-copy="trouble-{step['id']}">복사</button>
        </div>
        <pre class="prompt-text" id="trouble-{step['id']}">{esc(t['prompt'])}</pre>
      </div>
    </details>'''

    return f'''
  <section class="page" data-page="{step['id']}" id="{step['id']}">
    <div class="page-head">
      <span class="page-eyebrow">{PART_LABELS[step['part']]}</span>
      <div class="page-title-row">
        <label class="page-check-wrap">
          <input type="checkbox" class="check page-check" data-id="{step['id']}">
        </label>
        <h2>STEP {step['num']} · {esc(step['title'])}</h2>
        <span class="step-time">{esc(step['time'])}</span>
      </div>
      {todo_html}
    </div>
{intro}{lib_html}
    <div class="prompt-box">
      <div class="prompt-box-head">
        <span class="prompt-label">이 프롬프트를 AI에게 붙여넣기</span>
        <button class="copy-btn" data-copy="prompt-{step['id']}">복사</button>
      </div>
      <pre class="prompt-text" id="prompt-{step['id']}">{esc(step['prompt'])}</pre>
    </div>

    <div class="criteria-box">
      <p class="criteria-label">성공 기준</p>
      <ul>
{criteria_html}
      </ul>
    </div>

{trouble_html}
    <details class="answer-details">
      <summary>안 되면? 정답 코드 파일 받기</summary>
      <p class="tiny" style="margin-top: 4px;">완성된 전체 코드(main.py)를 받아서, 그 안의
        <code># STEP {step['num']}.</code> 로 시작하는 부분과 비교해본다.</p>
      <div class="actions" style="margin-top: 8px;">
        <button type="button" class="btn primary download-mainpy-btn">
          <span class="arrow">⬇</span> main.py 받기
        </button>
      </div>
    </details>
  </section>'''


step_pages_html = "\n".join(render_step_page(s, i, len(STEPS)) for i, s in enumerate(STEPS))

# ── TOC ──────────────────────────────────────────────────
TOC_LABELS = {
    "s0": "뼈대", "s1": "구글 뉴스", "s2": "DART",
    "s3": "HTML 보고서", "s4": "아웃룩 발송", "s5": "완성",
}

toc_part1 = "\n".join(
    f'      <a class="toc-link" data-page="{s["id"]}" href="#{s["id"]}"><span class="toc-badge">{s["num"]}</span>{TOC_LABELS[s["id"]]}</a>'
    for s in STEPS if s["part"] == 1
)
toc_part2 = "\n".join(
    f'      <a class="toc-link" data-page="{s["id"]}" href="#{s["id"]}"><span class="toc-badge">{s["num"]}</span>{TOC_LABELS[s["id"]]}</a>'
    for s in STEPS if s["part"] == 2
)
toc_part3 = "\n".join(
    f'      <a class="toc-link" data-page="{s["id"]}" href="#{s["id"]}"><span class="toc-badge">{s["num"]}</span>{TOC_LABELS[s["id"]]}</a>'
    for s in STEPS if s["part"] == 3
)

ALL_PAGE_IDS = ["prep"] + [s["id"] for s in STEPS] + ["apis", "apps"]
MAIN_PY_URL = "https://github.com/hong-seok-young/vibe-coding-education/blob/claude/vibe-coding-education-program-lgtqes/news-report-bot/main.py"
ZIP_URL = "https://github.com/hong-seok-young/vibe-coding-education/archive/refs/heads/claude/vibe-coding-education-program-lgtqes.zip"

# "정답 코드 파일 받기" 버튼용 — 완성본 main.py 를 base64 로 페이지에 박아 넣고
# 버튼 클릭 시 Blob 으로 풀어서 다운로드시킨다. 이 방식(HTML smuggling과 같은 패턴)이
# 회사 보안 소프트웨어에 막힐 수 있다는 걸 알고도, 사용자가 위험을 감수하고 요청해서 반영함.
import base64

with open(f"{REPO}/news-report-bot/main.py", "rb") as _f:
    MAIN_PY_B64 = base64.b64encode(_f.read()).decode("ascii")

fonts_head = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
      media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap"></noscript>'''

STYLE = '''<style>
  :root {
    --paper: #eef0ee;
    --surface: #ffffff;
    --surface-2: #e6e9e6;
    --ink: #1c2321;
    --ink-soft: #454e4b;
    --muted: #6b7570;
    --line: #d5d9d4;
    --line-strong: #b9c0ba;
    --accent: #c96a1a;
    --accent-ink: #ffffff;
    --accent-wash: #fbe9d7;
    --good: #3f7a52;
    --good-wash: #e3f0e6;
    --focus: #2f6fb0;
    --shadow: 0 1px 2px rgba(20, 24, 22, 0.06), 0 6px 20px -8px rgba(20, 24, 22, 0.12);
    --toc-w: 250px;
  }

  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --paper: #14181a;
      --surface: #1b2022;
      --surface-2: #222829;
      --ink: #e9ece9;
      --ink-soft: #c2c9c4;
      --muted: #92a09a;
      --line: #2c3436;
      --line-strong: #3a4345;
      --accent: #e69a4e;
      --accent-ink: #201002;
      --accent-wash: #3a2712;
      --good: #7ec293;
      --good-wash: #1c2c20;
      --focus: #7db3e8;
      --shadow: 0 1px 2px rgba(0, 0, 0, 0.3), 0 10px 28px -10px rgba(0, 0, 0, 0.5);
    }
  }

  :root[data-theme="dark"] {
    --paper: #14181a;
    --surface: #1b2022;
    --surface-2: #222829;
    --ink: #e9ece9;
    --ink-soft: #c2c9c4;
    --muted: #92a09a;
    --line: #2c3436;
    --line-strong: #3a4345;
    --accent: #e69a4e;
    --accent-ink: #201002;
    --accent-wash: #3a2712;
    --good: #7ec293;
    --good-wash: #1c2c20;
    --focus: #7db3e8;
    --shadow: 0 1px 2px rgba(0, 0, 0, 0.3), 0 10px 28px -10px rgba(0, 0, 0, 0.5);
  }

  * { box-sizing: border-box; }

  body {
    background: var(--paper);
    color: var(--ink);
    font-family: "IBM Plex Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    line-height: 1.6;
  }

  code, .mono {
    font-family: "IBM Plex Mono", ui-monospace, monospace;
  }

  /* ── 플로팅 목차 ── */

  .toc-toggle {
    display: none;
    position: fixed;
    top: 14px;
    left: 14px;
    z-index: 30;
    width: 40px;
    height: 40px;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    border: 1px solid var(--line-strong);
    background: var(--surface);
    color: var(--ink);
    box-shadow: var(--shadow);
    cursor: pointer;
    font-size: 16px;
  }

  .toc-toggle:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }

  .toc-backdrop {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(10, 12, 11, 0.4);
    z-index: 24;
  }

  .toc {
    position: fixed;
    top: 0;
    left: 0;
    width: var(--toc-w);
    height: 100vh;
    overflow-y: auto;
    background: var(--surface);
    border-right: 1px solid var(--line);
    padding: 22px 14px 30px;
    z-index: 25;
  }

  .toc-brand {
    font-size: 13px;
    font-weight: 700;
    color: var(--ink);
    padding: 0 10px;
    margin-bottom: 4px;
  }

  .toc-brand .sub {
    display: block;
    font-size: 11px;
    font-weight: 500;
    color: var(--muted);
    margin-top: 2px;
  }

  .toc-close {
    display: none;
    position: absolute;
    top: 14px;
    right: 12px;
    width: 30px;
    height: 30px;
    border-radius: 8px;
    border: 1px solid var(--line);
    background: var(--surface);
    color: var(--muted);
    cursor: pointer;
    font-size: 14px;
  }

  .toc-group-label {
    font-size: 10.5px;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 14px 10px 4px;
  }

  .toc-link {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 7px 10px;
    border-radius: 8px;
    font-size: 13px;
    color: var(--ink-soft);
    text-decoration: none;
    position: relative;
  }

  .toc-link:hover { background: var(--surface-2); color: var(--ink); }

  .toc-link:focus-visible { outline: 2px solid var(--focus); outline-offset: -2px; }

  .toc-link.current {
    background: var(--accent-wash);
    color: var(--accent);
    font-weight: 600;
  }

  .toc-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 999px;
    border: 1.5px solid var(--line-strong);
    font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: 10.5px;
    font-weight: 600;
    color: var(--muted);
    flex-shrink: 0;
  }

  .toc-link.done .toc-badge {
    background: var(--good);
    border-color: var(--good);
    color: #fff;
  }

  .toc-link.done .toc-badge::before { content: "✓"; }
  .toc-link.done .toc-badge > * { display: none; }

  @media (max-width: 900px) {
    .toc-toggle { display: flex; }
    .toc-backdrop.show { display: block; }
    .toc {
      transform: translateX(-100%);
      transition: transform 0.2s ease;
      box-shadow: var(--shadow);
    }
    .toc.open { transform: translateX(0); }
    .toc-close { display: block; }
    .content-outer { margin-left: 0 !important; }
  }

  @media (prefers-reduced-motion: reduce) {
    .toc { transition: none; }
  }

  /* ── 본문 레이아웃 ── */

  .content-outer {
    margin-left: var(--toc-w);
    min-height: 100vh;
  }

  .wrap {
    max-width: 720px;
    margin: 0 auto;
    padding: 40px 24px 90px;
  }

  h1 {
    font-size: clamp(24px, 4vw, 30px);
    font-weight: 700;
    margin: 0 0 8px;
    letter-spacing: -0.01em;
    text-wrap: balance;
  }

  h2 {
    font-size: 20px;
    font-weight: 700;
    margin: 0;
    text-wrap: balance;
  }

  .lede {
    color: var(--ink-soft);
    font-size: 15px;
    max-width: 62ch;
    margin: 0 0 20px;
  }

  .lede strong { color: var(--ink); }

  @media (prefers-reduced-motion: reduce) {
  }

  /* ── 페이지 전환 ── */

  .page { display: none; }
  .page.active { display: block; animation: fadeIn 0.15s ease; }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @media (prefers-reduced-motion: reduce) {
    .page.active { animation: none; }
  }

  /* prep 페이지 내부 (기존 체크리스트 스타일) */

  section.group { margin-bottom: 0; }

  .group-head { display: flex; align-items: baseline; gap: 10px; margin-bottom: 4px; }

  .group-head .num {
    font-size: 13px;
    font-weight: 600;
    color: var(--accent);
    background: var(--accent-wash);
    border-radius: 6px;
    padding: 2px 8px;
  }

  .group-head h2 { font-size: 17px; }

  .group-sub { color: var(--muted); font-size: 13.5px; margin: 0 0 14px 0; }

  .page-inner > section.group { margin-bottom: 30px; }

  .items { display: flex; flex-direction: column; gap: 10px; }

  .item {
    display: grid;
    grid-template-columns: 28px 1fr;
    gap: 14px;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 14px 16px;
    transition: border-color 0.15s ease, background 0.15s ease;
  }

  .item:has(.check:checked) { border-color: var(--good); background: var(--good-wash); }

  @media (prefers-reduced-motion: reduce) { .item { transition: none; } }

  .check-col { display: flex; justify-content: center; padding-top: 2px; }

  .check, .page-check {
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 6px;
    border: 1.5px solid var(--line-strong);
    background: var(--surface);
    cursor: pointer;
    display: grid;
    place-content: center;
    flex-shrink: 0;
  }

  .check:focus-visible, .page-check:focus-visible {
    outline: 2px solid var(--focus);
    outline-offset: 2px;
  }

  .check::after, .page-check::after {
    content: "";
    width: 10px;
    height: 6px;
    border-left: 2px solid var(--accent-ink);
    border-bottom: 2px solid var(--accent-ink);
    transform: rotate(-45deg) translateY(-1px);
    opacity: 0;
  }

  .check:checked, .page-check:checked { background: var(--good); border-color: var(--good); }
  .check:checked::after, .page-check:checked::after { opacity: 1; }

  .item-title {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    font-weight: 600;
    font-size: 15px;
    margin: 0 0 4px;
  }

  .tag {
    font-size: 11px;
    font-weight: 600;
    padding: 1px 7px;
    border-radius: 999px;
    letter-spacing: 0.02em;
  }

  .tag.required { background: var(--accent-wash); color: var(--accent); }
  .tag.free { background: var(--good-wash); color: var(--good); }

  .item p { margin: 0 0 8px; font-size: 13.5px; color: var(--ink-soft); }
  .item p:last-child { margin-bottom: 0; }
  .item .warn { color: var(--accent); }

  .actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: inherit;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none;
    padding: 7px 13px;
    border-radius: 8px;
    border: 1px solid var(--line-strong);
    color: var(--ink);
    background: var(--surface);
    cursor: pointer;
  }

  .btn:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .btn.primary { background: var(--accent); border-color: var(--accent); color: var(--accent-ink); }
  .btn .arrow { font-size: 15px; line-height: 1; }

  .tiny { font-size: 12px; color: var(--muted); margin: 10px 0 0; }

  /* STEP 0 의 완성 창 그림 */
  .shot { margin: 14px 0 6px; }
  .shot img {
    display: block; width: 100%; height: auto; background: #fff;
    border: 1px solid var(--line-strong); border-radius: 6px; box-shadow: var(--shadow);
  }

  /* API 목록 표 — 좁은 화면에서는 표 자체만 가로 스크롤된다 */
  .apitable-wrap { overflow-x: auto; margin-top: 10px; -webkit-overflow-scrolling: touch; }
  .apitable { width: 100%; min-width: 640px; border-collapse: collapse; font-size: 13px; }
  .apitable th, .apitable td {
    text-align: left; padding: 9px 12px 9px 0; vertical-align: top;
    border-bottom: 1px solid var(--line);
  }
  .apitable thead th {
    color: var(--muted); font-weight: 600; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.04em;
    border-bottom: 1px solid var(--line-strong); white-space: nowrap;
  }
  .apitable tbody tr:last-child td { border-bottom: none; }
  .apitable .api-name { font-weight: 600; color: var(--ink); white-space: nowrap; }
  .apitable .api-sub { display: block; color: var(--muted); font-size: 11px; font-weight: 400; }
  .apitable .api-quota { color: var(--muted); white-space: nowrap; }
  .apitable .api-pick { color: var(--accent); font-weight: 600; }
  .filetable { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
  .filetable th, .filetable td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); }
  .filetable th { color: var(--muted); font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; }
  .filetable td:last-child, .filetable th:last-child { text-align: right; }

  .install-details { margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--line); }
  .install-details summary { cursor: pointer; font-size: 13px; font-weight: 600; color: var(--ink-soft); }
  .install-details summary:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .install-details[open] summary { color: var(--ink); margin-bottom: 8px; }

  .install-list { margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 7px; font-size: 13px; color: var(--ink-soft); }
  .install-list strong { color: var(--ink); font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 0.95em; }

  .kv { display: grid; grid-template-columns: max-content 1fr; gap: 4px 12px; font-size: 13px; margin-top: 8px; }
  .kv dt { color: var(--muted); }
  .kv dd { margin: 0; }

  code {
    background: var(--surface-2);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 0.92em;
  }

  .callout {
    background: var(--surface);
    border: 1px solid var(--line);
    border-left: 3px solid var(--accent);
    border-radius: 0 12px 12px 0;
    padding: 16px 18px;
    font-size: 13.5px;
    color: var(--ink-soft);
    margin-top: 22px;
  }

  .callout strong { color: var(--ink); }
  .callout a { color: var(--accent); }

  /* ── 실습 STEP 페이지 ── */

  .page-head { margin-bottom: 18px; }

  .page-eyebrow {
    display: block;
    font-size: 11.5px;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 8px;
  }

  .page-title-row {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 8px;
  }

  .page-check-wrap { display: flex; }

  .page-title-row h2 { flex: 1; min-width: 160px; }

  .step-time {
    font-size: 12px;
    color: var(--muted);
    font-family: "IBM Plex Mono", ui-monospace, monospace;
    flex-shrink: 0;
  }

  .step-desc { font-size: 14px; color: var(--ink-soft); margin: 0; }

  .cmd-box {
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--surface-2);
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 14px;
    font-size: 12.5px;
    flex-wrap: wrap;
  }

  .cmd-label { color: var(--muted); flex-shrink: 0; }
  .cmd-text { font-family: "IBM Plex Mono", ui-monospace, monospace; color: var(--ink); flex: 1; min-width: 140px; }

  .prompt-box { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; margin-bottom: 16px; }

  .prompt-box-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    background: var(--surface-2);
    padding: 9px 14px;
    font-size: 12px;
    font-weight: 600;
    color: var(--ink-soft);
  }

  .prompt-text {
    margin: 0;
    padding: 16px;
    font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: 13px;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
    color: var(--ink);
  }

  .copy-btn {
    font-size: 11.5px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 6px;
    border: 1px solid var(--line-strong);
    background: var(--surface);
    color: var(--ink-soft);
    cursor: pointer;
    flex-shrink: 0;
  }

  .copy-btn:hover { color: var(--ink); }
  .copy-btn:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .copy-btn.copied { color: var(--good); border-color: var(--good); }

  .workflow-note {
    background: var(--accent-wash);
    border: 1px solid var(--accent);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 18px;
  }

  .workflow-note-title {
    font-size: 13.5px;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 8px;
  }

  .workflow-note ol {
    margin: 0;
    padding-left: 20px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .workflow-note li { font-size: 13px; color: var(--ink-soft); }
  .workflow-note strong { color: var(--ink); }
  .workflow-note code { background: var(--surface); }

  .criteria-box { background: var(--good-wash); border-radius: 10px; padding: 14px 16px; margin-bottom: 4px; }

  .criteria-label {
    font-size: 12px;
    font-weight: 700;
    color: var(--good);
    margin: 0 0 8px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .criteria-box ul { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 6px; }

  .criteria-box li { font-size: 13.5px; color: var(--ink-soft); padding-left: 22px; position: relative; }

  .criteria-box li::before {
    content: "✓";
    position: absolute;
    left: 0;
    color: var(--good);
    font-weight: 700;
  }

  .answer-details { margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--line); }
  .answer-details summary { cursor: pointer; font-size: 13.5px; font-weight: 600; color: var(--ink-soft); }
  .answer-details summary:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .answer-details[open] summary { color: var(--ink); margin-bottom: 12px; }

  .code-box { position: relative; }
  .code-box .copy-btn { position: absolute; top: 8px; right: 8px; }

  .code-block {
    margin: 0;
    background: var(--surface-2);
    border-radius: 10px;
    padding: 16px;
    overflow-x: auto;
    font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: 12.5px;
    line-height: 1.6;
    color: var(--ink);
    white-space: pre;
  }

  /* ── 페이지 이동 바 ── */

  .page-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-top: 34px;
    padding-top: 18px;
    border-top: 1px solid var(--line);
  }

  .page-nav-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 13.5px;
    font-weight: 600;
    padding: 9px 16px;
    border-radius: 9px;
    border: 1px solid var(--line-strong);
    background: var(--surface);
    color: var(--ink);
    cursor: pointer;
  }

  .page-nav-btn:hover { background: var(--surface-2); }
  .page-nav-btn:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .page-nav-btn:disabled { opacity: 0.35; cursor: default; }
  .page-nav-btn:disabled:hover { background: var(--surface); }
  .page-nav-btn.next { background: var(--accent); border-color: var(--accent); color: var(--accent-ink); }
  .page-nav-btn.next:hover { filter: brightness(1.05); }

  .page-nav-pos {
    font-size: 12px;
    color: var(--muted);
    font-family: "IBM Plex Mono", ui-monospace, monospace;
  }

  footer {
    margin-top: 44px;
    padding-top: 18px;
    border-top: 1px solid var(--line);
    font-size: 12px;
    color: var(--muted);
  }
</style>'''

TOC_HTML = f'''<button class="toc-toggle" id="tocToggle" aria-label="목차 열기" aria-expanded="false">☰</button>
<div class="toc-backdrop" id="tocBackdrop"></div>
<nav class="toc" id="toc" aria-label="실습 목차">
  <button class="toc-close" id="tocClose" aria-label="목차 닫기">✕</button>
  <div class="toc-brand">DART·뉴스 정보 크롤링 및 메일발송 프로그램 만들기<span class="sub">사전 준비부터 발송까지</span></div>

  <a class="toc-link" data-page="prep" href="#prep"><span class="toc-badge">0</span>사전 준비</a>

  <div class="toc-group-label">실습 1 · 수집</div>
{toc_part1}

  <div class="toc-group-label">실습 2 · 보고서</div>
{toc_part2}

  <div class="toc-group-label">실습 3 · 메일 발송</div>
{toc_part3}

  <div class="toc-group-label">참고</div>
      <a class="toc-link" data-page="apis" href="#apis"><span class="toc-badge">?</span>API 목록</a>
      <a class="toc-link" data-page="apps" href="#apps"><span class="toc-badge">+</span>The APPS</a>
</nav>'''



# ── API 안내 페이지 ───────────────────────────────────────
# 수치(한도·가격)는 2026-09-21 확인값이다. 자주 바뀌므로 발급처 화면을 우선한다.
APIS_PAGE = '''
  <section class="page" data-page="apis" id="apis">
    <div class="page-head">
      <span class="page-eyebrow">참고</span>
      <div class="page-title-row">
        <h2>다음에 붙여볼 API 목록</h2>
      </div>
      <p class="step-desc">오늘 만든 것은 DART 전용 프로그램이 아니라
        <strong>「인증키로 자료 받아 정리해서 메일 보내는 틀」</strong> 이다. 주소와 인증키만
        바꾸면 아래 것들이 똑같이 돌아간다. 아래 목록은 모두 사내망에서 응답이 오는 것을
        확인했다.</p>
    </div>

    <div class="workflow-note">
      <p class="workflow-note-title">API 가 뭔가 — 한 줄로</p>
      <ol>
        <li><strong>사람이 보라고 만든 것이 홈페이지, 프로그램이 받아가라고 열어둔 창구가 API 다.</strong>
          DART 홈페이지에서 눈으로 읽던 공시를, 오늘은 프로그램이 받아왔다. 그게 API 다.</li>
        <li><strong>인증키는 출입증이다.</strong> 누가 얼마나 가져가는지 세기 위해 발급받는다.
          그래서 남에게 주면 안 되고, 코드 안에 적어두면 안 된다 — 오늘 프로그램이 인증키를
          창의 입력 칸에서 받은 이유다.</li>
        <li><strong>대부분 무료다.</strong> 공공기관이 여는 것은 거의 다 무료이고, 하루에 몇 번까지
          쓸 수 있는지(호출 한도)만 정해져 있다. 개인이 쓰는 수준에서는 넘길 일이 거의 없다.</li>
      </ol>
    </div>

    <div class="criteria-box">
      <p class="criteria-label">난이도 — 인증 방식으로 갈린다</p>
      <ul>
        <li><strong>1단계 · 인증키 없음</strong> — 주소만 넣으면 끝. 오늘 쓴 구글 뉴스가 여기다.</li>
        <li><strong>2단계 · 인증키 하나</strong> — 발급받아 입력 칸에 붙여넣으면 끝.
          오늘 쓴 DART 가 여기고, <strong>아래 목록이 전부 2단계다.</strong>
          여기까지가 혼자 할 수 있는 선이다.</li>
        <li><strong>3단계 · 회사 아이디 연동(래디우스, RADIUS)</strong> — 개인이 발급받는 인증키가 아니라
          <strong>회사 계정으로 인증해서</strong> 붙는 방식. 인증 절차가 따로 있어 혼자 붙일 수 없다.
          <strong>DX팀에 문의.</strong></li>
        <li><strong>4단계 · 사내 시스템 자체</strong> — 그룹웨어, ERP 처럼 사내 데이터를 직접
          가져오는 것. 인증뿐 아니라 <strong>데이터를 써도 되는지</strong>부터 담당 부서 협의가 먼저다.</li>
      </ul>
    </div>

    <div class="criteria-box">
      <p class="criteria-label">무료 — 인증키만 받으면 쓸 수 있다</p>
      <div class="apitable-wrap">
      <table class="apitable">
        <thead><tr><th>API</th><th>무엇에 쓰나</th><th>발급처</th><th>한도</th></tr></thead>
        <tbody>
          <tr>
            <td class="api-name api-pick">나라장터 입찰공고<span class="api-sub">조달청</span></td>
            <td>공사·물품 입찰 공고를 업종·지역·금액으로 매일 받기.
              <strong>오늘 만든 것과 구조가 같다</strong> — 영업·견적에 바로 쓴다</td>
            <td><a href="https://www.data.go.kr/" target="_blank" rel="noopener">공공데이터포털</a></td>
            <td class="api-quota">하루 1,000건</td>
          </tr>
          <tr>
            <td class="api-name api-pick">기상청 단기예보·특보</td>
            <td>강우·강풍 예보로 현장 작업중지 판단, 공정 조정</td>
            <td><a href="https://www.data.go.kr/" target="_blank" rel="noopener">공공데이터포털</a></td>
            <td class="api-quota">하루 1,000건</td>
          </tr>
          <tr>
            <td class="api-name">에어코리아 대기질</td>
            <td>미세먼지 경보, 옥외작업·비산먼지 관리</td>
            <td><a href="https://www.data.go.kr/" target="_blank" rel="noopener">공공데이터포털</a></td>
            <td class="api-quota">하루 1,000건</td>
          </tr>
          <tr>
            <td class="api-name api-pick">공휴일 정보<span class="api-sub">한국천문연구원</span></td>
            <td><strong>공정표 작업일수 계산.</strong> 단순한데 활용도가 가장 높은 축</td>
            <td><a href="https://www.data.go.kr/" target="_blank" rel="noopener">공공데이터포털</a></td>
            <td class="api-quota">하루 1,000건</td>
          </tr>
          <tr>
            <td class="api-name">아파트 실거래가<span class="api-sub">국토교통부</span></td>
            <td>매매·전월세 실거래, 분양·개발 검토</td>
            <td><a href="https://www.data.go.kr/" target="_blank" rel="noopener">공공데이터포털</a></td>
            <td class="api-quota">하루 1,000건</td>
          </tr>
          <tr>
            <td class="api-name">건축물대장<span class="api-sub">건축HUB</span></td>
            <td>부지·건물 제원 조회</td>
            <td><a href="https://www.data.go.kr/" target="_blank" rel="noopener">공공데이터포털</a></td>
            <td class="api-quota">하루 1,000건</td>
          </tr>
          <tr>
            <td class="api-name">경제통계<span class="api-sub">한국은행 ECOS</span></td>
            <td>금리·환율·건설기성 등</td>
            <td><a href="https://ecos.bok.or.kr/api/" target="_blank" rel="noopener">ecos.bok.or.kr</a></td>
            <td class="api-quota">하루 2만 건</td>
          </tr>
          <tr>
            <td class="api-name">국가통계<span class="api-sub">KOSIS</span></td>
            <td>건설수주액, 자재 물가지수</td>
            <td><a href="https://kosis.kr/openapi/" target="_blank" rel="noopener">kosis.kr</a></td>
            <td class="api-quota">하루 2만 건</td>
          </tr>
          <tr>
            <td class="api-name">카카오 로컬</td>
            <td>주소를 좌표로 바꾸기, 현장 위치 지도</td>
            <td><a href="https://developers.kakao.com/" target="_blank" rel="noopener">developers.kakao.com</a></td>
            <td class="api-quota">하루 10만 건</td>
          </tr>
          <tr>
            <td class="api-name">네이버 개발자센터</td>
            <td>뉴스·블로그 검색 (구글 뉴스의 대안)</td>
            <td><a href="https://developers.naver.com/" target="_blank" rel="noopener">developers.naver.com</a></td>
            <td class="api-quota">하루 2만 5천 건</td>
          </tr>
          <tr>
            <td class="api-name">DART 전자공시<span class="api-sub">오늘 쓴 것</span></td>
            <td>상장사 공시. 계정당 인증키 1개, 개인은 즉시 발급</td>
            <td><a href="https://opendart.fss.or.kr/" target="_blank" rel="noopener">opendart.fss.or.kr</a></td>
            <td class="api-quota">하루 2만 건</td>
          </tr>
          <tr>
            <td class="api-name">구글 뉴스<span class="api-sub">오늘 쓴 것</span></td>
            <td>키워드 뉴스 검색. 구글이 공식 지원을 밝힌 적이 없어 바뀔 수 있다</td>
            <td class="api-quota">발급 불필요</td>
            <td class="api-quota">인증키 없음</td>
          </tr>
        </tbody>
      </table>
      </div>
      <p class="tiny" style="margin-top:8px;">주황색으로 표시한 셋이 우리 업무에 가장 가깝다.
        공공데이터포털 항목의 한도는 개발용 계정 기준이고, 실제 서비스용으로 신청하면
        하루 10만 건까지 늘어난다.</p>
    </div>

    <div class="criteria-box">
      <p class="criteria-label">유료 — AI API (쓴 만큼 돈이 나간다)</p>
      <p class="tiny" style="margin-bottom:6px;">모아온 기사를 <strong>요약·분류하고 중요도를
        매기는</strong> 데 쓴다. 오늘 만든 보고서에 붙이면 「읽을 것만 골라주는」 리포트가 된다.
        무료 한도가 아니라 <strong>쓴 만큼 과금</strong>된다(대개 선불 충전).</p>
      <div class="apitable-wrap">
      <table class="apitable">
        <thead><tr><th>제공사</th><th>대표 모델</th><th>발급처</th><th>참고</th></tr></thead>
        <tbody>
          <tr>
            <td class="api-name">Anthropic</td>
            <td>Claude</td>
            <td><a href="https://console.anthropic.com/" target="_blank" rel="noopener">console.anthropic.com</a></td>
            <td>긴 문서 정리에 강하다</td>
          </tr>
          <tr>
            <td class="api-name">OpenAI</td>
            <td>GPT</td>
            <td><a href="https://platform.openai.com/" target="_blank" rel="noopener">platform.openai.com</a></td>
            <td>자료와 예제가 가장 많다</td>
          </tr>
          <tr>
            <td class="api-name">Google</td>
            <td>Gemini</td>
            <td><a href="https://aistudio.google.com/" target="_blank" rel="noopener">aistudio.google.com</a></td>
            <td>무료 시험 한도가 있다</td>
          </tr>
          <tr>
            <td class="api-name">네이버클라우드</td>
            <td>HyperCLOVA X</td>
            <td><a href="https://clovastudio.ncloud.com/" target="_blank" rel="noopener">clovastudio.ncloud.com</a></td>
            <td>국내 서비스·국내 결제</td>
          </tr>
          <tr>
            <td class="api-name">업스테이지</td>
            <td>Solar</td>
            <td><a href="https://console.upstage.ai/" target="_blank" rel="noopener">console.upstage.ai</a></td>
            <td>국내 서비스, 문서 인식에 강하다</td>
          </tr>
          <tr>
            <td class="api-name">Microsoft</td>
            <td>Azure OpenAI</td>
            <td><a href="https://azure.microsoft.com/ko-kr/products/ai-services/openai-service" target="_blank" rel="noopener">azure.microsoft.com</a></td>
            <td><strong>사내 Azure 계약이 있으면 이쪽이 먼저다</strong></td>
          </tr>
        </tbody>
      </table>
      </div>
      <p class="tiny" style="margin-top:8px;">가격은 글자 100만 자 단위로 매겨진다. 가벼운 모델은
        100만 자에 1달러대, 가장 좋은 모델은 5달러대이고 <strong>받는 답변 쪽이 5배쯤 비싸다.</strong>
        기사 몇백 건 요약은 몇백 원 수준이다. 정확한 값은 각 발급처의 요금 안내를 볼 것.</p>
    </div>

    <div class="callout">
      <p><strong>AI API 는 혼자 신청하지 말 것.</strong> 두 가지가 먼저다 —
        <strong>결제 수단</strong>(개인 카드로 회사 일을 결제하면 정산이 곤란해진다)과
        <strong>보안 검토</strong>(사내 자료를 외부 AI 로 보내도 되는지는 자료 종류에 따라 다르다).
        <strong>DX팀에 먼저 문의할 것.</strong></p>
    </div>

    <div class="criteria-box">
      <p class="criteria-label">그 밖의 유료</p>
      <ul>
        <li><strong>유료 데이터 서비스</strong> — 증권사 시세, 신용평가, 해외 입찰정보 등은
          업체별 계약이 필요하다. 개인이 발급받는 성격이 아니다.</li>
      </ul>
    </div>

    <div class="workflow-note">
      <p class="workflow-note-title">인증키 발급 — 어디나 순서가 같다</p>
      <ol>
        <li><strong>회원가입</strong> — 발급처 사이트에 가입한다 (대부분 회사 메일로 가능).</li>
        <li><strong>인증키 신청</strong> — DART·ECOS·KOSIS 는 신청하면 <strong>바로 발급</strong>된다.
          카카오·네이버는 「애플리케이션 등록」 을 먼저 하면 키가 나온다.</li>
        <li><strong>공공데이터포털만 한 단계 더 있다</strong> — 아래 주의사항 참고.</li>
        <li><strong>발급받은 키는 프로그램 입력 칸에 붙여넣는다.</strong>
          코드 안에 적지 않는다. 오늘 만든 프로그램이 그렇게 되어 있다.</li>
      </ol>
    </div>

    <div class="criteria-box">
      <p class="criteria-label">주의 — 공공데이터포털은 DART 와 다르다</p>
      <ul>
        <li><strong>키 하나로 전부 되는 게 아니다.</strong> 계정 인증키는 하나지만,
          <strong>쓰려는 API 마다 「활용신청」 을 따로</strong> 해야 한다.</li>
        <li>자동승인되는 것도 있지만 <strong>심의 대상이면 1~2일</strong> 걸린다.
          쓸 API 를 미리 정해 신청까지 끝내둬야 한다.</li>
        <li>신청하지 않은 API 를 부르면 키가 멀쩡한데도 거부된다.
          <strong>키가 틀린 것으로 오해하기 쉬운 지점이다.</strong></li>
        <li>개발용 계정은 <strong>하루 1,000건</strong>, 실제 서비스용으로 신청하면
          <strong>하루 10만 건</strong>까지 늘어난다. 혼자 쓰기에는 개발용으로 충분하다.</li>
      </ul>
    </div>

    <div class="callout">
      <p><strong>한도와 가격은 바뀐다.</strong> 위 숫자는 2026년 9월에 확인한 값이다.
        실제로 쓸 때는 발급처 화면의 안내를 따른다. 그리고 어떤 API 든 오늘과 똑같이
        <strong>「막히면 에러 문장을 그대로 AI 에게 붙여넣기」</strong> 가 가장 빠른 해결책이다.</p>
    </div>
  </section>'''

# ── 마지막 안내 페이지 ────────────────────────────────────
# 실습이 끝난 사람에게 "만든 걸 어디에 올리는지" 를 알려주는 자리.
# 매뉴얼 파일은 여기에 넣지 않는다 (사내 배포 문서라 별도로 전달한다).
APPS_PAGE = '''
  <section class="page" data-page="apps" id="apps">
    <div class="page-head">
      <span class="page-eyebrow">참고</span>
      <div class="page-title-row">
        <h2>만든 걸 사내에 등록하기 — The APPS</h2>
      </div>
      <p class="step-desc">오늘 만든 프로그램은 내 PC 에만 있다. 팀에서 같이 쓰려면
        사내 앱 스토어인 <strong>The APPS</strong> 에 등록하면 된다. 흩어진 사내 웹·앱을
        한곳에서 찾고, 우리가 만든 것을 한곳에서 관리하는 곳이다.</p>
    </div>

    <div class="workflow-note">
      <p class="workflow-note-title">The APPS 는 이런 곳이다</p>
      <ol>
        <li><strong>찾기는 로그인 없이</strong> — 어떤 사내 앱이 있는지 검색해서 바로 쓸 수 있다.
          "출장비 정산" 처럼 하는 일로 찾아도 나온다.</li>
        <li><strong>등록은 누구나 신청</strong> — 이름·주소·설명·분류를 적어 올리면 된다.
          오늘 만든 것처럼 파일로 쓰는 도구도, 주소로 접속하는 웹앱도 둘 다 올릴 수 있다.</li>
        <li><strong>운영·보안 두 심사를 거쳐 게시된다</strong> — 특히 보안 심사에서
          <strong>파일 안에 인증키나 비밀번호가 들어있는지</strong> 를 본다. 오늘 실습에서
          DART 인증키를 코드가 아니라 창의 입력 칸에 넣은 것도 같은 이유다.</li>
        <li><strong>설치 횟수와 별점이 쌓인다</strong> — 누가 실제로 쓰는지 숫자로 남는다.</li>
      </ol>
    </div>

    <div class="criteria-box">
      <p class="criteria-label">바로 가기</p>
      <ul>
        <li><strong>주소</strong> —
          <a href="https://vibe-registry.xicna.app/" target="_blank" rel="noopener">vibe-registry.xicna.app</a>
          <strong>(오픈 전)</strong>
          <br>아직 정식 오픈 전이라 지금 눌러도 열리지 않을 수 있다. 오픈하면 따로 안내한다.
          열린 뒤에도 <strong>사내망에서만</strong> 접속되니, 집이나 휴대폰 네트워크에서
          안 열리면 회사 네트워크인지 먼저 확인한다.</li>
        <li><strong>사용 매뉴얼</strong> — 계정·권한·등록 절차를 담은 안내 자료는 따로 전달한다.</li>
      </ul>
    </div>
  </section>'''

PREP_PAGE = f'''
  <section class="page" data-page="prep" id="prep">
    <div class="page-inner">
      <h1>DART·뉴스 정보 크롤링 및 메일발송 프로그램 만들기</h1>

      <div class="group-head" style="margin-top: 26px;">
        <span class="num">0</span>
        <h2>사전 준비</h2>
      </div>
      <p class="group-sub">실습 전 준비해야 할 사항</p>

{sections_prep}

{callout_prep}
    </div>
  </section>'''


FOOTER = '''
  <footer>
    바이브 코딩 실습 · DART·뉴스 정보 크롤링 및 메일발송 프로그램 만들기 ·
    프로그램 창에 입력한 인증키는 <code>settings.json</code> 에 저장됩니다 — 이 파일은 공유하지 마세요 ·
    프롬프트는 예시입니다, 표현을 바꿔서 시도해봐도 좋습니다
  </footer>'''

SCRIPT = '''<script>
(function () {
  var PAGE_IDS = ''' + repr(ALL_PAGE_IDS).replace("'", '"') + ''';
  var STORAGE_KEY = "issuebot-checklist";
  var STATE_KEY = "issuebot-current-page";

  var boxes = Array.prototype.slice.call(document.querySelectorAll(".check, .page-check"));
  var pages = Array.prototype.slice.call(document.querySelectorAll(".page"));
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc-link"));
  var itemCountWordEl = document.getElementById("itemCountWord");
  var navPrevBtn = document.getElementById("pageNavPrev");
  var navNextBtn = document.getElementById("pageNavNext");
  var navPosEl = document.getElementById("pageNavPos");

  var toc = document.getElementById("toc");
  var tocToggle = document.getElementById("tocToggle");
  var tocClose = document.getElementById("tocClose");
  var tocBackdrop = document.getElementById("tocBackdrop");

  function loadState() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"); }
    catch (e) { return {}; }
  }

  function saveState(state) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }
    catch (e) { /* 저장 안 되면 세션 동안만 유지 */ }
  }

  function render() {
    // 진행률 표시는 두지 않는다. 체크박스는 스스로 확인하는 용도로만 쓰고,
    // 다 체크한 단계는 목차에서 색으로만 표시한다.
    if (itemCountWordEl) itemCountWordEl.textContent = "6가지";

    tocLinks.forEach(function (link) {
      var pageId = link.dataset.page;
      var pageEl = document.getElementById(pageId);
      if (!pageEl) return;
      var pageBoxes = pageEl.querySelectorAll(".check, .page-check");
      var allDone = pageBoxes.length > 0 &&
        Array.prototype.every.call(pageBoxes, function (b) { return b.checked; });
      link.classList.toggle("done", allDone);
    });
  }

  var state = loadState();
  boxes.forEach(function (box) {
    var id = box.dataset.id;
    if (state[id]) box.checked = true;
    box.addEventListener("change", function () {
      state[id] = box.checked;
      saveState(state);
      render();
    });
    box.addEventListener("click", function (e) { e.stopPropagation(); });
  });

  /* ── 페이지 전환 ── */

  function currentIndex() {
    var active = document.querySelector(".page.active");
    if (!active) return 0;
    var idx = PAGE_IDS.indexOf(active.dataset.page);
    return idx === -1 ? 0 : idx;
  }

  function goTo(pageId, opts) {
    opts = opts || {};
    if (PAGE_IDS.indexOf(pageId) === -1) pageId = PAGE_IDS[0];

    pages.forEach(function (p) { p.classList.toggle("active", p.dataset.page === pageId); });
    tocLinks.forEach(function (l) { l.classList.toggle("current", l.dataset.page === pageId); });

    var idx = PAGE_IDS.indexOf(pageId);
    navPrevBtn.disabled = idx <= 0;
    navNextBtn.disabled = idx >= PAGE_IDS.length - 1;
    navNextBtn.textContent = idx >= PAGE_IDS.length - 1 ? "완료" : "다음 →";
    navPosEl.textContent = (idx + 1) + " / " + PAGE_IDS.length;

    if (!opts.skipHash) {
      if (history.replaceState) history.replaceState(null, "", "#" + pageId);
      else location.hash = pageId;
    }
    try { sessionStorage.setItem(STATE_KEY, pageId); } catch (e) {}

    if (!opts.skipScroll) window.scrollTo(0, 0);
    closeToc();
  }

  tocLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      goTo(link.dataset.page);
    });
  });

  navPrevBtn.addEventListener("click", function () {
    var idx = currentIndex();
    if (idx > 0) goTo(PAGE_IDS[idx - 1]);
  });

  navNextBtn.addEventListener("click", function () {
    var idx = currentIndex();
    if (idx < PAGE_IDS.length - 1) goTo(PAGE_IDS[idx + 1]);
  });

  window.addEventListener("hashchange", function () {
    var id = location.hash.replace("#", "");
    if (id) goTo(id, { skipHash: true });
  });

  /* ── 목차 열기/닫기 (좁은 화면) ── */

  function openToc() {
    toc.classList.add("open");
    tocBackdrop.classList.add("show");
    tocToggle.setAttribute("aria-expanded", "true");
  }
  function closeToc() {
    toc.classList.remove("open");
    tocBackdrop.classList.remove("show");
    tocToggle.setAttribute("aria-expanded", "false");
  }
  tocToggle.addEventListener("click", function () {
    toc.classList.contains("open") ? closeToc() : openToc();
  });
  tocClose.addEventListener("click", closeToc);
  tocBackdrop.addEventListener("click", closeToc);

  /* ── 초기 페이지 결정: URL 해시 > 이전 세션 > 첫 페이지 ── */

  var initial = location.hash.replace("#", "");
  if (!initial) {
    try { initial = sessionStorage.getItem(STATE_KEY) || ""; } catch (e) { initial = ""; }
  }
  render();
  goTo(initial || PAGE_IDS[0], { skipHash: !initial, skipScroll: true });

  /* ── 복사 버튼 ── */

  function copyText(text, btn) {
    var settled = false;
    var done = function () {
      if (settled) return;
      settled = true;
      var original = btn.textContent;
      btn.textContent = "복사됨!";
      btn.classList.add("copied");
      setTimeout(function () {
        btn.textContent = original;
        btn.classList.remove("copied");
      }, 1500);
    };

    /* 클립보드 API가 권한 프롬프트 등으로 응답 없이 멈추는 경우를 대비해
       일정 시간 안에 안 끝나면 execCommand 방식으로 바로 넘어간다. */
    var timeoutId = setTimeout(function () { fallbackCopy(text, done); }, 600);

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        function () { clearTimeout(timeoutId); done(); },
        function () { clearTimeout(timeoutId); fallbackCopy(text, done); }
      );
    } else {
      clearTimeout(timeoutId);
      fallbackCopy(text, done);
    }
  }

  function fallbackCopy(text, done) {
    try {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      done();
    } catch (e) { /* 복사 실패 시 그냥 무시 */ }
  }

  Array.prototype.slice.call(document.querySelectorAll(".copy-btn")).forEach(function (btn) {
    btn.addEventListener("click", function () {
      var target = document.getElementById(btn.dataset.copy);
      if (!target) return;
      copyText(target.textContent, btn);
    });
  });

  /* ── "정답 코드 파일 받기" — main.py 를 base64 로 박아뒀다가 Blob 으로 내려받는다 ── */
  var MAIN_PY_B64 = "__MAIN_PY_B64__";
  Array.prototype.slice.call(document.querySelectorAll(".download-mainpy-btn")).forEach(function (btn) {
    btn.addEventListener("click", function () {
      try {
        var binary = atob(MAIN_PY_B64);
        var bytes = new Uint8Array(binary.length);
        for (var i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
        var blob = new Blob([bytes], { type: "text/x-python" });
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = "main.py";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(function () { URL.revokeObjectURL(url); }, 2000);
      } catch (e) {
        alert("다운로드에 실패했습니다. 강사에게 파일을 요청하세요.");
      }
    });
  });
})();
</script>'''
SCRIPT = SCRIPT.replace("__MAIN_PY_B64__", MAIN_PY_B64)

body = f'''{TOC_HTML}

<div class="content-outer">
  <div class="wrap">

{PREP_PAGE}
{step_pages_html}
{APIS_PAGE}
{APPS_PAGE}

    <div class="page-nav">
      <button class="page-nav-btn" id="pageNavPrev">← 이전</button>
      <span class="page-nav-pos" id="pageNavPos">1 / {len(ALL_PAGE_IDS)}</span>
      <button class="page-nav-btn next" id="pageNavNext">다음 →</button>
    </div>

{FOOTER}
  </div>
</div>'''

doc = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DART·뉴스 정보 크롤링 및 메일발송 프로그램 만들기</title>
{fonts_head}
{STYLE}
</head>
<body>
{body}

{SCRIPT}
</body>
</html>
'''

out_path = f"{REPO}/DART 뉴스 크롤링 및 메일발송 프로그램 만들기.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(doc)

# GitHub Pages 로 공유할 때 주소가 짧아지도록 같은 내용을 index.html 로도 쓴다.
# (한글·공백이 든 파일명은 주소에서 DART%20뉴스%20... 로 길게 늘어난다)
# 사람이 더블클릭해서 여는 것은 위의 한글 파일명 쪽을 그대로 쓴다.
index_path = f"{REPO}/index.html"
with open(index_path, "w", encoding="utf-8") as f:
    f.write(doc)

print("written:", out_path, len(doc), "chars,", len(ALL_PAGE_IDS), "pages")
print("written:", index_path, "(Pages 용 같은 사본)")
