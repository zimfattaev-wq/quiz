"""TSUE QUIZ v8: тренажёр без защиты от списывания, тренировка закрытых тестов, история,
серия дней 🔥 + напоминание, карточки, жалоба на вопрос, рейтинг недели, прогресс по предмету,
ответ на любой вопрос из банка. Подключается одной строкой в конце quiz_web.py: import quiz_v2"""
import os
import time
import html
import random
import asyncio
import logging
import datetime as dt

import quiz_core as C
import quiz_web as W

log = logging.getLogger("quiz-v2")
TZ = dt.timezone(dt.timedelta(hours=int(os.environ.get("TZ_HOURS", "5"))))   # Ташкент
REMIND_HOUR = int(os.environ.get("REMIND_HOUR", "19"))
_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
WEBAPP_URL = os.environ.get("WEBAPP_URL") or (f"https://{_DOMAIN}" if _DOMAIN else "")
BOT = {"token": "", "tasks": set()}
HIST_MAX, HIST_LOG = 50, 15        # сколько попыток хранить в истории / у скольких последних хранить разбор


def now():
    return dt.datetime.now(TZ)


def day(t=None):
    return (now() if t is None else dt.datetime.fromtimestamp(t, TZ)).strftime("%Y-%m-%d")


def week_key():
    y, w, _ = now().isocalendar()
    return f"{y}-W{w:02d}"


# ================== серия дней ==================
def mark_day(uid):
    u = C.user(uid)
    d = day()
    days = u.setdefault("days", [])
    if not days or days[-1] != d:
        days.append(d)
        del days[:-60]


def streak(u):
    days = set(u.get("days", []))
    cur = now().date()
    if cur.isoformat() not in days:
        cur -= dt.timedelta(days=1)
    n = 0
    while cur.isoformat() in days:
        n += 1
        cur -= dt.timedelta(days=1)
    return n


