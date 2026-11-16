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
</style>
<script>
(function(){
const X = {
 ru:{hist:"🕘 История",week:"🏆 Неделя",fire:"дн.",histH:"История",fAll:"Все",fZ:"📝 Зачёт",fP:"🔁 Тренировки",fT:"🏋️ Тренажёр",
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
 uz:{hist:"🕘 Tarix",week:"🏆 Hafta",fire:"kun",histH:"Tarix",fAll:"Hammasi",fZ:"📝 Hisobga",fP:"🔁 Mashqlar",fT:"🏋️ Trenajyor",
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
 en:{hist:"🕘 History",week:"🏆 Week",fire:"d",histH:"History",fAll:"All",fZ:"📝 Graded",fP:"🔁 Practice",fT:"🏋️ Trainer",
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
 zh:{hist:"🕘 历史",week:"🏆 本周",fire:"天",histH:"历史记录",fAll:"全部",fZ:"📝 正式",fP:"🔁 练习",fT:"🏋️ 练习库",
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
};

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
const _sd = screenDone;
screenDone = function(st, already) {
  _sd(st, already);
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
};

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
screenSubjects = async function() { await _ssb(); qbar(); };

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
    <div class="card">${w.items.length ? w.items.map(z => `<div class="wk ${z.uid === me ? "me" : ""}"><span>${["🥇","🥈","🥉"][z.place - 1] || z.place + "."} ${avaImg(z.uid, z.av, "avs")}${esc(z.name)}</span>
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
  deck.sort((a, b) => (a.st === 0 ? 0 : a.st == null ? 1 : 2) - (b
