"""
Quiz-бот: тесты с таймером, перемешиванием, одной попыткой и таблицей лидеров.
Админ создаёт тесты командой /new прямо в Telegram.
"""
import io
import os
import re
import csv
import json
import html
import time
import random
import logging
import secrets

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, MessageHandler,
                          ContextTypes, filters)

# ================== НАСТРОЙКИ ==================
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMINS = {x.strip().lstrip("@").lower() for x in os.environ.get("ADMINS", "fedex_azim").split(",") if x.strip()}
STATE_FILE = os.environ.get("STATE_FILE", "quiz.json")
DEFAULT_TIME = 20      # секунд на вопрос
LETTERS = "ABCDEFGH"
# ===============================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("quiz")
e = lambda s: html.escape(str(s or ""))

T = {
    "ru": {
        "lang": "🇷🇺 Язык: русский",
        "ask_name": "👋 Добро пожаловать!\n\n✍️ Напишите ваши <b>имя и фамилию</b> (как в журнале), например: <i>Azimov Aziz</i>",
        "bad_name": "❗ Напишите имя и фамилию — два слова, только буквы.",
        "hello": "✅ Приятно познакомиться, <b>{n}</b>!\n\nЧтобы пройти тест, откройте ссылку от преподавателя или отправьте <b>код теста</b>.",
        "ask_code": "🔑 Отправьте код теста (например: <code>A7K2Q9</code>) или откройте ссылку от преподавателя.",
        "no_quiz": "😕 Тест с таким кодом не найден.",
        "closed": "🔒 Этот тест закрыт преподавателем.",
        "done_before": "✅ Вы уже прошли этот тест: <b>{s} из {t}</b>, место {p} из {a}.\nПовторная попытка запрещена.",
        "intro": "📝 <b>{title}</b>\n\n❓ Вопросов: <b>{n}</b>\n⏱ На каждый вопрос: <b>{sec} сек</b>\n🔁 Попытка: <b>одна</b>\n\n"
                 "⚠️ Правила:\n• вопросы и варианты перемешаны у каждого;\n• вернуться к вопросу нельзя;\n"
                 "• не успели — ответ не засчитан;\n• при равных баллах выше тот, кто быстрее.\n\nУчастник: <b>{name}</b>",
        "start_btn": "▶️ Начать тест",
        "q": "❓ <b>Вопрос {i} из {n}</b>  ·  ⏱ {sec} сек\n\n{text}\n\n{opts}",
        "timeout": "⏰ Время вышло — ответ не засчитан.",
        "answered": "✔️ Ответ принят.",
        "late": "⏰ Время на этот вопрос уже вышло.",
        "result": "🏁 <b>Тест завершён!</b>\n\n📝 {title}\n✅ Правильных: <b>{s} из {t}</b> ({pct}%)\n⏱ Время: <b>{tm}</b>\n🏆 Место: <b>{p} из {a}</b>",
        "rename": "✍️ Напишите новые имя и фамилию:",
        "busy": "⏳ Сначала закончите текущий тест.",
    },
    "uz": {
        "lang": "🇺🇿 Til: oʻzbekcha",
        "ask_name": "👋 Xush kelibsiz!\n\n✍️ <b>Ism va familiyangizni</b> yozing (jurnaldagidek), masalan: <i>Azimov Aziz</i>",
        "bad_name": "❗ Ism va familiyani yozing — ikki soʻz, faqat harflar.",
        "hello": "✅ Tanishganimdan xursandman, <b>{n}</b>!\n\nTestni boshlash uchun oʻqituvchi havolasini oching yoki <b>test kodini</b> yuboring.",
        "ask_code": "🔑 Test kodini yuboring (masalan: <code>A7K2Q9</code>) yoki oʻqituvchi havolasini oching.",
        "no_quiz": "😕 Bunday kodli test topilmadi.",
        "closed": "🔒 Bu test oʻqituvchi tomonidan yopilgan.",
        "done_before": "✅ Siz bu testni topshirgansiz: <b>{s} / {t}</b>, {a} tadan {p}-oʻrin.\nQayta urinish mumkin emas.",
        "intro": "📝 <b>{title}</b>\n\n❓ Savollar: <b>{n}</b>\n⏱ Har bir savolga: <b>{sec} soniya</b>\n🔁 Urinish: <b>bitta</b>\n\n"
                 "⚠️ Qoidalar:\n• savollar va javoblar har kimda aralashtirilgan;\n• oldingi savolga qaytib boʻlmaydi;\n"
                 "• ulgurmasangiz — javob hisoblanmaydi;\n• ball teng boʻlsa, tezroq javob bergan yuqorida.\n\nIshtirokchi: <b>{name}</b>",
        "start_btn": "▶️ Testni boshlash",
        "q": "❓ <b>{n} tadan {i}-savol</b>  ·  ⏱ {sec} soniya\n\n{text}\n\n{opts}",
        "timeout": "⏰ Vaqt tugadi — javob hisoblanmadi.",
        "answered": "✔️ Javob qabul qilindi.",
        "late": "⏰ Bu savol uchun vaqt tugagan.",
        "result": "🏁 <b>Test yakunlandi!</b>\n\n📝 {title}\n✅ Toʻgʻri: <b>{s} / {t}</b> ({pct}%)\n⏱ Vaqt: <b>{tm}</b>\n🏆 Oʻrin: <b>{a} tadan {p}</b>",
        "rename": "✍️ Yangi ism va familiyani yozing:",
        "busy": "⏳ Avval joriy testni yakunlang.",
    },
}

