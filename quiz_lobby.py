"""Зал ожидания перед тестом: тест начинается, только когда одновременно собралось LOBBY_MIN человек.
Список группы (roster.json) — кто зашёл, кто нет; имена с опечатками сопоставляются со списком."""
import os
import re
import json
import time
import logging
from difflib import SequenceMatcher

import quiz_core as C
import quiz_web as W

log = logging.getLogger("quiz-lobby")
HERE = os.path.dirname(os.path.abspath(__file__))
LOBBY_MIN = int(os.environ.get("LOBBY_MIN", "18"))      # 0 — зал ожидания выключен
ALIVE = 20                                               # сек без отклика — человек вышел из зала
LOBBY = {}                                               # code -> {uid: last_seen}


# ================== список группы и сопоставление имён ==================
def groups():
    try:
        with open(os.path.join(HERE, "roster.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def roster(group=None):
    data = groups()
    if group is None:
        group = next(iter(data), "")
    return (group, data.get(group, [])) if group in data else ("", [])


CYR = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюяўқғҳ",
               ["a", "b", "v", "g", "d", "e", "yo", "j", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                "f", "x", "ts", "ch", "sh", "sh", "", "i", "", "e", "yu", "ya", "o", "q", "g", "h"]))


def norm(s):
    s = (s or "").lower()
    s = "".join(CYR.get(ch, ch) for ch in s)
    s = re.sub(r"[ʻʼ'’`‘]", "", s)
    s = s.replace("kh", "x").replace("h", "x").replace("yy", "y")
    return re.sub(r"[^a-z ]", " ", s).split()


def _sim(a, b):
    return SequenceMatcher(None, a, b).ratio()


def score(typed, full):
    """Насколько введённое имя похоже на имя из списка (0..1). Сравниваем фамилию и имя в любом порядке."""
    t, r = norm(typed), norm(full)[:3]
    if not t or not r:
        return 0.0
    vals = []
    for w in t[:3]:
        vals.append(max(max(_sim(w, x), _sim(w, x[:len(w)]) * 0.97 if len(w) >= 4 else 0) for x in r))
    s = sum(vals) / len(vals)
    if len(t) == 1:
        s *= 0.85                                       # одно слово — менее надёжно
    return s


def exact(typed, full):
    """Имя написано точно как в списке (каждое слово совпадает)?"""
    r = set(re.sub(r"[ʻʼ'’`‘]", "", (full or "").lower()).split())
    t = re.sub(r"[ʻʼ'’`‘]", "", (typed or "").lower()).split()
    return bool(t) and all(w in r for w in t)


def match_all(people, group=None):
    """people: [(uid, имя)] -> {uid: (индекс в списке, оценка)}; каждому из списка — не больше одного человека."""
    _, names = roster(group)
    pairs = sorted(((score(nm, full), uid, i) for uid, nm in people for i, full in enumerate(names)), reverse=True)
    out, used = {}, set()
    for sc, uid, i in pairs:
        if sc < 0.72 or uid in out or i in used:
            continue
        out[uid] = (i, sc)
        used.add(i)
    return out


# ================== зал ожидания ==================
def min_of(qz):
    """Сколько человек нужно для старта: своё число у теста (админ меняет в боте) или общее по умолчанию."""
    try:
        return max(0, int(qz.get("lobby_min", LOBBY_MIN)))
    except (TypeError, ValueError):
        return LOBBY_MIN


def need(qz):
    return min_of(qz) > 0 and C.kind(qz) != "trainer" and qz.get("open", True) and not qz.get("lobby_go")


def alive(code):
    now = time.time()
    room = LOBBY.setdefault(code, {})
    for uid in [u for u, t in room.items() if now - t > ALIVE]:
        room.pop(uid, None)
    return room


def launch(code, by="auto"):
    qz = C.STATE["quizzes"].get(code)
    if qz and not qz.get("lobby_go"):
        qz["lobby_go"] = int(time.time())
        C.save()
        log.info("Тест %s запущен из зала ожидания (%s, человек: %d)", code, by, len(LOBBY.get(code, {})))


