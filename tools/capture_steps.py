"""실습 페이지 STEP 1~5 에 넣을 「그 단계를 마친 화면」 을 찍는다.

    python tools/capture_steps.py 1 2 3        # 메일을 안 보내는 단계만
    python tools/capture_steps.py 1 2 3 4 5    # 4·5 는 실제로 메일이 나간다

news-report-bot/main.py 를 실제로 띄워 버튼 순서대로 기능을 돌리고, 단계가 끝날 때마다
창만 PNG 로 찍어 tools/step-shots/stepN.png 로 저장한다.

  · 인증키는 _lab/dart_key.txt 에서 읽는다. 찍는 순간에만 입력 칸을 ●●● 로 가렸다가 되돌린다
    (공개 페이지에 박히는 그림이라 진짜 키가 찍히면 안 된다).
  · 받는 사람 칸도 찍을 때만 예시 주소로 바꿔 보여준다.
  · 화면을 긁으면(ImageGrab) 사내 워터마크가 같이 찍히므로 capture_window.py 와 같은
    PrintWindow 방식을 쓴다.
"""
import io
import os
import sys
import threading
import time

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
APP = os.path.join(REPO, "news-report-bot", "main.py")
OUT_DIR = os.path.join(HERE, "step-shots")
SETTINGS = os.path.join(REPO, "news-report-bot", "settings.json")
KEY_FILE = os.path.join(REPO, "_lab", "dart_key.txt")

KEYWORDS = "삼성전자, 현대건설"
SHOWN_MAILTO = "example@xicna.com"
MAX_WIDTH = 900

steps = sorted({int(a) for a in sys.argv[1:]}) or [1, 2, 3]
mailto = os.environ.get("CAPTURE_MAILTO", "")   # 4·5 단계에서 실제로 받을 주소
STAGE_DIR = os.path.join(REPO, "news-report-bot", "단계별")
PURPOSE = "영업 · 수주"
if any(4 <= n <= 5 for n in steps) and not mailto:
    sys.exit("4·5 단계는 메일이 실제로 나간다 — CAPTURE_MAILTO 에 받을 주소를 넣고 실행할 것")


def grab(root, path):
    import win32gui, win32ui
    from ctypes import windll
    hwnd = windll.user32.GetParent(root.winfo_id()) or root.winfo_id()
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    w, h = right - left, bottom - top
    wdc = win32gui.GetWindowDC(hwnd)
    src = win32ui.CreateDCFromHandle(wdc)
    mem = src.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(src, w, h)
    mem.SelectObject(bmp)
    windll.user32.PrintWindow(hwnd, mem.GetSafeHdc(), 1)
    info = bmp.GetInfo()
    img = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]),
                           bmp.GetBitmapBits(True), "raw", "BGRX", 0, 1)
    win32gui.DeleteObject(bmp.GetHandle())
    mem.DeleteDC(); src.DeleteDC(); win32gui.ReleaseDC(hwnd, wdc)
    if img.width > MAX_WIDTH:
        img = img.resize((MAX_WIDTH, int(img.height * MAX_WIDTH / img.width)), Image.LANCZOS)
    img.convert("RGB").save(path, "PNG", optimize=True)
    print("저장:", path, img.size, "%.0f KB" % (os.path.getsize(path) / 1024))


def edge_shot(html_path, out):
    """HTML 파일을 엣지로 열어 페이지 전체를 PNG 로. 화면을 긁지 않아 워터마크가 없다."""
    import pathlib
    import subprocess
    from PIL import ImageChops
    edge = os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
                        "Microsoft", "Edge", "Application", "msedge.exe")
    subprocess.run([edge, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--user-data-dir=" + os.path.join(os.environ["TEMP"], "edge-shot"),
                    "--window-size=1100,2400", "--screenshot=" + out,
                    pathlib.Path(html_path).as_uri()], capture_output=True, timeout=90)
    img = Image.open(out).convert("RGB")
    bg = Image.new("RGB", img.size, img.getpixel((img.width - 1, img.height - 1)))
    box = ImageChops.difference(img, bg).getbbox()
    if box:
        img = img.crop((0, 0, img.width, min(img.height, box[3] + 24)))
    img.save(out, "PNG", optimize=True)
    print("저장:", out, img.size)


