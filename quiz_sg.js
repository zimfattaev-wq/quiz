<style>
.tabs.t3{grid-template-columns:repeat(3,1fr)}
.tabs.t3 button{font-size:14px;padding:10px 2px}
.sg-hero{background:#1b2a8f;color:#fff;border-radius:18px;padding:18px 16px;margin:4px 0 12px;position:relative;overflow:hidden}
.sg-hero h2{margin:0;font-size:30px;font-weight:900;line-height:1;letter-spacing:-.01em;color:#fff}
.sg-hero h2 span{color:#f3c34a}
.sg-hero p{margin:10px 0 0;color:#c9d0ff;font-size:14px;line-height:1.45}
.sg-set{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px;margin:0 0 12px}
.sg-set h4{margin:0 0 8px;font-size:14px;color:var(--hint)}
.sg-seg{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.sg-seg button{min-width:42px;height:40px;padding:0 10px;border-radius:10px;border:1.5px solid var(--line);background:#fff;color:var(--text);font-weight:700}
.sg-seg button.on{background:#1b2a8f;border-color:#1b2a8f;color:#fff}
.sg-names{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:12px}
.sg-names input{height:40px;border-radius:10px;border:1.5px solid var(--line);padding:0 10px;font:inherit;font-size:15px;background:#fff;color:var(--text);-webkit-user-select:text;user-select:text}
.sg-topic{display:flex;gap:12px;align-items:center;width:100%;text-align:left;padding:12px 14px;background:var(--card);border:1px solid var(--line);border-radius:14px;margin:0 0 8px;color:var(--text)}
.sg-topic b{flex:0 0 40px;height:40px;border-radius:10px;display:grid;place-items:center;background:#1b2a8f;color:#f3c34a;font-size:17px;font-weight:900}
.sg-topic span{font-weight:700;font-size:15px}.sg-topic small{display:block;color:var(--hint);font-weight:500;font-size:13px;margin-top:2px}
.sg-scores{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:6px;margin:8px 0}
.sg-team{background:var(--card);border:1.5px solid var(--line);border-radius:12px;padding:8px 10px;display:grid;grid-template-columns:1fr auto;align-items:center;gap:4px 8px}
.sg-team.lead{border-color:#f3c34a;box-shadow:0 0 0 2px rgba(243,195,74,.45)}
.sg-team .nm{font-weight:700;font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sg-team .sc{font-weight:900;font-size:21px;text-align:right;font-variant-numeric:tabular-nums}.sg-team .sc.neg{color:var(--red)}
.sg-team .adj{grid-column:1/-1;display:flex;gap:6px}
.sg-team .adj button{flex:1;height:32px;border-radius:9px;border:0;font-weight:800;font-size:13px}
.sg-mi{background:rgba(217,58,63,.12);color:var(--red)}.sg-pl{background:rgba(31,157,87,.14);color:var(--green)}
.sg-board{background:#121c63;border-radius:16px;padding:6px;display:grid;grid-template-columns:minmax(86px,1.6fr) repeat(5,minmax(0,1fr));gap:5px}
.sg-cat{display:flex;align-items:center;padding:4px 7px;border-radius:9px;background:#1b2a8f;color:#fff;font-weight:600;font-size:12px;line-height:1.2;min-height:52px;hyphens:auto;overflow-wrap:anywhere}
.sg-cell{min-height:52px;border-radius:9px;border:0;background:#1b2a8f;color:#f3c34a;font-weight:900;font-size:15px}
.sg-cell.done{background:transparent;color:transparent;box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.12)}
.sg-foot{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;margin:10px 0;color:var(--hint);font-size:14px}
.sg-foot button{background:none;border:0;color:var(--hint);text-decoration:underline;font-size:14px;padding:0}
.sg-end{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;margin-top:10px;text-align:center}
.sg-end h3{margin:0 0 6px;font-size:20px}
.sg-q{position:fixed;inset:0;z-index:60;background:#1b2a8f;color:#fff;display:flex;flex-direction:column;padding:calc(env(safe-area-inset-top,0px) + 14px) 16px calc(env(safe-area-inset-bottom,0px) + 14px);overflow-y:auto}
.sg-qh{display:flex;align-items:center;justify-content:space-between;gap:10px}
.sg-price{font-weight:900;color:#f3c34a;font-size:28px;line-height:1.1}.sg-price small{display:block;font-weight:600;font-size:14px;color:#c9d0ff}
.sg-tm{display:flex;align-items:center;gap:6px}
.sg-tb{height:38px;padding:0 10px;border-radius:10px;border:0;background:rgba(255,255,255,.14);color:#fff;font-weight:600;font-size:14px}
.sg-ring{width:58px;height:58px;position:relative}.sg-ring svg{width:100%;height:100%;transform:rotate(-90deg)}
.sg-ring circle{fill:none;stroke-width:6}.sg-ring .tr{stroke:rgba(255,255,255,.18)}.sg-ring .fg{stroke:#f3c34a;stroke-linecap:round;transition:stroke-dashoffset .25s linear}
.sg-ring b{position:absolute;inset:0;display:grid;place-items:center;font-size:19px;font-weight:900}.sg-ring.low .fg{stroke:#ff6b5e}
.sg-body{flex:1;display:flex;flex-direction:column;justify-content:center;gap:16px;padding:14px 0}
.sg-qt{font-size:23px;line-height:1.3;font-weight:700;margin:0;-webkit-user-select:text;user-select:text}
.sg-ans{background:rgba(255,255,255,.1);border-left:4px solid #f3c34a;border-radius:12px;padding:12px 14px;font-size:19px;font-weight:500;-webkit-user-select:text;user-select:text}
.sg-ans small{display:block;color:#f3c34a;font-size:13px;font-weight:700;margin-bottom:2px}
.sg-show{align-self:flex-start;height:48px;padding:0 20px;border-radius:14px;border:0;background:#f3c34a;color:#2a1d00;font-weight:800;font-size:16px}
.sg-aw p{margin:0 0 8px;color:#c9d0ff;font-size:13px}
.sg-tg{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:6px}
.sg-pick{display:flex;border-radius:12px;overflow:hidden;background:rgba(255,255,255,.1)}
.sg-pick .ok{flex:1;padding:10px 12px;text-align:left;font-weight:700;min-height:54px;border:0;background:none;color:#fff;font-size:15px}
.sg-pick .ok small{display:block;color:#f3c34a;font-weight:900}
.sg-pick .no{width:50px;border:0;font-weight:900;font-size:20px;background:rgba(214,69,61,.35);color:#fff}
.sg-nobody{margin-top:8px;width:100%;height:44px;border-radius:12px;border:0;background:rgba(255,255,255,.14);color:#fff;font-weight:600;font-size:15px}
.sg-flash{animation:sgfl .6s 2}@keyframes sgfl{50%{background:#8a1f1a}}
</style>
<script>
(function(){
const XS = {
 ru:{tab:"🎲 Своя игра",lead:"Классика как на ТВ: выбирайте тему и стоимость 100–500. Играйте одни или командами на одном телефоне — ведущий показывает вопрос, открывает ответ и начисляет баллы.",
  teams:"Сколько команд",timer:"Таймер на вопрос",noT:"Без таймера",sec:"с",team:"Команда",topics:"Тема игры",qs:"вопросов",played:"Сыграно",cont:"продолжить",
  back:"← Темы",left:"Осталось вопросов",all:"Все вопросы сыграны",reset:"Начать тему заново",reset2:"Нажмите ещё раз — счёт и вопросы обнулятся",
  win:"Победитель — ",draw:"Ничья",pause:"Пауза",resume:"Дальше",again:"Заново",show:"Показать ответ",ans:"Ответ",
  hint:"Нажмите на команду — баллы начислятся и вопрос закроется. «−» снимает баллы за ошибку.",nobody:"Никто не ответил — закрыть",solo:"Я",soloOk:"Знал ✅",empty:"Темы пока не добавлены"},
 uz:{tab:"🎲 Oʻz oʻyini",lead:"Televizordagidek: mavzu va 100–500 narxni tanlang. Yolgʻiz yoki bitta telefonda jamoalar boʻlib oʻynang — boshlovchi savolni koʻrsatadi, javobni ochadi va ball beradi.",
  teams:"Jamoalar soni",timer:"Savol taymeri",noT:"Taymersiz",sec:"s",team:"Jamoa",topics:"Oʻyin mavzusi",qs:"savol",played:"Oʻynaldi",cont:"davom etish",
  back:"← Mavzular",left:"Qolgan savollar",all:"Barcha savollar oʻynaldi",reset:"Mavzuni qaytadan boshlash",reset2:"Yana bosing — hisob va savollar tozalanadi",
  win:"Gʻolib — ",draw:"Durang",pause:"Pauza",resume:"Davom",again:"Qayta",show:"Javobni koʻrsatish",ans:"Javob",
  hint:"Jamoani bosing — ball qoʻshiladi va savol yopiladi. «−» xato uchun ball ayiradi.",nobody:"Hech kim javob bermadi — yopish",solo:"Men",soloOk:"Bildim ✅",empty:"Mavzular hali qoʻshilmagan"},
 en:{tab:"🎲 Jeopardy",lead:"Just like on TV: pick a category and a value from 100 to 500. Play solo or in teams on one phone — the host shows the question, reveals the answer and awards points.",
  teams:"Number of teams",timer:"Timer per question",noT:"No timer",sec:"s",team:"Team",topics:"Game topic",qs:"questions",played:"Played",cont:"continue",
  back:"← Topics",left:"Questions left",all:"All questions played",reset:"Restart topic",reset2:"Tap again — scores and questions will reset",
  win:"Winner — ",draw:"Draw",pause:"Pause",resume:"Resume",again:"Restart",show:"Show answer",ans:"Answer",
  hint:"Tap a team to award points and close the question. “−” takes points for a wrong answer.",nobody:"Nobody answered — close",solo:"Me",soloOk:"Knew it ✅",empty:"No topics yet"},
 zh:{tab:"🎲 抢答游戏",lead:"像电视节目一样：选择主题和分值 100–500。可以一个人玩，也可以在一部手机上分队玩——主持人出题、公布答案并计分。",
  teams:"队伍数量",timer:"每题计时",noT:"不计时",sec:"秒",team:"队伍",topics:"游戏主题",qs:"题",played:"已玩",cont:"继续",
  back:"← 主题",left:"剩余题目",all:"全部题目已完成",reset:"重新开始本主题",reset2:"再点一次——分数和题目将清零",
  win:"获胜者——",draw:"平局",pause:"暂停",resume:"继续",again:"重来",show:"显示答案",ans:"答案",
  hint:"点击队伍加分并关闭题目。“−”答错扣分。",nobody:"无人答对——关闭",solo:"我",soloOk:"答对 ✅",empty:"暂无主题"}
};
const xs = () => XS[S.lang] || XS.ru;
const PR = [100, 200, 300, 400, 500], TM = [0, 15, 30, 45, 60, 90], RC = 2 * Math.PI * 25;
const ld = (k, d) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } };
const sv = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };
const G = {data: null, cfg: ld("sg-cfg", {n: 1, names: [], timer: 30}), game: null, cur: null, t: null, left: 0, paused: false};

// ---------- третья вкладка ----------
function addTab() {
  const tb = document.querySelector(".tabs");
  if (!tb || tb.querySelector('[data-t="sg"]')) return;
  tb.classList.add("t3");
  tb.insertAdjacentHTML("beforeend", `<button data-t="sg">${xs().tab}</button>`);
  tb.querySelector('[data-t="sg"]').onclick = () => { hap(); S.tab = "sg"; screenSG(); };
}
const _dl3 = drawList;
drawList = function() { if (S.tab === "sg") return screenSG(); const r = _dl3(); addTab(); return r; };
const _ss3 = screenSubjects;
screenSubjects = async function() { await _ss3(); addTab(); };

function tabsHtml() {
  const l = L();
  return `<div class="tabs t3"><button data-t="test">${l.tabT}</button><button data-t="trainer">${l.tabR}</button><button data-t="sg" class="on">${xs().tab}</button></div>`;
}
function names() {
  const c = G.cfg;
  return Array.from({length: c.n}, (_, i) => (c.names[i] || "").trim() || (c.n === 1 ? xs().solo : `${xs().team} ${i + 1}`));
}

// ---------- главная: настройки и темы ----------
async function screenSG() {
  const t = xs();
  S.tab = "sg"; S.quiz = null; S.st = null;
  if (!G.data) {
    html('<div class="spin"><i></i></div>');
    const r = await api("/api/sg");
    G.data = r.ok ? r.topics : [];
    if (S.tab !== "sg") return;
  }
  const c = G.cfg;
  html(`<button class="pcard" id="pc">${S.me.av ? avaImg(S.me.uid, S.me.av, "ava") : '<span class="lv">👤</span>'}<span><b>${L().prof}</b><span>${esc(S.me.name || "")}</span></span></button>
    ${tabsHtml()}
    <div class="sg-hero"><h2>Своя <span>игра</span></h2><p>${t.lead}</p></div>
    <div class="sg-set"><h4>${t.teams}</h4><div class="sg-seg" id="sgn">${[1, 2, 3, 4, 5, 6].map(n => `<button data-n="${n}" class="${c.n === n ? "on" : ""}">${n}</button>`).join("")}</div>
    ${c.n > 1 ? `<div class="sg-names">${Array.from({length: c.n}, (_, i) => `<input data-i="${i}" maxlength="24" value="${esc(c.names[i] || "")}" placeholder="${t.team} ${i + 1}">`).join("")}</div>` : ""}
    <h4>${t.timer}</h4><div class="sg-seg" id="sgt" style="margin:0">${TM.map(s => `<button data-t="${s}" class="${c.timer === s ? "on" : ""}">${s ? s + " " + t.sec : t.noT}</button>`).join("")}</div></div>
    <h3>${t.topics}</h3>
    ${G.data.length ? G.data.map((d, i) => {
      const st = ld("sg-g" + d.id, null), tot = d.cats.length * 5;
      return `<button class="sg-topic" data-i="${i}"><b>${i + 1}</b><span>${esc(d.title)}<small>${st && st.used.length ? `${t.played} ${st.used.length} / ${tot} — ${t.cont}` : `${tot} ${t.qs}`}</small></span></button>`;
    }).join("") : `<div class="card muted" style="text-align:center">${t.empty}</div>`}`);
  setBack(null);
  $("#pc").onclick = () => { hap(); screenProfile(); };
  document.querySelectorAll(".tabs button").forEach(b => b.onclick = () => { hap(); S.tab = b.dataset.t; S.subj = ""; S.msg = ""; S.tab === "sg" ? screenSG() : drawList(); });
  document.querySelectorAll("#sgn button").forEach(b => b.onclick = () => { hap(); c.n = +b.dataset.n; sv("sg-cfg", c); screenSG(); });
  document.querySelectorAll("#sgt button").forEach(b => b.onclick = () => { hap(); c.timer = +b.dataset.t; sv("sg-cfg", c); screenSG(); });
  document.querySelectorAll(".sg-names input").forEach(inp => inp.oninput = () => { c.names[+inp.dataset.i] = inp.value; sv("sg-cfg", c); });
  document.querySelectorAll(".sg-topic").forEach(b => b.onclick = () => { hap(); startSG(+b.dataset.i); });
}

// ---------- игровое поле ----------
function startSG(i) {
  const d = G.data[i], n = G.cfg.n;
  let st = ld("sg-g" + d.id, null);
  if (!st || st.n !== n) st = {used: [], scores: Array(n).fill(0), n};
  G.game = {i, d, used: st.used, scores: st.scores, n, names: names(), armed: false};
  board();
}
const persist = () => { const g = G.game; sv("sg-g" + g.d.id, {used: g.used, scores: g.scores, n: g.n}); };
function board() {
  const t = xs(), g = G.game, tot = g.d.cats.length * 5, left = tot - g.used.length;
  const max = Math.max(...g.scores);
  let cells = "";
  g.d.cats.forEach((c, ci) => {
    cells += `<div class="sg-cat">${esc(c.name)}</div>`;
    PR.forEach((p, k) => { const id = ci * 5 + k, done = g.used.includes(id); cells += `<button class="sg-cell ${done ? "done" : ""}" data-id="${id}" ${done ? "disabled" : ""}>${p}</button>`; });
  });
  const win = g.names.filter((_, i) => g.scores[i] === max);
  html(`<button class="bk" id="bk">${t.back}</button><h2 style="margin:6px 0">🎲 ${esc(g.d.title)}</h2>
    <div class="sg-scores">${g.names.map((nm, i) => `<div class="sg-team ${g.n > 1 && g.scores[i] === max && max > 0 ? "lead" : ""}"><span class="nm">${esc(nm)}</span>
      <span class="sc ${g.scores[i] < 0 ? "neg" : ""}">${g.scores[i]}</span><div class="adj"><button class="sg-mi" data-i="${i}" data-d="-100">−100</button><button class="sg-pl" data-i="${i}" data-d="100">+100</button></div></div>`).join("")}</div>
    <div class="sg-board">${cells}</div>
    ${left ? "" : `<div class="sg-end"><h3>🏆 ${win.length > 1 && g.n > 1 ? t.draw : (g.n > 1 ? t.win + esc(win[0]) : g.scores[0])}</h3><div class="muted">${g.names.map((nm, i) => esc(nm) + ": " + g.scores[i]).join(" · ")}</div></div>`}
    <div class="sg-foot"><span>${left ? `${t.left}: ${left}` : t.all}</span><button id="rs">${g.armed ? t.reset2 : t.reset}</button></div>`);
  const out = () => { G.game = null; screenSG(); };
  $("#bk").onclick = out; setBack(out);
  document.querySelectorAll(".sg-team button").forEach(b => b.onclick = () => { hap(); g.scores[+b.dataset.i] += +b.dataset.d; persist(); board(); });
  document.querySelectorAll(".sg-cell:not(.done)").forEach(b => b.onclick = () => { hap(); openQ(+b.dataset.id); });
  $("#rs").onclick = () => {
    if (!g.armed) { g.armed = true; board(); $("#rs").style.color = "var(--red)"; setTimeout(() => { if (G.game === g && g.armed) { g.armed = false; board(); } }, 4000); return; }
    g.armed = false; g.used = []; g.scores = Array(g.n).fill(0); persist(); board(); hap("ok");
  };
}

// ---------- вопрос ----------
function openQ(id) {
  const t = xs(), g = G.game, c = g.d.cats[Math.floor(id / 5)], price = PR[id % 5], [q, a] = c.qs[id % 5];
  G.cur = {id, price};
  const o = document.createElement("div");
  o.className = "sg-q"; o.id = "sgq";
  o.innerHTML = `<div class="sg-qh"><div class="sg-price"><small>${esc(c.name)}</small>${price}</div>
    ${G.cfg.timer ? `<div class="sg-tm"><button class="sg-tb" id="tp">${t.pause}</button><button class="sg-tb" id="tr">${t.again}</button>
      <div class="sg-ring" id="rg"><svg viewBox="0 0 58 58"><circle class="tr" cx="29" cy="29" r="25"/><circle class="fg" id="rf" cx="29" cy="29" r="25"/></svg><b id="tn"></b></div></div>` : ""}</div>
    <div class="sg-body"><p class="sg-qt">${esc(q)}</p><div class="sg-ans" id="an" hidden><small>${t.ans}</small>${esc(a)}</div><button class="sg-show" id="sh">${t.show}</button></div>
    <div class="sg-aw"><p>${t.hint}</p><div class="sg-tg">${g.names.map((nm, i) => `<div class="sg-pick"><button class="ok" data-i="${i}">${g.n === 1 ? t.soloOk : esc(nm)}<small>+${price}</small></button><button class="no" data-i="${i}">−</button></div>`).join("")}</div>
    <button class="sg-nobody" id="nb">${t.nobody}</button></div>`;
  document.body.appendChild(o);
  document.body.style.overflow = "hidden";
  o.querySelector("#sh").onclick = () => { hap(); o.querySelector("#an").hidden = false; o.querySelector("#sh").remove(); };
  o.querySelectorAll(".ok").forEach(b => b.onclick = () => { hap("ok"); g.scores[+b.dataset.i] += price; closeQ(); });
  o.querySelectorAll(".no").forEach(b => b.onclick = () => { hap("bad"); g.scores[+b.dataset.i] -= price; closeQ(); });
  o.querySelector("#nb").onclick = () => { hap(); closeQ(); };
  if (G.cfg.timer) { o.querySelector("#tp").onclick = () => { G.paused = !G.paused; o.querySelector("#tp").textContent = G.paused ? t.resume : t.pause; }; o.querySelector("#tr").onclick = startT; startT(); }
  setBack(() => closeQ(true));
}
function closeQ(cancel) {
  stopT();
  const o = $("#sgq"); if (o) o.remove();
  document.body.style.overflow = "";
  if (!cancel && G.cur) { G.game.used.push(G.cur.id); persist(); }
  G.cur = null;
  if (G.game) board();
}
function startT() {
  stopT(); G.left = G.cfg.timer; G.paused = false;
  const p = $("#tp"); if (p) p.textContent = xs().pause;
  drawT();
  G.t = setInterval(() => { if (G.paused) return; G.left--; drawT(); if (G.left <= 0) { stopT(); timeUp(); } }, 1000);
}
function stopT() { clearInterval(G.t); G.t = null; }
function drawT() {
  const n = $("#tn"), f = $("#rf"); if (!n || !f) return;
  n.textContent = Math.max(G.left, 0);
  f.style.strokeDasharray = RC; f.style.strokeDashoffset = RC * (1 - Math.max(G.left, 0) / G.cfg.timer);
  $("#rg").classList.toggle("low", G.left <= 5);
}
function timeUp() {
  const q = $("#sgq"); if (!q) return;
  q.classList.remove("sg-flash"); void q.offsetWidth; q.classList.add("sg-flash"); hap("bad");
  try {
    const ac = new (window.AudioContext || window.webkitAudioContext)();
    [0, .25, .5].forEach(t => { const o = ac.createOscillator(), g = ac.createGain(); o.frequency.value = t < .5 ? 660 : 440; o.connect(g); g.connect(ac.destination);
      g.gain.setValueAtTime(.25, ac.currentTime + t); g.gain.exponentialRampToValueAtTime(.001, ac.currentTime + t + .22); o.start(ac.currentTime + t); o.stop(ac.currentTime + t + .23); });
  } catch (e) {}
}
})();
</script>
