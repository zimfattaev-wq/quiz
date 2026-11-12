"""
TSUE QUIZ: тесты в мини-приложении. Любой может прислать тест — админ одобряет.
"""
import io
import os
import csv
import html
import logging

from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, WebAppInfo,
                      MenuButtonWebApp)
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, MessageHandler,
                          TypeHandler, filters)

import quiz_core as C
from quiz_parse import parse, docx_text
from quiz_web import good_name

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMINS = {x.strip().lstrip("@").lower() for x in os.environ.get("ADMINS", "fedex_azim").split(",") if x.strip()}
_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
WEBAPP_URL = os.environ.get("WEBAPP_URL") or (f"https://{_DOMAIN}" if _DOMAIN else "")
VERSION = "quiz v3"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("quiz")
e = lambda s: html.escape(str(s or ""))
DRAFTS = {}
WAIT_NAME = set()     # кто сейчас вводит новое имя (/name)
WEB = {"ok": False, "err": "не запускался"}
try:
    from quiz_web import start_web
except Exception as _ex:
    start_web = None
    WEB["err"] = f"quiz_web.py: {_ex}"

LANGS = {"ru": "🇷🇺 Русский", "uz": "🇺🇿 Oʻzbekcha", "en": "🇬🇧 English", "zh": "🇨🇳 中文"}
FORMAT = ("<pre>Название: Тест по микроэкономике\nПредмет: Микроэкономика\nВремя: 30\n\n"
          "1. Что такое инфляция?\nA) Рост общего уровня цен\nB) Снижение цен\nC) Рост ВВП\nD) Безработица\n"
          "Ответ: A\n\n2. Спрос — это...\nA) желание\nB) желание и возможность купить *\nC) цена\nD) товар</pre>")
