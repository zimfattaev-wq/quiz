"""Логика тестов: хранение, попытки, таймер на сервере, рейтинг. Общая для бота и мини-приложения."""
import os
import json
import time
import random
import secrets
import logging

log = logging.getLogger("quiz")
STATE_FILE = os.environ.get("STATE_FILE", "quiz.json")
GRACE = 5          # секунд запаса на задержку сети (мобильный интернет)
MAX_POINTS = 50    # максимальный балл


def _load():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            st = json.load(f)
    except Exception:
        st = {}
    for k in ("quizzes", "users", "attempts", "sessions", "admins", "tsess"):
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


def add_quiz(qz, owner, author="", approved=True, kind="test"):
    code = new_code()
    qz.update(open=approved, created=time.time(), owner=str(owner), author=author,
              status="approved" if approved else "pending", kind=kind)
    qz.setdefault("subject", "")
    STATE["quizzes"][code] = qz
    save()
    return code


def visible(qz):
    return qz.get("status", "approved") == "approved"


def kind(qz):
    """test — тест для всех с рейтингом (1 попытка); trainer — тренажёр (сколько угодно раз)."""
    return "trainer" if qz.get("kind") == "trainer" else "test"


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
    tr = kind(qz) == "trainer"
    return {"code": code.upper(), "title": qz["title"], "subject": qz.get("subject", ""),
            "author": qz.get("author", ""), "n": qz["count"], "sec": qz["time"], "max": MAX_POINTS,
            "open": qz.get("open", True), "kind": kind(qz),
            "result": None if tr else result_of(code.upper(), uid),
            "train": user(uid).get("train", {}).get(code.upper()) if tr else None,
            "review": not qz.get("open", True)}


def start(uid, code):
    """Начать попытку. Возвращает код ошибки или None."""
    code = (code or "").upper()
    qz = STATE["quizzes"].get(code)
    if not qz or not visible(qz):
        return "no_quiz"
    if kind(qz) == "trainer":
        return "trainer"
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
    """Повторный запрос (если ответ «потерялся» в сети) не засчитывается дважды — сверяем номер вопроса."""
    _expire(uid)
    s = STATE["sessions"].get(str(uid))
    if s and s["i"] == i and s["sent"]:
        _record(uid, k if k >= 0 else None, "answer" if k >= 0 else "timeout")
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
        "tests": sum(1 for q in qs.values() if visible(q) and kind(q) == "test"),
        "trainers": sum(1 for q in qs.values() if visible(q) and kind(q) == "trainer"),
        "train_runs": sum(r.get("runs", 0) for u in users for r in u.get("train", {}).values()),
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
            "history": hist, "trainers": trainers_of(uid)}


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
        tests.append([qz["title"], "Тренажёр" if kind(qz) == "trainer" else "Тест", qz.get("subject", ""), qz.get("author", ""), len(qz["questions"]), qz["count"],
                      qz["time"], len(rows),
                      round(sum(pct(a["score"], a["total"]) for a in rows) / len(rows)) if rows else 0,
                      {"pending": "на проверке"}.get(qz.get("status"), "открыт" if qz.get("open", True) else "закрыт"),
                      time.strftime("%d.%m.%Y", time.localtime(qz.get("created", 0)))])
    return users, results, tests


def top_users(n=20):
    users, _, _ = export_data()
    return [u for u in users if u[2]][:n]


# ================== ТРЕНАЖЁР ==================
# Сколько угодно попыток, после каждого ответа сразу видно правильно/неправильно.
# Таймер и защита от сворачивания — как в тестах. В рейтинг и опыт не идёт.
# Режимы по предмету (весь банк тренажёров с этим предметом):
#   mist — работа над ошибками (последний ответ неверный), hard — трудные, fav — избранное,
#   rand — случайные (сначала нерешённые), exam — пробный экзамен (ответы в конце, общий таймер),
#   retry — работа над ошибками последней попытки.
import hashlib as _hl

MODES = ("t", "mist", "hard", "fav", "rand", "exam", "retry")
NO_SUBJ = "—"


