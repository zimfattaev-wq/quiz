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
MAX_POINTS = 50    # максимальный балл


def _load():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            st = json.load(f)
    except Exception:
        st = {}
    for k in ("quizzes", "users", "attempts", "sessions", "admins"):
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


def today():
    return time.strftime("%Y-%m-%d")


def touch(uid, username="", first=""):
    """Учёт пользователей: когда пришёл впервые и когда был последний раз."""
    u = user(uid)
    d = today()
    changed = False
    if "first" not in u:
        u["first"], changed = d, True
    if u.get("last") != d:
        u["last"], changed = d, True
    if username and u.get("username") != username:
        u["username"], changed = username, True
    if first and not u.get("tg_name"):
        u["tg_name"], changed = first, True
    if changed:
        save()


def add_quiz(qz, owner, author="", approved=True):
    code = new_code()
    qz.update(open=approved, created=time.time(), owner=str(owner), author=author,
              status="approved" if approved else "pending")
    qz.setdefault("subject", "")
    STATE["quizzes"][code] = qz
    save()
    return code


def visible(qz):
    return qz.get("status", "approved") == "approved"


def points(score, total):
    return round(MAX_POINTS * score / max(total, 1))


def pct(score, total):
    return round(100 * score / max(total, 1))


# ================== РЕЙТИНГ ==================
def ranking(code):
    rows = [a for a in STATE["attempts"].get(code, {}).values() if a.get("done")]
    rows.sort(key=lambda a: (-a["score"] / max(a["total"], 1), a["time"]))
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
            "pct": pct(a["score"], a["total"]), "points": points(a["score"], a["total"]),
            "max": MAX_POINTS, "left": a.get("left", 0)}


def top(code, n=10):
    return [{"name": a["name"], "score": a["score"], "total": a["total"], "time": round(a["time"]),
             "pct": pct(a["score"], a["total"]), "points": points(a["score"], a["total"])}
            for a in ranking(code)[:n]]


# ================== ПРОХОЖДЕНИЕ ==================
def info(code, uid):
    qz = STATE["quizzes"].get((code or "").upper())
    if not qz or not visible(qz):
        return None
    return {"code": code.upper(), "title": qz["title"], "subject": qz.get("subject", ""),
            "author": qz.get("author", ""), "n": qz["count"], "sec": qz["time"], "max": MAX_POINTS,
            "open": qz.get("open", True), "result": result_of(code.upper(), uid)}


def start(uid, code):
    """Начать попытку. Возвращает код ошибки или None."""
    code = (code or "").upper()
    qz = STATE["quizzes"].get(code)
    if not qz or not visible(qz):
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
    shuf = []
    for i in order:
        n = len(qz["questions"][i]["opts"])
        shuf.append(random.sample(range(n), n))
    STATE["attempts"].setdefault(code, {})[str(uid)] = {
        "uid": str(uid), "name": user(uid)["name"], "score": 0, "total": qz["count"], "time": 0.0,
        "done": False, "started": time.time(), "answers": [], "left": 0}
    STATE["sessions"][str(uid)] = {"code": code, "order": order, "shuf": shuf, "i": 0, "sent": None}
    save()
    return None


def _record(uid, choice, how="answer"):
    s = STATE["sessions"][str(uid)]
    qz = STATE["quizzes"][s["code"]]
    att = STATE["attempts"][s["code"]][str(uid)]
    q_idx = s["order"][s["i"]]
    spent = min(time.time() - (s["sent"] or time.time()), qz["time"])
    ok = False
    if choice is not None and 0 <= choice < len(s["shuf"][s["i"]]):
        ok = s["shuf"][s["i"]][choice] == qz["questions"][q_idx]["right"]
    att["score"] += int(ok)
    att["time"] += spent
    att["answers"].append([q_idx, int(ok)])
    if how == "leave":
        att["left"] = att.get("left", 0) + 1
    s["i"] += 1
    s["sent"] = None
    if s["i"] >= len(s["order"]):
        att["done"] = True
        STATE["sessions"].pop(str(uid), None)
    save()


def _expire(uid):
    """Засчитать как неверные все вопросы, время которых вышло (таймер считается на сервере)."""
    while True:
        s = STATE["sessions"].get(str(uid))
        if not s or not s["sent"]:
            return
        qz = STATE["quizzes"].get(s["code"])
        if not qz:
            STATE["sessions"].pop(str(uid), None)
            return
        if time.time() - s["sent"] <= qz["time"] + GRACE:
            return
        _record(uid, None, "timeout")


def state(uid):
    """Текущее состояние для мини-приложения (без правильных ответов!)."""
    _expire(uid)
    s = STATE["sessions"].get(str(uid))
    if not s:
        return {"status": "idle"}
    qz = STATE["quizzes"][s["code"]]
    if not s["sent"]:
        s["sent"] = time.time()
        save()
    q = qz["questions"][s["order"][s["i"]]]
    left = max(0, qz["time"] - (time.time() - s["sent"]))
    return {"status": "question", "code": s["code"], "title": qz["title"], "i": s["i"], "n": len(s["order"]),
            "sec": qz["time"], "left": round(left, 1), "text": q["q"],
            "opts": [q["opts"][j] for j in s["shuf"][s["i"]]]}


def answer(uid, i, k):
    _expire(uid)
    s = STATE["sessions"].get(str(uid))
    if s and s["i"] == i and s["sent"]:
        _record(uid, k)
    return after(uid, s["code"] if s else None)


def leave(uid):
    """Студент свернул приложение во время вопроса — вопрос сгорает."""
    _expire(uid)
    s = STATE["sessions"].get(str(uid))
    if s and s["sent"]:
        _record(uid, None, "leave")
    return after(uid, s["code"] if s else None)


def after(uid, code):
    st = state(uid)
    if st["status"] == "idle" and code:
        st = {"status": "done", "code": code, "title": STATE["quizzes"].get(code, {}).get("title", ""),
              "result": result_of(code, uid), "top": top(code)}
    return st


# ================== СТАТИСТИКА БОТА ==================
def bot_stats():
    from collections import Counter
    d = today()
    week = time.strftime("%Y-%m-%d", time.localtime(time.time() - 6 * 86400))
    users = STATE["users"].values()
    qs = STATE["quizzes"]
    done = [a for atts in STATE["attempts"].values() for a in atts.values() if a.get("done")]
    done_today = [a for a in done if time.strftime("%Y-%m-%d", time.localtime(a.get("started", 0))) == d]
    subj = Counter((q.get("subject") or "—") for q in qs.values() if visible(q))
    popular = sorted(((len(ranking(c)), q["title"]) for c, q in qs.items() if visible(q)), reverse=True)[:5]
    return {
        "users": len(STATE["users"]),
        "with_name": sum(1 for u in users if u.get("name")),
        "active_today": sum(1 for u in users if u.get("last") == d),
        "active_week": sum(1 for u in users if u.get("last", "") >= week),
        "new_today": sum(1 for u in users if u.get("first") == d),
        "new_week": sum(1 for u in users if u.get("first", "") >= week),
        "tests": sum(1 for q in qs.values() if visible(q)),
        "open": sum(1 for q in qs.values() if visible(q) and q.get("open", True)),
        "pending": sum(1 for q in qs.values() if q.get("status") == "pending"),
        "attempts": len(done), "attempts_today": len(done_today),
        "avg_pct": round(sum(pct(a["score"], a["total"]) for a in done) / len(done)) if done else 0,
        "in_progress": len(STATE["sessions"]),
        "subjects": subj.most_common(5), "popular": popular,
        "langs": Counter(u.get("lang", "—") for u in users),
    }