T = {
    "ru": {"welcome": "👋 <b>TSUE QUIZ</b>\n\n📚 Нажмите кнопку ниже — откроется список всех тестов по предметам. "
                      "Выберите любой и проходите!\n\n➕ Хотите добавить свой тест? /add",
           "open": "📚 Открыть тесты",
           "add": "➕ <b>Как добавить свой тест</b>\n\nОтправьте мне <b>файл Word (.docx) или .txt</b> — или команду /new, "
                  "затем текст теста и /done.\n\nФормат:\n" + FORMAT +
                  "\n✅ Правильный ответ — строка «Ответ: A» или звёздочка * у варианта.\n"
                  "После проверки тест появится у всех в приложении.",
           "draft": "📥 Принято ({n}). Ещё текст или /done", "start_draft": "✍️ Вставьте текст теста, затем /done",
           "sent": "📨 Тест «{t}» ({n} вопр.) отправлен на проверку. Я сообщу, когда его одобрят.",
           "ok": "✅ Ваш тест «{t}» одобрен и опубликован! Его уже видят все в приложении.",
           "no": "❌ Ваш тест «{t}» не прошёл проверку.",
           "bad": "❗ Не нашёл ни одного вопроса с правильным ответом. Формат: /add",
           "badfile": "❗ Пришлите файл .docx или .txt (старый .doc — «Сохранить как» → .docx)."},
    "uz": {"welcome": "👋 <b>TSUE QUIZ</b>\n\n📚 Quyidagi tugmani bosing — fanlar boʻyicha barcha testlar roʻyxati "
                      "ochiladi. Istalganini tanlang!\n\n➕ Oʻz testingizni qoʻshmoqchimisiz? /add",
           "open": "📚 Testlarni ochish",
           "add": "➕ <b>Oʻz testingizni qanday qoʻshish</b>\n\nMenga <b>Word (.docx) yoki .txt fayl</b> yuboring — yoki /new "
                  "buyrugʻi, keyin test matni va /done.\n\nFormat:\n" + FORMAT.replace("Название", "Nomi")
                  .replace("Предмет", "Fan").replace("Время", "Vaqt").replace("Ответ", "Javob") +
                  "\n✅ Toʻgʻri javob — «Javob: A» qatori yoki variantdagi * belgisi.\n"
                  "Tekshiruvdan soʻng test hammaga koʻrinadi.",
           "draft": "📥 Qabul qilindi ({n}). Yana matn yoki /done", "start_draft": "✍️ Test matnini yuboring, keyin /done",
           "sent": "📨 «{t}» testi ({n} savol) tekshiruvga yuborildi. Tasdiqlanganda xabar beraman.",
           "ok": "✅ «{t}» testingiz tasdiqlandi va eʼlon qilindi!",
           "no": "❌ «{t}» testingiz tekshiruvdan oʻtmadi.",
           "bad": "❗ Toʻgʻri javobli savol topilmadi. Format: /add",
           "badfile": "❗ .docx yoki .txt fayl yuboring."},
    "en": {"welcome": "👋 <b>TSUE QUIZ</b>\n\n📚 Tap the button below to see all tests by subject. "
                      "Choose any and start!\n\n➕ Want to add your own test? /add",
           "open": "📚 Open tests",
           "add": "➕ <b>How to add your test</b>\n\nSend me a <b>Word (.docx) or .txt file</b> — or /new, then the "
                  "test text and /done.\n\nFormat:\n" + FORMAT.replace("Название", "Title").replace("Предмет", "Subject")
                  .replace("Время", "Time").replace("Ответ", "Answer") +
                  "\n✅ Correct answer — line «Answer: A» or * after the option.\nAfter review the test is visible to everyone.",
           "draft": "📥 Received ({n}). More text or /done", "start_draft": "✍️ Paste the test text, then /done",
           "sent": "📨 Test «{t}» ({n} q.) was sent for review. I'll tell you when it is approved.",
           "ok": "✅ Your test «{t}» is approved and published!", "no": "❌ Your test «{t}» was not approved.",
           "bad": "❗ No questions with a correct answer found. Format: /add",
           "badfile": "❗ Send a .docx or .txt file."},
    "zh": {"welcome": "👋 <b>TSUE QUIZ</b>\n\n📚 点击下方按钮查看各科目的全部测验，任选一个开始吧！\n\n➕ 想添加自己的测验？/add",
           "open": "📚 打开测验",
           "add": "➕ <b>如何添加测验</b>\n\n发送 <b>Word (.docx) 或 .txt 文件</b>，或发送 /new，然后发送测验文本并 /done。\n\n"
                  "格式：\n" + FORMAT.replace("Название", "Title").replace("Предмет", "Subject")
                  .replace("Время", "Time").replace("Ответ", "Answer") + "\n✅ 正确答案：写「Answer: A」或在选项后加 *。\n审核通过后所有人可见。",
           "draft": "📥 已收到（{n}）。继续发送或 /done", "start_draft": "✍️ 请粘贴测验文本，然后 /done",
           "sent": "📨 测验「{t}」（{n} 题）已提交审核，通过后会通知您。",
           "ok": "✅ 您的测验「{t}」已通过审核并发布！", "no": "❌ 您的测验「{t}」未通过审核。",
           "bad": "❗ 未找到带正确答案的题目。格式：/add", "badfile": "❗ 请发送 .docx 或 .txt 文件。"},
}


