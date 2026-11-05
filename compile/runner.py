"""Runs submitted code against one or more inputs.

On Vercel, every call gets its own Vercel Sandbox: a Firecracker microVM (Arch Linux image with
g++ and python3, 1 vCPU, no network access) that compiles the code once, runs it on every input
with a per-test time limit, and is destroyed afterwards. Anywhere else (local runs, the Docker
image) it falls back to g++ / python in a temporary folder, as before.
"""
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

TIME_LIMIT = 5          # seconds per test case
COMPILE_LIMIT = 30      # seconds for g++
MAX_OUTPUT = 64 * 1024  # characters kept per stream
SANDBOX_IMAGE = os.environ.get("JUDGE_SANDBOX_IMAGE", "vercel/sandbox/arch")
LANGUAGES = ("cpp", "py")

# Runs inside the sandbox: executes the program once per input file and prints the results as JSON,
# so a whole test suite costs one round trip.
DRIVER = r'''
import json, subprocess, sys
lang, n, tl, cap = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
cmd = ["/tmp/judge/main"] if lang == "cpp" else ["python3", "/tmp/judge/main.py"]
res = []
for i in range(n):
    with open(f"/tmp/judge/in{i}.txt", "rb") as f:
        try:
            p = subprocess.run(cmd, stdin=f, capture_output=True, timeout=tl)
            res.append({"out": p.stdout.decode(errors="replace")[:cap],
                        "err": p.stderr.decode(errors="replace")[:cap], "tle": False})
        except subprocess.TimeoutExpired:
            res.append({"out": "", "err": "", "tle": True})
print(json.dumps(res))
'''


@dataclass
class RunResult:
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


def use_sandbox():
    return os.environ.get("VERCEL") == "1" or os.environ.get("JUDGE_USE_SANDBOX") == "1"


def run_many(language, code, inputs):
    """Run `code` once per input. Returns one RunResult per input, in order."""
    inputs = [(i or "").replace("\r\n", "\n") for i in inputs]
    if language not in LANGUAGES:
        return [RunResult(stderr=f"Unsupported language: {language}") for _ in inputs]
    if not inputs:
        return []
    try:
        if use_sandbox():
            return _run_in_sandbox(language, code, inputs)
        return _run_locally(language, code, inputs)
    except Exception as e:  # runner unavailable (quota, network, ...): report it, don't crash the page
        return [RunResult(stderr=f"Error: the code runner is unavailable right now ({e})") for _ in inputs]


def _run_in_sandbox(language, code, inputs):
    from vercel.sandbox import NetworkPolicy, SandboxResources
    from vercel.sandbox import sync as sandbox

    box = sandbox.create_sandbox(
        image=SANDBOX_IMAGE,
        network_policy=NetworkPolicy.deny_all(),
        resources=SandboxResources(vcpus=1),
        execution_time_limit=120,
        persistent=False,
        tags={"app": "royscode"},
    )
    try:
        with box.fs.batch(cwd="/tmp/judge") as batch:
            batch.write_text("main.cpp" if language == "cpp" else "main.py", code)
            batch.write_text("driver.py", DRIVER)
            for i, text in enumerate(inputs):
                batch.write_text(f"in{i}.txt", text)
        if language == "cpp":
            c = box.run_command("g++", ["-O2", "-o", "/tmp/judge/main", "/tmp/judge/main.cpp"],
                                capture_output=True, kill_after=COMPILE_LIMIT)
            if c.returncode != 0:
                return [RunResult(stderr=(c.stderr or "Compilation failed")[:MAX_OUTPUT]) for _ in inputs]
        p = box.run_command("python3", ["/tmp/judge/driver.py", language, str(len(inputs)),
                                        str(TIME_LIMIT), str(MAX_OUTPUT)],
                            capture_output=True, kill_after=TIME_LIMIT * len(inputs) + 30)
        if p.returncode != 0:
            raise RuntimeError((p.stderr or "driver failed").strip()[-300:])
        return [RunResult(r["out"], r["err"], r["tle"]) for r in json.loads(p.stdout)]
    finally:
        try:
            box.stop()
            box.destroy()
        except Exception:
            pass


def _run_locally(language, code, inputs):
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        if language == "cpp":
            src, exe = tmp / "main.cpp", tmp / "main"
            src.write_text(code, encoding="utf-8")
            c = subprocess.run(["g++", "-O2", str(src), "-o", str(exe)],
                               capture_output=True, text=True, timeout=COMPILE_LIMIT)
            if c.returncode != 0:
                return [RunResult(stderr=c.stderr[:MAX_OUTPUT]) for _ in inputs]
            cmd = [str(exe)]
        else:
            src = tmp / "main.py"
            src.write_text(code, encoding="utf-8")
            cmd = [sys.executable, str(src)]
        for text in inputs:
            try:
                p = subprocess.run(cmd, input=text, capture_output=True, text=True, timeout=TIME_LIMIT)
                results.append(RunResult(p.stdout[:MAX_OUTPUT], p.stderr[:MAX_OUTPUT]))
            except subprocess.TimeoutExpired:
                results.append(RunResult(timed_out=True))
    return results