HELP_ADMIN = (
    "🛠 <b>Команды админа</b>\n"
    "/new — создать тест\n/quizzes — мои тесты и статистика\n\n"
    "<b>Формат теста</b> (отправьте одним или несколькими сообщениями, затем /done):\n"
    "<pre>Название: Микроэкономика — тест 1\nВремя: 20\nВопросов: 15\n\n"
    "1. Что такое инфляция?\n+ Рост общего уровня цен\n- Снижение цен\n- Рост ВВП\n- Рост безработицы\n\n"
    "2. Следующий вопрос?\n- Неверно\n+ Верно</pre>\n"
    "«+» — правильный ответ, «−» — неверный. «Время» — секунд на вопрос, «Вопросов» — сколько выдавать каждому "
    "из всего банка (если не указать — все)."
)


# ================== ХРАНИЛИЩЕ ==================
def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            st = json.load(f)
    except Exception:
        st = {}
    for k in ("quizzes", "users", "attempts", "sessions"):
        st.setdefault(k, {})
    return st


STATE = load_state()


def save():
    try:
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(STATE, f, ensure_ascii=False)
        os.replace(tmp, STATE_FILE)
    except Exception:
        log.exception("Не удалось сохранить")


DRAFTS = {}   # админ -> накопленный текст теста
WAIT = {}     # uid -> "name" | "code"


def user(uid):
    return STATE["users"].setdefault(str(uid), {})


def lang_of(uid):
    return user(uid).get("lang", "ru")


def tr(uid, key, **kw):
    s = T[lang_of(uid)][key]
    return s.format(**kw) if kw else s


def is_admin(u):
    return bool(u) and ((u.username or "").lower() in ADMINS or str(u.id) in ADMINS)


def fmt_time(sec):
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


# ================== РАЗБОР ТЕСТА ==================
def parse_quiz(text):
    title, per_q, count, questions, cur = "Тест", DEFAULT_TIME, None, [], None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        low = line.lower()
        m = re.match(r"^(название|nomi|title)\s*:\s*(.+)$", low)
        if m:
            title = line.split(":", 1)[1].strip()
            continue
        m = re.match(r"^(время|vaqt|time)\s*:\s*(\d+)", low)
        if m:
            per_q = max(5, min(300, int(m.group(2))))
            continue
        m = re.match(r"^(вопросов|savollar|questions)\s*:\s*(\d+)", low)
        if m:
            count = int(m.group(2))
            continue
        if line[0] in "+-−–":
            if cur is None:
                continue
            ans = line[1:].strip()
            if ans:
                cur["opts"].append(ans)
                if line[0] == "+":
                    cur["right"] = len(cur["opts"]) - 1
            continue
        cur = {"q": re.sub(r"^\d+[.)]\s*", "", line), "opts": [], "right": None}
        questions.append(cur)
    good = [q for q in questions if len(q["opts"]) >= 2 and q["right"] is not None]
    bad = len(questions) - len(good)
    count = min(count or len(good), len(good))
    return {"title": title, "time": per_q, "count": count, "questions": good}, bad