def qid(q):
    """Один и тот же вопрос в разных тренажёрах = один id (статистика и избранное общие)."""
    return _hl.sha1((q["q"].strip().lower() + "|" + q["opts"][q["right"]].strip().lower()).encode()).hexdigest()[:12]


def subj_of(qz):
    return (qz.get("subject") or "").strip() or NO_SUBJ


def trainer_quizzes(subject=None):
    out = [(c, q) for c, q in STATE["quizzes"].items()
           if visible(q) and kind(q) == "trainer" and q.get("open", True)]
    if subject is not None:
        out = [(c, q) for c, q in out if subj_of(q) == subject]
    return sorted(out, key=lambda x: -x[1].get("created", 0))


def bank(subject):
    """Все вопросы предмета без повторов: qid -> [code, index]."""
    b = {}
    for code, qz in trainer_quizzes(subject):
        for i, q in enumerate(qz["questions"]):
            b.setdefault(qid(q), [code, i])
    return b


def _qst(uid):
    return user(uid).setdefault("qs", {})          # qid -> [верно, ошибок, последний(1/0), секунд, замеров]


def subjects(uid):
    st = _qst(uid)
    res = {}
    for code, qz in trainer_quizzes():
        res.setdefault(subj_of(qz), []).append(code)
    out = []
    for name, codes in res.items():
        b = bank(name)
        ok = sum(1 for k in b if k in st and st[k][2] == 1)
        bad = sum(1 for k in b if k in st and st[k][2] == 0)
        out.append({"name": name, "trainers": len(codes), "total": len(b), "ok": ok, "bad": bad})
    out.sort(key=lambda x: (x["name"] == NO_SUBJ, x["name"]))
    return out


def _hard(uid, b, n=30):
    st = _qst(uid)
    ids = [k for k in b if k in st and st[k][1] > 0]
    ids.sort(key=lambda k: (-(st[k][1] / (st[k][0] + st[k][1])), -st[k][1]))
    return ids[:n]


def subject_info(uid, name):
    b = bank(name)
    st = _qst(uid)
    fav = set(user(uid).get("fav", []))
    tr = user(uid).get("train", {})
    items = []
    for code, qz in trainer_quizzes(name):
        items.append({"code": code, "title": qz["title"], "n": min(qz["count"], len(qz["questions"])),
                      "sec": qz["time"], "train": tr.get(code)})
    return {"name": name, "total": len(b),
            "ok": sum(1 for k in b if k in st and st[k][2] == 1),
            "bad": sum(1 for k in b if k in st and st[k][2] == 0),
            "mist": sum(1 for k in b if k in st and st[k][2] == 0),
            "hard": len(_hard(uid, b)), "fav": sum(1 for k in b if k in fav), "trainers": items,
            "sec": items[0]["sec"] if items else 30}


def _new_session(uid, items, mode, title, subject, code="", exam=False, mins=0):
    shuf = []
    for c, i in items:
        n = len(STATE["quizzes"][c]["questions"][i]["opts"])
        shuf.append(random.sample(range(n), n))
    STATE["tsess"][str(uid)] = {"code": code, "items": items, "shuf": shuf, "i": 0, "sent": None, "score": 0,
                                "time": 0.0, "left": 0, "fb": None, "log": [], "mode": mode, "title": title,
                                "subject": subject, "exam": exam, "limit": mins * 60, "start": time.time()}
    save()