for _l, _d in {
    'ru': {
        'lv': ['🌱 Новичок', '📘 Знаток', '🎯 Эксперт', '🏆 Мастер', '👑 Легенда'],
        'prof': "👤 <b>{name}</b>\n{lv} · <b>{xp}</b> опыта{nxt}\n\n📝 Тестов: <b>{tests}</b>\n📈 Средний результат: <b>{pct}%</b> · {pts}/50 баллов\n🏅 Лучший: <b>{best}%</b>",
        'nxt': "\n⬆️ До следующего уровня: {n}",
        'subj': "\n\n📘 <b>По предметам:</b>",
        'hist': "\n\n🗂 <b>Последние тесты:</b>",
        'nohist': "\n\nВы ещё не прошли ни одного теста. Откройте приложение 👇",
        'noname': "Сначала откройте приложение и укажите имя 👇",
        'ask_name': "✍️ Напишите правильные <b>имя и фамилию</b> (как в журнале), например: <i>Azimov Aziz</i>",
        'bad_name': "❗ Нужно два слова, только буквы. Попробуйте ещё раз или /cancel",
        'name_ok': "✅ Имя изменено: <b>{n}</b>\nОно обновилось и во всех ваших результатах.",
        'cancel': "Отменено.",
    },
    'uz': {
        'lv': ['🌱 Yangi boshlovchi', '📘 Bilimdon', '🎯 Ekspert', '🏆 Usta', '👑 Afsona'],
        'prof': "👤 <b>{name}</b>\n{lv} · <b>{xp}</b> tajriba{nxt}\n\n📝 Testlar: <b>{tests}</b>\n📈 Oʻrtacha natija: <b>{pct}%</b> · {pts}/50 ball\n🏅 Eng yaxshi: <b>{best}%</b>",
        'nxt': "\n⬆️ Keyingi darajagacha: {n}",
        'subj': "\n\n📘 <b>Fanlar boʻyicha:</b>",
        'hist': "\n\n🗂 <b>Soʻnggi testlar:</b>",
        'nohist': "\n\nSiz hali birorta test topshirmagansiz. Ilovani oching 👇",
        'noname': "Avval ilovani ochib, ismingizni kiriting 👇",
        'ask_name': "✍️ Toʻgʻri <b>ism va familiyangizni</b> yozing (jurnaldagidek), masalan: <i>Azimov Aziz</i>",
        'bad_name': "❗ Ikki soʻz, faqat harflar boʻlishi kerak. Qayta urinib koʻring yoki /cancel",
        'name_ok': "✅ Ism oʻzgartirildi: <b>{n}</b>\nBarcha natijalaringizda ham yangilandi.",
        'cancel': "Bekor qilindi.",
    },
    'en': {
        'lv': ['🌱 Beginner', '📘 Learner', '🎯 Expert', '🏆 Master', '👑 Legend'],
        'prof': "👤 <b>{name}</b>\n{lv} · <b>{xp}</b> XP{nxt}\n\n📝 Tests: <b>{tests}</b>\n📈 Average: <b>{pct}%</b> · {pts}/50 points\n🏅 Best: <b>{best}%</b>",
        'nxt': "\n⬆️ To next level: {n}",
        'subj': "\n\n📘 <b>By subject:</b>",
        'hist': "\n\n🗂 <b>Recent tests:</b>",
        'nohist': "\n\nYou haven't taken any tests yet. Open the app 👇",
        'noname': "First open the app and enter your name 👇",
        'ask_name': "✍️ Type your correct <b>first and last name</b>, e.g. <i>Azimov Aziz</i>",
        'bad_name': "❗ Two words, letters only. Try again or /cancel",
        'name_ok': "✅ Name changed: <b>{n}</b>\nIt was updated in all your results too.",
        'cancel': "Cancelled.",
    },
    'zh': {
        'lv': ['🌱 新手', '📘 学徒', '🎯 专家', '🏆 大师', '👑 传奇'],
        'prof': "👤 <b>{name}</b>\n{lv} · <b>{xp}</b> 经验{nxt}\n\n📝 测验：<b>{tests}</b>\n📈 平均成绩：<b>{pct}%</b> · {pts}/50 分\n🏅 最佳：<b>{best}%</b>",
        'nxt': "\n⬆️ 距下一级：{n}",
        'subj': "\n\n📘 <b>各科成绩：</b>",
        'hist': "\n\n🗂 <b>最近的测验：</b>",
        'nohist': "\n\n您还没有完成任何测验。请打开应用 👇",
        'noname': "请先打开应用并输入姓名 👇",
        'ask_name': "✍️ 请输入正确的<b>名和姓</b>，例如：<i>Azimov Aziz</i>",
        'bad_name': "❗ 需要两个词，只能是字母。请重试或 /cancel",
        'name_ok': "✅ 姓名已修改：<b>{n}</b>\n所有成绩中的姓名也已更新。",
        'cancel': "已取消。",
    },
}.items():
    T[_l].update(_d)

ADMIN_HELP = ("🛠 <b>Админ</b>\n/quizzes — все тесты, статистика, Excel, настройки\n/pending — тесты на проверке\n"
              "/stats — статистика бота\n/diag — проверка работы\n\nВаши тесты публикуются сразу, тесты других — "
              "после вашего ✅.")


def is_admin(u):
    return bool(u) and ((u.username or "").lower() in ADMINS or str(u.id) in ADMINS)


def lang(uid):
    return C.user(uid).get("lang", "ru")


