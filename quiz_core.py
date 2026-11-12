"""Логика тестов: хранение, попытки, таймер на сервере, рейтинг. Общая для бота и мини-приложения."""
import os
import json
import time
import random
import secrets
import logging

log = logging.getLogger("quiz")
STATE_FILE = os.environ.get("STATE_FILE", "quiz.json")
GRACE = 2          # секунд запаса на задержку сети


def _load():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            st = json.load(f)
    except Exception:
        st = {}
    for k in ("quizzes", "users", "attempts", "sessions"):
        st.setdefault(k, {})
    return st


STATE = _load()


def save():
    try:
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(STATE, f, ensure_ascii=False)
        os.replace(tmp, STATE_FILE)
    except Exception:
        log.exception("Не удалось сохранить")


def user(uid):
    return STATE["users"].setdefault(str(uid), {})


def new_code():
    while True:
        c = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(6))
        if c not in STATE["quizzes"]:
            return c


def add_quiz(qz, owner):
    code = new_code()
    qz.update(open=True, created=time.time(), owner=str(owner))
    STATE["quizzes"][code] = qz
    save()
    return code


# ================== РЕЙТИНГ ==================
def ranking(code):
    rows = [a for a in STATE["attempts"].get(code, {}).values() if a.get("done")]
    rows.sort(key=lambda a: (-a["score"], a["time"]))
    return rows


def place_of(code, uid):
    rows = ranking(code)
    for i, a in enumerate(rows, 1):
        if a["uid"] == str(uid):
            return i, len(rows)
    return None, len(rows)


def result_of(code, uid):
    a = STATE["attempts"].get(code, {}).get(str(uid))
    if not a or not a.get("done"):
        return None
    p, n = place_of(code, uid)
    return {"score": a["score"], "total": a["total"], "time": round(a["time"]), "place": p, "all": n,
            "pct": round(100 * a["score"] / max(a["total"], 1)), "left": a.get("left", 0)}


def top(code, n=10):
    return [{"name": a["name"], "score": a["score"], "total": a["total"], "time": round(a["time"])}
            for a in ranking(code)[:n]]


# ================== ПРОХОЖДЕНИЕ ==================
def info(code, uid):
    qz = STATE["quizzes"].get((code or "").upper())
    if not qz:
        return None
    return {"code": code.upper(), "title": qz["title"], "n": qz["count"], "sec": qz["time"],
            "open": qz.get("open", True), "result": result_of(code.upper(), uid)}


def start(uid, code):
    """Начать попытку. Возвращает код ошибки или None."""
    code = (code or "").upper()
    qz = STATE["quizzes"].get(code)
    if not qz:
        return "no_quiz"
    if not user(uid).get("name"):
        return "no_name"
    if str(uid) in STATE["sessions"]:
        return None                     # уже идёт — просто продолжаем
    if str(uid) in STATE["attempts"].get(code, {}):
        return "done"                   # одна попытка, даже если бросили
    if not qz.get("open", True):
        return "closed"
    order = random.sample(range(len(qz["questions"])), qz["count"])
    shuf = [random.sample(range(len(qz["questions"][i]["opts"])), len(qz["questions"][i]
