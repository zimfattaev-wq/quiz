<style>
.qbar{display:flex;gap:8px;margin:8px 0 4px}
.qbar button{flex:1;border:1px solid var(--line);background:#fff;color:var(--text);border-radius:14px;padding:10px 6px;font-size:14px;font-weight:700}
.qbar button.fire{flex:0 0 auto;padding:10px 14px;color:#e8590c}
.qbar button.fire.off{color:var(--hint)}
body:not(.lock) .qtext,body:not(.lock) .opt span,body:not(.lock) .rq,body:not(.lock) .rq *,body:not(.lock) .fc,body:not(.lock) .fc *{-webkit-user-select:text;user-select:text}
.rep{display:block;margin:12px auto 0;background:none;border:0;color:var(--hint);font-size:14px;text-decoration:underline}
.ovl{position:fixed;inset:0;background:rgba(11,31,68,.45);display:flex;align-items:flex-end;justify-content:center;z-index:50}
.ovl .box{background:#fff;width:100%;max-width:560px;border-radius:20px 20px 0 0;padding:18px 16px calc(18px + env(safe-area-inset-bottom))}
.ovl textarea{width:100%;min-height:90px;border:1px solid var(--line);border-radius:12px;padding:10px;font:inherit;font-size:16px;margin:10px 0;-webkit-user-select:text;user-select:text}
.badge{display:inline-block;font-size:11px;font-weight:800;border-radius:8px;padding:2px 7px;margin-left:6px;vertical-align:middle}
.badge.z{background:#eaf1ff;color:var(--accent)}.badge.p{background:#fff1e6;color:#d9480f}.badge.r{background:#ebfbee;color:var(--green)}
.hi{display:flex;align-items:center;gap:10px;width:100%;text-align:left;background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px;margin:8px 0;color:var(--text)}
.hi .tt{flex:1;min-width:0}.hi .tt b{display:block;font-size:15px}.hi .tt span{font-size:12px;color:var(--hint)}
.hi .pc{font-weight:800;color:var(--accent);white-space:nowrap}.hi .ic{font-size:22px}
.fc{min-height:220px;display:flex;flex-direction:column;justify-content:center;text-align:center;background:#fff;border:2px solid var(--line);
  border-radius:20px;padding:22px;margin:12px 0;cursor:pointer;transition:transform .35s;font-size:18px;font-weight:700;line-height:1.4}
.fc.back{border-color:var(--green);background:rgba(31,157,87,.06)}
.fc .hint{font-size:13px;font-weight:500;color:var(--hint);margin-top:14px}
.fc .ans{color:var(--green);font-size:19px;margin-top:12px}
.flip{transform:rotateY(90deg)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.two .btn{margin:0}.btn.red{background:var(--red)}.btn.green{background:var(--green)}
.days{display:flex;gap:5px;justify-content:center;margin:12px 0}
.days i{width:16px;height:16px;border-radius:5px;background:var(--line)}.days i.on{background:#fd7e14}
.big2{font-size:56px;font-weight:900;text-align:center;color:#e8590c;line-height:1.1}
.pk{display:flex;gap:10px;width:100%;text-align:left;background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px;margin:8px 0;color:var(--text);font-size:15px;line-height:1.35}
.pk .no{color:var(--hint);font-weight:700;min-width:30px}.pk .s{margin-left:auto}
.wk{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid var(--line)}
.wk:last-child{border-bottom:0}.wk.me{background:#eaf1ff;border-radius:10px;padding:9px 8px}
.weak{display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--line)}
.weak:last-child{border-bottom:0}.weak span{flex:1;font-size:14px}.weak button{border:0;background:#eaf1ff;color:var(--accent);border-radius:10px;padding:7px 10px;font-weight:700}
.nav{display:flex;gap:8px;align-items:center;margin:10px 0 2px}
.nav button{border:1px solid var(--line);background:#fff;color:var(--accent);border-radius:12px;padding:9px 0;font-size:16px;font-weight:800}
.nav .ar{width:52px}.nav .num{flex:1}
.nav button:disabled{opacity:.35}
.grid{display:grid;grid-template-columns:repeat(6,1fr);gap:7px;max-height:55vh;overflow:auto;margin:12px 0}
.grid button{border:1px solid var(--line);background:#fff;color:var(--text);border-radius:10px;padding:10px 0;font-weight:700;font-size:15px}
.grid button.ok{background:rgba(31,157,87,.15);border-color:var(--green);color:var(--green)}
.grid button.bad{background:rgba(217,58,63,.12);border-color:var(--red);color:var(--red)}
.grid button.dn{background:var(--line);color:var(--hint)}
.grid button.cur{background:var(--accent);border-color:var(--accent);color:#fff}
.lg{display:flex;gap:12px;flex-wrap:wrap;font-size:12px;color:var(--hint)}
.course{margin:18px 0 6px;font-size:15px;color:var(--accent);text-transform:uppercase;letter-spacing:.03em}
.fnd{display:inline-block;font-size:11px;font-weight:800;color:#a86a00;background:#fff4d6;border-radius:7px;padding:1px 6px;margin-left:4px;vertical-align:middle}
[data-pu]{cursor:pointer}
.pubg{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:12px 0}
.pubg div{background:#f3f6fc;border-radius:12px;padding:10px 4px;text-align:center}.pubg b{display:block;font-size:19px;color:var(--accent)}.pubg span{font-size:11px;color:var(--hint)}
.fline{background:#fff8e6;border:1px solid #f3d58a;color:#7a5200;border-radius:12px;padding:9px 12px;font-size:14px;font-weight:600;margin:8px 0}
</style>
<script>
(function(){
const X = {
 ru:{pubDays:"дней занимался",pubStreak:"серия сейчас",pubBest:"лучшая серия",pubSolved:"решено вопросов",pubRight:"верно",pubLearned:"выучено",pubTests:"тестов",pubAvg:"средний %",pubTop:"лучший %",founder:"Основатель",founderOf:"👑 Основатель TSUE QUIZ: ",lastT:"Последние тесты",place:"место",rankH:"Места всех участников",goNo:"Перейти к вопросу",cur:"сейчас",solved:"решён",curQ:"➡️ К текущему вопросу",qNo:"Вопрос",pcert:"🏅 Сертификат тренировки",pcRib:"ТРЕНИРОВКА · ТЕСТ ЗАКРЫТ",pcSub:"не в зачёт — тренировочная попытка",pcL2:"прошёл(ла) тренировку по тесту",hist:"🕘 История",week:"🏆 Неделя",fire:"дн.",histH:"История",fAll:"Все",fZ:"📝 Зачёт",fP:"🔁 Тренировки",fT:"🏋️ Тренажёр",
  z:"зачёт",p:"тренировка",r:"тренажёр",noHist:"Пока пусто — пройдите тест или тренировку",noRev:"Разбор будет доступен после закрытия теста",
  oldRev:"Для старых попыток разбор не сохранился",
  pracH:"Тренировка теста",pracRules:["🔒 тест закрыт — тренируйтесь сколько угодно","📊 не идёт в рейтинг, статистику и Excel — только в историю",
   "⏱ без таймера, после ответа сразу видно — верно или нет","✅ можно сворачивать и выходить"],pracGo:"🔁 Начать тренировку",pracBtn:"🔁 Тренировка (не в зачёт)",
  pracBadge:"🔁 Тренировка",myRes:"🏁 Мой результат",toTests:"📝 К тестам",pracRuns:"тренировок",
  report:"⚠️ Ошибка в вопросе",repH:"Что не так с вопросом?",repPh:"Например: правильный ответ другой, опечатка…",repSend:"Отправить",
  repOk:"✅ Спасибо! Админ проверит вопрос",repLimit:"Сегодня уже много жалоб, попробуйте завтра",cancel:"Отмена",
  streakH:"Серия дней",streakD:"дней подряд",best:"рекорд",todayOk:"✅ Сегодня вы уже занимались",todayNo:"Сегодня ещё не занимались — ответьте хотя бы на 1 вопрос",
  remOn:"🔔 Напоминание вечером: включено",remOff:"🔕 Напоминание вечером: выключено",remHint:"Если вы не занимались — бот напомнит в {h}:00",
  weekH:"Рейтинг недели",weekD:"Верные ответы в тренажёре за неделю. Сброс каждый понедельник.",corr:"верных",ans:"ответов",youPlace:"Ваше место",
  weekEmpty:"На этой неделе ещё никто не занимался — будьте первым!",notIn:"Вы ещё не в рейтинге — ответьте на вопросы в тренажёре",
  learned:"📈 Выучено",of:"из",weakH:"Темы с ошибками",fix:"🔁 Исправить",
  cards:"🃏 Карточки",cardsD:"вопрос → переверни → «знаю / не знаю»",pick:"🎯 Выбрать вопрос",pickD:"любой вопрос из банка — ответьте на него",
  tap:"👆 нажмите, чтобы перевернуть",know:"✅ Знаю",dont:"❌ Не знаю",cardsDone:"Карточки пройдены!",known:"знаю",unknown:"не знаю",
  again:"🔁 Ещё раз",onlyUnk:"🔁 Только «не знаю»",fNew:"🆕 Новые",fBad:"❌ С ошибкой",fFav:"⭐",search:"Поиск вопроса",
  next:"➡️ Следующий",toListQ:"📋 К списку",chooseAns:"Выберите ответ",free:"✅ можно сворачивать и подглядывать",
  modes:{prac:"Тренировка теста",tmist:"Ошибки темы",t:"Тренажёр",mist:"Работа над ошибками",hard:"Трудные",fav:"Избранное",rand:"Случайные",exam:"Пробный экзамен",retry:"Работа над ошибками",test:"Тест"}},
 uz:{pubDays:"kun shugʻullangan",pubStreak:"hozirgi seriya",pubBest:"eng uzun seriya",pubSolved:"yechilgan savol",pubRight:"toʻgʻri",pubLearned:"oʻrganilgan",pubTests:"test",pubAvg:"oʻrtacha %",pubTop:"eng yaxshi %",founder:"Asoschi",founderOf:"👑 TSUE QUIZ asoschisi: ",lastT:"Oxirgi testlar",place:"oʻrin",rankH:"Barcha ishtirokchilar oʻrinlari",goNo:"Savolga oʻtish",cur:"hozir",solved:"yechilgan",curQ:"➡️ Joriy savolga",qNo:"Savol",pcert:"🏅 Mashq sertifikati",pcRib:"MASHQ · TEST YOPILGAN",pcSub:"hisobga olinmaydi — mashq urinishi",pcL2:"test boʻyicha mashqni bajardi",hist:"🕘 Tarix",week:"🏆 Hafta",fire:"kun",histH:"Tarix",fAll:"Hammasi",fZ:"📝 Hisobga",fP:"🔁 Mashqlar",fT:"🏋️ Trenajyor",
  z:"hisobga",p:"mashq",r:"trenajyor",noHist:"Hozircha boʻsh — test yoki mashq topshiring",noRev:"Tahlil test yopilgandan keyin ochiladi",
  oldRev:"Eski urinishlar tahlili saqlanmagan",
  pracH:"Test mashqi",pracRules:["🔒 test yopilgan — xohlagancha mashq qiling","📊 reyting, statistika va Excelga kirmaydi — faqat tarixga",
   "⏱ taymersiz, javobdan keyin toʻgʻri-notoʻgʻriligi darhol koʻrinadi","✅ ilovani yopish va chiqish mumkin"],pracGo:"🔁 Mashqni boshlash",pracBtn:"🔁 Mashq (hisobga olinmaydi)",
  pracBadge:"🔁 Mashq",myRes:"🏁 Natijam",toTests:"📝 Testlarga",pracRuns:"mashq",
  report:"⚠️ Savolda xato",repH:"Savolda nima notoʻgʻri?",repPh:"Masalan: toʻgʻri javob boshqa, imlo xatosi…",repSend:"Yuborish",
  repOk:"✅ Rahmat! Admin savolni tekshiradi",repLimit:"Bugun shikoyatlar koʻp, ertaga urinib koʻring",cancel:"Bekor qilish",
  streakH:"Kunlar seriyasi",streakD:"kun ketma-ket",best:"rekord",todayOk:"✅ Bugun shugʻullandingiz",todayNo:"Bugun hali shugʻullanmadingiz — kamida 1 savolga javob bering",
  remOn:"🔔 Kechki eslatma: yoqilgan",remOff:"🔕 Kechki eslatma: oʻchirilgan",remHint:"Shugʻullanmasangiz — bot {h}:00 da eslatadi",
  weekH:"Hafta reytingi",weekD:"Hafta davomida trenajyordagi toʻgʻri javoblar. Har dushanba yangilanadi.",corr:"toʻgʻri",ans:"javob",youPlace:"Sizning oʻrningiz",
  weekEmpty:"Bu hafta hali hech kim shugʻullanmadi — birinchi boʻling!",notIn:"Siz hali reytingda yoʻqsiz — trenajyorda savollarga javob bering",
  learned:"📈 Oʻrganildi",of:"/",weakH:"Xatoli mavzular",fix:"🔁 Tuzatish",
  cards:"🃏 Kartochkalar",cardsD:"savol → aylantiring → «bilaman / bilmayman»",pick:"🎯 Savol tanlash",pickD:"bankdan istalgan savol — javob bering",
  tap:"👆 aylantirish uchun bosing",know:"✅ Bilaman",dont:"❌ Bilmayman",cardsDone:"Kartochkalar tugadi!",known:"bilaman",unknown:"bilmayman",
  again:"🔁 Yana",onlyUnk:"🔁 Faqat «bilmayman»",fNew:"🆕 Yangi",fBad:"❌ Xatoli",fFav:"⭐",search:"Savol qidirish",
  next:"➡️ Keyingi",toListQ:"📋 Roʻyxatga",chooseAns:"Javobni tanlang",free:"✅ ilovani yopish va qarash mumkin",
  modes:{prac:"Test mashqi",tmist:"Mavzu xatolari",t:"Trenajyor",mist:"Xatolar ustida ishlash",hard:"Qiyin",fav:"Saralangan",rand:"Tasodifiy",exam:"Sinov imtihoni",retry:"Xatolar ustida ishlash",test:"Test"}},
 en:{pubDays:"days practiced",pubStreak:"current streak",pubBest:"best streak",pubSolved:"questions solved",pubRight:"correct",pubLearned:"learned",pubTests:"tests",pubAvg:"average %",pubTop:"best %",founder:"Founder",founderOf:"👑 TSUE QUIZ founder: ",lastT:"Recent tests",place:"place",rankH:"Everyone's places",goNo:"Go to question",cur:"now",solved:"solved",curQ:"➡️ Back to current question",qNo:"Question",pcert:"🏅 Practice certificate",pcRib:"PRACTICE · TEST CLOSED",pcSub:"not graded — practice attempt",pcL2:"completed a practice of the test",hist:"🕘 History",week:"🏆 Week",fire:"d",histH:"History",fAll:"All",fZ:"📝 Graded",fP:"🔁 Practice",fT:"🏋️ Trainer",
  z:"graded",p:"practice",r:"trainer",noHist:"Nothing yet — take a test or a practice",noRev:"Review opens after the test is closed",
  oldRev:"Review wasn't saved for old attempts",
  pracH:"Test practice",pracRules:["🔒 the test is closed — practice as much as you like","📊 not counted in ranking, stats or Excel — history only",
   "⏱ no timer, see right or wrong after each answer","✅ you may leave or minimize the app"],pracGo:"🔁 Start practice",pracBtn:"🔁 Practice (not graded)",
  pracBadge:"🔁 Practice",myRes:"🏁 My result",toTests:"📝 To tests",pracRuns:"practices",
  report:"⚠️ Report a mistake",repH:"What's wrong with this question?",repPh:"E.g. the right answer is different, a typo…",repSend:"Send",
  repOk:"✅ Thanks! The admin will check it",repLimit:"Too many reports today, try tomorrow",cancel:"Cancel",
  streakH:"Day streak",streakD:"days in a row",best:"record",todayOk:"✅ You've practiced today",todayNo:"Not practiced today — answer at least 1 question",
  remOn:"🔔 Evening reminder: on",remOff:"🔕 Evening reminder: off",remHint:"If you haven't practiced, the bot reminds you at {h}:00",
  weekH:"Weekly ranking",weekD:"Correct trainer answers this week. Resets every Monday.",corr:"correct",ans:"answers",youPlace:"Your place",
  weekEmpty:"Nobody has practiced this week yet — be the first!",notIn:"You're not ranked yet — answer trainer questions",
  learned:"📈 Learned",of:"of",weakH:"Topics with mistakes",fix:"🔁 Fix",
  cards:"🃏 Flashcards",cardsD:"question → flip → “know / don't know”",pick:"🎯 Pick a question",pickD:"any question from the bank — answer it",
  tap:"👆 tap to flip",know:"✅ Know",dont:"❌ Don't know",cardsDone:"Flashcards done!",known:"know",unknown:"don't know",
  again:"🔁 Again",onlyUnk:"🔁 Only “don't know”",fNew:"🆕 New",fBad:"❌ Wrong",fFav:"⭐",search:"Search a question",
  next:"➡️ Next",toListQ:"📋 To list",chooseAns:"Choose an answer",free:"✅ you may minimize and look things up",
  modes:{prac:"Test practice",tmist:"Topic mistakes",t:"Trainer",mist:"Mistakes",hard:"Hard",fav:"Favorites",rand:"Random",exam:"Mock exam",retry:"Mistakes",test:"Test"}},
 zh:{pubDays:"练习天数",pubStreak:"当前连续",pubBest:"最长连续",pubSolved:"已答题目",pubRight:"答对",pubLearned:"已掌握",pubTests:"测验",pubAvg:"平均 %",pubTop:"最佳 %",founder:"创始人",founderOf:"👑 TSUE QUIZ 创始人：",lastT:"最近的测验",place:"名次",rankH:"全部参与者排名",goNo:"跳到题目",cur:"当前",solved:"已答",curQ:"➡️ 回到当前题",qNo:"题目",pcert:"🏅 练习证书",pcRib:"练习 · 测验已关闭",pcSub:"不计分——练习记录",pcL2:"完成了测验练习",hist:"🕘 历史",week:"🏆 本周",fire:"天",histH:"历史记录",fAll:"全部",fZ:"📝 正式",fP:"🔁 练习",fT:"🏋️ 练习库",
  z:"正式",p:"练习",r:"练习库",noHist:"暂无记录——去做测验或练习吧",noRev:"测验关闭后可查看解析",
  oldRev:"旧记录没有保存解析",
  pracH:"测验练习",pracRules:["🔒 测验已关闭——可无限次练习","📊 不计入排名、统计和 Excel——只记入历史",
   "⏱ 不限时，作答后立即显示对错","✅ 可以离开或最小化应用"],pracGo:"🔁 开始练习",pracBtn:"🔁 练习（不计分）",
  pracBadge:"🔁 练习",myRes:"🏁 我的成绩",toTests:"📝 返回测验",pracRuns:"次练习",
  report:"⚠️ 题目有误",repH:"题目哪里有问题？",repPh:"例如：正确答案不对、错别字…",repSend:"发送",
  repOk:"✅ 谢谢！管理员会检查",repLimit:"今天反馈太多，请明天再试",cancel:"取消",
  streakH:"连续天数",streakD:"天连续",best:"纪录",todayOk:"✅ 今天已练习",todayNo:"今天还没练习——至少回答 1 题",
  remOn:"🔔 晚间提醒：开",remOff:"🔕 晚间提醒：关",remHint:"如果没练习，机器人会在 {h}:00 提醒",
  weekH:"本周排行",weekD:"本周练习中的正确答案数。每周一重置。",corr:"正确",ans:"作答",youPlace:"你的名次",
  weekEmpty:"本周还没有人练习——做第一个吧！",notIn:"你还未上榜——去练习答题吧",
  learned:"📈 已掌握",of:"/",weakH:"错误较多的主题",fix:"🔁 纠正",
  cards:"🃏 卡片",cardsD:"题目 → 翻面 → “会 / 不会”",pick:"🎯 选择题目",pickD:"题库中任选一题作答",
  tap:"👆 点击翻面",know:"✅ 会",dont:"❌ 不会",cardsDone:"卡片完成！",known:"会",unknown:"不会",
  again:"🔁 再来",onlyUnk:"🔁 只看“不会”",fNew:"🆕 新题",fBad:"❌ 错题",fFav:"⭐",search:"搜索题目",
  next:"➡️ 下一题",toListQ:"📋 返回列表",chooseAns:"请选择答案",free:"✅ 可以最小化和查资料",
  modes:{prac:"测验练习",tmist:"主题错题",t:"练习",mist:"错题练习",hard:"难题",fav:"收藏",rand:"随机",exam:"模拟考试",retry:"错题练习",test:"测验"}}
};
const x = () => X[S.lang] || X.ru;
// режимы для экрана итогов
Object.keys(X).forEach(k => { if (T[k] && T[k].modes) Object.assign(T[k].modes, {prac: X[k].modes.prac, tmist: X[k].modes.tmist}); });
// правила тренажёра: без «вопрос сгорает» и без таймера на вопрос
Object.keys(T).forEach(k => {
  const fr = (X[k] || X.ru).free, l = T[k];
  const strip = a => (a || []).filter(s => !/^⚠️/.test(s) && !/(таймер на каждый|taymer|timer on every|每题限时)/i.test(s));
  if (l.trRules) l.trRules = [...strip(l.trRules), fr];
  if (l.randRules) l.randRules = [...strip(l.randRules), fr];
  if (l.examRules) l.examRules = [...strip(l.examRules), fr];
});
const trainerQ = () => S.st && (S.st.status === "tquestion" || S.st.status === "tnext");
// сворачивание/копирование в тренажёре не наказывается
window.addEventListener("visibilitychange", e => { if (trainerQ()) e.stopImmediatePropagation(); }, true);
window.addEventListener("contextmenu", e => { if (!document.body.classList.contains("lock")) e.stopImmediatePropagation(); }, true);
const _dl = doLeave;
doLeave = async function() { if (trainerQ()) return; return _dl(); };
const _html = html;
html = function(h) { document.body.classList.remove("lock"); return _html(h); };
function overlay(inner) {
  const o = document.createElement("div"); o.className = "ovl"; o.innerHTML = `<div class="box">${inner}</div>`;
  o.onclick = e => { if (e.target === o) o.remove(); };
  document.body.appendChild(o); return o;
}
function toast(t) { const o = overlay(`<div style="text-align:center;font-weight:700;padding:8px">${esc(t)}</div>`); setTimeout(() => o.remove(), 1800); }
function reportBox(payload) {
  const t = x();
  const o = overlay(`<b>${t.repH}</b><textarea id="rpt" placeholder="${t.repPh}"></textarea>
    <div class="two"><button class="btn ghost" id="rpc">${t.cancel}</button><button class="btn" id="rps">${t.repSend}</button></div>`);
  o.querySelector("#rpc").onclick = () => o.remove();
  o.querySelector("#rps").onclick = async () => {
    o.querySelector("#rps").disabled = true;
    const r = await api("/api/report", {...payload, text: o.querySelector("#rpt").value});
    o.remove(); hap(r.ok ? "ok" : "bad");
    toast(r.ok ? t.repOk : (r.error === "limit" ? t.repLimit : L().net));
  };
}
const repBtn = payload => { const b = document.createElement("button"); b.className = "rep"; b.textContent = x().report; b.onclick = () => reportBox(payload); return b; };

// ---------- вопрос: в тренажёре — секундомер вместо таймера, жалоба ----------
const _sq = screenQuestion;
screenQuestion = function(st) {
  _sq(st);
  if (st.status === "question") { document.body.classList.add("lock"); return; }
  if (st.status !== "tquestion") return;
  if (st.free) {
    clearInterval(S.tick);
    const el = $("#tm"), t0 = Date.now();
    if (el) {
      el.classList.add("wide"); el.classList.remove("warn");
      const tk = () => { const e = $("#tm"); if (e) e.textContent = "⏱ " + fmt((Date.now() - t0) / 1000); };
      tk(); S.tick = setInterval(tk, 1000);
    }
  }
  if (st.mode === "prac") { const m = document.querySelector(".top .muted"); if (m) m.insertAdjacentHTML("afterbegin", `<span class="badge p">${x().pracBadge}</span> `); }
  const card = document.querySelector("#app .card");
  if (card) card.appendChild(repBtn({i: st.i}));
  if (st.no && st.nav && card) {
    const b = document.querySelector(".top .muted b"); if (b) b.textContent = st.no;
    card.parentNode.insertBefore(navBar(st, st.no - 1), card);
  }
};


// ---------- навигация по вопросам: ◀ ▶ и выбор номера ----------
function navTo(st, p) {                         // p — номер с нуля
  if (S.busy || p < 0 || p >= st.nav.length) return;
  const v = st.nav[p];
  if (p === st.no - 1) return show(st);
  if (v == null) return goto(p);
  if (v === 2) return;                          // экзамен: ответы в конце
  screenTView(st, p);
}
async function goto(p) {
  if (S.busy) return;
  S.busy = true; hap();
  const r = await api("/api/tgoto", {p});
  S.busy = false;
  r.state ? show(r.state) : resync();
}
function navGrid(st, curP) {
  const t = x(), cls = v => v == null ? "" : v === 1 ? "ok" : v === 0 ? "bad" : "dn";
  const o = overlay(`<b>${t.goNo}</b><div class="lg"><span>🟦 ${t.cur}</span><span>🟩 ✅</span><span>🟥 ❌</span></div>
    <div class="grid">${st.nav.map((v, p) => `<button data-p="${p}" class="${p === curP ? "cur" : cls(v)}" ${v === 2 ? "disabled" : ""}>${p + 1}</button>`).join("")}</div>
    <button class="btn ghost" id="gx">${x().cancel}</button>`);
  o.querySelector("#gx").onclick = () => o.remove();
  o.querySelectorAll(".grid button").forEach(b => b.onclick = () => { o.remove(); navTo(st, +b.dataset.p); });
  const c = o.querySelector(".grid .cur"); if (c) c.scrollIntoView({block: "center"});
}
function navBar(st, p) {
  const d = document.createElement("div"); d.className = "nav";
  d.innerHTML = `<button class="ar" id="nvp" ${p <= 0 ? "disabled" : ""}>◀</button>
    <button class="num" id="nvn">№ ${p + 1} / ${st.nav.length} ▾</button>
    <button class="ar" id="nvx" ${p >= st.nav.length - 1 ? "disabled" : ""}>▶</button>`;
  d.querySelector("#nvp").onclick = () => navTo(st, p - 1);
  d.querySelector("#nvx").onclick = () => navTo(st, p + 1);
  d.querySelector("#nvn").onclick = () => { hap(); navGrid(st, p); };
  return d;
}
async function screenTView(st, p) {
  const t = x(), l = L();
  const r = await api("/api/tview?p=" + p);
  if (!r.ok) return show(st);
  const v = r.item;
  html(`<div class="top"><div class="muted">🏋️ ${t.qNo} <b>${v.no}</b> ${l.of} ${v.n} · ${t.solved}</div></div>
    <div class="card"><div class="qtext">${esc(v.q)}</div>
    ${v.opts.map((o, k) => `<div class="ro ${k === v.right ? "right" : (k === v.chosen ? "wrong" : "")}">${k === v.right ? "✅" : (k === v.chosen ? "❌" : "▫️")} ${esc(o)}${k === v.chosen && k !== v.right ? `<span class="muted"> — ${l.yours}</span>` : ""}</div>`).join("")}
    ${v.chosen === -1 ? `<div class="muted">⏰ ${l.noAns}</div>` : ""}</div>
    <button class="btn" id="cq">${t.curQ} (№ ${st.no})</button>`);
  $("#app").insertBefore(navBar(st, p), $("#app .card"));
  $("#cq").onclick = () => show(st);
  setBack(() => show(st));
}


// ---------- основатель и профиль любого участника ----------
const isF = uid => S.me && S.me.founder && String(uid) === String(S.me.founder.uid);
window.fmark = uid => isF(uid) ? `<span class="fnd">👑 ${x().founder}</span>` : "";
window.showPub = async function(uid) {
  hap();
  const r = await api("/api/pub?uid=" + encodeURIComponent(uid));
  if (!r.ok) return;
  const p = r.p, t = x(), l = L();
  const o = overlay(`<div style="display:flex;gap:12px;align-items:center">${p.av ? avaImg(p.uid, p.av, "ava") : `<span class="lv" style="font-size:34px">${l.lvls[p.level].split(" ")[0]}</span>`}
    <div><b style="font-size:18px">${esc(p.name)}</b>${p.founder ? `<span class="fnd">👑 ${t.founder}</span>` : ""}<div class="muted">${l.lvls[p.level]} · ${p.xp} ${l.xp}</div></div></div>
    <div class="pubg"><div><b>${p.days}</b><span>📅 ${t.pubDays}</span></div><div><b>🔥 ${p.streak}</b><span>${t.pubStreak}</span></div><div><b>${p.best_streak}</b><span>${t.pubBest}</span></div>
    <div><b>${p.solved}</b><span>🏋️ ${t.pubSolved}</span></div><div><b>${p.right}</b><span>✅ ${t.pubRight}</span></div><div><b>${p.learned}</b><span>📈 ${t.pubLearned}</span></div>
    <div><b>${p.tests}</b><span>📝 ${t.pubTests}</span></div><div><b>${p.avg}%</b><span>${t.pubAvg}</span></div><div><b>${p.best}%</b><span>${t.pubTop}</span></div></div>
    ${p.history.length ? `<b>${t.lastT}</b>${p.history.map(h => `<div class="wk"><span>${esc(h.title)}</span><span><b>${h.pct}%</b> · ${h.place}/${h.all}</span></div>`).join("")}` : ""}
    <button class="btn ghost" id="pbx" style="margin-top:12px">✖️</button>`);
  o.querySelector(".box").style.maxHeight = "85vh"; o.querySelector(".box").style.overflow = "auto";
  o.querySelector("#pbx").onclick = () => o.remove();
};
document.addEventListener("click", e => { const el = e.target.closest("[data-pu]"); if (el && !e.target.closest(".ovl")) window.showPub(el.dataset.pu); });
function founderLine() { const f = S.me && S.me.founder; return f ? `<div class="fline">${x().founderOf}<b>${esc(f.name)}</b></div>` : ""; }
const _tri = screenTrIntro;
screenTrIntro = function() { const r = _tri(); const c = document.querySelector("#app .card"); if (c && !c.querySelector(".fline")) c.insertAdjacentHTML("beforeend", founderLine()); return r; };

// ---------- закрытые тесты: тренировка ----------
function screenPrac(q) {
  const t = x(), l = L(), p = q.prac;
  html(`${backBtn()}<div class="card">${q.subject ? `<span class="subj">${esc(q.subject)}</span>` : ""}<h2>🔁 ${esc(q.title)}</h2>
    <div class="facts"><div><b>${q.n}</b><span>${l.q}</span></div><div><b>${p ? p.best + "%" : "—"}</b><span>${l.bestR}</span></div>
    <div><b>${p ? p.runs : 0}</b><span>${t.pracRuns}</span></div></div>
    <ul class="rules">${t.pracRules.map(r => `<li>${r}</li>`).join("")}</ul>
    <button class="btn" id="go">${t.pracGo}</button>
    ${q.result ? `<button class="btn ghost" id="res">${t.myRes} · ${q.result.pct}%</button>` : ""}</div>`);
  wireBack(toList);
  $("#go").onclick = () => { S.subjName = null; S.tab = "test"; startMode({mode: "prac", code: q.code}); };
  if ($("#res")) $("#res").onclick = () => _intro();
}
const _intro = screenIntro;
screenIntro = function() {
  const q = S.quiz;
  if (q && q.kind !== "trainer" && q.open === false && !q.result) return screenPrac(q);
  return _intro();
};
async function fullRank(st) {
  const code = st.code || (S.quiz && S.quiz.code);
  if (!code) return;
  const r = await api("/api/rank?q=" + encodeURIComponent(code));
  if (!r.ok || !r.items.length || !$("#again")) return;
  document.querySelectorAll("#app .lb").forEach(x => x.closest(".card").remove());
  const t = x(), me = r.me;
  const box = document.createElement("div");
  box.className = "card";
  box.innerHTML = `<b>🏆 ${t.rankH} — ${r.items.length}</b><div class="lb">${r.items.map((z, i) =>
    `<div class="${z.uid === me ? "me" : ""}" data-pu="${z.uid}"><span>${["🥇","🥈","🥉"][i] || (i + 1) + "."} ${avaImg(z.uid, z.av, "avs")}${esc(z.name)}${fmark(z.uid)}</span><span>${z.pct}% · ${z.points}/50 · ${fmt(z.time)}</span></div>`).join("")}</div>`;
  $("#again").parentNode.insertBefore(box, $("#again"));
}
const _sd = screenDone;
screenDone = function(st, already) {
  _sd(st, already);
  fullRank(st);
  if (!st.review || !st.code) return;
  const b = document.createElement("button"); b.className = "btn"; b.textContent = x().pracBtn;
  b.onclick = () => { S.subjName = null; S.tab = "test"; startMode({mode: "prac", code: st.code}); };
  const a = $("#again"); if (a) a.parentNode.insertBefore(b, a);
};
const _std = screenTrDone;
screenTrDone = function(st) {
  _std(st);
  if (st.mode !== "prac") return;
  const out = async () => { await api("/api/tstop", {}); S.tab = "test"; S.quiz = null; S.st = null; screenList(); };
  const b = $("#lst"); if (b) { b.textContent = x().toTests; b.onclick = out; }
  wireBack(out);
  const card = document.querySelector("#app .card");
  if (card && st.code) {
    card.insertAdjacentHTML("beforeend", `<button class="btn" id="pc2" style="margin-top:10px">${x().pcert}</button><div id="pcm" class="muted" style="margin-top:8px"></div>`);
    $("#pc2").onclick = () => { hap(); pracCert(st); };
  }
};


// ---------- сертификат тренировки (тест закрыт) ----------
async function pracCert(st) {
  const l = L(), t = x(), r = st.result || {}, msg = $("#pcm");
  msg.textContent = l.certMaking;
  const W = 1080, H = 1350, c = document.createElement("canvas"); c.width = W; c.height = H;
  const g2 = c.getContext("2d"), F = '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif';
  g2.fillStyle = "#ffffff"; g2.fillRect(0, 0, W, H);
  const g = g2.createLinearGradient(0, 0, W, 0); g.addColorStop(0, "#7a3b00"); g.addColorStop(1, "#e8590c");
  g2.fillStyle = g; g2.fillRect(0, 0, W, 300);
  g2.strokeStyle = "#e8590c"; g2.lineWidth = 14; g2.strokeRect(30, 30, W - 60, H - 60);
  g2.strokeStyle = "#868e96"; g2.lineWidth = 4; g2.setLineDash([18, 12]); g2.strokeRect(56, 56, W - 112, H - 112); g2.setLineDash([]);
  try {
    const img = new Image(); img.src = "/logo";
    await new Promise((ok, no) => { img.onload = ok; img.onerror = no; });
    g2.save(); g2.beginPath(); g2.arc(W / 2, 300, 110, 0, Math.PI * 2); g2.fillStyle = "#fff"; g2.fill(); g2.clip();
    g2.drawImage(img, W / 2 - 100, 200, 200, 200); g2.restore();
  } catch (e) {}
  g2.textAlign = "center"; g2.fillStyle = "#fff"; g2.font = `800 54px ${F}`; g2.fillText("TSUE QUIZ", W / 2, 140);
  g2.fillStyle = "#0b1f44"; g2.font = `800 76px ${F}`; g2.fillText(l.certT, W / 2, 490);
  g2.fillStyle = "#e8590c"; g2.font = `800 34px ${F}`; g2.fillText("🔁 " + t.pcRib, W / 2, 545);
  g2.fillStyle = "#5d6f92"; g2.font = `400 34px ${F}`; g2.fillText(l.certL1, W / 2, 600);
  g2.fillStyle = "#0b1f44"; g2.font = `800 62px ${F}`; wrapText(g2, S.me.name || "", W / 2, 680, W - 180, 68, 2);
  g2.fillStyle = "#5d6f92"; g2.font = `400 34px ${F}`; g2.fillText(t.pcL2, W / 2, 755);
  g2.fillStyle = "#0b1f44"; g2.font = `700 42px ${F}`;
  let y = wrapText(g2, "«" + (st.title || "") + "»", W / 2, 815, W - 180, 52, 2);
  const cy = Math.min(1090, Math.max(1040, y + 150));
  g2.beginPath(); g2.arc(W / 2, cy, 115, 0, Math.PI * 2); g2.fillStyle = "#fff4e6"; g2.fill();
  g2.lineWidth = 14; g2.strokeStyle = "#e8590c"; g2.beginPath();
  g2.arc(W / 2, cy, 115, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * (r.pct || 0) / 100); g2.stroke();
  g2.fillStyle = "#e8590c"; g2.font = `800 70px ${F}`; g2.fillText((r.pct ?? 0) + "%", W / 2, cy + 24);
  g2.fillStyle = "#0b1f44"; g2.font = `800 44px ${F}`;
  g2.fillText(`${r.points ?? 0}/${r.max ?? 50}`, 205, cy - 5); g2.fillText(`${r.score ?? 0}/${r.total ?? 0}`, W - 205, cy - 5);
  g2.fillStyle = "#5d6f92"; g2.font = `400 26px ${F}`;
  g2.fillText(l.pts, 205, cy + 35, 250); g2.fillText(l.corr, W - 205, cy + 35, 250);
  g2.font = `400 28px ${F}`; g2.fillText(`${t.pcSub}  ·  ${new Date().toLocaleDateString()}`, W / 2, 1250);
  // диагональная лента «тренировка»
  g2.save(); g2.translate(W - 170, 170); g2.rotate(Math.PI / 4);
  g2.fillStyle = "rgba(232,89,12,.92)"; g2.fillRect(-260, -34, 520, 68);
  g2.fillStyle = "#fff"; g2.font = `800 30px ${F}`; g2.fillText(t.pcRib.split(" · ")[0], 0, 11); g2.restore();
  const res = await api("/api/pcert", {code: st.code, img: c.toDataURL("image/jpeg", 0.85)}, {timeout: 30000, tries: 2});
  msg.textContent = res.ok ? l.certSent : "❗ " + (res.error === "net" ? l.net : (res.error || "error"));
  hap(res.ok ? "ok" : "bad");
}

// ---------- быстрая панель: серия, история, неделя ----------
function qbar() {
  const pc = $("#pc");
  if (!pc || $("#qbar")) return;
  const t = x(), n = (S.me && S.me.streak) || 0;
  pc.insertAdjacentHTML("afterend", `<div class="qbar" id="qbar"><button class="fire ${n ? "" : "off"}" id="qf">🔥 ${n}</button>
    <button id="qh">${t.hist}</button><button id="qw">${t.week}</button></div>`);
  $("#qf").onclick = () => { hap(); screenStreak(); };
  $("#qh").onclick = () => { hap(); screenHistory(); };
  $("#qw").onclick = () => { hap(); screenWeek(); };
}
const _dlst = drawList;
drawList = function() {
  const r = _dlst();
  if (S.tab !== "trainer") {
    qbar();
    const t = x();
    document.querySelectorAll(".qitem").forEach(b => {
      const q = (S.items || []).find(z => z.code === b.dataset.c);
      if (!q || q.kind === "trainer" || q.open !== false) return;
      const s = b.querySelector(".st");
      if (!q.result) { b.querySelector(".ic").textContent = "🔒"; if (s) { s.textContent = t.pracBadge + (q.prac ? " · " + q.prac.best + "%" : ""); s.classList.add("ok"); } }
      else if (s) s.insertAdjacentHTML("beforeend", "<br>🔁");
    });
  }
  return r;
};
const _ssb = screenSubjects;
screenSubjects = async function() {
  await _ssb(); qbar();
  let last = null;
  document.querySelectorAll(".scard").forEach(b => {
    const c = b.dataset.course || "";
    if (c && c !== last) b.insertAdjacentHTML("beforebegin", `<h3 class="course">🎓 ${esc(c)}</h3>`);
    last = c;
  });
};
// курс каждого предмета — из ответа /api/subjects
const _api0 = api;
api = async function(path, ...a) {
  const r = await _api0(path, ...a);
  if (path === "/api/subjects" && r && r.items) S.subjCourses = r.items.map(x => x.course || "");
  return r;
};
const _htmlC = html;
html = function(h) {
  const out = _htmlC(h);
  if (S.subjCourses && document.querySelector(".scard")) document.querySelectorAll(".scard").forEach(b => { b.dataset.course = S.subjCourses[+b.dataset.i] || ""; });
  return out;
};

async function refreshStreak() { const r = await api("/api/streak"); if (r.ok && S.me) S.me.streak = r.streak.n; return r.streak; }

// ---------- серия дней ----------
async function screenStreak() {
  html('<div class="spin"><i></i></div>');
  const st = await refreshStreak();
  const t = x();
  if (!st) return toList();
  html(`${backBtn()}<div class="card" style="text-align:center"><h2>🔥 ${t.streakH}</h2>
    <div class="big2">${st.n}</div><div class="muted">${t.streakD} · ${t.best}: <b>${st.best}</b></div>
    <div class="days">${st.days.map(d => `<i class="${d ? "on" : ""}"></i>`).join("")}</div>
    <div class="muted">${st.today ? t.todayOk : t.todayNo}</div>
    <button class="btn ghost" id="rm" style="margin-top:14px">${st.remind ? t.remOn : t.remOff}</button>
    <div class="muted">${t.remHint.replace("{h}", st.hour)}</div></div>`);
  wireBack(toList);
  $("#rm").onclick = async () => { hap(); await api("/api/remind", {on: !st.remind}); screenStreak(); };
}

// ---------- история ----------
async function screenHistory(f) {
  const t = x(), l = L();
  f = f || S.hf || "all"; S.hf = f;
  html('<div class="spin"><i></i></div>');
  const r = await api("/api/history");
  if (!r.ok) return toList();
  const items = r.items.filter(h => f === "all" || (f === "z" && h.kind === "test") || (f === "p" && h.kind === "prac") || (f === "r" && h.kind === "train"));
  const ic = h => h.kind === "test" ? "📝" : h.kind === "prac" ? "🔁" : (h.mode === "exam" ? "🎓" : "🏋️");
  const bd = h => h.kind === "test" ? `<span class="badge z">${t.z}</span>` : h.kind === "prac" ? `<span class="badge p">${t.p}</span>` : `<span class="badge r">${t.r}</span>`;
  const nm = h => h.kind === "train" && h.mode !== "t" ? (t.modes[h.mode] || h.title) : h.title;
  html(`${backBtn()}<h2>🕘 ${t.histH}</h2>
    <div class="chips">${[["all", t.fAll], ["z", t.fZ], ["p", t.fP], ["r", t.fT]].map(c => `<button data-f="${c[0]}" class="${f === c[0] ? "on" : ""}">${c[1]}</button>`).join("")}</div>
    ${items.length ? items.map((h, i) => `<button class="hi" data-i="${i}"><span class="ic">${ic(h)}</span><span class="tt"><b>${esc(nm(h))}${bd(h)}</b>
      <span>${h.subject ? esc(h.subject) + " · " : ""}${h.date}</span></span>
      <span class="pc">${h.pct}%<br><span class="muted">${h.score}/${h.total}${h.points != null ? " · " + h.points + "/50" : ""}</span></span></button>`).join("")
      : `<div class="card muted" style="text-align:center">${t.noHist}</div>`}`);
  wireBack(toList);
  document.querySelectorAll(".chips button").forEach(b => b.onclick = () => screenHistory(b.dataset.f));
  document.querySelectorAll(".hi").forEach(b => b.onclick = async () => {
    const h = items[+b.dataset.i];
    if (!h.rev) return toast(h.kind === "test" ? t.noRev : t.oldRev);
    hap();
    const d = await api("/api/hitem?id=" + encodeURIComponent(h.id));
    if (!d.ok) return toast(h.kind === "test" ? t.noRev : t.oldRev);
    drawReview(d.items, nm(h), h.kind !== "test" && d.items.some(z => !z.ok), () => screenHistory());
  });
}

// ---------- рейтинг недели ----------
async function screenWeek() {
  const t = x();
  html('<div class="spin"><i></i></div>');
  const r = await api("/api/week");
  if (!r.ok) return toList();
  const w = r.week, me = S.me.uid;
  html(`${backBtn()}<h2>🏆 ${t.weekH}</h2><div class="muted">${w.from} – ${w.to} · ${t.weekD}</div>
    ${w.me ? `<div class="card" style="text-align:center"><div class="muted">${t.youPlace}</div><div class="big">${w.me.place}<span class="muted" style="font-size:16px"> / ${w.all}</span></div>
      <div class="muted">✅ ${w.me.c} ${t.corr} · ${w.me.n} ${t.ans}</div></div>` : `<div class="card muted" style="text-align:center">${t.notIn}</div>`}
    <div class="card">${w.items.length ? w.items.map(z => `<div class="wk ${z.uid === me ? "me" : ""}" data-pu="${z.uid}"><span>${["🥇","🥈","🥉"][z.place - 1] || z.place + "."} ${avaImg(z.uid, z.av, "avs")}${esc(z.name)}${fmark(z.uid)}</span>
      <span><b>${z.c}</b> <span class="muted">/ ${z.n}</span></span></div>`).join("") : `<div class="muted" style="text-align:center">${t.weekEmpty}</div>`}</div>`);
  wireBack(toList);
}

// ---------- предмет: прогресс, слабые темы, карточки, выбор вопроса ----------
const _ssj = screenSubject;
screenSubject = async function(name) {
  await _ssj(name);
  if (S.subjName !== name || !$(".mlist")) return;
  const t = x();
  const ml = $(".mlist");
  ml.insertAdjacentHTML("afterbegin", `<button class="mrow" data-v="cards"><span><b>${t.cards}</b><span>${t.cardsD}</span></span><span class="go">›</span></button>
    <button class="mrow" data-v="pick"><span><b>${t.pick}</b><span>${t.pickD}</span></span><span class="go">›</span></button>`);
  ml.querySelector('[data-v="cards"]').onclick = e => { e.stopImmediatePropagation(); hap(); screenCards(name); };
  ml.querySelector('[data-v="pick"]').onclick = e => { e.stopImmediatePropagation(); hap(); screenPick(name); };
  const r = await api("/api/progress?s=" + encodeURIComponent(name));
  if (!r.ok || S.subjName !== name) return;
  const p = r.progress, card = document.querySelector("#app .card");
  if (!card) return;
  card.insertAdjacentHTML("beforebegin", founderLine());
  card.insertAdjacentHTML("afterbegin", `<div style="display:flex;justify-content:space-between;font-weight:800"><span>${t.learned} ${p.ok} ${t.of} ${p.total}</span><span style="color:var(--green)">${p.pct}%</span></div>`);
  if (p.weak.length) {
    card.insertAdjacentHTML("afterend", `<div class="card"><b>${t.weakH}</b>${p.weak.map(w => `<div class="weak"><span>${esc(w.title)}<br><span class="muted">❌ ${w.bad} · ✅ ${w.ok} / ${w.total}</span></span>
      <button data-c="${w.code}">${t.fix}</button></div>`).join("")}</div>`);
    document.querySelectorAll(".weak button").forEach(b => b.onclick = () => startMode({mode: "tmist", code: b.dataset.c}));
  }
};

// ---------- карточки ----------
async function screenCards(name, only) {
  const t = x();
  html('<div class="spin"><i></i></div>');
  const r = await api("/api/cards?s=" + encodeURIComponent(name));
  if (!r.ok) return screenSubject(name);
  let deck = r.items.filter(c => !only || only.includes(c.id));
  deck.sort(() => Math.random() - .5);
  deck.sort((a, b) => (a.st === 0 ? 0 : a.st == null ? 1 : 2) - (b.st === 0 ? 0 : b.st == null ? 1 : 2));
  let i = 0, kn = 0, unk = [];
  const back = () => screenSubject(name);
  const draw = () => {
    if (i >= deck.length) {
      html(`${backBtn()}<div class="card" style="text-align:center"><h2>🃏 ${t.cardsDone}</h2>
        <div class="facts" style="grid-template-columns:1fr 1fr"><div><b style="color:var(--green)">${kn}</b><span>${t.known}</span></div><div><b style="color:var(--red)">${unk.length}</b><span>${t.unknown}</span></div></div>
        ${unk.length ? `<button class="btn" id="unk">${t.onlyUnk} (${unk.length})</button>` : ""}
        <button class="btn ghost" id="ag">${t.again}</button></div>`);
      wireBack(back);
      if ($("#unk")) $("#unk").onclick = () => screenCards(name, unk.slice());
      $("#ag").onclick = () => screenCards(name);
      hap("ok");
      return;
    }
    const c = deck[i];
    html(`${backBtn()}<div class="top"><div class="muted">🃏 <b>${i + 1}</b> / ${deck.length}</div><div class="muted">✅ ${kn} · ❌ ${unk.length}</div></div>
      <div class="prog"><i style="width:${100 * i / deck.length}%"></i></div>
      <div class="fc" id="fc">${c.st === 0 ? "❌ " : c.st === 1 ? "✅ " : ""}${esc(c.q)}<div class="hint">${t.tap}</div></div>
      <div class="two"><button class="btn red" id="no">${t.dont}</button><button class="btn green" id="yes">${t.know}</button></div>`);
    wireBack(back);
    const fc = $("#fc");
    let flipped = false;
    fc.onclick = () => {
      if (window.getSelection && String(window.getSelection())) return;
      hap(); fc.classList.add("flip");
      setTimeout(() => {
        flipped = !flipped;
        fc.classList.toggle("back", flipped);
        fc.innerHTML = flipped ? `<div class="muted" style="font-weight:600">${esc(c.q)}</div><div class="ans">✅ ${esc(c.a)}</div>`
          : `${esc(c.q)}<div class="hint">${t.tap}</div>`;
        fc.classList.remove("flip");
      }, 180);
    };
    const mark = know => { api("/api/card", {s: name, id: c.id, know}); know ? kn++ : unk.push(c.id); hap(know ? "ok" : "bad"); i++; draw(); };
    $("#yes").onclick = () => mark(true);
    $("#no").onclick = () => mark(false);
    $("#app").appendChild(repBtn({id: c.id, s: name}));
  };
  draw();
}

// ---------- выбрать любой вопрос и ответить ----------
async function screenPick(name) {
  const t = x();
  html('<div class="spin"><i></i></div>');
  const r = await api("/api/qlist?s=" + encodeURIComponent(name));
  if (!r.ok) return screenSubject(name);
  const all = r.items;
  const P = S.pick && S.pick.name === name ? S.pick : (S.pick = {name, q: "", f: "all", lim: 60});
  html(`${backBtn()}<h2>🎯 ${esc(subjName(name))}</h2>
    <input id="sq" placeholder="${t.search}" autocomplete="off" value="${esc(P.q)}">
    <div class="chips" style="margin-top:10px">${[["all", t.fAll], ["none", t.fNew], ["bad", t.fBad], ["fav", t.fFav]].map(c =>
      `<button data-f="${c[0]}" class="${P.f === c[0] ? "on" : ""}">${c[1]}</button>`).join("")}</div><div id="pl"></div>`);
  wireBack(() => { S.pick = null; screenSubject(name); });
  const list = () => {
    const s = P.q.trim().toLowerCase();
    return all.filter(z => (P.f === "all" || (P.f === "none" && z.st == null) || (P.f === "bad" && z.st === 0) || (P.f === "fav" && z.fav))
      && (!s || z.q.toLowerCase().includes(s) || String(z.no) === s));
  };
  const draw = () => {
    const ls = list();
    $("#pl").innerHTML = `<div class="muted">${L().found}: <b>${ls.length}</b></div>` + ls.slice(0, P.lim).map(z =>
      `<button class="pk" data-id="${z.id}"><span class="no">${z.no}.</span><span>${z.fav ? "⭐ " : ""}${hl(z.q, P.q.trim().toLowerCase())}</span>
       <span class="s">${z.st === 0 ? "❌" : z.st === 1 ? "✅" : ""}</span></button>`).join("")
      + (ls.length > P.lim ? `<button class="btn ghost" id="more">${L().showMore}</button>` : "");
    if ($("#more")) $("#more").onclick = () => { P.lim += 100; draw(); };
    document.querySelectorAll(".pk").forEach(b => b.onclick = () => { hap(); const ids = list().map(z => z.id); screenOne(name, b.dataset.id, ids); });
  };
  $("#sq").oninput = e => { P.q = e.target.value; P.lim = 60; draw(); };
  document.querySelectorAll(".chips button").forEach(b => b.onclick = () => {
    P.f = b.dataset.f; P.lim = 60; document.querySelectorAll(".chips button").forEach(z => z.classList.toggle("on", z === b)); draw();
  });
  draw();
}
async function screenOne(name, id, ids) {
  const t = x(), l = L();
  html('<div class="spin"><i></i></div>');
  const r = await api("/api/one?s=" + encodeURIComponent(name) + "&id=" + id);
  if (!r.ok) return screenPick(name);
  const q = r.q, pos = ids.indexOf(id);
  html(`${backBtn()}<div class="top"><div class="muted">🎯 ${pos + 1} / ${ids.length}</div>
    <div class="tr"><button class="star ${q.fav ? "on" : ""}" id="star">${q.fav ? "★" : "☆"}</button></div></div>
    <div class="card"><span class="subj">${esc(q.title)}</span><div class="qtext">${esc(q.text)}</div>
    ${q.opts.map((o, k) => `<button class="opt" data-k="${k}"><b>${LET[k]}</b><span>${esc(o)}</span></button>`).join("")}
    <div class="fb" id="fb"></div></div>
    <div class="two"><button class="btn ghost" id="tl">${t.toListQ}</button><button class="btn" id="nx">${t.next}</button></div>`);
  const toPick = () => screenPick(name);
  wireBack(toPick);
  document.querySelector("#app .card").appendChild(repBtn({id, s: name}));
  $("#tl").onclick = toPick;
  const nextId = ids[(pos + 1) % ids.length];
  $("#nx").onclick = () => screenOne(name, nextId, ids);
  $("#star").onclick = async () => { hap(); const f = await api("/api/qfav", {id}); if (f.ok) { const b = $("#star"); b.textContent = f.fav ? "★" : "☆"; b.classList.toggle("on", f.fav); } };
  let done = false;
  document.querySelectorAll(".opt").forEach(b => b.onclick = async () => {
    if (done) return; done = true; hap();
    document.querySelectorAll(".opt").forEach(z => z.disabled = true);
    b.classList.add("sel");
    const a = await api("/api/oneans", {id, k: +b.dataset.k});
    if (!a.ok) { done = false; return screenOne(name, id, ids); }
    const res = a.res;
    document.querySelectorAll(".opt").forEach((z, j) => { z.classList.remove("sel"); if (j === res.right) z.classList.add("right"); else if (j === res.chosen) z.classList.add("wrong"); });
    const f = $("#fb"); f.textContent = res.ok ? l.right : l.wrong; f.className = "fb " + (res.ok ? "ok" : "bad");
    hap(res.ok ? "ok" : "bad");
  });
}

// ---------- профиль: кнопки истории и недели ----------
const _sp = screenProfile;
screenProfile = async function() {
  await _sp();
  const pc = document.querySelector("#app .pcard");
  if (!pc || $("#qbar")) return;
  pc.insertAdjacentHTML("afterend", `<div class="qbar" id="qbar"><button class="fire" id="qf">🔥 ${(S.me && S.me.streak) || 0}</button>
    <button id="qh">${x().hist}</button><button id="qw">${x().week}</button></div>`);
  $("#qf").onclick = () => screenStreak();
  $("#qh").onclick = () => screenHistory();
  $("#qw").onclick = () => screenWeek();
};
// после тренировки обновить серию
const _show = show;
show = async function(st) { if (st && (st.status === "tdone" || st.status === "done")) refreshStreak(); return _show(st); };
})();
</script>