def t(uid, key, **kw):
    s = T[lang(uid)][key]
    return s.format(**kw) if kw else s


def app_kb(uid, code=None):
    url = WEBAPP_URL + (f"/?q={code}" if code else "/")
    return InlineKeyboardMarkup([[InlineKeyboardButton(t(uid, "open"), web_app=WebAppInfo(url=url))]])


async def track(update: Update, ctx):
    u = update.effective_user
    if u:
        C.touch(u.id, u.username or "", u.first_name or "")
        if is_admin(u) and str(update.effective_chat.id) not in C.STATE["admins"]:
            C.STATE["admins"][str(update.effective_chat.id)] = u.username or ""
            C.save()


# ================== ВСЕ ==================
async def cmd_start(update: Update, ctx):
    uid = update.effective_user.id
    code = ctx.args[0].upper() if ctx.args else ""
    if "lang" not in C.user(uid):
        kb = [[InlineKeyboardButton(v, callback_data=f"lg:{k}:{code}")] for k, v in LANGS.items()]
        await update.message.reply_text("🌐 Выберите язык / Tilni tanlang / Choose language / 选择语言",
                                        reply_markup=InlineKeyboardMarkup(kb))
        return
    await entry(update.message, uid, code)
    if is_admin(update.effective_user):
        await update.message.reply_text(ADMIN_HELP, parse_mode="HTML")


async def entry(message, uid, code=""):
    ok = code and C.info(code, uid)
    await message.reply_text(t(uid, "welcome"), parse_mode="HTML", reply_markup=app_kb(uid, code if ok else None))


async def cmd_add(update: Update, ctx):
    await update.message.reply_text(t(update.effective_user.id, "add"), parse_mode="HTML")


async def cmd_new(update: Update, ctx):
    DRAFTS[update.effective_user.id] = []
    await update.message.reply_text(t(update.effective_user.id, "start_draft"))


async def cmd_done(update: Update, ctx):
    uid = update.effective_user.id
    if uid in DRAFTS:
        await submit(update, ctx, "\n".join(DRAFTS.pop(uid)), "Тест")


async def on_document(update: Update, ctx):
    uid = update.effective_user.id
    doc = update.message.document
    name = (doc.file_name or "test").rsplit(".", 1)
    ext = name[-1].lower() if len(name) > 1 else ""
    if ext not in ("docx", "txt"):
        await update.message.reply_text(t(uid, "badfile"))
        return
    data = bytes(await (await doc.get_file()).download_as_bytearray())
    try:
        text = docx_text(data) if ext == "docx" else data.decode("utf-8-sig", errors="replace")
    except Exception:
        await update.message.reply_text(t(uid, "badfile"))
        return
    await submit(update, ctx, text, name[0])


async def submit(update, ctx, text, title):
    u = update.effective_user
    qz, bad = parse(text, title=title)
    if not qz["questions"]:
        await update.message.reply_text(t(u.id, "bad"))
        return
    author = C.user(u.id).get("name") or u.full_name or ""
    if u.username:
        author += f" (@{u.username})"
    admin = is_admin(u)
    code = C.add_quiz(qz, u.id, author, approved=admin)
    warn = f"\n⚠️ Пропущено {len(bad)} вопр. без правильного ответа." if bad else ""
    if admin:
        await update.message.reply_text(f"✅ <b>Тест опубликован!</b>\n\n{card_text(code)}{warn}",
                                        parse_mode="HTML", reply_markup=admin_kb(code))
        return
    await update.message.reply_text(t(u.id, "sent", t=e(qz["title"]), n=len(qz["questions"])) + warn)
    for chat_id in list(C.STATE["admins"]):
        try:
            await ctx.bot.send_message(int(chat_id), "🆕 <b>Новый тест на проверку</b>\n\n" + preview(code),
                                       parse_mode="HTML", reply_markup=review_kb(code))
        except Exception:
            log.exception("Админ %s не получил уведомление", chat_id)


