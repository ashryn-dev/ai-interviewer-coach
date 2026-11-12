# Scores a finished coding round. No AI call is used, so it never hits an API limit.
# The returned keys match what renderFeedback() in templates/coding.html reads.

from problems import PROBLEMS

LIMIT_SECONDS = 20 * 60


def _int(value, high=10**7):
    try:
        v = int(value)
    except (TypeError, ValueError):
        v = 0
    return max(0, min(high, v))


def _plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def build_feedback(data):
    problem = PROBLEMS.get(data.get("problem", ""))
    title = problem["title"] if problem else "this problem"
    hint_total = len(problem["hints"]) if problem else 3

    total = _int(data.get("total"))
    passed = min(_int(data.get("passed")), total) if total else 0
    status = str(data.get("status", "not_run"))
    runs = _int(data.get("runs"))
    hints = _int(data.get("hints"))
    spoken = _int(data.get("spoken_words"))
    seconds = _int(data.get("seconds"))

    # ---- score (out of 100) ----
    correctness = round(60 * passed / total) if total else 0
    independence = max(0, 15 - 5 * hints)
    if spoken >= 100:
        communication = 15
    elif spoken >= 50:
        communication = 12
    elif spoken >= 20:
        communication = 8
    elif spoken > 0:
        communication = 4
    else:
        communication = 0
    process = (5 if runs >= 1 else 0) + (5 if seconds <= LIMIT_SECONDS else 0)
    score = correctness + independence + communication + process

    # A hire needs a working, efficient solution, whatever else went well.
    if status == "timeout":
        score = min(score, 65)
    if not (total > 0 and passed == total):
        score = min(score, 74)

    if score >= 75:
        verdict, level = "Hire", ""
    elif score >= 55:
        verdict, level = "Borderline", "mid"
    else:
        verdict, level = "Needs work", "low"

    all_passed = total > 0 and passed == total

    # ---- what went well ----
    well = []
    if all_passed:
        well.append(f"Clean result: all {total} tests passed on {title}.")
    elif passed > 0:
        well.append(f"{passed} of {total} tests passed.")
    if hints == 0 and passed > 0:
        well.append("You worked without using any hints.")
    if spoken >= 50:
        well.append(f"You thought aloud: about {spoken} words while coding.")
    if all_passed and runs <= 3:
        well.append(f"You got there in {_plural(runs, 'run')}.")
    if all_passed and seconds <= LIMIT_SECONDS:
        well.append(f"Finished in {seconds // 60}m {seconds % 60:02d}s, inside the 20 minute limit.")
    if not well:
        well.append(f"You started on {title} and put code in front of the interviewer.")

    # ---- what held you back ----
    held = []
    if runs == 0 or status == "not_run":
        held.append("You never ran your code, so none of it was tested. Run it early and often.")
    elif status == "timeout":
        held.append("Your solution timed out on the large test. It probably checks every pair or repeats work.")
    elif status == "compile_error":
        held.append("Your last run had a syntax or name error, so no tests could run.")
    elif status == "error":
        held.append("Your last run could not complete.")
    elif total and passed < total:
        held.append(f"{_plural(total - passed, 'test')} still failing, so some cases or edge cases are not handled.")
    if hints >= 2:
        held.append(f"You used {hints} of {hint_total} hints.")
    if spoken == 0:
        held.append("You said nothing while coding. An interviewer can only score thinking they can hear.")
    elif spoken < 20:
        held.append(f"You said only {spoken} words while coding. Think aloud more.")
    if seconds > LIMIT_SECONDS:
        held.append("You went over the 20 minute limit.")
    if runs >= 6 and not all_passed:
        held.append(f"You ran your code {runs} times. Reason through the failing case before running again.")
    if not held:
        held.append("Nothing major. Next time, state the time and space complexity out loud.")

    # ---- the one thing to fix first ----
    if runs == 0 or status == "not_run":
        fix = "Run your code against the tests before you finish, even when it is incomplete."
    elif status == "compile_error":
        fix = "Fix the error shown in the test panel first. A solution that does not run scores nothing."
    elif status == "timeout":
        fix = "Before coding, say the brute-force idea, its cost, and then a faster approach. Aim for a single pass."
    elif total and passed < total:
        fix = "Take the first failing test, trace it by hand, and handle that case before anything else."
    elif spoken < 20:
        fix = "Explain your approach out loud while you code. Say what you will try, why, and what could break."
    elif hints >= 2:
        fix = "Try the first idea for a few more minutes before opening a hint, and say what you are stuck on."
    else:
        fix = "After it passes, state the time and space complexity and name one edge case you checked."

    return {
        "score": score,
        "verdict": verdict,
        "level": level,
        "went_well": well,
        "held_back": held,
        "fix_first": fix,
        "breakdown": {
            "correctness": correctness,
            "independence": independence,
            "communication": communication,
            "process": process,
        },
    }