def tr_start(uid, code=None, mode="t", subject=None, n=20, mins=0):
    if not user(uid).get("name"):
        return "no_name"
    s = STATE["tsess"].get(str(uid))
    if mode == "t":
        code = (code or "").upper()
        qz = STATE["quizzes"].get(code)
        if not qz or not visible(qz) or kind(qz) != "trainer":
            return "no_quiz"
        if not qz.get("open", True):
            return "closed"
        if s and s.get("code") == code and s.get("mode") == "t" and not s.get("result") and "items" in s:
            return None                                 # уже идёт — продолжаем
        k = min(qz["count"], len(qz["questions"]))
        items = [[code, i] for i in random.sample(range(len(qz["questions"])), k)]
        _new_session(uid, items, "t", qz["title"], subj_of(qz), code=code)
        return None
    if mode == "retry":                                 # ошибки последней попытки
        if not s or not s.get("result"):
            return "empty"
        items = [[c, i] for c, i, ch, ok in s.get("log", []) if not ok and c in STATE["quizzes"]]
        if not items:
            return "empty"
        random.shuffle(items)
        _new_session(uid, items, "retry", s["title"], s.get("subject", ""), code=s.get("code", ""))
        return None
    if mode not in MODES or subject is None:
        return "bad_request"
    b = bank(subject)
    if not b:
        return "no_quiz"
    st = _qst(uid)
    if mode == "mist":
        ids = [k for k in b if k in st and st[k][2] == 0]
        random.shuffle(ids)
    elif mode == "hard":
        ids = _hard(uid, b)
        random.shuffle(ids)
    elif mode == "fav":
        fav = set(user(uid).get("fav", []))
        ids = [k for k in b if k in fav]
        random.shuffle(ids)
    else:                                               # rand / exam: сначала нерешённые, потом ошибки, потом остальное
        n = max(5, min(int(n or 20), 200))
        ids = list(b)
        random.shuffle(ids)
        if mode == "rand":
            ids.sort(key=lambda k: 0 if k not in st else (1 if st[k][2] == 0 else 2))
        ids = ids[:n]
    if not ids:
        return "empty"
    title = {"mist": "Работа над ошибками", "hard": "Трудные вопросы", "fav": "Избранное",
             "rand": "Случайные вопросы", "exam": "Пробный экзамен"}[mode]
    mins = max(0, min(int(mins or 0), 300))
    _new_session(uid, [b[k] for k in ids], mode, title, subject, exam=(mode == "exam"), mins=mins if mode == "exam" else 0)
    return None


def _q_of(s, i):
    c, qi = s["items"][i]
    qz = STATE["quizzes"][c]
    return qz, qz["questions"][qi]


def _tr_record(uid, choice, how="answer"):
    s = STATE["tsess"][str(uid)]
    qz, q = _q_of(s, s["i"])
    sh = s["shuf"][s["i"]]
    valid = choice is not None and 0 <= choice < len(sh)
    ok = valid and sh[choice] == q["right"]
    spent = min(time.time() - (s["sent"] or time.time()), qz["time"] if not s.get("exam") else 600)
    s["score"] += int(ok)
    s["time"] += spent
    if how == "leave":
        s["left"] += 1
    r = _qst(uid).setdefault(qid(q), [0, 0, None, 0, 0])   # общая статистика по вопросу
    r[0 if ok else 1] += 1
    r[2] = 1 if ok else 0
    r[3] = round(r[3] + spent, 1)
    r[4] += 1
    c, qi = s["items"][s["i"]]
    s["log"].append([c, qi, sh[choice] if valid else -1, int(ok)])
    s["fb"] = {"i": s["i"], "ok": bool(ok), "right": sh.index(q["right"]) if q["right"] in sh else -1,
               "chosen": choice if valid else -1, "how": how}
    s["i"] += 1
    s["sent"] = None
    if s["i"] >= len(s["items"]):
        _tr_finish(uid, s)
    save()


def _tr_finish(uid, s):
    total = len(s["items"])
    p = pct(s["score"], total)
    best = runs = None
    if s.get("mode") == "t" and s.get("code"):
        rec = user(uid).setdefault("train", {}).setdefault(s["code"], {"runs": 0, "best": 0, "last": 0})
        rec["runs"] += 1
        rec["best"] = max(rec["best"], p)
        rec["last"] = p
        rec["date"] = time.strftime("%d.%m.%Y")
        best, runs = rec["best"], rec["runs"]
    el = time.time() - s.get("start", time.time())
    h = user(uid).setdefault("thist", [])
    h.append({"title": s["title"], "subject": s.get("subject", ""), "mode": s.get("mode", "t"), "score": s["score"],
              "total": total, "pct": p, "time": round(s["time"] if not s.get("exam") else el), "date": time.strftime("%d.%m.%Y %H:%M")})
    del h[:-40]
    s["result"] = {"score": s["score"], "total": total, "pct": p, "points": points(s["score"], total),
                   "max": MAX_POINTS, "time": round(s["time"] if not s.get("exam") else el), "left": s["left"],
                   "best": best, "runs": runs, "wrong": total - s["score"]}