async def cmd_profile(update: Update, ctx):
    uid = update.effective_user.id
    if not C.user(uid).get("name"):
        await update.message.reply_text(t(uid, "noname"), reply_markup=app_kb(uid))
        return
    p = C.profile(uid)
    nxt = t(uid, "nxt").format(n=p["lvl_to"] - p["xp"]) if p["lvl_to"] else ""
    text = t(uid, "prof").format(name=e(p["name"]), lv=T[lang(uid)]["lv"][p["level"]], xp=p["xp"], nxt=nxt,
                                 tests=p["tests"], pct=p["avg_pct"], pts=p["avg_points"], best=p["best"])
    if p["subjects"]:
        text += t(uid, "subj") + "".join(f"\n• {e(s[0])} — {s[1]}% ({s[2]})" for s in p["subjects"][:8])
    if p["history"]:
        text += t(uid, "hist") + "".join(f"\n• {e(h['title'][:40])} — <b>{h['pct']}%</b> · {h['points']}/50 · "
                                         f"{h['place']}/{h['all']}" for h in p["history"][:5])
    else:
        text += t(uid, "nohist")
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=app_kb(uid))


async def cmd_name(update: Update, ctx):
    uid = update.effective_user.id
    WAIT_NAME.add(uid)
    await update.message.reply_text(t(uid, "ask_name"), parse_mode="HTML")


async def cmd_cancel(update: Update, ctx):
    uid = update.effective_user.id
    WAIT_NAME.discard(uid)
    DRAFTS.pop(uid, None)
    await update.message.reply_text(t(uid, "cancel"))


async def on_text(update: Update, ctx):
    uid = update.effective_user.id
    if uid in WAIT_NAME:
        name = " ".join(w.capitalize() for w in (update.message.text or "").split())
        if not good_name(name):
            await update.message.reply_text(t(uid, "bad_name"))
            return
        WAIT_NAME.discard(uid)
        C.user(uid)["name"] = name
        for atts in C.STATE["attempts"].values():
            if str(uid) in atts:
                atts[str(uid)]["name"] = name
        C.save()
        await update.message.reply_text(t(uid, "name_ok").format(n=e(name)), parse_mode="HTML")
        return
    if uid in DRAFTS:
        DRAFTS[uid].append(update.message.text or "")
        await update.message.reply_text(t(uid, "draft", n=len(DRAFTS[uid])))
        return
    await entry(update.message, uid)


# ================== АДМИН ==================
def card_text(code):
    qz = C.STATE["quizzes"][code]
    st = {"approved": "🟢 открыт" if qz.get("open", True) else "🔒 закрыт", "pending": "⏳ на проверке"}
    return (f"📝 <b>{e(qz['title'])}</b>\n📘 Предмет: {e(qz.get('subject') or '—')}\n"
            f"👤 Автор: {e(qz.get('author') or '—')}\n"
            f"❓ В банке: {len(qz['questions'])} · каждому: {qz['count']} · ⏱ {qz['time']} сек\n"
            f"Статус: {st.get(qz.get('status', 'approved'), '')}")


def preview(code):
    qz = C.STATE["quizzes"][code]
    out = [card_text(code), "", "<b>Первые вопросы:</b>"]
    for i, q in enumerate(qz["questions"][:3], 1):
        out.append(f"\n{i}. {e(q['q'][:150])}")
        out += [f"{'✅' if k == q['right'] else '▫️'} {e(o[:80])}" for k, o in enumerate(q["opts"])]
    return "\n".join(out)[:4000]


def review_kb(code):
    return InlineKeyboardMarkup([[InlineKeyboardButton("✅ Разрешить", callback_data=f"ap:{code}"),
                                  InlineKeyboardButton("❌ Отклонить", callback_data=f"rj:{code}")]])


def stats_text(code):
    qz = C.STATE["quizzes"][code]
    rows = C.ranking(code)
    out = [card_text(code), f"👥 Прошли: <b>{len(rows)}</b>"]
    if rows:
        avg = sum(C.pct(a["score"], a["total"]) for a in rows) / len(rows)
        out.append(f"📈 Средний результат: <b>{avg:.0f}%</b> · {C.points(avg, 100)}/{C.MAX_POINTS} баллов\n")
        for i, a in enumerate(rows[:25], 1):
            flag = f" ⚠️{a['left']}" if a.get("left") else ""
            out.append(f"{['🥇', '🥈', '🥉'][i - 1] if i <= 3 else f'{i}.'} {e(a['name'])} — "
                       f"<b>{C.pct(a['score'], a['total'])}%</b> · {C.points(a['score'], a['total'])}/50 · "
                       f"{a['score']}/{a['total']} верно{flag}")
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
    return "\n".join(out)[:4000]