def streak_info(uid):
    u = C.user(uid)
    days = sorted(set(u.get("days", [])))
    best = run = 0
    prev = None
    for d in days:
        x = dt.date.fromisoformat(d)
        run = run + 1 if prev and (x - prev).days == 1 else 1
        best = max(best, run)
        prev = x
    last14 = [(now().date() - dt.timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
    return {"n": streak(u), "best": best, "today": day() in days, "remind": u.get("remind", True),
            "days": [1 if d in days else 0 for d in last14], "hour": REMIND_HOUR}


# ================== рейтинг недели ==================
def week_add(uid, ok):
    u = C.user(uid)
    k = week_key()
    w = u.get("wk")
    if not w or w.get("k") != k:
        w = u["wk"] = {"k": k, "c": 0, "n": 0}
    w["n"] += 1
    w["c"] += int(bool(ok))


def week_top(uid, n=30):
    k = week_key()
    rows = [(x, u) for x, u in C.STATE["users"].items() if (u.get("wk") or {}).get("k") == k and u["wk"]["n"]]
    rows.sort(key=lambda r: (-r[1]["wk"]["c"], -r[1]["wk"]["n"]))
    out, me = [], None
    for i, (x, u) in enumerate(rows, 1):
        row = {"place": i, "uid": x, "name": u.get("name") or u.get("tg_name") or "—", "av": u.get("avatar"),
               "c": u["wk"]["c"], "n": u["wk"]["n"]}
        if i <= n:
            out.append(row)
        if x == str(uid):
            me = row
    mon = now().date() - dt.timedelta(days=now().weekday())
    return {"items": out, "me": me, "all": len(rows),
            "from": mon.strftime("%d.%m"), "to": (mon + dt.timedelta(days=6)).strftime("%d.%m")}


# ================== обёртки ядра ==================
_SKIP = {"on": False}
_orig_qst = C._qst


def _qst(uid):
    if _SKIP["on"]:
        return {}                                   # тренировка закрытого теста не трогает статистику
    return _orig_qst(uid)


C._qst = _qst

_orig_tr_record = C._tr_record


def _tr_record(uid, choice, how="answer"):
    s = C.STATE["tsess"].get(str(uid))
    if not s:
        return _orig_tr_record(uid, choice, how)
    mode = s.get("mode")
    try:
        _, q = C._q_of(s, s["i"])
        sh = s["shuf"][s["i"]]
        ok = choice is not None and 0 <= choice < len(sh) and sh[choice] == q["right"]
    except Exception:
        ok = False
    mark_day(uid)
    if mode != "prac":
        week_add(uid, ok)
    _SKIP["on"] = mode == "prac"
    try:
        return _orig_tr_record(uid, choice, how)
    finally:
        _SKIP["on"] = False


C._tr_record = _tr_record


def _pos(s):
    p = s.get("pos")
    if not p or len(p) != len(s["items"]):
        p = s["pos"] = list(range(len(s["items"])))
    return p


def _swap(s, i, j):
    if i == j:
        return
    p = _pos(s)
    for k in ("items", "shuf"):
        s[k][i], s[k][j] = s[k][j], s[k][i]
    p[i], p[j] = p[j], p[i]


def _advance(s):
    """После ответа — следующий по номеру нерешённый вопрос (после 49-го идёт 50-й)."""
    i = s["i"]
    if s.get("result") or i == 0 or i >= len(s["items"]):
        return
    p = _pos(s)
    last, rest = p[i - 1], p[i:]
    nxt = min((x for x in rest if x > last), default=min(rest))
    _swap(s, i, p.index(nxt, i))


_tr_record_v8 = C._tr_record


def _tr_record_nav(uid, choice, how="answer"):
    s = C.STATE["tsess"].get(str(uid))
    if s:
        _pos(s)
    r = _tr_record_v8(uid, choice, how)
    s = C.STATE["tsess"].get(str(uid))
    if s and not s.get("result"):
        _advance(s)
    return r


C._tr_record = _tr_record_nav


def tr_goto(uid, p):
    s = C.STATE["tsess"].get(str(uid))
    if not s or s.get("result"):
        return "no_session"
    pos = _pos(s)
    if p not in pos[s["i"]:]:
        return "done"
    _swap(s, s["i"], pos.index(p, s["i"]))
    s["sent"] = None
    C.save()
    return None


def tr_view(uid, p):
    """Уже решённый вопрос этой тренировки (в экзамене — нельзя, ответы в конце)."""
    s = C.STATE["tsess"].get(str(uid))
    if not s or s.get("exam"):
        return None
    pos = _pos(s)
    if p not in pos[:s["i"]]:
        return None
    k = pos.index(p)
    if k >= len(s.get("log", [])):
        return None
    c, qi, ch, ok = s["log"][k]
    qz = C.STATE["quizzes"].get(c)
    if not qz:
        return None
    q = qz["questions"][qi]
    return {"no": p + 1, "n": len(pos), "q": q["q"], "opts": q["opts"], "right": q["right"], "chosen": ch, "ok": ok}


def _nav(uid, st):
    """В состояние вопроса — его номер и карта: какие номера уже решены."""
    s = C.STATE["tsess"].get(str(uid))
    if not s or st.get("status") != "tquestion" or s.get("result"):
        return
    pos = _pos(s)
    nav = [None] * len(pos)
    for k in range(min(s["i"], len(s.get("log", [])))):
        nav[pos[k]] = 2 if s.get("exam") else s["log"][k][3]
    st["no"] = pos[s["i"]] + 1
    st["nav"] = nav

_orig_record = C._record


def _record(uid, choice, how="answer"):
    mark_day(uid)
    return _orig_record(uid, choice, how)


C._record = _record

_orig_tr_finish = C._tr_finish


def _tr_finish(uid, s):
    _orig_tr_finish(uid, s)
    u = C.user(uid)
    mode = s.get("mode", "t")
    if mode == "prac":
        th = u.get("thist", [])
        if th and th[-1].get("mode") == "prac":
            th.pop()                                # в статистику тренажёра не идёт
        rec = u.setdefault("prac", {}).setdefault(s.get("code", ""), {"runs": 0, "best": 0, "last": 0})
        rec["runs"] += 1
        rec["best"] = max(rec["best"], s["result"]["pct"])
        rec["last"] = s["result"]["pct"]
        rec["res"] = {k: s["result"][k] for k in ("score", "total", "pct", "points")}
        rec["date"] = day()
        s["result"]["best"], s["result"]["runs"] = rec["best"], rec["runs"]
    h = u.setdefault("hist", [])
    u["hseq"] = u.get("hseq", 0) + 1
    h.append({"id": u["hseq"], "k": "prac" if mode == "prac" else "train", "m": mode, "t": s["title"],
              "s": s.get("subject", ""), "c": s.get("code", ""), "sc": s["score"], "n": len(s["items"]),
              "p": s["result"]["pct"], "ts": int(time.time()), "log": list(s.get("log", []))})
    del h[:-HIST_MAX]
    for x in h[:-HIST_LOG]:
        x.pop("log", None)


C._tr_finish = _tr_finish

# тренажёр: сворачивать можно, время на вопрос не сгорает (у экзамена общий таймер остаётся)
_orig_tr_expire = C._tr_expire


def _tr_expire(uid):
    s = C.STATE["tsess"].get(str(uid))
    if s and not s.get("exam"):
        return None
    return _orig_tr_expire(uid)


C._tr_expire = _tr_expire
C.tr_leave = lambda uid: C.tr_state(uid)


# ================== тренировка закрытого теста ==================
def prac_start(uid, code):
    code = (code or "").upper()
    qz = C.STATE["quizzes"].get(code)
    if not qz or not C.visible(qz) or C.kind(qz) == "trainer":
        return "no_quiz"
    if qz.get("open", True):
        return "open"                               # пока тест открыт — ответы не показываем
    if not C.user(uid).get("name"):
        return "no_name"
    if str(uid) in C.STATE["sessions"]:
        return "busy"
    k = min(qz["count"], len(qz["questions"]))
    items = [[code, i] for i in random.sample(range(len(qz["questions"])), k)]
    C._new_session(uid, items, "prac", qz["title"], qz.get("subject", ""), code=code)
    return None


def prac_retry(uid):
    s = C.STATE["tsess"].get(str(uid))
    items = [[c, i] for c, i, ch, ok in (s or {}).get("log", []) if not ok and c in C.STATE["quizzes"]]
    if not items:
        return "empty"
    random.shuffle(items)
    C._new_session(uid, items, "prac", s["title"], s.get("subject", ""), code=s.get("code", ""))
    return None


def topic_mist(uid, code):
    """Ошибки одной темы (одного тренажёра)."""
    code = (code or "").upper()
    qz = C.STATE["quizzes"].get(code)
    if not qz or C.kind(qz) != "trainer":
        return "no_quiz"
    st = _orig_qst(uid)
    items = [[code, i] for i, q in enumerate(qz["questions"]) if (st.get(C.qid(q)) or [0, 0, None])[2] == 0]
    if not items:
        return "empty"
    random.shuffle(items)
    C._new_session(uid, items, "tmist", qz["title"], C.subj_of(qz), code=code)
    return None


# ================== прогресс по предмету ==================
def progress(uid, name):
    st = _orig_qst(uid)
    b = C.bank(name)
    ok = sum(1 for k in b if k in st and st[k][2] == 1)
    topics = []
    for code, qz in C.trainer_quizzes(name):
        ids = {C.qid(q) for q in qz["questions"]}
        bad = sum(1 for k in ids if k in st and st[k][2] == 0)
        good = sum(1 for k in ids if k in st and st[k][2] == 1)
        topics.append({"code": code, "title": qz["title"], "bad": bad, "ok": good, "total": len(ids)})
    if len(topics) > 1:                             # «Все вопросы» — не тема, пропускаем
        topics = [t for t in topics if t["total"] < 0.9 * len(b)] or topics
    weak = sorted([t for t in topics if t["bad"]], key=lambda t: (-t["bad"] / t["total"], -t["bad"]))[:5]
    return {"total": len(b), "ok": ok, "pct": round(100 * ok / len(b)) if b else 0, "weak": weak}


# ================== банк: карточки и «любой вопрос» ==================
def _find(name, qid_):
    b = C.bank(name) if name is not None else {}
    if qid_ in b:
        return b[qid_]
    for code, qz in C.STATE["quizzes"].items():   # запасной путь: искать везде
        for i, q in enumerate(qz.get("questions", [])):
            if C.qid(q) == qid_:
                return [code, i]
    return None


def _rec_q(uid, q, ok, spent=0.0):
    r = _orig_qst(uid).setdefault(C.qid(q), [0, 0, None, 0, 0])
    r[0 if ok else 1] += 1
    r[2] = 1 if ok else 0
    if spent:
        r[3] = round(r[3] + min(spent, 300), 1)
        r[4] += 1


def qlist(uid, name, answers=False):
    st = _orig_qst(uid)
    fav = set(C.user(uid).get("fav", []))
    out = []
    for n, (k, (c, i)) in enumerate(C.bank(name).items(), 1):
        q = C.STATE["quizzes"][c]["questions"][i]
        r = st.get(k)
        row = {"id": k, "no": n, "q": q["q"], "fav": k in fav, "st": None if not r else r[2]}
        if answers:
            row["a"] = q["opts"][q["right"]]
        out.append(row)
    return out


def one_get(uid, name, qid_):
    loc = _find(name, qid_)
    if not loc:
        return None
    c, i = loc
    q = C.STATE["quizzes"][c]["questions"][i]
    sh = random.sample(range(len(q["opts"])), len(q["opts"]))
    C.user(uid)["one"] = {"id": qid_, "c": c, "i": i, "sh": sh, "t": time.time()}
    r = _orig_qst(uid).get(qid_)
    return {"id": qid_, "text": q["q"], "opts": [q["opts"][j] for j in sh], "title": C.STATE["quizzes"][c]["title"],
            "fav": qid_ in set(C.user(uid).get("fav", [])), "st": None if not r else r[2]}


def one_answer(uid, qid_, k):
    o = C.user(uid).get("one")
    if not o or o["id"] != qid_ or o["c"] not in C.STATE["quizzes"]:
        return None
    q = C.STATE["quizzes"][o["c"]]["questions"][o["i"]]
    sh = o["sh"]
    ok = 0 <= k < len(sh) and sh[k] == q["right"]
    _rec_q(uid, q, ok, time.time() - o["t"])
    mark_day(uid)
    week_add(uid, ok)
    C.user(uid).pop("one", None)
    C.save()
    return {"ok": ok, "right": sh.index(q["right"]), "chosen": k}


def card_mark(uid, name, qid_, know):
    loc = _find(name, qid_)
    if not loc:
        return False
    _rec_q(uid, C.STATE["quizzes"][loc[0]]["questions"][loc[1]], bool(know))
    mark_day(uid)
    C.save()
    return True


def fav_toggle(uid, qid_):
    fav = C.user(uid).setdefault("fav", [])
    fav.remove(qid_) if qid_ in fav else fav.append(qid_)
    C.save()
    return qid_ in fav


# ================== история ==================
def history(uid):
    u = C.user(uid)
    if "hist" not in u:                             # старые тренировки (без разбора)
        h = u["hist"] = []
        for n, x in enumerate(u.get("thist", []), 1):
            try:
                ts = int(time.mktime(time.strptime(x["date"], "%d.%m.%Y %H:%M")))
            except Exception:
                ts = 0
            h.append({"id": -n, "k": "train", "m": x.get("mode", "t"), "t": x.get("title", ""), "s": x.get("subject", ""),
                      "c": "", "sc": x.get("score", 0), "n": x.get("total", 0), "p": x.get("pct", 0), "ts": ts})
        C.save()
    out = []
    for x in u["hist"]:
        out.append({"id": str(x["id"]), "kind": x["k"], "mode": x["m"], "title": x["t"], "subject": x["s"] if x["s"] != C.NO_SUBJ else "",
                    "score": x["sc"], "total": x["n"], "pct": x["p"], "ts": x["ts"], "rev": bool(x.get("log"))})
    for code, atts in C.STATE["attempts"].items():
        a = atts.get(str(uid))
        qz = C.STATE["quizzes"].get(code)
        if not a or not a.get("done") or not qz:
            continue
        out.append({"id": "t:" + code, "kind": "test", "mode": "test", "title": qz["title"], "subject": qz.get("subject", ""),
                    "score": a["score"], "total": a["total"], "pct": C.pct(a["score"], a["total"]),
                    "points": C.points(a["score"], a["total"]), "ts": int(a.get("started", 0)),
                    "rev": not qz.get("open", True), "code": code})
    out.sort(key=lambda x: -x["ts"])
    for x in out:
        x["date"] = dt.datetime.fromtimestamp(x["ts"], TZ).strftime("%d.%m.%Y %H:%M") if x["ts"] else ""
    return out


def hist_item(uid, hid):
    if hid.startswith("t:"):
        items, err = C.review(uid, hid[2:])
        return items, err
    for x in C.user(uid).get("hist", []):
        if str(x["id"]) == hid:
            if not x.get("log"):
                return None, "no_log"
            return C.tr_items({"log": x["log"]}), None
    return None, "no_item"


# ================== отправка в Telegram ==================
async def tg_send(chat_id, text, button=None):
    import httpx
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if button and WEBAPP_URL:
        data["reply_markup"] = {"inline_keyboard": [[{"text": button, "web_app": {"url": WEBAPP_URL + "/"}}]]}
    async with httpx.AsyncClient(timeout=20) as cl:
        r = await cl.post(f"https://api.telegram.org/bot{BOT['token']}/sendMessage", json=data)
        return r.json().get("ok")


def bg(coro):
    try:
        t = asyncio.get_running_loop().create_task(coro)
        BOT["tasks"].add(t)
        t.add_done_callback(BOT["tasks"].discard)
    except RuntimeError:
        coro.close()


async def _send_report(text):
    for chat in list(C.STATE["admins"]):
        try:
            await tg_send(chat, text)
        except Exception:
            log.exception("Жалоба не отправлена")


def report(uid, body):
    u = C.user(uid)
    d = day()
    rp = u.get("rep") or {}
    if rp.get("d") != d:
        rp = u["rep"] = {"d": d, "n": 0}
    if rp["n"] >= 15:
        return "limit"
    loc = None
    if body.get("id"):
        loc = _find(body.get("s"), str(body["id"]))
    elif body.get("i") is not None:
        s = C.STATE["tsess"].get(str(uid))
        try:
            i = int(body["i"])
            loc = s["items"][i] if s and 0 <= i < len(s["items"]) else None
        except (TypeError, ValueError):
            loc = None
    if not loc or loc[0] not in C.STATE["quizzes"]:
        return "no_item"
    qz = C.STATE["quizzes"][loc[0]]
    q = qz["questions"][loc[1]]
    e = html.escape
    opts = "\n".join(("✅ " if j == q["right"] else "▫️ ") + e(o) for j, o in enumerate(q["opts"]))
    who = e(u.get("name") or u.get("tg_name") or "—") + (f" (@{e(u['username'])})" if u.get("username") else "")
    note = e(str(body.get("text") or "").strip()[:800]) or "—"
    text = (f"⚠️ <b>Ошибка в вопросе</b>\n👤 {who}\n📚 {e(qz['title'])} · <code>{loc[0]}</code> · вопрос №{loc[1] + 1}\n\n"
            f"<b>{e(q['q'])}</b>\n{opts}\n\n💬 {note}")
    rp["n"] += 1
    C.save()
    bg(_send_report(text[:4000]))
    return None


PCERT = {"ru": "🔁 <b>Тренировка</b> · тест закрыт, не в зачёт\n🏅 {name}: {pct}% ({points}/50) — «{title}»",
         "uz": "🔁 <b>Mashq</b> · test yopilgan, hisobga olinmaydi\n🏅 {name}: {pct}% ({points}/50) — «{title}»",
         "en": "🔁 <b>Practice</b> · test closed, not graded\n🏅 {name}: {pct}% ({points}/50) — “{title}”",
         "zh": "🔁 <b>练习</b> · 测验已关闭，不计分\n🏅 {name}：{pct}%（{points}/50）—「{title}」"}


async def _send_photo(chat_id, data, caption):
    import httpx
    async with httpx.AsyncClient(timeout=30) as cl:
        await cl.post(f"https://api.telegram.org/bot{BOT['token']}/sendPhoto",
                      data={"chat_id": str(chat_id), "caption": caption, "parse_mode": "HTML"},
                      files={"photo": ("certificate.jpg", data, "image/jpeg")})


def prac_cert(uid, body):
    import base64
    code = str(body.get("code", "")).upper()
    u = C.user(uid)
    rec = (u.get("prac") or {}).get(code)
    qz = C.STATE["quizzes"].get(code)
    if not rec or not rec.get("res") or not qz:
        return "no_result"
    try:
        data = base64.b64decode(str(body.get("img", "")).split(",")[-1])
    except Exception:
        return "bad_image"
    if not data.startswith(b"\xff\xd8") or len(data) > 3_000_000:
        return "bad_image"
    lang = u.get("lang") if u.get("lang") in PCERT else "ru"
    r = rec["res"]
    cap = PCERT[lang].format(name=html.escape(u.get("name") or ""), pct=r["pct"], points=r["points"],
                             title=html.escape(qz["title"]))
    bg(_send_photo(uid, data, cap))
    return None


REMIND = {"ru": ("🔥 Серия <b>{n}</b> дн. подряд! Сегодня вы ещё не занимались — 5 минут в тренажёре, и серия продолжится.",
                 "🏋️ Открыть тренажёр"),
          "uz": ("🔥 Ketma-ket <b>{n}</b> kun! Bugun hali shugʻullanmadingiz — trenajyorda 5 daqiqa va seriya davom etadi.",
                 "🏋️ Trenajyorni ochish"),
          "en": ("🔥 <b>{n}</b>-day streak! You haven't practiced today — 5 minutes in the trainer keeps it going.",
                 "🏋️ Open trainer"),
          "zh": ("🔥 已连续 <b>{n}</b> 天！今天还没练习——在练习中花 5 分钟即可保持连续记录。", "🏋️ 打开练习")}


async def remind_loop():
    while True:
        try:
            await asyncio.sleep(600)
            if not BOT["token"] or not (REMIND_HOUR <= now().hour < 23):
                continue
            d = day()
            sent = 0
            for uid, u in list(C.STATE["users"].items()):
                if not u.get("remind", True) or u.get("remd") == d or d in u.get("days", []):
                    continue
                n = streak(u)
                if n < 1:
                    continue
                u["remd"] = d
                lang = u.get("lang") if u.get("lang") in REMIND else "ru"
                try:
                    await tg_send(uid, REMIND[lang][0].format(n=n), REMIND[lang][1])
                    sent += 1
                except Exception:
                    pass
                await asyncio.sleep(0.05)
            if sent:
                C.save()
                log.info("Напоминаний о серии: %d", sent)
        except asyncio.CancelledError:
            return
        except Exception:
            log.exception("Напоминания")


# ================== курсы (группы предметов в тренажёре) ==================
COURSES = [("1 курс · ИК N1", ["Философия", "Религиоведение", "Oʻzbek tili"]),
           ("2 курс · ИК N1", ["Бухгалтерский учёт", "Бизнес-право"])]
_COURSE = {subj: (i, name) for i, (name, subjs) in enumerate(COURSES) for subj in subjs}


def _courses(items):
    for x in items:
        i, name = _COURSE.get(x["name"], (len(COURSES), ""))
        x["course"], x["ci"] = name, i
    items.sort(key=lambda x: (x["ci"], x["name"] == C.NO_SUBJ, x["name"]))


# ================== API ==================
_orig_handle = W.handle


def _num(x, d=0):
    try:
        return int(x)
    except (TypeError, ValueError):
        return d


def _free(st):
    """Тренажёр: без таймера на вопрос (сворачивать можно), показываем секундомер."""
    if isinstance(st, dict) and st.get("status") == "tquestion" and not st.get("exam"):
        st["left"] = 3600                           # старая страница не «сожжёт» вопрос
        st["free"] = True
    return st


def handle(method, path, query, body, user):
    r = _handle2(method, path, query, body, user)
    if r is None:
        r = _orig_handle(method, path, query, body, user)
    if isinstance(r, dict):
        if isinstance(r.get("state"), dict):
            _free(r["state"])
            if user:
                _nav(str(user["id"]), r["state"])
        if path == "/api/me" and user and r.get("ok"):
            r["streak"] = streak(C.user(user["id"]))
            r["v"] = 8
        if path == "/api/subjects" and r.get("ok"):
            _courses(r.get("items") or [])
        if path == "/api/list" and user and r.get("ok"):
            _list_extra(str(user["id"]), r)
    return r


def _list_extra(uid, r):
    have = {q["code"] for q in r["items"]}
    pr = C.user(uid).get("prac", {})
    for code, qz in sorted(C.STATE["quizzes"].items(), key=lambda x: -x[1].get("created", 0)):
        if code in have or C.kind(qz) == "trainer" or qz.get("open", True):
            continue
        q = C.info(code, uid)
        if q:
            r["items"].append(q)
    for q in r["items"]:
        if q.get("kind") != "trainer" and not q.get("open", True):
            q["prac"] = pr.get(q["code"])


def _handle2(method, path, query, body, user):
    if not user or not path.startswith("/api/"):
        return None
    uid = str(user["id"])
    post = method == "POST"
    if path == "/api/tanswer" and post and _num(body.get("k"), -1) < 0:
        s = C.STATE["tsess"].get(uid)
        if s and not s.get("exam"):                 # в тренажёре время не выходит — «таймаут» не засчитываем
            return {"ok": True, "state": C.tr_state(uid)}
    if path == "/api/tstart" and post:
        mode = body.get("mode")
        cur = C.STATE["tsess"].get(uid) or {}
        err = "skip"
        if mode == "prac":
            err = prac_start(uid, body.get("code") or cur.get("code"))
        elif mode == "retry" and cur.get("mode") == "prac":
            err = prac_retry(uid)
        elif mode == "tmist":
            err = topic_mist(uid, body.get("code") or cur.get("code"))
        if err == "skip":
            return None
        if err:
            return {"ok": False, "error": err}
        return {"ok": True, "state": C.tr_state(uid)}
    if path == "/api/tgoto" and post:
        err = tr_goto(uid, _num(body.get("p"), -1))
        return {"ok": not err, "error": err, "state": C.tr_state(uid)}
    if path == "/api/tview":
        v = tr_view(uid, _num(query.get("p"), -1))
        return {"ok": bool(v), "item": v}
    if path == "/api/pcert" and post:
        err = prac_cert(uid, body)
        return {"ok": not err, "error": err}
    if path == "/api/history":
        return {"ok": True, "items": history(uid), "streak": streak_info(uid)}
    if path == "/api/hitem":
        items, err = hist_item(uid, query.get("id", ""))
        return {"ok": items is not None, "items": items, "error": err}
    if path == "/api/streak":
        return {"ok": True, "streak": streak_info(uid)}
    if path == "/api/remind" and post:
        C.user(uid)["remind"] = bool(body.get("on"))
        C.save()
        return {"ok": True, "streak": streak_info(uid)}
    if path == "/api/week":
        return {"ok": True, "week": week_top(uid)}
    if path == "/api/progress":
        return {"ok": True, "progress": progress(uid, query.get("s", ""))}
    if path == "/api/qlist":
        return {"ok": True, "items": qlist(uid, query.get("s", ""))}
    if path == "/api/cards":
        return {"ok": True, "items": qlist(uid, query.get("s", ""), answers=True)}
    if path == "/api/card" and post:
        return {"ok": card_mark(uid, body.get("s"), str(body.get("id", "")), body.get("know"))}
    if path == "/api/one":
        q = one_get(uid, query.get("s"), query.get("id", ""))
        return {"ok": bool(q), "q": q, "error": None if q else "no_item"}
    if path == "/api/oneans" and post:
        r = one_answer(uid, str(body.get("id", "")), _num(body.get("k"), -1))
        return {"ok": bool(r), "res": r, "error": None if r else "stale"}
    if path == "/api/qfav" and post:
        return {"ok": True, "fav": fav_toggle(uid, str(body.get("id", "")))}
    if path == "/api/report" and post:
        err = report(uid, body)
        return {"ok": not err, "error": err}
    return None


W.handle = handle

# ================== старт: веб + напоминания ==================
_orig_start_web = W.start_web


async def start_web(token):
    BOT["token"] = token
    server = await _orig_start_web(token)
    bg(remind_loop())
    log.info("quiz v8: история, серия, карточки, неделя — включены")
    if not _js.rstrip().endswith("</script>") or "screenOne" not in _js:
        log.error("quiz_v2.js ОБРЕЗАН: %d строк — загрузите файл заново целиком (должно быть 452 строки)", _js.count("\n"))
    else:
        log.info("quiz_v2.js в порядке: %d строк", _js.count("\n"))
    return server


W.start_web = start_web

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz_v2.js"), encoding="utf-8") as _f:
    _js = _f.read()
W.ADMIN_JS = W.ADMIN_JS + "\n" + _js