def _tr_expire(uid):
    while True:
        s = STATE["tsess"].get(str(uid))
        if not s or s.get("result"):
            return
        if "items" not in s:                            # старый формат сессии
            STATE["tsess"].pop(str(uid), None)
            return
        if any(c not in STATE["quizzes"] for c, _ in s["items"][s["i"]:]):
            STATE["tsess"].pop(str(uid), None)
            return
        if s.get("exam"):
            if s.get("limit") and time.time() - s["start"] > s["limit"] + GRACE:
                if not s["sent"]:
                    s["sent"] = time.time()
                _tr_record(uid, None, "timeout")
                continue
            return
        if not s["sent"]:
            return
        qz, _ = _q_of(s, s["i"])
        if time.time() - s["sent"] <= qz["time"] + GRACE:
            return
        _tr_record(uid, None, "timeout")


def tr_items(s):
    out = []
    for c, qi, ch, ok in s.get("log", []):
        qz = STATE["quizzes"].get(c)
        if qz and qi < len(qz["questions"]):
            q = qz["questions"][qi]
            out.append({"q": q["q"], "opts": q["opts"], "right": q["right"], "chosen": ch, "ok": ok})
    return out


def tr_state(uid, peek=False):
    """peek=True — не запускать таймер следующего вопроса (пока студент смотрит, верно или нет)."""
    _tr_expire(uid)
    s = STATE["tsess"].get(str(uid))
    if not s:
        return {"status": "idle"}
    base = {"code": s.get("code", ""), "title": s["title"], "subject": s.get("subject", ""), "mode": s.get("mode", "t")}
    if s.get("result"):
        return {"status": "tdone", **base, "result": s["result"], "fb": s.get("fb"), "items": tr_items(s)}
    if s.get("exam"):
        peek = False                                     # в экзамене ответ не показываем — сразу следующий
    if peek and not s["sent"]:
        return {"status": "tnext", **base, "fb": s.get("fb"), "score": s["score"]}
    if not s["sent"]:
        s["sent"] = time.time()
        save()
    qz, q = _q_of(s, s["i"])
    if s.get("exam"):
        left = round(max(0, s["limit"] - (time.time() - s["start"])), 1) if s.get("limit") else None
        sec, el = s.get("limit", 0), round(time.time() - s["start"])
    else:
        left = round(max(0, qz["time"] - (time.time() - s["sent"])), 1)
        sec, el = qz["time"], 0
    return {"status": "tquestion", **base, "i": s["i"], "n": len(s["items"]), "sec": sec, "left": left,
            "elapsed": el, "exam": bool(s.get("exam")), "text": q["q"],
            "opts": [q["opts"][j] for j in s["shuf"][s["i"]]], "score": s["score"],
            "fav": qid(q) in set(user(uid).get("fav", [])), "fb": None if s.get("exam") else s.get("fb")}


def tr_answer(uid, i, k):
    _tr_expire(uid)
    s = STATE["tsess"].get(str(uid))
    if s and not s.get("result") and s["i"] == i and s["sent"]:
        _tr_record(uid, k if k >= 0 else None, "answer" if k >= 0 else "timeout")
    return tr_state(uid, peek=True)


def tr_leave(uid):
    _tr_expire(uid)
    s = STATE["tsess"].get(str(uid))
    if s and not s.get("result") and s["sent"]:
        _tr_record(uid, None, "leave")
    return tr_state(uid)


def tr_finish_exam(uid):
    """Досрочно завершить экзамен: оставшиеся вопросы — без ответа."""
    s = STATE["tsess"].get(str(uid))
    while s and s.get("exam") and not s.get("result"):
        if not s["sent"]:
            s["sent"] = time.time()
        _tr_record(uid, None, "timeout")
    return tr_state(uid)