def status(uid, code, join=True):
    code = (code or "").upper()
    qz = C.STATE["quizzes"].get(code)
    if not qz or not C.visible(qz) or C.kind(qz) == "trainer":
        return {"ok": False, "error": "no_quiz"}
    if not qz.get("open", True):
        return {"ok": False, "error": "closed"}
    uid = str(uid)
    room = alive(code)
    done = str(uid) in C.STATE["attempts"].get(code, {})
    if join and not done and C.user(uid).get("name"):
        room[uid] = time.time()
    if not qz.get("lobby_go") and len(room) >= min_of(qz) > 0:
        launch(code)
    people = [(u, C.user(u).get("name") or "") for u in room]
    group, names = roster(qz.get("group") or "")
    m = match_all(people, group)
    joined = []
    for u, nm in people:
        i, sc = m.get(u, (None, 0))
        joined.append({"name": nm, "me": u == uid, "roster": names[i] if i is not None else None,
                       "typo": i is not None and not exact(nm, names[i]), "av": C.user(u).get("avatar"), "uid": u})
    joined.sort(key=lambda x: (x["roster"] is None, x["roster"] or x["name"]))
    got = {i for i, _ in m.values()}
    # кто уже начал тест (после запуска) — тоже «зашёл»
    started = [(u, a.get("name", "")) for u, a in C.STATE["attempts"].get(code, {}).items() if u not in room]
    ms = match_all(started, group) if started else {}
    got |= {i for i, _ in ms.values()}
    return {"ok": True, "code": code, "title": qz["title"], "need": min_of(qz), "n": len(room), "go": bool(qz.get("lobby_go")) or not min_of(qz),
            "group": group, "joined": joined, "missing": [nm for i, nm in enumerate(names) if i not in got],
            "started": len(started), "me_in": uid in room, "done": done, "admin": W.is_admin_uid(uid)}


# ================== тесты только для группы ==================
def member(uid, group):
    """Студент из этой группы? Узнаём по имени и фамилии (опечатки допускаются)."""
    if W.is_admin_uid(uid):
        return True
    _, names = roster(group)
    nm = C.user(uid).get("name") or ""
    return bool(nm and names) and max(score(nm, full) for full in names) >= 0.72


def closed_to(uid, qz):
    """Тест открыт только для группы, а этот человек не из неё. После закрытия теста — доступен всем."""
    g = qz.get("group")
    return bool(g) and C.kind(qz) != "trainer" and qz.get("open", True) and not member(uid, g)


if not C.STATE.get("grp_v1"):                       # тесты, открытые сейчас, — только для MMT-403/26
    _g = next(iter(groups()), "")
    for _qz in C.STATE["quizzes"].values():
        if _g and C.kind(_qz) != "trainer" and _qz.get("open", True) and _qz.get("status", "approved") == "approved":
            _qz.setdefault("group", _g)
    C.STATE["grp_v1"] = True
    C.save()


# ================== API ==================
_prev_handle = W.handle


def _blocked(user, code):
    qz = C.STATE["quizzes"].get(str(code or "").upper())
    return qz.get("group") if qz and closed_to(str(user["id"]), qz) else None


def handle(method, path, query, body, user):
    if user:
        code = query.get("code") or query.get("q") if method == "GET" else body.get("code")
        if path in ("/api/quiz", "/api/start", "/api/lobby", "/api/lobby/go") and code:
            g = _blocked(user, code)
            if g:
                return {"ok": False, "error": "group", "group": g}
    if user and path.startswith("/api/lobby"):
        uid = str(user["id"])
        if path == "/api/lobby":
            return status(uid, query.get("code"), join=query.get("watch") != "1")
        if path == "/api/lobby/leave" and method == "POST":
            LOBBY.get(str(body.get("code", "")).upper(), {}).pop(uid, None)
            return {"ok": True}
        if path == "/api/lobby/go" and method == "POST":
            if not W.is_admin_uid(uid):
                return {"ok": False, "error": "admin"}
            launch(str(body.get("code", "")).upper(), by="админ")
            return status(uid, body.get("code"))
    if user and path == "/api/start" and method == "POST":
        qz = C.STATE["quizzes"].get(str(body.get("code", "")).upper())
        uid = str(user["id"])
        if qz and need(qz) and not W.is_admin_uid(uid) and uid not in C.STATE["sessions"] \
                and uid not in C.STATE["attempts"].get(str(body.get("code", "")).upper(), {}):
            return {"ok": False, "error": "lobby"}
    r = _prev_handle(method, path, query, body, user)
    if user and isinstance(r, dict) and r.get("ok"):
        uid = str(user["id"])
        if path == "/api/list":
            r["items"] = [q for q in r.get("items") or [] if not (C.STATE["quizzes"].get(q.get("code", "")) and
                                                                  closed_to(uid, C.STATE["quizzes"][q["code"]]))]
        if path == "/api/me" and isinstance(r.get("quiz"), dict) and _blocked(user, r["quiz"].get("code")):
            r["quiz"] = None
    if isinstance(r, dict) and r.get("ok"):
        for q in ([r["quiz"]] if isinstance(r.get("quiz"), dict) else []) + (r.get("items") or [] if path == "/api/list" else []):
            qz = C.STATE["quizzes"].get(q.get("code", ""))
            if qz and isinstance(q, dict) and C.kind(qz) != "trainer":
                q["lobby"] = {"need": min_of(qz), "go": not need(qz), "n": len(alive(q["code"]))}
                q["group"] = qz.get("group") or ""
    return r


W.handle = handle

with open(os.path.join(HERE, "quiz_lobby.js"), encoding="utf-8") as _f:
    W.ADMIN_JS = W.ADMIN_JS + "\n" + _f.read()
