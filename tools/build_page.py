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


# ── STEP 카드 렌더링 (한 STEP = 한 페이지) ──────────────────

WORKFLOW_NOTE = '''
    <div class="workflow-note">
      <p class="workflow-note-title">여기서부터는 진짜로 코드를 짠다 — AI는 이렇게 쓴다</p>
      <ol>
        <li>여기서 말하는 "AI"는 사내에서 쓰는 <strong>대화형 챗봇</strong>이다. 프롬프트를 넣으면
          그에 맞는 <strong>파이썬 코드 파일(.py)을 다운로드</strong>할 수 있게 준다 — 이 페이지처럼
          직접 실행해주지는 않고, 내 PC의 파일을 열어보거나 고쳐주지도 않는다.</li>
        <li>아래 <strong>프롬프트를 복사</strong>해서 그 AI 채팅창에 그대로 붙여넣는다.</li>
        <li>AI가 내려주는 파일을 받는다. <strong>지금은 이 단계가 처음이라 내 PC에 아무 파일도
          없다</strong> — 실습용 폴더를 하나 정해두고(바탕화면에 새로 만들어도 된다) 받은 파일을
          그 안으로 옮겨둔다. 어디에 어떤 이름으로 저장하고 어떻게 실행하는지는 AI가 알려주니
          그대로 따라 하면 된다.</li>
        <li><strong>다음 단계부터는 매번 파일을 새로 받는다.</strong> AI는 파일을 내려주기만 하니,
          같은 이름으로 또 받으면 브라우저가 <code>main (2).py</code>, <code>main (3).py</code>
          처럼 뒤에 번호를 붙여 저장한다. <strong>이름을 맞추려고 애쓸 필요 없다 — 방금 받은
          가장 최신 파일을 실행하면 된다.</strong> 단 <strong>폴더는 처음 정한 그대로 계속 쓴다</strong>
          — 창에 입력해둔 인증키 같은 값이 프로그램 파일과 같은 폴더에 저장되기 때문에, 폴더를
          옮겨 다니면 매번 처음부터 다시 입력해야 한다.</li>
        <li><strong>다음 단계로 넘어갈 때도 같은 대화창에서 계속 이어서 물어봐야 한다.</strong>
          새 대화를 시작하면 AI가 지금까지 짜준 코드를 기억하지 못한다. AI는 내 PC의 파일을 직접
          열어보지 못하니, 매번 "지금까지 코드 전체를 다시 통째로 달라"고 요청해서 파일을 새로
          받는 식으로 진행한다 (아래 프롬프트마다 이미 그렇게 요청하도록 되어 있다).</li>
        <li>이 AI 툴은 질문마다 답하는 모델이 자동으로 바뀐다("스마트 라우팅"). 어떤 모델은 파일을
          바로 첨부해주고, 어떤 모델은 파일 대신 채팅창에 코드를 텍스트로 그대로 보여준다. <strong>파일
          첨부 대신 텍스트로 나오면, 화면 위쪽에서 모델을 Gemini로 바꾼 뒤 같은 프롬프트를 다시
          넣어본다</strong> — 그래도 안 되면 이 페이지의 "정답 코드 파일 받기" 버튼을 대신 쓴다.</li>
      </ol>
    </div>
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
    intro = WORKFLOW_NOTE if step["id"] == "s0" else ""

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
      <span class="page-eyebrow">{"추가실습" if step['part'] == 3 else f"실습 {step['part']} · {'수집' if step['part'] == 1 else '메일 발송'}"}</span>
      <div class="page-title-row">
        <label class="page-check-wrap">
          <input type="checkbox" class="check page-check" data-id="{step['id']}">
        </label>
        <h2>STEP {step['num']} · {esc(step['title'])}</h2>
        <span class="step-time">{esc(step['time'])}</span>
      </div>
      <p class="step-desc">{esc(step['desc'])}</p>
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
    "s0": "뼈대", "s1": "구글 뉴스", "s2": "DART", "s3": "정리",
    "s4": "메일 본문", "s5": "아웃룩 발송", "s6": "완성",
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

ALL_PAGE_IDS = ["prep"] + [s["id"] for s in STEPS] + ["stuck"]
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

  .toc-mini-progress {
    margin: 14px 10px 16px;
    padding: 10px 12px;
    background: var(--surface-2);
    border-radius: 10px;
  }

  .toc-mini-progress .n {
    font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: 13px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }

  .toc-mini-track {
    margin-top: 6px;
    height: 5px;
    border-radius: 999px;
    background: var(--line);
    overflow: hidden;
  }

  .toc-mini-fill {
    height: 100%;
    width: 0%;
    background: var(--accent);
    border-radius: inherit;
    transition: width 0.3s ease;
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

  .progress-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: var(--shadow);
    margin-bottom: 30px;
  }

  .progress-top {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 10px;
  }

  .progress-top .label { font-size: 13px; color: var(--muted); }

  .progress-top .stat-value {
    font-size: 15px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    font-family: "IBM Plex Mono", ui-monospace, monospace;
  }

  .progress-track {
    height: 8px;
    border-radius: 999px;
    background: var(--surface-2);
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    width: 0%;
    background: var(--accent);
    border-radius: inherit;
    transition: width 0.35s ease;
  }

  .progress-note { margin: 12px 0 0; font-size: 12.5px; color: var(--muted); }

  @media (prefers-reduced-motion: reduce) {
    .progress-fill, .toc-mini-fill { transition: none; }
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

  <div class="toc-mini-progress">
    <span class="n"><span id="tocDone">0</span> / <span id="tocTotal">0</span> 완료</span>
    <div class="toc-mini-track"><div class="toc-mini-fill" id="tocFill"></div></div>
  </div>

  <a class="toc-link" data-page="prep" href="#prep"><span class="toc-badge">0</span>사전 준비</a>

  <div class="toc-group-label">실습 1 · 수집</div>
{toc_part1}

  <div class="toc-group-label">실습 2 · 메일 발송</div>
{toc_part2}

  <div class="toc-group-label">참고</div>
      <a class="toc-link" data-page="stuck" href="#stuck"><span class="toc-badge">!</span>막히면 여기</a>
</nav>'''

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


