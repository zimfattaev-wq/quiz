"""
TDIU Quiz: тесты в мини-приложении. Админ загружает Word/txt прямо в чат.
"""
import io
import os
import csv
import html
import logging

from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, WebAppInfo,
                      MenuButtonWebApp)
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

import quiz_core as C
from quiz_parse import parse, docx_text
from quiz_web import start_web

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMINS = {x.strip().lstrip("@").lower() for x in os.environ.get("ADMINS", "fedex_azim").split(",") if x.strip()}
_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
WEBAPP_URL = os.environ.get("WEBAPP_URL") or (f"https://{_DOMAIN}" if _DOMAIN else "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("quiz")
e = lambda s: html.escape(str(s or ""))
DRAFTS = {}

LANGS = {"ru": "🇷🇺 Русский", "uz": "🇺🇿 Oʻzbekcha", "en": "🇬🇧 English", "zh": "🇨🇳 中文"}
T = {
    "ru": {"welcome": "👋 <b>Тесты ТГЭУ</b>\n\nНажмите кнопку ниже, чтобы открыть тест. Если у вас есть код от "
                      "преподавателя — введите его в приложении.", "open": "📝 Открыть тест",
           "quiz": "📝 <b>{t}</b>\n\nНажмите кнопку, чтобы начать 👇"},
    "uz": {"welcome": "👋 <b>TDIU testlari</b>\n\nTestni ochish uchun quyidagi tugmani bosing. Oʻqituvchidan kod "
                      "olgan boʻlsangiz — ilovada kiriting.", "open": "📝 Testni ochish",
           "quiz": "📝 <b>{t}</b>\n\nBoshlash uchun tugmani bosing 👇"},
    "en": {"welcome": "👋 <b>TSUE Quiz</b>\n\nTap the button below to open a test. If your teacher gave you a "
                      "code — enter it in the app.", "open": "📝 Open test",
           "quiz": "📝 <b>{t}</b>\n\nTap the button to start 👇"},
    "zh": {"welcome": "👋 <b>塔什干国立经济大学测验</b>\n\n点击下方按钮打开测验。如果老师给了代码，请在应用中输入。",
           "open": "📝 打开测验", "quiz": "📝 <b>{t}</b>\n\n点击按钮开始 👇"},
}

ADMIN_HELP = (
    "🛠 <b>Как загрузить тест</b>\n\n"
    "1️⃣ Просто <b>отправьте мне файл Word (.docx) или .txt</b> с тестом.\n"
    "2️⃣ Или команда /new → вставьте текст → /done\n\n"
    "<b>Формат:</b>\n<pre>Название: Микроэкономика — тест 1\nВремя: 30\nВопросов: 20\n\n"
    "1. Что такое инфляция?\nA) Рост общего уровня цен\nB) Снижение цен\nC) Рост ВВП\nD) Безработица\nОтвет: A\n\n"
    "2. Спрос — это...\nа) желание\nб) желание и возможность купить *\nв) цена\nг) товар</pre>\n"
    "✅ Правильный ответ: строка <code>Ответ: A</code> (или <code>Javob: B</code>), либо звёздочка <code>*</code> "
    "у варианта.\n✅ Можно A) B) C) D) или а) б) в) г).\n"
    "«Название», «Время» (сек на вопрос) и «Вопросов» (сколько выдать каждому) — необязательно, их можно "
    "поменять кнопками после загрузки.\n\n📚 Мои тесты: /quizzes"
)


def is_admin(u):
    return bool(u) and ((u.username or "").lower() in ADMINS or str(u.id) in ADMINS)


def lang(uid):
    return C.user(uid).get("lang", "ru")


def app_button(uid, code=None):
    url = WEBAPP_URL + (f"/?q={code}" if code else "/")
    return InlineKeyboardMarkup([[InlineKeyboardButton(T[lang(uid)]["open"], web_app=WebAppInfo(url=url))]])


# ================== СТУДЕНТ ==================
async def cmd_start(update: Update, ctx):
    uid = update.effective_user.id
    code = (ctx.args[0].upper() if ctx.args else "")
    if "lang" not in C.user(uid):
        kb = [[InlineKeyboardButton(v, callback_data=f"lg:{k}:{code}")] for k, v in LANGS.items()]
        await update.message.reply_text("🌐 Выберите язык / Tilni tanlang / Choose language / 选择语言",
                                        reply_markup=InlineKeyboardMarkup(kb))
        return
    await send_entry(update.message, uid, code)
    if is_admin(update.effective_user) and not code:
        await update.message.reply_text(ADMIN_HELP, parse_mode="HTML")


async def cmd_help(update: Update, ctx):
    if is_admin(update.effective_user):
        await update.message.reply_text(ADMIN_HELP, parse_mode="HTML")
    else:
        await send_entry(update.message, update.effective_user.id, None)


async def send_entry(message, uid, code):
    l = lang(uid)
    qz = C.STATE["quizzes"].get(code) if code else None
    text = T[l]["quiz"].format(t=e(qz["title"])) if qz else T[l]["welcome"]
    await message.reply_text(text, parse_mode="HTML", reply_markup=app_button(uid, code if qz else None))


# ================== АДМИН ==================
def stats_text(code):
    qz = C.STATE["quizzes"][code]
    rows = C.ranking(code)
    out = [f"📊 <b>{e(qz['title'])}</b>",
           f"🔑 Код: <code>{code}</code> · {'🟢 открыт' if qz.get('open', True) else '🔒 закрыт'}",
           f"❓ В банке: {len(qz['questions'])} · каждому: {qz['count']} · ⏱ {qz['time']} сек",
           f"👥 Прошли: <b>{len(rows)}</b>"]
    if rows:
        out.append(f"📈 Средний балл: <b>{sum(a['score'] for a in rows) / len(rows):.1f} из {qz['count']}</b>\n")
        for i, a in enumerate(rows[:25], 1):
            flag = f" ⚠️{a['left']}" if a.get("left") else ""
            out.append(f"{['🥇', '🥈', '🥉'][i - 1] if i <= 3 else f'{i}.'} {e(a['name'])} — "
                       f"<b>{a['score']}/{a['total']}</b> · {int(a['time'] // 60)}:{int(a['time'] % 60):02d}{flag}")
        if len(rows) > 25:
            out.append(f"… ещё {len(rows) - 25} — полный список в Excel")
        stat = {}
        for a in rows:
            for qi, ok in a["answers"]:
                c = stat.setdefault(qi, [0, 0])
                c[0] += ok
                c[1] += 1
        hard = sorted((c[0] / c[1], qi) for qi, c in stat.items() if c[1])[:3]
        if hard:
            out.append("\n🤯 <b>Самые сложные вопросы:</b>")
            out += [f"• {round(r * 100)}% верно — {e(qz['questions'][qi]['q'][:70])}" for r, qi in hard]
        out.append("\n⚠️N — сколько раз студент сворачивал приложение")
    return "\n".join(out)[:4000]


def admin_kb(code, bot_name):
    qz = C.STATE["quizzes"][code]
    total = len(qz["questions"])
    times = [InlineKeyboardButton(("✅" if qz["time"] == s else "") + f"{s}с", callback_data=f"tm:{code}:{s}")
             for s in (15, 20, 30, 45, 60)]
    counts = [InlineKeyboardButton(("✅" if qz["count"] == n else "") + str(n), callback_data=f"ct:{code}:{n}")
              for n in (10, 15, 20, 25, 30) if n < total]
    counts.append(InlineKeyboardButton(("✅" if qz["count"] == total else "") + f"Все {total}",
                                       callback_data=f"ct:{code}:{total}"))
    return InlineKeyboardMarkup([
        times, counts,
        [InlineKeyboardButton("🔄 Статистика", callback_data=f"st:{code}"),
         InlineKeyboardButton("📥 Excel", callback_data=f"csv:{code}")],
        [InlineKeyboardButton("🔒 Закрыть" if qz.get("open", True) else "🟢 Открыть", callback_data=f"op:{code}"),
         InlineKeyboardButton("🗑 Удалить", callback_data=f"del:{code}")],
        [InlineKeyboardButton("🔗 Ссылка для студентов", url=f"https://t.me/{bot_name}?start={code}")],
    ])


async def create_from_text(message, ctx, text, title):
    qz, bad = parse(text, title=title)
    if not qz["questions"]:
        await message.reply_text("❗ Не нашёл ни одного вопроса с правильным ответом.\n\n" + ADMIN_HELP,
                                 parse_mode="HTML")
        return
    code = C.add_quiz(qz, message.chat.id)
    link = f"https://t.me/{ctx.bot.username}?start={code}"
    warn = ""
    if bad:
        warn = f"\n\n⚠️ Пропущено {len(bad)} вопр. (нет правильного ответа или меньше 2 вариантов):\n" + \
               "\n".join("• " + e(b) for b in bad[:5])
    await message.reply_text(
        f"✅ <b>Тест загружен!</b>\n\n📝 {e(qz['title'])}\n❓ Вопросов: <b>{len(qz['questions'])}</b>\n"
        f"🔑 Код: <code>{code}</code>\n\n🔗 Отправьте студентам эту ссылку:\n{link}{warn}\n\n"
        f"Ниже можно поменять время на вопрос и сколько вопросов выдавать каждому 👇",
        parse_mode="HTML", reply_markup=admin_kb(code, ctx.bot.username))


async def on_document(update: Update, ctx):
    if not is_admin(update.effective_user):
        return
    doc = update.message.document
    name = (doc.file_name or "test").rsplit(".", 1)
    ext = name[-1].lower() if len(name) > 1 else ""
    if ext not in ("docx", "txt"):
        await update.message.reply_text("❗ Пришлите файл Word (.docx) или .txt. Старый формат .doc — "
                                        "откройте в Word и «Сохранить как» → .docx.")
        return
    data = bytes(await (await doc.get_file()).download_as_bytearray())
    try:
        text = docx_text(data) if ext == "docx" else data.decode("utf-8-sig", errors="replace")
    except Exception:
        await update.message.reply_text("❗ Не удалось прочитать файл. Сохраните его заново как .docx.")
        return
    await create_from_text(update.message, ctx, text, name[0])


async def cmd_new(update: Update, ctx):
    if is_admin(update.effective_user):
        DRAFTS[update.effective_user.id] = []
        await update.message.reply_text(ADMIN_HELP + "\n\n✍️ Вставьте текст теста (можно несколькими "
                                        "сообщениями), затем отправьте /done", parse_mode="HTML")


async def cmd_done(update: Update, ctx):
    uid = update.effective_user.id
    if is_admin(update.effective_user) and uid in DRAFTS:
        await create_from_text(update.message, ctx, "\n".join(DRAFTS.pop(uid)), "Тест")


async def cmd_quizzes(update: Update, ctx):
    if not is_admin(update.effective_user):
        return
    qs = sorted(C.STATE["quizzes"].items(), key=lambda x: -x[1].get("created", 0))
    if not qs:
        await update.message.reply_text("Тестов пока нет. Пришлите мне файл Word с тестом 📄")
        return
    kb = [[InlineKeyboardButton(f"{'🟢' if q.get('open', True) else '🔒'} {q['title'][:35]} · "
                                f"{len(C.ranking(c))} чел.", callback_data=f"st:{c}")] for c, q in qs[:40]]
    await update.message.reply_text("📚 <b>Ваши тесты</b> — нажмите, чтобы открыть статистику:",
                                    parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))


