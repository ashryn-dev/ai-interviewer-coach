import json
import os
import subprocess
import sys
import tempfile
import time

from problems import PROBLEMS

TIME_LIMIT_SECONDS = 6
VISIBLE_TESTS = 3
MARK = "@@RESULT@@ "

HARNESS = '''
import json, sys

{user_code}

_tests = json.load(open(sys.argv[1]))
try:
    _fn = {fname}
except NameError:
    print("{mark}" + json.dumps({{"fatal": "Function {fname} is not defined. Keep the function name from the starter code."}}), flush=True)
    sys.exit(0)

for _i, (_args, _expected) in enumerate(_tests):
    try:
        _got = _fn(*_args)
        _got = json.loads(json.dumps(_got))
        print("{mark}" + json.dumps({{"i": _i, "got": _got}}), flush=True)
    except Exception as _e:
        print("{mark}" + json.dumps({{"i": _i, "error": type(_e).__name__ + ": " + str(_e)}}), flush=True)
'''


def _same(got, expected, mode):
    if mode == "sorted" and isinstance(got, list) and isinstance(expected, list):
        try:
            return sorted(got) == sorted(expected)
        except TypeError:
            return False
    return got == expected


def _short(value, limit=120):
    text = json.dumps(value)
    return text if len(text) <= limit else text[:limit] + "..."


def run_tests(problem_id, code):
    problem = PROBLEMS.get(problem_id)
    if problem is None:
        return {"status": "error", "message": "Unknown problem.", "passed": 0, "total": 0, "tests": []}

    tests = problem["tests"]
    total = len(tests)
    script = HARNESS.format(user_code=code, fname=problem["function"], mark=MARK)

    with tempfile.TemporaryDirectory() as folder:
        script_path = os.path.join(folder, "solution_run.py")
        tests_path = os.path.join(folder, "tests.json")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)
        with open(tests_path, "w", encoding="utf-8") as f:
            json.dump(tests, f)

        started = time.time()
        timed_out = False
        try:
            proc = subprocess.run(
                [sys.executable, "-I", script_path, tests_path],
                capture_output=True, text=True, timeout=TIME_LIMIT_SECONDS,
                stdin=subprocess.DEVNULL, cwd=folder,
            )
            stdout, stderr = proc.stdout or "", proc.stderr or ""
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            raw = exc.stdout or b""
            stdout = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
            stderr = ""
        seconds = round(time.time() - started, 2)

    outputs = {}
    fatal = None
    for line in stdout.splitlines():
        if line.startswith(MARK):
            try:
                item = json.loads(line[len(MARK):])
            except ValueError:
                continue
            if "fatal" in item:
                fatal = item["fatal"]
            else:
                outputs[item["i"]] = item

    if fatal:
        return {"status": "error", "message": fatal, "passed": 0, "total": total, "tests": [], "seconds": seconds}

    if not outputs and not timed_out and stderr.strip():
        last = stderr.strip().splitlines()[-3:]
        return {"status": "compile_error", "message": "\n".join(last), "passed": 0, "total": total, "tests": [], "seconds": seconds}

    results = []
    passed = 0
    for i, (args, expected) in enumerate(tests):
        visible = i < VISIBLE_TESTS
        item = outputs.get(i)
        entry = {"index": i + 1, "visible": visible, "passed": False}
        if item is None:
            entry["note"] = "Time limit exceeded" if timed_out else "No result"
        elif "error" in item:
            entry["note"] = item["error"]
        elif _same(item["got"], expected, problem["compare"]):
            entry["passed"] = True
            passed += 1
        else:
            entry["note"] = "Wrong answer"
        if visible:
            entry["input"] = _short(args)
            entry["expected"] = _short(expected)
            if item is not None and "got" in item:
                entry["got"] = _short(item["got"])
        results.append(entry)

    status = "timeout" if timed_out else ("passed" if passed == total else "failed")
    message = ""
    if timed_out:
        message = f"Time limit of {TIME_LIMIT_SECONDS} seconds exceeded. Your solution is correct on some inputs but too slow on a large one."
    return {"status": status, "message": message, "passed": passed, "total": total, "tests": results, "seconds": seconds}