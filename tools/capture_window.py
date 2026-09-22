"""실습 페이지 STEP 0 에 넣을 프로그램 창 그림을 찍는다.

    python tools/capture_window.py && python tools/build_page.py

main.py 의 창 구성을 바꿨으면 이걸 다시 돌려야 페이지 그림도 맞는다
(check_page.py 가 그림과 png 파일이 어긋나면 잡아준다).

news-report-bot/main.py 를 실제로 띄워서 창 영역만 잘라 PNG 로 저장한다.
STEP 0 의 결과물(빈 틀)을 보여주는 것이 목적이라 값은 채우지 않는다.
"""
import io
import os
import runpy
import sys
import time
import tkinter as tk

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
APP = os.path.join(REPO, "news-report-bot", "main.py")
OUT = os.path.join(HERE, "program-window.png")
MAX_WIDTH = 900          # 페이지에 박을 때 이 정도면 충분하다

# 저장해둔 설정이 있으면 입력 칸이 채워진 채로 찍힌다 — 빈 틀을 찍으려고 잠시 치운다.
settings = os.path.join(REPO, "news-report-bot", "settings.json")
stashed = None
if os.path.exists(settings):
    with open(settings, "rb") as f:
        stashed = f.read()
    os.remove(settings)

_orig_mainloop = tk.Misc.mainloop


def fake_mainloop(self, *a, **k):
    root = self.winfo_toplevel()
    root.attributes("-topmost", True)     # 다른 창에 가리지 않게
    root.lift()
    root.update()
    time.sleep(1.2)                        # 글꼴·위젯이 다 그려질 때까지
    root.update()

    # 화면을 긁으면(ImageGrab) 사내 보안 워터마크(이름/소속/IP)까지 같이 찍힌다.
    # 창 핸들에 대고 PrintWindow 를 쓰면 창이 스스로 그린 픽셀만 받아 워터마크가 빠진다.
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
    windll.user32.PrintWindow(hwnd, mem.GetSafeHdc(), 1)   # 1 = 클라이언트 영역만
    info = bmp.GetInfo()
    img = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]),
                           bmp.GetBitmapBits(True), "raw", "BGRX", 0, 1)
    win32gui.DeleteObject(bmp.GetHandle())
    mem.DeleteDC(); src.DeleteDC(); win32gui.ReleaseDC(hwnd, wdc)
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        img = img.resize((MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)
    img.convert("RGB").save(OUT, "PNG", optimize=True)
    print("저장:", OUT, img.size, "%.0f KB" % (os.path.getsize(OUT) / 1024))
    root.destroy()


tk.Misc.mainloop = fake_mainloop
tk.Tk.mainloop = fake_mainloop

try:
    runpy.run_path(APP, run_name="__main__")
except SystemExit:
    pass
finally:
    # 실습용으로 저장돼 있던 설정을 되돌려 놓는다
    if stashed is not None:
        with open(settings, "wb") as f:
            f.write(stashed)
    # 캡처 과정에서 새로 생긴 빈 설정 파일은 치운다
    if stashed is None and os.path.exists(settings):
        os.remove(settings)