async def on_text(update: Update, ctx):
    uid = update.effective_user.id
    if uid in DRAFTS:
        DRAFTS[uid].append(update.message.text or "")
        await update.message.reply_text(f"📥 Принято ({len(DRAFTS[uid])}). Ещё текст или /done")
        return
    text = (update.message.text or "").strip().upper()
    await send_entry(update.message, uid, text if text in C.STATE["quizzes"] else None)


async def on_button(update: Update, ctx):
    q = update.callback_query
    parts = q.data.split(":")
    kind = parts[0]
    if kind == "lg":
        C.user(q.from_user.id)["lang"] = parts[1]
        C.save()
        await q.answer(LANGS[parts[1]])
        await send_entry(q.message, q.from_user.id, parts[2] if len(parts) > 2 else "")
        return
    code = parts[1] if len(parts) > 1 else ""
    if not is_admin(q.from_user) or code not in C.STATE["quizzes"]:
        await q.answer()
        return
    qz = C.STATE["quizzes"][code]
    if kind == "tm":
        qz["time"] = int(parts[2])
    elif kind == "ct":
        qz["count"] = min(int(parts[2]), len(qz["questions"]))
    elif kind == "op":
        qz["open"] = not qz.get("open", True)
    elif kind == "del":
        await q.answer()
        await q.message.reply_text(f"Удалить «{e(qz['title'])}» и все результаты?", parse_mode="HTML",
                                   reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                       "🗑 Да, удалить", callback_data=f"del2:{code}")]]))
        return
    elif kind == "del2":
        C.STATE["quizzes"].pop(code, None)
        C.STATE["attempts"].pop(code, None)
        C.save()
        await q.answer("Удалено")
        await q.edit_message_text("🗑 Тест удалён.")
        return
    elif kind == "csv":
        await q.answer()
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=";")
        w.writerow(["Место", "Имя и фамилия", "Баллы", "Из", "%", "Время (сек)", "Сворачивал"])
        for i, a in enumerate(C.ranking(code), 1):
            w.writerow([i, a["name"], a["score"], a["total"], round(100 * a["score"] / max(a["total"], 1)),
                        round(a["time"]), a.get("left", 0)])
        await ctx.bot.send_document(q.message.chat.id, InputFile(
            io.BytesIO(("\ufeff" + buf.getvalue()).encode("utf-8")), filename=f"{code}_results.csv"))
        return
    C.save()
    await q.answer("✅")
    try:
        await q.edit_message_text(stats_text(code), parse_mode="HTML", reply_markup=admin_kb(code, ctx.bot.username))
    except Exception:
        await q.message.reply_text(stats_text(code), parse_mode="HTML", reply_markup=admin_kb(code, ctx.bot.username))


async def post_init(app):
    app.bot_data["web"] = await start_web(BOT_TOKEN)
    if WEBAPP_URL:
        try:
            await app.bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(text="📝 Test", web_app=WebAppInfo(url=WEBAPP_URL)))
        except Exception:
            log.exception("Кнопка меню не установлена")


def main():
    if not WEBAPP_URL:
        log.warning("Нет адреса мини-приложения: в Railway нажмите Generate Domain")
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("new", cmd_new))
    app.add_handler(CommandHandler("done", cmd_done))
    app.add_handler(CommandHandler("quizzes", cmd_quizzes))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.Document.ALL & filters.ChatType.PRIVATE, on_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, on_text))
    log.info("Quiz-бот запущен: тестов %d", len(C.STATE["quizzes"]))
    app.run_polling()


if __name__ == "__main__":
    main()