def admin_kb(code):
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
    ])


async def cmd_quizzes(update: Update, ctx):
    if not is_admin(update.effective_user):
        return
    qs = sorted(C.STATE["quizzes"].items(), key=lambda x: -x[1].get("created", 0))
    if not qs:
        await update.message.reply_text("Тестов пока нет. Пришлите файл Word с тестом 📄")
        return
    icon = lambda q: "⏳" if q.get("status") == "pending" else ("🟢" if q.get("open", True) else "🔒")
    kb = [[InlineKeyboardButton(f"{icon(q)} {(q.get('subject') or '')[:15]} · {q['title'][:28]} · "
                                f"{len(C.ranking(c))} чел.", callback_data=f"st:{c}")] for c, q in qs[:50]]
    await update.message.reply_text("📚 <b>Все тесты</b> (⏳ — ждут проверки):", parse_mode="HTML",
                                    reply_markup=InlineKeyboardMarkup(kb))


async def cmd_pending(update: Update, ctx):
    if not is_admin(update.effective_user):
        return
    pend = [c for c, q in C.STATE["quizzes"].items() if q.get("status") == "pending"]
    if not pend:
        await update.message.reply_text("✅ Нет тестов на проверке.")
    for code in pend[:10]:
        await update.message.reply_text("⏳ <b>На проверке</b>\n\n" + preview(code), parse_mode="HTML",
                                        reply_markup=review_kb(code))


async def cmd_stats(update: Update, ctx):
    if not is_admin(update.effective_user):
        return
    s = C.bot_stats()
    subj = "\n".join(f"  • {e(n)} — {c}" for n, c in s["subjects"]) or "  —"
    pop = "\n".join(f"  {i}. {e(tl[:35])} — {n} чел." for i, (n, tl) in enumerate(s["popular"], 1)) or "  —"
    lg = " · ".join(f"{LANGS.get(k, k).split()[0]} {v}" for k, v in s["langs"].most_common())
    await update.message.reply_text(
        f"📊 <b>Статистика TSUE QUIZ</b>\n\n"
        f"👤 Пользователей: <b>{s['users']}</b> (с именем: {s['with_name']})\n"
        f"🟢 Активны сегодня: <b>{s['active_today']}</b> · за 7 дней: <b>{s['active_week']}</b>\n"
        f"🆕 Новых сегодня: <b>{s['new_today']}</b> · за 7 дней: <b>{s['new_week']}</b>\n\n"
        f"📚 Тестов: <b>{s['tests']}</b> (открыто {s['open']}) · ⏳ на проверке: <b>{s['pending']}</b>\n"
        f"✍️ Пройдено тестов: <b>{s['attempts']}</b> · сегодня: <b>{s['attempts_today']}</b>\n"
        f"⏳ Проходят прямо сейчас: <b>{s['in_progress']}</b>\n"
        f"📈 Средний результат: <b>{s['avg_pct']}%</b> · {C.points(s['avg_pct'], 100)}/50 баллов\n\n"
        f"📘 <b>Предметы:</b>\n{subj}\n\n🏆 <b>Популярные тесты:</b>\n{pop}\n\n🌐 Языки: {lg or '—'}",
        parse_mode="HTML")


async def cmd_diag(update: Update, ctx):
    if not is_admin(update.effective_user):
        return
    try:
        with open(C.STATE_FILE, "a", encoding="utf-8"):
            pass
        storage = f"✅ {C.STATE_FILE}"
    except Exception as ex:
        storage = f"❌ {C.STATE_FILE}: {ex}"
    await update.message.reply_text(
        f"🛠 <b>Диагностика</b> ({VERSION})\n\n"
        f"🌐 Мини-приложение: {'✅ работает' if WEB['ok'] else '❌ ' + e(WEB['err'])}\n"
        f"🔗 Адрес: {e(WEBAPP_URL or 'нет — нажмите Generate Domain в Railway')}\n"
        f"💾 База данных: {e(storage)}\n"
        f"👤 Пользователей: {len(C.STATE['users'])} · 📚 тестов: {len(C.STATE['quizzes'])}\n"
        f"👮 Админов для уведомлений: {len(C.STATE['admins'])}", parse_mode="HTML")


