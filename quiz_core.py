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
             "pct": pct(a["score"], a["total"]), "points": points(a["score"], a["total"]),
             "uid": a["uid"], "av": STATE["users"].get(a["uid"], {}).get("avatar")}
            for a in ranking(code)[:n]]


# ================== ПРОХОЖДЕНИЕ ==================
def info(code, uid):
    qz = STATE["quizzes"].get((code or "").upper())
    if not qz or not visible(qz):
        return None
    return {"code": code.upper(), "title": qz["title"], "subject": qz.get("subject", ""),
            "author": qz.get("author", ""), "n": qz["count"], "sec": qz["time"], "max": MAX_POINTS,
            "open": qz.get("open", True), "result": result_of(code.upper(), uid),
            "review": not qz.get("open", True)}


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
    chosen = s["shuf"][s["i"]][choice] if choice is not None and 0 <= choice < len(s["shuf"][s["i"]]) else -1
    att.setdefault("chosen", []).append(chosen)        # для разбора ошибок
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
        qz = STATE["quizzes"].get(code, {})
        st = {"status": "done", "code": code, "title": qz.get("title", ""), "subject": qz.get("subject", ""),
              "result": result_of(code, uid), "top": top(code), "review": not qz.get("open", True)}
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


# ================== РАЗБОР ОШИБОК ==================
def review(uid, code):
    """Разбор доступен только после того, как админ закрыл тест (чтобы ответы не утекли)."""
    code = (code or "").upper()
    qz = STATE["quizzes"].get(code)
    a = STATE["attempts"].get(code, {}).get(str(uid))
    if not qz or not a or not a.get("done"):
        return None, "no_result"
    if qz.get("open", True):
        return None, "open"
    chosen = a.get("chosen", [])
    items = []
    for n, (qi, ok) in enumerate(a["answers"]):
        if qi >= len(qz["questions"]):
            continue
        q = qz["questions"][qi]
        items.append({"q": q["q"], "opts": q["opts"], "right": q["right"], "ok": ok,
                      "chosen": chosen[n] if n < len(chosen) else None})
    return items, None


# ================== ЛИЧНЫЙ ПРОФИЛЬ ==================
LEVELS = [0, 100, 300, 700, 1500]      # опыт (сумма баллов) для уровней


def profile(uid):
    hist = []
    for code, atts in STATE["attempts"].items():
        a = atts.get(str(uid))
        qz = STATE["quizzes"].get(code)
        if not a or not a.get("done") or not qz or not visible(qz):
            continue
        p, n = place_of(code, uid)
        hist.append({"code": code, "title": qz["title"], "subject": qz.get("subject", ""),
                     "pct": pct(a["score"], a["total"]), "points": points(a["score"], a["total"]),
                     "score": a["score"], "total": a["total"], "place": p, "all": n,
                     "date": time.strftime("%d.%m.%Y", time.localtime(a.get("started", 0)))})
    hist.sort(key=lambda h: h["date"][6:] + h["date"][3:5] + h["date"][:2], reverse=True)
    xp = sum(h["points"] for h in hist)
    lvl = max(i for i, v in enumerate(LEVELS) if xp >= v)
    nxt = LEVELS[lvl + 1] if lvl + 1 < len(LEVELS) else None
    subj = {}
    for h in hist:
        s = subj.setdefault(h["subject"] or "—", [0, 0])
        s[0] += h["pct"]
        s[1] += 1
    return {"name": user(uid).get("name"), "uid": str(uid), "av": user(uid).get("avatar"), "xp": xp, "level": lvl, "lvl_from": LEVELS[lvl], "lvl_to": nxt,
            "tests": len(hist), "avg_pct": round(sum(h["pct"] for h in hist) / len(hist)) if hist else 0,
            "avg_points": round(sum(h["points"] for h in hist) / len(hist)) if hist else 0,
            "best": max((h["pct"] for h in hist), default=0),
            "correct": sum(h["score"] for h in hist),
            "subjects": sorted(([k, round(v[0] / v[1]), v[1]] for k, v in subj.items()), key=lambda x: -x[1]),
            "history": hist}


# ================== ПОЛНАЯ СТАТИСТИКА (Excel) ==================
def level_of(xp):
    return max(i for i, v in enumerate(LEVELS) if xp >= v)


def export_data():
    """Все пользователи, все попытки и все тесты — для Excel."""
    per_user = {}
    results = []
    for code, atts in STATE["attempts"].items():
        qz = STATE["quizzes"].get(code)
        if not qz:
            continue
        rows = ranking(code)
        place = {a["uid"]: i for i, a in enumerate(rows, 1)}
        for a in atts.values():
            if not a.get("done"):
                continue
            u = STATE["users"].get(a["uid"], {})
            pc, pt = pct(a["score"], a["total"]), points(a["score"], a["total"])
            results.append([a["name"], "@" + u["username"] if u.get("username") else "", qz["title"],
                            qz.get("subject", ""), pc, pt, a["score"], a["total"], place.get(a["uid"]), len(rows),
                            time.strftime("%d.%m.%Y %H:%M", time.localtime(a.get("started", 0))),
                            round(a["time"]), a.get("left", 0)])
            d = per_user.setdefault(a["uid"], [])
            d.append((pc, pt))
    users = []
    for uid, u in STATE["users"].items():
        d = per_user.get(uid, [])
        xp = sum(x[1] for x in d)
        users.append([u.get("name") or u.get("tg_name") or "", "@" + u["username"] if u.get("username") else "",
                      len(d), round(sum(x[0] for x in d) / len(d)) if d else 0,
                      round(sum(x[1] for x in d) / len(d)) if d else 0, max((x[0] for x in d), default=0),
                      xp, level_of(xp), u.get("first", ""), u.get("last", ""), u.get("lang", ""), uid])
    users.sort(key=lambda r: (-r[6], -r[2]))
    results.sort(key=lambda r: (r[2], -r[4]))
    tests = []
    for code, qz in sorted(STATE["quizzes"].items(), key=lambda x: -x[1].get("created", 0)):
        rows = ranking(code)
        tests.append([qz["title"], qz.get("subject", ""), qz.get("author", ""), len(qz["questions"]), qz["count"],
                      qz["time"], len(rows),
                      round(sum(pct(a["score"], a["total"]) for a in rows) / len(rows)) if rows else 0,
                      {"pending": "на проверке"}.get(qz.get("status"), "открыт" if qz.get("open", True) else "закрыт"),
                      time.strftime("%d.%m.%Y", time.localtime(qz.get("created", 0)))])
    return users, results, tests


def top_users(n=20):
    users, _, _ = export_data()
    return [u for u in users if u[2]][:n]