# ── "막히면 여기" 페이지 ──────────────────────────────────
# 이 목록은 상상이 아니라 실제로 이 프로그램을 사내 환경에서 끝까지 돌려보면서
# 하나씩 부딪힌 것들이다. 순서도 실제로 막힌 순서에 가깝다.
STUCK_PAGE = '''
  <section class="page" data-page="stuck" id="stuck">
    <div class="page-head">
      <span class="page-eyebrow">참고</span>
      <div class="page-title-row">
        <h2>막히면 여기</h2>
      </div>
      <p class="step-desc">실제로 사내 PC에서 끝까지 돌려보며 부딪힌 것들이다.
        증상만 보고 바로 찾아갈 수 있게 정리했다.</p>
    </div>

    <div class="workflow-note">
      <p class="workflow-note-title">먼저 이것부터 — 에러 문장을 그대로 AI에게 붙여넣기</p>
      <p class="tiny">아래를 다 읽을 필요 없다. <strong>프로그램 창이나 검은 창에 나온 문장을
        통째로 복사해서 AI 채팅창에 붙여넣고 "이거 왜 이래?"라고 물어보는 것이 가장 빠르다.</strong>
        아래는 그렇게 해도 안 풀릴 때, 혹은 강사가 원인을 빨리 짚어야 할 때 보는 목록이다.</p>
    </div>

    <div class="criteria-box">
      <p class="criteria-label">수집이 안 될 때</p>
      <ul>
        <li><strong>뉴스 결과 칸에 <code>CERTIFICATE_VERIFY_FAILED</code></strong>
          — 회사 보안 장비가 인터넷 통신을 중간에서 열어보고 자기 인증서로 다시 서명해
          넘겨준다. 크롬은 회사가 윈도우에 심어둔 인증서를 보기 때문에 잘 되는데,
          프로그램만 막히는 이유다.
          <strong>원인은 거의 항상 라이브러리 선택이다.</strong> <code>requests</code> 는
          윈도우 인증서 저장소를 보지 않고 <code>certifi</code> 라는 자기 목록만 보는데,
          거기에 회사 인증서가 없다. 반면 파이썬에 원래 들어있는 <code>urllib</code> 과
          그것을 쓰는 <code>feedparser</code> 는 윈도우 저장소를 보므로 그냥 된다
          (측정값: <code>urllib</code> 은 루트 인증서 67개 = 윈도우 저장소,
          <code>requests</code> 는 121개 = certifi 번들).
          <strong>STEP 1 의 "막히면" 안내</strong>를 펼쳐서 프롬프트를 이어 넣는다.
          코드에 <code>import requests</code> 가 보이면 그게 원인이다.
          인증서 검사를 아예 끄는 방식은 쓰지 않는다.</li>
        <li><strong>수집하고 나면 프로그램이 느려지거나 멈춘다</strong> — 결과 칸에 넣은 줄이
          너무 많은 것이다. 원인은 둘 중 하나다. ① <strong>DART 를 회사명 없이 돌렸다</strong> —
          일주일치 공시는 수천 건이라 그게 전부 쏟아진다. 회사명을 넣고 다시 누른다.
          ② <strong>AI가 버튼을 누를 때마다 지금까지 모은 걸 전부 다시 늘어놓게 만들었다</strong> —
          STEP 1·2 프롬프트에 "새로 가져온 것만 보여줘"가 들어가 있지만 AI가 무시할 때가 있다.
          <strong>STEP 3</strong> 을 먼저 적용하면 정리된다.
          결과 칸을 비우고 싶으면 프로그램을 껐다 켜면 된다 — 입력값은 남아있다.</li>
        <li><strong>뉴스가 전부 <code>검색 실패</code></strong> — 회사가 구글 뉴스를 막았을 수 있다.
          <code>한국뉴스_점검.py</code> 를 실행하면 구글만 막힌 건지 네트워크 전체가 막힌
          건지 구분해준다. 네트워크 전체가 막힌 게 아니라면 키워드를 바꿔 다시 눌러본다.</li>
        <li><strong>뉴스가 <code>0건</code></strong> (실패는 아님) — 그 키워드로 걸리는 기사가 없는
          것이다. 더 넓은 단어로 바꿔본다.</li>
        <li><strong>DART 가 <code>0건</code></strong> — 이유가 세 가지다. ① 그 기간에 공시가 아예
          없다(주말·공휴일이면 정상) ② 공시는 많았지만 그 회사 것이 없다 ③ 인증키 문제.
          프로그램이 이 셋을 구분해 알려주게 만들어 두었으니 DART 결과 칸의 문장을 먼저 읽는다.
          <code>dart_점검.py</code> 를 실행하면 기간을 1일/3일/7일로 늘려가며 각각 몇 건인지
          보여준다.</li>
        <li><strong>결과가 엉뚱한 칸에 들어간다 / 제목을 눌러도 원문이 안 열린다</strong>
          — AI가 STEP 0 의 칸 나누기나 링크 연결을 빠뜨린 것이다. 다음을 이어서 넣는다 —
          <em>"뉴스 수집 결과는 뉴스 칸에만, DART 수집 결과는 DART 칸에만 들어가게 해줘.
          그리고 두 칸 모두 항목 제목을 누르면 그 원문이 브라우저에서 열리게 하고, 제목은
          파란색에 밑줄로 보여줘. 전체를 통째로 다시 줘."</em></li>
        <li><strong>DART 에서 회사가 안 걸린다</strong> — <strong>정식 명칭으로</strong> 넣는다.
          <code>현대차</code> 는 DART 에 등록된 이름(현대자동차)과 달라서 안 걸린다.
          <strong>짧게 넣는 것은 해결책이 아니다</strong> — <code>삼성</code> 으로 넣으면 최근
          일주일에 140건이 걸리는데 그중 94건이 삼성자산운용 ETF 투자설명서이고 정작
          삼성전자는 0건이었다(실측). 노이즈만 폭증한다. <code>dart_점검.py</code> 를 실행하면
          걸린 회사별 건수를 찍어주니, 거기서 실제 등록된 이름을 확인해 그대로 넣는다.</li>
      </ul>
    </div>

    <div class="criteria-box">
      <p class="criteria-label">메일이 안 갈 때</p>
      <ul>
        <li><strong><code>클래식 아웃룩 자동 발송이 안 됩니다</code></strong> — "새 아웃룩"만 깔린
          PC에서 정상적으로 뜨는 메시지다. 오류가 아니다. 프로그램이 대신 메일 창을
          열어주니 <strong>[보내기]만 누르면 된다.</strong></li>
        <li><strong>메일 창도 안 뜬다</strong> — 아웃룩이 꺼져 있거나 로그인이 안 된 경우가
          대부분이다. 아웃룩을 먼저 켜서 로그인 화면이 없는지 확인한다.</li>
        <li><strong><code>pywin32 가 설치되어 있지 않습니다</code></strong> — 사전 준비의 설치
          파일을 안 돌렸거나, <strong>다른 파이썬 버전에 깔린 경우</strong>다. 여러 버전이 깔린
          PC에서 흔하다. 사전 준비의 <code>파이썬 설치.bat</code> 을 다시 더블클릭하면 된다.</li>
        <li><strong>받는 사람이 없다고 나온다</strong> — 창의 "메일 받을 사람" 칸이 비어 있다.</li>
      </ul>
    </div>

    <div class="criteria-box">
      <p class="criteria-label">AI 쪽에서 막힐 때</p>
      <ul>
        <li><strong>프로그램 창이 아예 안 뜨고 검은 창만 깜빡한다 /
          <code>SyntaxError</code></strong>
          — <strong>AI가 첨부한 파일이 깨진 것이다.</strong> 파일로 만들어지는 과정에서
          <strong>역슬래시(<code>\\</code>)가 전부 사라지는</strong> 일이 있다. 줄바꿈을 뜻하는
          <code>\\n</code> 이 통째로 없어지면서 글자가 두 줄로 찢어지고, 파이썬은 거기서 읽기를
          멈춘다. <strong>실제로 발생한 사례다</strong> — 같은 대화에서 첫 파일은 정상이었고 두 번째
          파일만 깨졌으니, 언제 터질지 모른다고 보면 된다. 코드를 볼 필요 없이 아래를 그대로
          넣으면 된다 —
          <em>"받은 파일을 실행하니 SyntaxError 가 떴어. 파일에서 역슬래시가 전부 사라져서 글자가
          찢어진 것 같아. 코드 안에 역슬래시를 아예 쓰지 않는 방식으로 바꿔줘 — 줄바꿈은
          chr(10), 탭은 chr(9) 로. 그렇게 전체를 통째로 다시 줘."</em>
          각 STEP 프롬프트 맨 끝에 이걸 미리 막는 문장이 들어가 있지만 AI가 무시할 때가 있다.
          <strong>압축을 안 푼 채 실행한 경우와 증상이 똑같으니</strong>, 검은 창 마지막 줄에
          <code>SyntaxError</code> 가 있는지로 구분한다.</li>
        <li><strong>파일을 안 주고 채팅창에 코드만 보여준다</strong> — 이 AI 툴은 질문마다 답하는
          모델이 자동으로 바뀐다. 화면 위쪽에서 <strong>모델을 Gemini 로 바꾼 뒤 같은 프롬프트를
          다시</strong> 넣어본다. 그래도 안 되면 각 STEP 의 <strong>"정답 코드 파일 받기"</strong> 버튼을
          쓴다.</li>
        <li><strong>앞 단계에서 되던 기능이 사라졌다</strong> — AI가 바뀐 부분만 주면서 나머지를
          빠뜨린 것이다. "앞 단계까지 되던 기능을 하나도 빼지 말고 전체를 통째로 다시 줘"라고
          다시 요청한다. (각 프롬프트에 이미 그렇게 적혀 있다)</li>
        <li><strong>새 대화창에서 물어봤더니 엉뚱한 걸 준다</strong> — AI는 앞서 짜준 코드를
          기억하지 못한다. <strong>처음부터 끝까지 같은 대화창에서</strong> 이어 물어봐야 한다.</li>
        <li><strong>받은 파일이 <code>main (2).py</code>, <code>main (3).py</code> 로 쌓인다</strong>
          — 정상이다. 이름을 맞추려 애쓰지 말고 <strong>방금 받은 가장 최신 파일</strong>을 실행한다.
          단 <strong>폴더는 처음 정한 그대로</strong> 쓴다 — 입력해둔 인증키가 프로그램 파일과 같은
          폴더에 저장되기 때문이다.</li>
      </ul>
    </div>

    <div class="criteria-box">
      <p class="criteria-label">사전 준비가 안 될 때</p>
      <ul>
        <li><strong>검은 창이 깜빡하고 바로 닫힌다</strong> — 압축을 안 푼 채 ZIP 안에서 실행한
          경우가 대부분이다. 압축을 먼저 푼다.</li>
        <li><strong>파란 경고창 <code>Windows의 PC 보호</code></strong> —
          <code>추가 정보</code> → <code>실행</code> 을 누르면 된다.</li>
        <li><strong>부품 받기가 인증서 오류로 실패</strong> — 설치 파일이 자동으로 한 번 더
          시도하게 되어 있다. 그래도 안 되면 사전 준비 페이지 맨 아래 「막히면」 안내를 따른다.</li>
        <li><strong>설치 파일 자체가 회사 정책에 막힌다</strong> — 개인이 풀 수 없는 경우가 있다.
          <strong>화면을 캡처해서 강사에게 보여주는 것</strong>이 가장 빠르다.</li>
      </ul>
    </div>

    <div class="callout">
      <p><strong>점검용 파일 두 개</strong> — 실습 폴더의 <code>news-report-bot</code> 안에 있다.
        수집이 왜 안 되는지 프로그램과 따로 확인해볼 때 쓴다.</p>
      <ul style="margin:8px 0 0; padding-left:20px;">
        <li><code>한국뉴스_점검.py</code> — 구글 뉴스가 이 네트워크에서 실제로 되는지,
          그리고 requests 와 urllib 중 무엇이 막히는지 보여준다. 그냥 실행하면 된다.</li>
        <li><code>dart_점검.py</code> — DART 가 왜 0건인지 짚어준다. 파일을 열어 인증키와
          회사 이름을 채운 뒤 실행한다.</li>
      </ul>
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
  var doneCountEl = document.getElementById("doneCount");
  var totalCountEl = document.getElementById("totalCount");
  var fillEl = document.getElementById("progressFill");
  var noteEl = document.getElementById("progressNote");
  var itemCountWordEl = document.getElementById("itemCountWord");
  var tocDoneEl = document.getElementById("tocDone");
  var tocTotalEl = document.getElementById("tocTotal");
  var tocFillEl = document.getElementById("tocFill");
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
    var total = boxes.length;
    var done = boxes.filter(function (b) { return b.checked; }).length;
    totalCountEl.textContent = String(total);
    doneCountEl.textContent = String(done);
    tocTotalEl.textContent = String(total);
    tocDoneEl.textContent = String(done);
    var pct = total ? (done / total) * 100 : 0;
    fillEl.style.width = pct + "%";
    tocFillEl.style.width = pct + "%";
    if (itemCountWordEl) itemCountWordEl.textContent = "6가지";
    noteEl.textContent = done === 0
      ? "체크박스는 이 브라우저에만 저장됩니다 · 아직 시작 전"
      : done === total
        ? "체크박스는 이 브라우저에만 저장됩니다 · 전부 완료, 수고했다"
        : "체크박스는 이 브라우저에만 저장됩니다 · 진행 중";

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

    <div class="progress-card">
      <div class="progress-top">
        <span class="label">전체 진행률</span>
        <span class="stat-value"><span id="doneCount">0</span> / <span id="totalCount">0</span> 완료</span>
      </div>
      <div class="progress-track"><div class="progress-fill" id="progressFill"></div></div>
      <p class="progress-note" id="progressNote">체크박스는 이 브라우저에만 저장됩니다 · 아직 시작 전</p>
    </div>
{PREP_PAGE}
{step_pages_html}
{STUCK_PAGE}

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

print("written:", out_path, len(doc), "chars,", len(ALL_PAGE_IDS), "pages")