def new_code():
    while True:
        c = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(6))
        if c not in STATE["quizzes"]:
            return c


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


# ================== ПРОХОЖДЕНИЕ ==================
async def open_quiz(message, uid, code, ctx):
    code = code.strip().upper()
    qz = STATE["quizzes"].get(code)
    if not qz:
        await message.reply_text(tr(uid, "no_quiz"))
        return
    if not user(uid).get("name"):
        WAIT[uid] = "name"
        user(uid)["pending"] = code
        save()
        await message.reply_text(tr(uid, "ask_name"), parse_mode="HTML")
        return
    att = STATE["attempts"].get(code, {}).get(str(uid))
    if att and att.get("done"):
        p, a = place_of(code, uid)
        await message.reply_text(tr(uid, "done_before", s=att["score"], t=att["total"], p=p, a=a), parse_mode="HTML")
        return
    if not qz.get("open", True):
        await message.reply_text(tr(uid, "closed"))
        return
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(tr(uid, "start_btn"), callback_data=f"go:{code}")]])
    await message.reply_text(tr(uid, "intro", title=e(qz["title"]), n=qz["count"], sec=qz["time"],
                                name=e(user(uid)["name"])), parse_mode="HTML", reply_markup=kb)


async def start_attempt(bot, chat_id, uid, code, ctx):
    qz = STATE["quizzes"].get(code)
    if not qz or not qz.get("open", True):
        return
    atts = STATE["attempts"].setdefault(code, {})
    if str(uid) in atts:            # одна попытка, даже если тест бросили на середине
        return
    order = random.sample(range(len(qz["questions"])), qz["count"])
    shuffles = [random.sample(range(len(qz["questions"][i]["opts"])), len(qz["questions"][i]["opts"])) for i in order]
    atts[str(uid)] = {"uid": str(uid), "name": user(uid)["name"], "score": 0, "total": qz["count"],
                      "time": 0.0, "done": False, "started": time.time(), "answers": []}
    STATE["sessions"][str(uid)] = {"code": code, "order": order, "shuf": shuffles, "i": 0, "sent": 0}
    save()
    await send_question(bot, chat_id, uid, ctx)


async def send_question(bot, chat_id, uid, ctx):
    s = STATE["sessions"].get(str(uid))
    if not s:
        return
    qz = STATE["quizzes"][s["code"]]
    if s["i"] >= len(s["order"]):
        await finish(bot, chat_id, uid)
        return
    q = qz["questions"][s["order"][s["i"]]]
    shuf = s["shuf"][s["i"]]
    opts = "\n".join(f"<b>{LETTERS[k]})</b> {e(q['opts'][j])}" for k, j in enumerate(shuf))
    btns = [InlineKeyboardButton(LETTERS[k], callback_data=f"a:{s['i']}:{k}") for k in range(len(shuf))]
    kb = InlineKeyboardMarkup([btns[i:i + 4] for i in range(0, len(btns), 4)])
    msg = await bot.send_message(chat_id, tr(uid, "q", i=s["i"] + 1, n=len(s["order"]), sec=qz["time"],
                                             text=e(q["q"]), opts=opts),
                                 parse_mode="HTML", reply_markup=kb, protect_content=True)
    s["sent"], s["msg"] = time.time(), msg.message_id
    save()
    ctx.job_queue.run_once(on_timeout, qz["time"] + 1, data={"uid": uid, "chat": chat_id, "i": s["i"]},
                           name=f"t{uid}")