def main():
    basic = [n for n in steps if n <= 5]
    if basic:
        run_app(APP, basic)
    for n in (6, 7, 8):
        if n in steps:
            run_app(os.path.join(STAGE_DIR, "STEP%d.py" % n), [n])
    if 8 in steps:
        import glob
        reports = sorted(glob.glob(os.path.join(STAGE_DIR, "이슈리포트_*.html")),
                         key=os.path.getmtime)
        edge_shot(reports[-1], os.path.join(OUT_DIR, "step8-report.png"))


def run_app(app, shots):
    os.makedirs(OUT_DIR, exist_ok=True)
    key = io.open(KEY_FILE, encoding="utf-8").read().strip()

    stashed = None
    if os.path.exists(SETTINGS):
        with open(SETTINGS, "rb") as f:
            stashed = f.read()

    src = io.open(app, encoding="utf-8").read()
    src = src.replace("root.mainloop()", "__capture_hook__()\nroot.mainloop()")
    ns = {"__name__": "__main__", "__file__": app}

    def hook():
        root = ns["root"]
        root.attributes("-topmost", True)
        kw, to, key_entry = ns["kw_entry"], ns["to_entry"], ns["key_entry"]

        def set_entry(e, text):
            e.delete(0, "end"); e.insert(0, text)

        set_entry(kw, KEYWORDS)
        set_entry(to, mailto or SHOWN_MAILTO)
        set_entry(key_entry, key)
        if "purpose_box" in ns:               # 알파 실습 — 목적을 고르면 관심 키워드가 채워진다
            ns["purpose_box"].set(PURPOSE)
            ns["apply_purpose"]()

        def shoot(n):
            done = threading.Event()

            def do():
                real_to = to.get()
                set_entry(key_entry, "●" * 16)
                set_entry(to, SHOWN_MAILTO)
                root.update()
                grab(root, os.path.join(OUT_DIR, "step%d.png" % n))
                set_entry(key_entry, key)
                set_entry(to, real_to)
                done.set()
            time.sleep(1.5)            # 결과 칸·진행 상황이 다 그려질 때까지
            root.after(0, do)
            done.wait()

        def work():
            import pythoncom          # 아웃룩(COM)은 부르는 스레드마다 초기화해야 한다
            pythoncom.CoInitialize()
            if shots[0] >= 6:
                # 알파 실습은 뉴스·DART 를 모은 화면을 찍는다. STEP 8 은 보고서까지 만든다.
                ns["collect_news"]()
                ns["collect_dart"]()
                if shots[0] == 8:
                    ns["save_report"]()
                else:
                    shoot(shots[0])
                root.after(0, root.destroy)
                return
            actions = {1: "collect_news", 2: "collect_dart", 3: "save_report",
                       4: "send_mail", 5: "run_all"}
            for n in range(1, max(shots) + 1):
                if n == 5:
                    # 전체 실행은 결과 칸을 비운 상태에서 처음부터 다시 돈다
                    ns["COLLECTED"].clear()
                ns[actions[n]]()
                if n in shots:
                    shoot(n)
            root.after(0, root.destroy)

        threading.Thread(target=work, daemon=True).start()

    ns["__capture_hook__"] = hook
    try:
        exec(compile(src, app, "exec"), ns)
    finally:
        if stashed is not None:
            with open(SETTINGS, "wb") as f:
                f.write(stashed)
        elif os.path.exists(SETTINGS):
            os.remove(SETTINGS)


if __name__ == "__main__":
    main()
