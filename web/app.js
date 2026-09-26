const $ = (selector) => document.querySelector(selector);
const state = { packs: [], pack: null, draft: null, run: null, busy: false, filter: "all", poll: 0, submitKey: null };
const statuses = {queued:"대기 중",running:"실행 중",awaiting_review:"사람 검토 대기",completed:"검토 완료",failed:"실행 실패"};
const stages = [["normalize","문서 준비"],["extract","기준 추출"],["retrieve","근거 검색"],["review","검토"],["critic","검증"]];
function el(tag, className = "", text = "") {
  const node = document.createElement(tag);
  if (className) node.className = className;
  node.textContent = text;
  return node;
}
function button(text, className, action) {
  const node = el("button", className, text);
  node.type = "button";
  node.addEventListener("click", () => perform(action));
  return node;
}
function notice(message = "") {
  $("#notice").textContent = message;
  $("#notice").classList.toggle("hidden", !message);
}
async function api(path, options = {}) {
  const response = await fetch(path, { ...options, headers: {"Content-Type":"application/json", ...options.headers}});
  const body = await response.json();
  if (!response.ok) {
    const detail = Array.isArray(body.detail) ? body.detail.map(item => item.msg).join(" / ") : body.detail;
    throw new Error(body.error?.message || detail || "요청에 실패했습니다.");
  }
  return body;
}
async function perform(action) {
  try { await action(); } catch (error) { notice(error.message || "작업을 완료하지 못했습니다."); }
}
function switchView(view) {
  ["workspace","history","guide"].forEach(name => $("#"+name+"-view").classList.toggle("hidden", name !== view));
  document.querySelectorAll(".nav").forEach(node => node.classList.toggle("active", node.dataset.view === view));
  if (view === "history") perform(loadHistory);
}
function setBusy(value) {
  state.busy = value;
  document.querySelectorAll(".input-panel button, .input-panel input, .input-panel select, .input-panel textarea, .pack").forEach(node => node.disabled = value);
  $("#run").textContent = value ? "검토 실행 중…" : "검토 실행 →";
}
function markDirty() {
  state.submitKey = null;
  if (state.run && !state.busy) {
    state.run = null;
    state.poll++;
    renderResults();
  }
}
function renderPacks() {
  const container = $("#packs");
  container.replaceChildren();
  state.packs.forEach((pack, index) => {
    const selected = state.pack?.id === pack.id;
    const node = button("", "pack " + (selected ? "selected" : ""), () => choosePack(pack.id));
    node.setAttribute("aria-label", pack.name);
    node.setAttribute("aria-pressed", String(selected));
    node.append(el("span","pack-symbol", index ? "◫" : "◈"));
    const copy = el("div");
    copy.append(el("strong","",pack.name), el("p","",pack.description));
    node.append(copy, el("span","pack-check", selected ? "✓" : ""));
    node.disabled = state.busy;
    container.append(node);
  });
}
async function choosePack(id) {
  if (state.busy) return;
  const example = await api("/api/packs/"+encodeURIComponent(id)+"/example");
  state.pack = state.packs.find(pack => pack.id === id);
  state.draft = example;
  state.submitKey = null;
  state.run = null;
  state.filter = "all";
  state.poll++;
  notice();
  renderPacks();
  renderInputs();
  renderResults();
}
function renderInputs() {
  $("#run-title").value = state.draft.title;
  $("#run-mode").value = state.draft.mode;
  updateModeNote();
  const container = $("#documents");
  container.replaceChildren();
  state.draft.documents.forEach((doc, index) => {
    const wrap = el("section","document");
    const top = el("div","doc-top");
    top.append(el("span","",doc.role === "basis" ? state.pack.basis_label : state.pack.target_label));
    const fileLabel = el("label","doc-file","TXT · MD 불러오기");
    const file = el("input");
    file.type = "file"; file.accept = ".txt,.md"; file.hidden = true;
    file.addEventListener("change", () => perform(async () => {
      if (!file.files[0]) return;
      if (file.files[0].size > 150000) throw new Error("파일은 150KB 이하여야 합니다.");
      const text = await file.files[0].text();
      if (text.includes("\u0000")) throw new Error("UTF-8 텍스트 파일을 선택하세요.");
      doc.content = text; doc.title = file.files[0].name;
      markDirty(); renderInputs();
    }));
    fileLabel.append(file); top.append(fileLabel);
    const meta = el("div","doc-meta");
    const title = el("input","control doc-title");
    title.value = doc.title; title.maxLength = 160; title.setAttribute("aria-label", "문서 "+(index+1)+" 이름");
    title.addEventListener("input", () => {doc.title = title.value; markDirty();});
    const version = el("input","control doc-version");
    version.value = doc.version; version.maxLength = 40; version.setAttribute("aria-label","문서 "+(index+1)+" 버전");
    version.addEventListener("input", () => {doc.version = version.value; markDirty();});
    meta.append(title, version);
    const area = el("textarea");
    area.value = doc.content; area.maxLength = 30000;
    area.setAttribute("aria-label",doc.role === "basis" ? "기준 문서 내용" : "검토 대상 내용");
    area.addEventListener("input", () => {doc.content = area.value; markDirty();});
    const complete = el("label","doc-complete");
    const check = el("input"); check.type = "checkbox"; check.checked = doc.complete;
    check.addEventListener("change", () => {doc.complete = check.checked; markDirty();});
    complete.append(check, document.createTextNode("검토 범위의 전체 문서입니다"));
    wrap.append(top, meta, area, complete); container.append(wrap);
  });
}
function updateModeNote() {
  $("#mode-note").textContent = state.draft.mode === "demo"
    ? "예제의 고정 응답입니다. AI 분석이 아닙니다."
    : "설정된 모델 서버로 문서가 전송됩니다.";
}
async function startRun() {
  if (!state.draft || state.busy) return;
  notice();
  state.filter = "all";
  setBusy(true);
  try {
    const run = await api("/api/runs", {
      method:"POST", headers:{"Idempotency-Key":state.submitKey ||= crypto.randomUUID()},
      body:JSON.stringify(state.draft),
    });
    state.submitKey = null;
    state.run = run; renderResults();
    await pollRun(run.id);
  } catch (error) { setBusy(false); throw error; }
}
async function pollRun(id) {
  const token = ++state.poll;
  while (token === state.poll) {
    const run = await api("/api/runs/"+id);
    if (token !== state.poll) return;
    if (!state.run || run.revision !== state.run.revision) {state.run = run; renderResults();}
    if (!["queued","running"].includes(run.status)) {
      setBusy(false);
      if (run.error) notice(run.error.message);
      return;
    }
    await new Promise(resolve => setTimeout(resolve, 500));
  }
}
function renderMetrics() {
  const run = state.run;
  const items = run?.items || [];
  const issueCount = items.filter(item => item.verdict !== "covered").length;
  const decided = items.filter(item => item.decision).length;
  const ms = run ? run.trace.reduce((total, event) => total + event.duration_ms, 0) : null;
  const values = [
    ["검토 항목",run ? items.length : "—","건"],
    ["확인할 항목",run ? issueCount : "—","건"],
    ["의견 저장",run ? decided : "—","건"],
    ["실행 시간",ms === null ? "—" : (ms / 1000).toFixed(2),"초"],
  ];
  $("#metrics").replaceChildren(...values.map(([label,value,unit]) => {
    const node = el("div","metric");
    const line = el("div");
    line.append(el("span","metric-value",String(value)),el("span","metric-unit",unit));
    node.append(el("span","metric-label",label),line);return node;
  }));
}
function renderResults() {
  renderMetrics();
  const run = state.run;
  $("#run-badge").textContent = run ? statuses[run.status] : "실행 대기";
  $("#run-badge").className = "badge " + (run?.status || "neutral");
  $("#pipeline").replaceChildren(...stages.map(([id,label]) => {
    const done = run?.trace.some(event => event.stage === id);
    const active = run?.stage === id && run?.status === "running";
    return el("span","pipeline-step" + (done ? " done" : active ? " active" : ""),label);
  }));
  const result = $("#result-content");
  result.replaceChildren();
  $("#result-footer").classList.add("hidden");
  if (!run || ["queued","running"].includes(run.status)) {
    const empty = el("div","empty");
    empty.append(el("div","empty-symbol",run ? "↻" : "✓"),
      el("h3","",run ? "근거를 연결하고 있습니다" : "검토할 문서를 준비해 주세요"),
      el("p","",run ? "완료되면 기준별 판정과 수정안을 보여드립니다." : "예제를 실행하면 원문 근거부터 사람의 검토까지 전체 흐름을 볼 수 있습니다."));
    result.append(empty); return;
  }
  if (run.status === "failed") {
    const empty = el("div","empty");
    empty.append(el("h3","","검토를 완료하지 못했습니다"),el("p","",run.error?.message || ""));
    result.append(empty);return;
  }
  const info = el("div","run-info");
  info.append(el("strong","",run.request.mode === "demo" ? "예제 재생 · 실제 AI 분석 아님" : "모델 분석 · 사람 확인 필요"));
  info.append(el("div","",run.request.title));
  result.append(info);
  const toolbar = el("div","result-toolbar");
  [["all","전체"],...Object.entries(run.pack.labels)].forEach(([key,label]) => {
    const count = key === "all" ? run.items.length : run.items.filter(item=>item.verdict===key).length;
    toolbar.append(button(label+" "+count,"filter-button" + (state.filter === key ? " active" : ""),() => {state.filter=key;renderResults();}));
  });
  result.append(toolbar);
  const items = run.items.filter(item => state.filter === "all" || item.verdict === state.filter);
  if (!items.length) result.append(el("div","empty","해당 판정의 항목이 없습니다."));
  items.forEach(item => result.append(renderFinding(item,run)));
  const footer = $("#result-footer");footer.replaceChildren();footer.classList.remove("hidden");
  const report = el("a","download-link","보고서 내려받기");
  report.href = "/api/runs/"+run.id+"/report.md"; report.download = "review-"+run.id+".md";
  footer.append(report,button("JSON 내보내기","download-link",()=>downloadJSON(run)),el("span","run-version","revision "+run.revision));
  if (run.audit.length) {
    const audit = el("details", "audit-log");
    audit.append(el("summary", "", "검토 이력 " + run.audit.length + "건"));
    run.audit.slice().reverse().forEach(entry => {
      const actionName = {accept:"채택", reject:"반려", edit:"수정"}[entry.action];
      const line = el("div", "audit-entry");
      line.append(el("strong", "", entry.criterion_id + " · " + actionName + " · " + entry.actor));
      line.append(el("p", "", entry.note || "메모 없음"));
      line.append(el("small", "", new Date(entry.at).toLocaleString("ko-KR")));
      audit.append(line);
    });
    footer.append(audit);
  }
}
function renderFinding(item,run) {
  const criterion = run.criteria.find(c => c.id === item.criterion_id);
  const node = el("article","finding");
  const heading = el("div","finding-heading");
  heading.append(el("span","finding-id",item.criterion_id),el("span","badge "+item.verdict,run.pack.labels[item.verdict]));
  node.append(heading,el("h3","finding-title",criterion?.title || item.criterion_id),el("p","finding-reason",item.reason));
  const evidence = el("div","evidence-row");
  if (criterion) evidence.append(button("기준 원문","evidence-button",()=>showEvidence(criterion.source.chunk_id,run)));
  item.evidence.forEach((citation,index) => evidence.append(button("근거 "+(index+1)+" · "+citation.chunk_id,"evidence-button",()=>showEvidence(citation.chunk_id,run))));
  node.append(evidence);
  const suggestion = item.decision?.action === "edit" ? item.decision.edited_suggestion : item.suggestion;
  if (suggestion) {
    const box=el("div","suggestion");
    box.append(el("span","suggestion-label",item.decision?.action==="edit" ? "담당자가 수정한 제안" : "수정 제안"),document.createTextNode(suggestion));
    node.append(box);
  }
  item.validation_issues.forEach(issue=>node.append(el("div","validation-note",issue)));
  if (item.decision) {
    const actionName={accept:"채택",reject:"반려",edit:"수정"}[item.decision.action];
    node.append(el("p","decision-summary","의견 저장됨 · "+item.decision.actor+" · "+actionName));
  }
  const details=el("details","decision-form");details.append(el("summary","",item.decision ? "검토 의견 변경" : "검토 의견 남기기"));
  const fields=el("div","decision-fields");
  const actorLabel=el("label","","담당자");
  const actor=el("input"); actor.placeholder="이름 또는 역할";actor.value=item.decision?.actor || "PM";
  actor.setAttribute("aria-label",item.criterion_id+" 담당자");actorLabel.append(actor);
  const actionLabel=el("label","","결정");
  const action=el("select");action.setAttribute("aria-label",item.criterion_id+" 결정");
  [["accept","의견 채택"],["reject","반려"],["edit","제안 수정"]].forEach(([value,text])=>{const option=el("option","",text);option.value=value;action.append(option);});
  action.value=item.decision?.action || "accept"; actionLabel.append(action);
  const noteLabel=el("label","full","검토 메모 · 반려/수정 시 필수");
  const note=el("textarea");note.value=item.decision?.note || "";note.setAttribute("aria-label",item.criterion_id+" 검토 메모");noteLabel.append(note);
  const editLabel=el("label","full","수정할 제안");
  const edit=el("textarea");edit.value=item.decision?.edited_suggestion || item.suggestion || "";edit.setAttribute("aria-label",item.criterion_id+" 수정 제안");editLabel.append(edit);
  editLabel.classList.toggle("hidden",action.value!=="edit");
  action.addEventListener("change",()=>editLabel.classList.toggle("hidden",action.value!=="edit"));
  fields.append(actorLabel,actionLabel,noteLabel,editLabel);
  const save=button("의견 저장","save-button",async()=>{
    save.disabled=true;
    try{
      const updated=await api("/api/runs/"+run.id+"/decisions",{method:"POST",body:JSON.stringify({
        revision:run.revision,criterion_id:item.criterion_id,action:action.value,
        actor:actor.value,note:note.value,edited_suggestion:action.value==="edit"?edit.value:null
      })});
      state.run=updated;notice();renderResults();
    }finally{save.disabled=false;}
  });
  details.append(fields,save);node.append(details);return node;
}
function showEvidence(id,run) {
  const chunk=run.chunks.find(chunk=>chunk.id===id);
  if(!chunk)throw new Error("근거를 찾을 수 없습니다.");
  $("#evidence-title").textContent=chunk.document_title;
  $("#evidence-meta").textContent=chunk.document_version+" · 문단 "+chunk.paragraph+" · "+chunk.id;
  $("#evidence-text").textContent=chunk.text;$("#evidence-dialog").showModal();
}
function downloadJSON(run) {
  const url=URL.createObjectURL(new Blob([JSON.stringify(run,null,2)],{type:"application/json"}));
  const link=el("a");link.href=url;link.download="review-"+run.id+".json";link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
async function loadHistory() {
  const {runs}=await api("/api/runs");
  const container=$("#history-list");container.replaceChildren();
  if(!runs.length){container.append(el("div","empty","저장된 실행이 없습니다. 첫 검토를 시작해 보세요."));return;}
  runs.forEach(run=>{
    const row=button("","history-row",()=>openRun(run.id));
    const copy=el("div");copy.append(el("strong","",run.title),el("small","",run.pack_name+" · "+new Date(run.created_at).toLocaleString("ko-KR")+" · "+(run.mode==="demo"?"예제":"모델")));
    row.append(copy,el("span","badge "+run.status,statuses[run.status]));container.append(row);
  });
}
async function openRun(id) {
  const run=await api("/api/runs/"+id);
  state.poll++;state.run=run;state.draft=structuredClone(run.request);
  state.pack=run.pack;state.filter="all";setBusy(false);
  renderPacks();renderInputs();renderResults();switchView("workspace");notice();
  if(["queued","running"].includes(run.status)){
    setBusy(true);
    try { await pollRun(id); } finally { if (state.run?.id === id) setBusy(false); }
  }
}
document.querySelectorAll(".nav").forEach(node=>node.addEventListener("click",()=>switchView(node.dataset.view)));
$("#run-title").addEventListener("input",()=>{state.draft.title=$("#run-title").value;markDirty();});
$("#run-mode").addEventListener("change",()=>{state.draft.mode=$("#run-mode").value;markDirty();updateModeNote();});
$("#load-example").addEventListener("click",()=>perform(()=>choosePack(state.pack.id)));
$("#run").addEventListener("click",()=>perform(startRun));
$("#refresh-history").addEventListener("click",()=>perform(loadHistory));
$("#close-evidence").addEventListener("click",()=>$("#evidence-dialog").close());
$("#import-json").addEventListener("change",()=>perform(async()=>{
  const file=$("#import-json").files[0];if(!file)return;
  if(file.size>500000)throw new Error("JSON 파일은 500KB 이하여야 합니다.");
  const input=JSON.parse(await file.text());
  const pack=state.packs.find(pack=>pack.id===input.pack_id);
  if(!pack || !Array.isArray(input.documents) || input.documents.length<2 || input.documents.length>8
    || !input.documents.every(doc=>typeof doc.content==="string" && typeof doc.title==="string" && typeof doc.version==="string" && ["basis","target"].includes(doc.role))
    || !["demo","model"].includes(input.mode))throw new Error("업무 팩에 맞는 RunRequest JSON이 필요합니다.");
  state.pack=pack;state.draft=input;state.run=null;state.submitKey=null;state.poll++;
  renderPacks();renderInputs();renderResults();notice();
}));
await perform(async()=>{
  const [health,registry]=await Promise.all([api("/api/health"),api("/api/packs")]);
  state.packs=registry.packs;
  $("#connection").textContent=health.model_ready?"모델 연결 설정됨":"로컬 데모 준비됨";
  $("#run-mode option[value=model]").disabled=!health.model_ready;
  await choosePack(state.packs.find(pack=>pack.id==="requirements-review")?.id || state.packs[0].id);
});