async def record(bot, chat_id, uid, choice, ctx):
    """choice: номер выбранного варианта на экране или None (время вышло)."""
    s = STATE["sessions"].get(str(uid))
    qz = STATE["quizzes"][s["code"]]
    att = STATE["attempts"][s["code"]][str(uid)]
    q_idx = s["order"][s["i"]]
    spent = min(time.time() - s["sent"], qz["time"])
    ok = choice is not None and s["shuf"][s["i"]][choice] == qz["questions"][q_idx]["right"]
    att["score"] += int(ok)
    att["time"] += spent
    att["answers"].append([q_idx, int(ok)])
    for j in ctx.job_queue.get_jobs_by_name(f"t{uid}"):
        j.schedule_removal()
    try:
        await bot.edit_message_reply_markup(chat_id, s["msg"], reply_markup=None)
    except Exception:
        pass
    s["i"] += 1
    save()
    await send_question(bot, chat_id, uid, ctx)


async def on_timeout(ctx: ContextTypes.DEFAULT_TYPE):
    d = ctx.job.data
    s = STATE["sessions"].get(str(d["uid"]))
    if not s or s["i"] != d["i"]:
        return
    await ctx.bot.send_message(d["chat"], tr(d["uid"], "timeout"))
    await record(ctx.bot, d["chat"], d["uid"], None, ctx)


async def finish(bot, chat_id, uid):
    s = STATE["sessions"].pop(str(uid), None)
    if not s:
        return
    att = STATE["attempts"][s["code"]][str(uid)]
    att["done"] = True
    save()
    p, a = place_of(s["code"], uid)
    pct = round(100 * att["score"] / max(att["total"], 1))
    await bot.send_message(chat_id, tr(uid, "result", title=e(STATE["quizzes"][s["code"]]["title"]),
                                       s=att["score"], t=att["total"], pct=pct, tm=fmt_time(att["time"]), p=p, a=a),
                           parse_mode="HTML")


# ================== АДМИН ==================
def quiz_stats(code):
    qz = STATE["quizzes"][code]
    rows = ranking(code)
    lines = [f"📊 <b>{e(qz['title'])}</b>  ·  код <code>{code}</code>",
             f"{'🟢 открыт' if qz.get('open', True) else '🔒 закрыт'} · участников: <b>{len(rows)}</b>"]
    if rows:
        avg = sum(a["score"] for a in rows) / len(rows)
        lines.append(f"Средний балл: <b>{avg:.1f} из {qz['count']}</b>\n")
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        for i, a in enumerate(rows[:30], 1):
            lines.append(f"{medals.get(i, f'{i}.')} {e(a['name'])} — <b>{a['score']}/{a['total']}</b> · {fmt_time(a['time'])}")
        if len(rows) > 30:
            lines.append(f"… и ещё {len(rows) - 30} (полный список — в файле)")
        stat = {}
        for a in rows:
            for qi, ok in a["answers"]:
                c = stat.setdefault(qi, [0, 0])
                c[0] += ok
                c[1] += 1
        hard = sorted(((c[0] / c[1], qi) for qi, c in stat.items() if c[1]), key=lambda x: x[0])[:3]
        if hard:
            lines.append("\n🤯 <b>Самые сложные вопросы:</b>")
            for r, qi in hard:
                lines.append(f"• {round(r * 100)}% верно — {e(qz['questions'][qi]['q'][:70])}")
    return "\n".join(lines)[:4000]


def quiz_kb(code, bot_name):
    qz = STATE["quizzes"][code]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Обновить", callback_data=f"st:{code}"),
         InlineKeyboardButton("📥 Excel (CSV)", callback_data=f"csv:{code}")],
        [InlineKeyboardButton("🔒 Закрыть" if qz.get("open", True) else "🟢 Открыть", callback_data=f"tg:{code}"),
         InlineKeyboardButton("🗑 Удалить", callback_data=f"del:{code}")],
        [InlineKeyboardButton("🔗 Ссылка на тест", url=f"https://t.me/{bot_name}?start={code}")],
    ])


async def cmd_new(update: Update, ctx):
    if not is_admin(update.effective_user):
        return
    DRAFTS[update.effective_user.id] = []
    await update.message.reply_text(HELP_ADMIN + "\n\n✍️ Жду текст теста. Когда закончите — отправьте /done",
                                    parse_mode="HTML")


