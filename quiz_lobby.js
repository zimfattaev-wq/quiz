<style>
.lb-big{font-size:46px;font-weight:900;text-align:center;line-height:1;color:var(--accent);margin:6px 0}
.lb-big span{font-size:22px;color:var(--hint)}
.lb-bar{height:10px;border-radius:6px;background:var(--line);overflow:hidden;margin:10px 0 8px}
.lb-bar i{display:block;height:100%;background:var(--green);border-radius:6px;transition:width .4s}
.lb-h{margin:14px 0 6px;font-size:15px;font-weight:800}
.lb-p{display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--line);font-size:15px}
.lb-p:last-child{border-bottom:0}
.lb-p .nm{flex:1;min-width:0}
.lb-p .nm small{display:block;color:#d9480f;font-size:12px;font-weight:600}
.lb-p .nm small.ext{color:var(--hint)}
.lb-p.me{background:#eaf1ff;border-radius:10px;padding:8px}
.lb-dot{width:9px;height:9px;border-radius:50%;background:var(--green);flex:none;animation:lbp 1.6s infinite}
@keyframes lbp{50%{opacity:.35}}
.lb-miss{color:var(--hint)}
</style>
<script>
(function(){
const XL = {
 ru:{enter:"👥 Войти в зал ожидания",title:"Зал ожидания",of:"из",wait:"Тест начнётся сам, когда одновременно соберутся {n} человек. Не закрывайте приложение — если выйти, место в зале пропадёт.",
  go:"🚀 Набралось! Тест начинается…",inRoom:"✅ В зале",miss:"⏳ Ещё не зашли",typo:"имя с ошибкой — написано: ",ext:"нет в списке группы",me:"вы",
  force:"▶️ Запустить тест сейчас (админ)",already:"Тест уже запущен — можно начинать",start:"▶️ Начать тест",started:"уже начали тест",nobody:"Все из списка зашли 🎉",
  need:"Для начала нужно {n} человек одновременно"},
 uz:{enter:"👥 Kutish zaliga kirish",title:"Kutish zali",of:"/",wait:"Bir vaqtda {n} kishi yigʻilganda test oʻzi boshlanadi. Ilovani yopmang — chiqsangiz, zaldagi oʻrningiz yoʻqoladi.",
  go:"🚀 Yigʻildi! Test boshlanmoqda…",inRoom:"✅ Zalda",miss:"⏳ Hali kirmaganlar",typo:"ism xato yozilgan: ",ext:"guruh roʻyxatida yoʻq",me:"siz",
  force:"▶️ Testni hozir boshlash (admin)",already:"Test allaqachon boshlangan — boshlash mumkin",start:"▶️ Testni boshlash",started:"testni boshlagan",nobody:"Roʻyxatdagilarning hammasi kirdi 🎉",
  need:"Boshlash uchun bir vaqtda {n} kishi kerak"},
 en:{enter:"👥 Enter the waiting room",title:"Waiting room",of:"of",wait:"The test starts by itself once {n} people are here at the same time. Keep the app open — if you leave, you lose your place.",
  go:"🚀 Everyone's here! Starting…",inRoom:"✅ In the room",miss:"⏳ Not here yet",typo:"name has a typo — typed: ",ext:"not in the group list",me:"you",
  force:"▶️ Start the test now (admin)",already:"The test has started — you can begin",start:"▶️ Start test",started:"already started",nobody:"Everyone from the list is here 🎉",
  need:"{n} people must be here at once to start"},
 zh:{enter:"👥 进入等候室",title:"等候室",of:"/",wait:"同时到齐 {n} 人后测验会自动开始。请不要关闭应用——离开会失去位置。",
  go:"🚀 人齐了！测验开始…",inRoom:"✅ 已进入",miss:"⏳ 尚未进入",typo:"姓名有误——填写为：",ext:"不在班级名单中",me:"你",
  force:"▶️ 立即开始测验（管理员）",already:"测验已开始——可以作答",start:"▶️ 开始测验",started:"已开始作答",nobody:"名单上的人都到了 🎉",
  need:"需要同时有 {n} 人才能开始"}
};
const xl = () => XL[S.lang] || XL.ru;
let LB = null;   // {code, t}

const _in = screenIntro;
screenIntro = function() {
  const r = _in();
  const q = S.quiz;
  if (q && q.kind !== "trainer" && q.open && !q.result && q.lobby && !q.lobby.go && $("#go")) {
    $("#go").textContent = xl().enter;
    $("#go").insertAdjacentHTML("beforebegin", `<div class="muted" style="margin:8px 0">👥 ${xl().need.replace("{n}", q.lobby.need)}</div>`);
    $("#go").onclick = () => { hap(); screenLobby(q); };
  }
  return r;
};
// на всякий случай: сервер ответил «нужен зал ожидания»
const _apiL = api;
api = async function(path, body, ...a) {
  const r = await _apiL(path, body, ...a);
  if (path === "/api/start" && r && r.error === "lobby" && S.quiz) { setTimeout(() => screenLobby(S.quiz), 0); return {ok: false, error: "net"}; }
  return r;
};

function stopLobby(leave) {
  if (!LB) return;
  clearTimeout(LB.t);
  if (leave) api("/api/lobby/leave", {code: LB.code});
  LB = null;
}
async function begin(code) {
  stopLobby(false);
  const r = await _apiL("/api/start", {code});
  if (r.ok) return show(r.state);
  if (r.error === "done") { const x = await api("/api/result?q=" + code); return screenDone({result: x.result, top: x.top, title: S.quiz && S.quiz.title, code}, true); }
  screenList(L()[r.error === "closed" ? "closed" : "noQuiz"]);
}
async function screenLobby(q) {
  stopLobby(false);
  LB = {code: q.code, t: null};
  const me = LB;
  html('<div class="spin"><i></i></div>');
  const out = () => { stopLobby(true); toList(); };
  setBack(out);
  const tick = async () => {
    if (LB !== me) return;
    if (document.hidden) { me.t = setTimeout(tick, 1500); return; }
    const r = await api("/api/lobby?code=" + encodeURIComponent(q.code));
    if (LB !== me) return;
    if (!r.ok) { stopLobby(false); return screenList(L()[r.error === "closed" ? "closed" : "noQuiz"]); }
    if (r.done) return begin(q.code);
    if (r.go && !r.admin) { draw(r, true); hap("ok"); return setTimeout(() => begin(q.code), 900); }
    draw(r, false);
    me.t = setTimeout(tick, 2000);
  };
  const draw = (r, going) => {
    const t = xl(), pct = Math.min(100, Math.round(100 * r.n / Math.max(1, r.need)));
    html(`${backBtn()}<div class="card"><h2>👥 ${t.title}</h2><div class="muted">📝 ${esc(r.title)}${r.group ? " · " + esc(r.group) : ""}</div>
      <div class="lb-big">${r.n} <span>${t.of} ${r.need}</span></div><div class="lb-bar"><i style="width:${pct}%"></i></div>
      <div class="muted">${going ? `<b style="color:var(--green)">${t.go}</b>` : (r.go ? t.already : t.wait.replace("{n}", r.need))}</div>
      ${r.go && r.admin ? `<button class="btn" id="lbs">${t.start}</button>` : ""}
      ${!r.go && r.admin ? `<button class="btn ghost" id="lbf" style="margin-top:10px">${t.force}</button>` : ""}</div>
      <div class="card"><div class="lb-h">${t.inRoom} — ${r.joined.length}${r.started ? ` · ${r.started} ${t.started}` : ""}</div>
      ${r.joined.map(p => `<div class="lb-p ${p.me ? "me" : ""}"><span class="lb-dot"></span>${avaImg(p.uid, p.av, "avs")}<span class="nm">${esc(p.roster || p.name)}${p.me ? ` <span class="muted">(${t.me})</span>` : ""}
        ${p.roster && p.typo ? `<small>⚠️ ${t.typo}«${esc(p.name)}»</small>` : ""}${!p.roster ? `<small class="ext">❔ ${t.ext}</small>` : ""}</span></div>`).join("")}
      ${r.group ? `<div class="lb-h">${t.miss} — ${r.missing.length}</div>${r.missing.length ? r.missing.map(n => `<div class="lb-p lb-miss">⚪️ <span class="nm">${esc(n)}</span></div>`).join("") : `<div class="muted">${t.nobody}</div>`}` : ""}</div>`);
    wireBack(out);
    if ($("#lbf")) $("#lbf").onclick = async () => { hap(); const x = await api("/api/lobby/go", {code: q.code}); if (x.ok) begin(q.code); };
    if ($("#lbs")) $("#lbs").onclick = () => { hap(); begin(q.code); };
  };
  tick();
}
document.addEventListener("visibilitychange", () => { if (!document.hidden && LB) { clearTimeout(LB.t); const q = S.quiz; if (q && q.code === LB.code) screenLobby(q); } });
})();
</script>