def tr_fav(uid, i):
    s = STATE["tsess"].get(str(uid))
    if not s or i >= len(s["items"]):
        return None
    _, q = _q_of(s, i)
    k = qid(q)
    fav = user(uid).setdefault("fav", [])
    if k in fav:
        fav.remove(k)
    else:
        fav.append(k)
    save()
    return k in fav


def tr_stop(uid):
    STATE["tsess"].pop(str(uid), None)
    save()
    return {"status": "idle"}


def cheat(uid, name):
    """Все вопросы предмета с правильными ответами (для подготовки)."""
    fav = set(user(uid).get("fav", []))
    st = _qst(uid)
    out = []
    for k, (c, i) in bank(name).items():
        q = STATE["quizzes"][c]["questions"][i]
        r = st.get(k)
        out.append({"q": q["q"], "a": q["opts"][q["right"]], "fav": k in fav,
                    "st": None if not r else (1 if r[2] == 1 else 0)})
    return out


def tr_stats(uid, name):
    b = bank(name)
    st = _qst(uid)
    inf = subject_info(uid, name)
    get = lambda k: STATE["quizzes"][b[k][0]]["questions"][b[k][1]]
    hard = [{"q": get(k)["q"], "a": get(k)["opts"][get(k)["right"]], "w": st[k][1], "c": st[k][0]}
            for k in _hard(uid, b, 10)]
    slow = sorted([k for k in b if k in st and st[k][4]], key=lambda k: -st[k][3] / st[k][4])[:5]
    slow = [{"q": get(k)["q"], "avg": round(st[k][3] / st[k][4])} for k in slow]
    hist = [h for h in reversed(user(uid).get("thist", [])) if (h.get("subject") or NO_SUBJ) == name][:15]
    done = [x for x in b if x in st]
    return {"name": name, "total": inf["total"], "ok": inf["ok"], "bad": inf["bad"],
            "answers": sum(st[k][0] + st[k][1] for k in done), "right": sum(st[k][0] for k in done),
            "trainers": inf["trainers"], "hist": hist, "hard": hard, "slow": slow}


def trainers_of(uid):
    out = []
    for code, rec in user(uid).get("train", {}).items():
        qz = STATE["quizzes"].get(code)
        if qz and visible(qz):
            out.append({"code": code, "title": qz["title"], "subject": qz.get("subject", ""), **rec})
    out.sort(key=lambda r: -r["runs"])
    return out


# ================== ГОТОВЫЕ ТРЕНАЖЁРЫ ИЗ ФАЙЛА ==================
# seed_trainers.json лежит рядом с ботом. Каждый тренажёр добавляется один раз (по ключу),
# потом им можно управлять как обычным: /quizzes → время, закрыть, удалить.
SEED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed_trainers.json")


def load_seeds():
    try:
        with open(SEED_FILE, encoding="utf-8") as f:
            items = json.load(f)
    except FileNotFoundError:
        return 0
    except Exception:
        log.exception("seed_trainers.json не прочитан")
        return 0
    done = STATE.setdefault("seeded", [])
    by_key = {it["key"]: it for it in items}
    base = time.time()
    added = 0
    for n, it in enumerate(items):
        if it["key"] in done:
            continue
        qs = it.get("questions")
        if qs is None:                                   # «все вопросы» собираются из нескольких тестов
            qs = [q for k in it.get("from", []) for q in by_key.get(k, {}).get("questions", [])]
        if not qs:
            continue
        qz = {"title": it["title"], "subject": it.get("subject", ""), "time": it.get("time", 30),
              "count": min(it.get("count", len(qs)), len(qs)), "questions": [dict(q) for q in qs]}
        code = add_quiz(qz, "seed", "TSUE QUIZ", approved=True, kind="trainer")
        STATE["quizzes"][code]["created"] = base - n          # порядок в списке как в файле
        STATE["quizzes"][code]["seed"] = it["key"]
        done.append(it["key"])
        added += 1
    if added:
        save()
        log.info("Добавлено готовых тренажёров: %d", added)
    return added


load_seeds()