async def cmd_done(update: Update, ctx):
    uid = update.effective_user.id
    if not is_admin(update.effective_user) or uid not in DRAFTS:
        return
    qz, bad = parse_quiz("\n".join(DRAFTS.pop(uid)))
    if not qz["questions"]:
        await update.message.reply_text("❗ Не нашёл ни одного вопроса. Проверьте формат: /new")
        return
    code = new_code()
    qz.update(open=True, created=time.time())
    STATE["quizzes"][code] = qz
    save()
    warn = f"\n⚠️ Пропущено вопросов с ошибкой: {bad} (нет «+» или меньше 2 вариантов)" if bad else ""
    link = f"https://t.me/{ctx.bot.username}?start={code}"
    await update.message.reply_text(
        f"✅ Тест создан!\n\n📝 <b>{e(qz['title'])}</b>\n❓ В банке: {len(qz['questions'])} · каждому: {qz['count']}\n"
        f"⏱ {qz['time']} сек на вопрос\n🔑 Код: <code>{code}</code>\n🔗 Ссылка для студентов:\n{link}{warn}",
        parse_mode="HTML", reply_markup=quiz_kb(code, ctx.bot.username))


async def cmd_quizzes(update: Update, ctx):
    if not is_admin(update.effective_user):
        return
    if not STATE["quizzes"]:
        await update.message.reply_text("Тестов пока нет. Создайте: /new")
        return
    rows = [[InlineKeyboardButton(f"{'🟢' if q.get('open', True) else '🔒'} {q['title'][:40]} · "
                                  f"{len(ranking(c))} чел.", callback_data=f"st:{c}")]
            for c, q in sorted(STATE["quizzes"].items(), key=lambda x: -x[1].get("created", 0))]
    await update.message.reply_text("📚 Ваши тесты:", reply_markup=InlineKeyboardMarkup(rows))


# ================== ОБРАБОТЧИКИ ==================
def lang_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🇷🇺 Русский", callback_data="lg:ru"),
                                  InlineKeyboardButton("🇺🇿 Oʻzbekcha", callback_data="lg:uz")]])


async def cmd_start(update: Update, ctx):
    uid = update.effective_user.id
    code = ctx.args[0] if ctx.args else None
    if code:
        user(uid)["pending"] = code.upper()
        save()
    if "lang" not in user(uid):
        await update.message.reply_text("🌐 Выберите язык / Tilni tanlang", reply_markup=lang_kb())
        return
    await after_lang(update.message, uid, ctx)


async def after_lang(message, uid, ctx):
    if str(uid) in STATE["sessions"]:
        await message.reply_text(tr(uid, "busy"))
        return
    if not user(uid).get("name"):
        WAIT[uid] = "name"
        await message.reply_text(tr(uid, "ask_name"), parse_mode="HTML")
        return
    code = user(uid).pop("pending", None)
    save()
    if code:
        await open_quiz(message, uid, code, ctx)
    else:
        WAIT[uid] = "code"
        await message.reply_text(tr(uid, "ask_code"), parse_mode="HTML")


async def cmd_name(update: Update, ctx):
    uid = update.effective_user.id
    WAIT[uid] = "name"
    await update.message.reply_text(tr(uid, "rename"))


async def on_text(update: Update, ctx):
    uid, text = update.effective_user.id, (update.message.text or "").strip()
    if uid in DRAFTS:
        DRAFTS[uid].append(text)
        await update.message.reply_text(f"📥 Принято ({len(DRAFTS[uid])} сообщ.). Ещё текст или /done")
        return
    if str(uid) in STATE["sessions"]:
        await update.message.reply_text(tr(uid, "busy"))
        return
    if WAIT.get(uid) == "name":
        words = text.split()
        if len(words) < 2 or len(text) > 60 or not all(re.fullmatch(r"[^\W\d_ʻʼ'’-]+(['ʻʼ’-][^\W\d_]+)*", w) for w in words):
            await update.message.reply_text(tr(uid, "bad_name"))
            return
        user(uid)["name"] = " ".join(w.capitalize() for w in words)
        WAIT.pop(uid, None)
        save()
        await update.message.reply_text(tr(uid, "hello", n=e(user(uid)["name"])), parse_mode="HTML")
        code = user(uid).pop("pending", None)
        if code:
            await open_quiz(update.message, uid, code, ctx)
        return
    if re.fullmatch(r"[A-Za-z0-9]{6}", text):
        await open_quiz(update.message, uid, text, ctx)
        return
    await update.message.reply_text(tr(uid, "ask_code"), parse_mode="HTML")