async def on_button(update: Update, ctx):
    q = update.callback_query
    parts = q.data.split(":")
    kind = parts[0]
    if kind == "lg":
        C.user(q.from_user.id)["lang"] = parts[1]
        C.save()
        await q.answer(LANGS[parts[1]])
        await entry(q.message, q.from_user.id, parts[2] if len(parts) > 2 else "")
        return
    code = parts[1] if len(parts) > 1 else ""
    if not is_admin(q.from_user) or code not in C.STATE["quizzes"]:
        await q.answer()
        return
    qz = C.STATE["quizzes"][code]
    if kind in ("ap", "rj"):
        if qz.get("status") != "pending":
            await q.answer("Уже рассмотрено")
            return
        author = qz.get("owner")
        if kind == "ap":
            qz.update(status="approved", open=True)
            C.save()
            await q.answer("✅ Опубликован")
            await q.edit_message_text("✅ <b>Одобрено и опубликовано</b>\n\n" + card_text(code), parse_mode="HTML",
                                      reply_markup=admin_kb(code))
        else:
            C.STATE["quizzes"].pop(code, None)
            C.save()
            await q.answer("❌ Отклонён")
            await q.edit_message_text(f"❌ Отклонено: {e(qz['title'])}", parse_mode="HTML")
        try:
            await ctx.bot.send_message(int(author), t(author, "ok" if kind == "ap" else "no", t=qz["title"]),
                                       reply_markup=app_kb(author) if kind == "ap" else None)
        except Exception:
            pass
        return
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
        w.writerow(["Место", "Имя и фамилия", "%", "Баллы из 50", "Правильных", "Всего вопросов",
                    "Время (сек)", "Сворачивал"])
        for i, a in enumerate(C.ranking(code), 1):
            w.writerow([i, a["name"], C.pct(a["score"], a["total"]), C.points(a["score"], a["total"]),
                        a["score"], a["total"], round(a["time"]), a.get("left", 0)])
        await ctx.bot.send_document(q.message.chat.id, InputFile(
            io.BytesIO(("\ufeff" + buf.getvalue()).encode("utf-8")), filename=f"{qz['title'][:30]}.csv"))
        return
    if qz.get("status") == "pending" and kind == "st":
        await q.answer()
        await q.message.reply_text("⏳ <b>На проверке</b>\n\n" + preview(code), parse_mode="HTML",
                                   reply_markup=review_kb(code))
        return
    C.save()
    await q.answer("✅")
    try:
        await q.edit_message_text(stats_text(code), parse_mode="HTML", reply_markup=admin_kb(code))
    except Exception:
        await q.message.reply_text(stats_text(code), parse_mode="HTML", reply_markup=admin_kb(code))


async def post_init(app):
    if start_web:
        try:
            app.bot_data["web"] = await start_web(BOT_TOKEN)
            WEB.update(ok=True, err="")
        except Exception as ex:
            WEB.update(ok=False, err=f"{type(ex).__name__}: {ex}")
            log.exception("Мини-приложение не запустилось")
    if WEBAPP_URL:
        try:
            await app.bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(text="📚 Tests", web_app=WebAppInfo(url=WEBAPP_URL)))
        except Exception:
            log.exception("Кнопка меню не установлена")


def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(TypeHandler(Update, track), group=-1)
    for name, fn in [("start", cmd_start), ("help", cmd_add), ("add", cmd_add), ("new", cmd_new),
                     ("profile", cmd_profile), ("name", cmd_name), ("cancel", cmd_cancel),
                     ("done", cmd_done), ("quizzes", cmd_quizzes), ("pending", cmd_pending),
                     ("stats", cmd_stats), ("diag", cmd_diag)]:
        app.add_handler(CommandHandler(name, fn))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.Document.ALL & filters.ChatType.PRIVATE, on_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, on_text))
    log.info("TSUE QUIZ запущен: тестов %d", len(C.STATE["quizzes"]))
    app.run_polling()


if __name__ == "__main__":
    main()
