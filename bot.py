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
VERSION = "quiz v7"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("quiz")
e = lambda s: html.escape(str(s or ""))
DRAFTS = {}
UPLOADS = {}          # загруженный тест ждёт выбора: тест или тренажёр
K = {   # тест / тренажёр
    "ru": {"kind_q": "📦 Принято: «{t}» — {n} вопр.\n\nКуда добавить?",
           "k_test": "📝 Тест (для всех, с рейтингом)", "k_tr": "🏋️ Тренажёр (практика)",
           "add_more": "\n\n🏋️ После загрузки выберите: <b>тест</b> (одна попытка, рейтинг) или <b>тренажёр</b> "
                       "(сколько угодно раз, сразу видно правильный ответ).", "expired": "Загрузите файл ещё раз."},
    "uz": {"kind_q": "📦 Qabul qilindi: «{t}» — {n} savol\n\nQayerga qoʻshamiz?",
           "k_test": "📝 Test (hamma uchun, reyting)", "k_tr": "🏋️ Trenajor (mashq)",
           "add_more": "\n\n🏋️ Yuklagandan soʻng tanlang: <b>test</b> (bitta urinish, reyting) yoki <b>trenajor</b> "
                       "(xohlagancha, toʻgʻri javob darhol koʻrinadi).", "expired": "Faylni qayta yuboring."},
    "en": {"kind_q": "📦 Received: “{t}” — {n} q.\n\nWhere to add it?",
           "k_test": "📝 Test (for everyone, ranked)", "k_tr": "🏋️ Trainer (practice)",
           "add_more": "\n\n🏋️ After uploading choose: <b>test</b> (one attempt, ranking) or <b>trainer</b> "
                       "(unlimited, correct answer shown at once).", "expired": "Please send the file again."},
    "zh": {"kind_q": "📦 已收到：「{t}」— {n} 题\n\n添加到哪里？",
           "k_test": "📝 测验（所有人，排名）", "k_tr": "🏋️ 练习（无限次）",
           "add_more": "\n\n🏋️ 上传后请选择：<b>测验</b>（一次机会，排名）或 <b>练习</b>（无限次，立即显示正确答案）。",
           "expired": "请重新发送文件。"},
}
TIMES = (10, 15, 30, 40, 60)
WAIT_NAME = set()     # кто сейчас вводит новое имя (/name)
EDIT = {}             # админ -> (поле, код теста): ждём новый предмет или название
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

for _l, _d in {
    'ru': {
        't_head': "\n\n🗂 <b>Пройденные тесты:</b>",
        't_subj': "📘 Предмет: {s}",
        't_res': "✅ <b>{pct}%</b> · 🎯 <b>{pts}/50</b> баллов · ✔️ {c}/{n} верно",
        't_place': "🏆 Место {p} из {a} · 📅 {d}",
        'btn_certs': "🏅 Мои сертификаты",
        'certs_none': "У вас пока нет сертификатов.\nОткройте пройденный тест в приложении и нажмите «🏅 Сертификат».",
        'certs_head': "🏅 <b>Ваши сертификаты: {n}</b>",
        'subj_head': "\n\n📘 <b>По предметам:</b>",
    },
    'uz': {
        't_head': "\n\n🗂 <b>Topshirilgan testlar:</b>",
        't_subj': "📘 Fan: {s}",
        't_res': "✅ <b>{pct}%</b> · 🎯 <b>{pts}/50</b> ball · ✔️ {c}/{n} toʻgʻri",
        't_place': "🏆 {a} tadan {p}-oʻrin · 📅 {d}",
        'btn_certs': "🏅 Sertifikatlarim",
        'certs_none': "Sizda hali sertifikat yoʻq.\nIlovada topshirilgan testni oching va «🏅 Sertifikat» tugmasini bosing.",
        'certs_head': "🏅 <b>Sertifikatlaringiz: {n}</b>",
        'subj_head': "\n\n📘 <b>Fanlar boʻyicha:</b>",
    },
    'en': {
        't_head': "\n\n🗂 <b>Completed tests:</b>",
        't_subj': "📘 Subject: {s}",
        't_res': "✅ <b>{pct}%</b> · 🎯 <b>{pts}/50</b> points · ✔️ {c}/{n} correct",
        't_place': "🏆 Place {p} of {a} · 📅 {d}",
        'btn_certs': "🏅 My certificates",
        'certs_none': "You have no certificates yet.\nOpen a completed test in the app and tap «🏅 Certificate».",
        'certs_head': "🏅 <b>Your certificates: {n}</b>",
        'subj_head': "\n\n📘 <b>By subject:</b>",
    },
    'zh': {
        't_head': "\n\n🗂 <b>已完成的测验：</b>",
        't_subj': "📘 科目：{s}",
        't_res': "✅ <b>{pct}%</b> · 🎯 <b>{pts}/50</b> 分 · ✔️ 答对 {c}/{n}",
        't_place': "🏆 第 {p} 名 / 共 {a} 人 · 📅 {d}",
        'btn_certs': "🏅 我的证书",
        'certs_none': "您还没有证书。\n请在应用中打开已完成的测验，点击「🏅 证书」。",
        'certs_head': "🏅 <b>您的证书：{n}</b>",
        'subj_head': "\n\n📘 <b>各科成绩：</b>",
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


def k(uid, key):
    return K.get(lang(uid), K["ru"])[key]


async def cmd_add(update: Update, ctx):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, "add") + k(uid, "add_more"), parse_mode="HTML")


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
    """Файл разобран — спрашиваем: тест для всех или тренажёр."""
    u = update.effective_user
    qz, bad = parse(text, title=title)
    if not qz["questions"]:
        await update.message.reply_text(t(u.id, "bad"))
        return
    UPLOADS[u.id] = (qz, bad)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(k(u.id, "k_test"), callback_data="kd:test")],
                               [InlineKeyboardButton(k(u.id, "k_tr"), callback_data="kd:trainer")]])
    await update.message.reply_text(k(u.id, "kind_q").format(t=qz["title"], n=len(qz["questions"])), reply_markup=kb)


async def publish(bot, u, chat_id, qz, bad, kind):
    author = C.user(u.id).get("name") or u.full_name or ""
    if u.username:
        author += f" (@{u.username})"
    admin = is_admin(u)
    code = C.add_quiz(qz, u.id, author, approved=admin, kind=kind)
    warn = f"\n⚠️ Пропущено {len(bad)} вопр. без правильного ответа." if bad else ""
    if admin:
        await bot.send_message(chat_id, f"✅ <b>Опубликовано!</b>\n\n{card_text(code)}{warn}",
                               parse_mode="HTML", reply_markup=admin_kb(code))
        return
    await bot.send_message(chat_id, t(u.id, "sent", t=e(qz["title"]), n=len(qz["questions"])) + warn)
    for chat_id in list(C.STATE["admins"]):
        try:
            await bot.send_message(int(chat_id), "🆕 <b>Новый тест на проверку</b>\n\n" + preview(code),
                                       parse_mode="HTML", reply_markup=review_kb(code))
        except Exception:
            log.exception("Админ %s не получил уведомление", chat_id)

