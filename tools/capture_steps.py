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
if any(n >= 4 for n in steps) and not mailto:
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


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    key = io.open(KEY_FILE, encoding="utf-8").read().strip()

    stashed = None
    if os.path.exists(SETTINGS):
        with open(SETTINGS, "rb") as f:
            stashed = f.read()

    src = io.open(APP, encoding="utf-8").read()
    src = src.replace("root.mainloop()", "__capture_hook__()\nroot.mainloop()")
    ns = {"__name__": "__main__", "__file__": APP}

    def hook():
        root = ns["root"]
        root.attributes("-topmost", True)
        kw, to, key_entry = ns["kw_entry"], ns["to_entry"], ns["key_entry"]

        def set_entry(e, text):
            e.delete(0, "end"); e.insert(0, text)

        set_entry(kw, KEYWORDS)
        set_entry(to, mailto or SHOWN_MAILTO)
        set_entry(key_entry, key)

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
            actions = {1: "collect_news", 2: "collect_dart", 3: "save_report",
                       4: "send_mail", 5: "run_all"}
            last = max(steps)
            for n in range(1, last + 1):
                if n == 5:
                    # 전체 실행은 결과 칸을 비운 상태에서 처음부터 다시 돈다
                    ns["COLLECTED"].clear()
                ns[actions[n]]()
                if n in steps:
                    shoot(n)
            root.after(0, root.destroy)

        threading.Thread(target=work, daemon=True).start()

    ns["__capture_hook__"] = hook
    try:
        exec(compile(src, APP, "exec"), ns)
    finally:
        if stashed is not None:
            with open(SETTINGS, "wb") as f:
                f.write(stashed)
        elif os.path.exists(SETTINGS):
            os.remove(SETTINGS)


if __name__ == "__main__":
    main()