async def on_button(update: Update, ctx):
    q = update.callback_query
    uid, chat_id, data = q.from_user.id, q.message.chat.id, q.data
    kind, _, rest = data.partition(":")
    if kind == "lg":
        user(uid)["lang"] = rest
        save()
        await q.answer(T[rest]["lang"])
        await after_lang(q.message, uid, ctx)
        return
    if kind == "go":
        await q.answer()
        try:
            await q.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        await start_attempt(ctx.bot, chat_id, uid, rest, ctx)
        return
    if kind == "a":
        s = STATE["sessions"].get(str(uid))
        i, _, k = rest.partition(":")
        if not s or int(i) != s["i"]:
            await q.answer()
            return
        qz = STATE["quizzes"][s["code"]]
        if time.time() - s["sent"] > qz["time"] + 1:
            await q.answer(tr(uid, "late"), show_alert=True)
            await record(ctx.bot, chat_id, uid, None, ctx)
            return
        await q.answer(tr(uid, "answered"))
        await record(ctx.bot, chat_id, uid, int(k), ctx)
        return
    # ---- админские кнопки ----
    if not is_admin(q.from_user) or rest not in STATE["quizzes"]:
        await q.answer()
        return
    if kind == "tg":
        STATE["quizzes"][rest]["open"] = not STATE["quizzes"][rest].get("open", True)
        save()
    if kind == "del":
        await q.answer()
        await q.message.reply_text(f"Удалить тест {rest} со всеми результатами?", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🗑 Да, удалить", callback_data=f"del2:{rest}")]]))
        return
    if kind == "del2":
        STATE["quizzes"].pop(rest, None)
        STATE["attempts"].pop(rest, None)
        save()
        await q.answer("Удалено")
        await q.edit_message_text("🗑 Тест удалён.")
        return
    if kind == "csv":
        await q.answer()
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=";")
        w.writerow(["Место", "Имя и фамилия", "Баллы", "Из", "%", "Время (сек)"])
        for i, a in enumerate(ranking(rest), 1):
            w.writerow([i, a["name"], a["score"], a["total"], round(100 * a["score"] / max(a["total"], 1)),
                        round(a["time"])])
        data_bytes = ("\ufeff" + buf.getvalue()).encode("utf-8")
        await ctx.bot.send_document(chat_id, InputFile(io.BytesIO(data_bytes), filename=f"results_{rest}.csv"))
        return
    await q.answer()
    try:
        await q.edit_message_text(quiz_stats(rest), parse_mode="HTML", reply_markup=quiz_kb(rest, ctx.bot.username))
    except Exception:
        await q.message.reply_text(quiz_stats(rest), parse_mode="HTML", reply_markup=quiz_kb(rest, ctx.bot.username))


async def post_init(app):
    # если бот перезапустился посреди теста — продолжаем с текущего вопроса
    for uid, s in list(STATE["sessions"].items()):
        try:
            await app.bot.send_message(int(uid), "🔄 Бот перезапустился, продолжаем тест.")
            s["i"] = min(s["i"], len(s["order"]))
            await send_question(app.bot, int(uid), int(uid), app)
        except Exception:
            log.exception("Не удалось продолжить тест %s", uid)


def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("name", cmd_name))
    app.add_handler(CommandHandler("new", cmd_new))
    app.add_handler(CommandHandler("done", cmd_done))
    app.add_handler(CommandHandler("quizzes", cmd_quizzes))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, on_text))
    log.info("Quiz-бот запущен: тестов %d", len(STATE["quizzes"]))
    app.run_polling()


if __name__ == "__main__":
    main()
