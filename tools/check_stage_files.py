"""단계별 정답 파일이 실제로 열리고 단계에 맞게 동작하는지 확인한다.

    python tools/make_stage_files.py && python tools/check_stage_files.py

파일마다 창을 실제로 띄워서
  · 창이 열리는지 (문법만 맞고 실행이 안 되는 경우를 잡는다)
  · 입력 칸 3개 / 버튼 5개 / 결과 칸 3개가 다 있는지
  · 그 단계까지 연결된 버튼은 일을 하고, 아직인 버튼은 안내만 내는지
를 본다. 인터넷을 쓰는 버튼은 누르지 않는다 — 여기서 보려는 것은 구조다.
"""

import io
import os
import runpy
import sys
import time
import tkinter as tk

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
STAGE_DIR = os.path.join(REPO, "news-report-bot", "단계별")

# 단계별로 "아직 준비 중" 안내가 떠야 하는 버튼
PENDING = {
    0: ["뉴스 수집하기", "DART 수집하기", "보고서 만들기", "메일 보내기", "전체 실행"],
    1: ["DART 수집하기", "보고서 만들기", "메일 보내기", "전체 실행"],
    2: ["보고서 만들기", "메일 보내기", "전체 실행"],
    3: ["메일 보내기", "전체 실행"],
    4: ["전체 실행"],
    5: [],
}
# 그 단계에서 눌러도 인터넷을 쓰지 않는 버튼 (안전하게 눌러볼 수 있다)
SAFE_CLICK = {0: "뉴스 수집하기", 1: "DART 수집하기", 2: "보고서 만들기",
              3: "메일 보내기", 4: "전체 실행", 5: None}

problems = []


def walk(w, out=None):
    out = [] if out is None else out
    out.append(w)
    for c in w.winfo_children():
        walk(c, out)
    return out


def run_stage(stage):
    path = os.path.join(STAGE_DIR, "STEP%d.py" % stage)
    result = {}

    orig = tk.Misc.mainloop

    def fake(self, *a, **k):
        # 진짜 mainloop 을 돌려야 한다. update() 로만 돌리면 프로그램이 뒤에서
        # 돌리는 작업(스레드)이 창을 건드릴 때 "main thread is not in main loop"
        # 로 죽어서, 멀쩡한 파일도 실패로 보인다.
        root = self.winfo_toplevel()
        ws = walk(root)
        btns = [w for w in ws if isinstance(w, tk.Button)]
        texts = [w for w in ws if isinstance(w, tk.Text)]
        result["entries"] = len([w for w in ws if isinstance(w, tk.Entry)])
        result["buttons"] = [str(b.cget("text")) for b in btns]
        result["boxes"] = len(texts)

        def finish():
            result["log"] = texts[-1].get("1.0", "end-1c") if texts else ""
            root.quit()

        def drive():
            want = SAFE_CLICK[stage]
            target = next((b for b in btns if str(b.cget("text")) == want), None) if want else None
            if target:
                target.invoke()
                root.after(1500, finish)
            else:
                finish()

        root.after(200, drive)
        orig(root)
        try:
            root.destroy()
        except tk.TclError:
            pass

    tk.Misc.mainloop = fake
    tk.Tk.mainloop = fake
    try:
        runpy.run_path(path, run_name="__main__")
    except Exception as ex:
        problems.append("STEP%d 실행 실패: %s: %s" % (stage, type(ex).__name__, ex))
        return None
    finally:
        tk.Misc.mainloop = orig
        tk.Tk.mainloop = orig
    return result


def main():
    if not os.path.isdir(STAGE_DIR):
        print("단계별 폴더가 없다 — tools/make_stage_files.py 를 먼저 실행할 것")
        return 1

    for stage in range(6):
        r = run_stage(stage)
        if r is None:
            continue
        label = "STEP%d" % stage
        if r["entries"] != 3:
            problems.append("%s 입력 칸이 %d개다 (기대 3)" % (label, r["entries"]))
        if len(r["buttons"]) != 5:
            problems.append("%s 버튼이 %d개다 (기대 5)" % (label, len(r["buttons"])))
        if r["boxes"] != 3:
            problems.append("%s 결과 칸이 %d개다 (기대 3)" % (label, r["boxes"]))

        note = r.get("log", "")
        want = SAFE_CLICK[stage]
        if want and want in PENDING[stage]:
            if "아직 준비 중" not in note:
                problems.append("%s: 아직 안 붙인 「%s」 를 눌렀는데 안내가 없다" % (label, want))
        elif want:
            if "아직 준비 중" in note:
                problems.append("%s: 이미 붙인 「%s」 가 준비 중이라고 한다" % (label, want))

        pend = ", ".join(PENDING[stage]) or "없음"
        print("  %s  입력 %d · 버튼 %d · 결과칸 %d  | 준비 중: %s"
              % (label, r["entries"], len(r["buttons"]), r["boxes"], pend))

    src = io.open(os.path.join(REPO, "news-report-bot", "main.py"), encoding="utf-8").read()
    last = io.open(os.path.join(STAGE_DIR, "STEP5.py"), encoding="utf-8").read()
    if src != last:
        problems.append("STEP5.py 가 main.py 와 다르다 — make_stage_files.py 를 다시 실행할 것")

    if problems:
        print("\n문제 %d건" % len(problems))
        for p in problems:
            print("  -", p)
        return 1
    print("\n이상 없음 — 단계별 파일 6개 모두 열리고 단계에 맞게 동작한다")
    return 0


if __name__ == "__main__":
    sys.exit(main())
