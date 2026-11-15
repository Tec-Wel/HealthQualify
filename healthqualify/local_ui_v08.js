"use strict";
let csrf="",user=null,needsSetup=false,lastObservation=null,overview={systems:[],runs:[],deviations:[],protocols:[]};
const $=id=>document.getElementById(id);
function showMessage(message, bad=false){$("notification").textContent=message||"";$("notification").style.color=bad?"#9b2d2d":"#087f75";}
function safeShort(s,n=18){return String(s||"").slice(0,n);}
async function api(path,body,method){
 const headers={"X-HQ-Request":"1"};
 if(csrf && body!==undefined)headers["X-HQ-CSRF"]=csrf;
 if(body!==undefined)headers["Content-Type"]="application/json";
 const response=await fetch(path,{method:method||(body===undefined?"GET":"POST"),
  headers,credentials:"same-origin",cache:"no-store",
  body:body===undefined?undefined:JSON.stringify(body)});
 const data=await response.json();
 if(!response.ok)throw new Error(data.error||"Request failed");
 return data;
}
function makeCell(text){let td=document.createElement("td");td.textContent=String(text??"—");return td;}
function addRow(table,values){let row=document.createElement("tr");for(const value of values)row.append(makeCell(value));$(table).append(row);}
function clear(id){$(id).replaceChildren();}
function navigate(section){
 document.querySelectorAll(".content").forEach(e=>e.classList.toggle("active",e.id===section));
 document.querySelectorAll("aside nav button").forEach(b=>{
  if(b.dataset.section===section)b.setAttribute("aria-current","page");else b.removeAttribute("aria-current");
 });
 const names={overview:"Workspace overview",journey:"Guided qualification",
  qualification:"Qualification & evidence",agents:"Five qualification agents",
  reviews:"QA review queue",localai:"Local Qwen setup"};
 $("pageTitle").textContent=names[section]||"HealthQualify";
 if(section==="reviews")loadReviews();
 if(section==="localai")loadModel();
}
async function init(){
 const setup=await api("/api/setup");needsSetup=setup.needs_setup;
 try{
  const session=await api("/api/session");csrf=session.csrf;user=session.user;enterApp();
 }catch{
  $("auth").hidden=false;$("app").style.display="none";
  $("authTitle").textContent=needsSetup?"Set up your private workspace":"Welcome back";
  $("authDescription").textContent=needsSetup?
   "Create a local administrator account. No cloud account or API tokens required.":
   "Sign in with your local HealthQualify account.";
  $("authButton").textContent=needsSetup?"Create local admin":"Sign in";
  $("password").autocomplete=needsSetup?"new-password":"current-password";
 }
}
async function enterApp(){
 $("auth").hidden=true;$("app").style.display="block";
 $("userLabel").textContent=user.username+" · "+user.role;
 await refresh();
}
async function refresh(){
 overview=await api("/api/overview");
 $("numSystems").textContent=overview.systems.length;
 $("numRuns").textContent=overview.runs.length;
 $("numDeviations").textContent=overview.deviations.filter(d=>d.status!=="RESOLVED").length;
 for(const id of ["runsTable","deviationsTable","systemSelect","traceability"])clear(id);
 for(const r of overview.runs){
  const s=r.summary;
  addRow("runsTable",[safeShort(r.id,12),s.PASS||0,s.FAIL||0,s.ERROR||0,s.NOT_RUN||0,"NO"]);
 }
 for(const d of overview.deviations)
  addRow("deviationsTable",[d.test_id,d.kind,d.status,safeShort(d.run_id,14)]);
 const newest=overview.runs[0];
 if(newest){
  const table=document.createElement("table");
  const header=document.createElement("thead"),headRow=document.createElement("tr");
  for(const label of ["Requirement","Test IDs","Outcome","Evidence refs"]){
   const cell=document.createElement("th");cell.textContent=label;headRow.append(cell);
  }
  header.append(headRow);table.append(header);
  const body=document.createElement("tbody");
  for(const t of newest.traceability){
   const row=document.createElement("tr");
   for(const val of [t.requirement_id,t.test_ids.join(", "),t.status,
                     (t.evidence_refs||[]).join(", ")])row.append(makeCell(val));
   body.append(row);
  }
  table.append(body);$("traceability").append(table);
 }else $("traceability").textContent="No runs yet. Start the synthetic example.";
 for(const s of overview.systems){
  const opt=document.createElement("option");opt.value=s.id;opt.textContent=s.name+" · "+safeShort(s.id,8);
  $("systemSelect").append(opt);
 }
}
const agentNames=[
 ["release-impact","Release Impact","Maps changed components to relevant qualification tests."],
 ["gap-hunter","Gap Hunter","Identifies missing links, execution gaps and uncertain evidence."],
 ["failure-investigation","Failure Investigator","Flags nonpassing outcomes and repeated failures."],
 ["qa-readiness","QA Readiness","Prepares advisory findings for human review."],
 ["dependency-investigator","Dependency Investigator","Flags unknown or mapped system dependencies."]
];
for(const [name,title,description] of agentNames){
 const card=document.createElement("div");card.className="card agent-card";
 const h=document.createElement("h3");h.textContent=title;
 const p=document.createElement("p");p.textContent=description;
 const button=document.createElement("button");button.className="secondary";button.textContent="Investigate";
 button.onclick=async()=>{
  const system_id=$("systemSelect").value;
  if(!system_id)return showMessage("Run the synthetic qualification first.",true);
  button.disabled=true;showMessage("Running "+title+"...");
  try{
   const report=await api("/api/agent",{system_id,agent:name});
   $("agentResult").textContent=JSON.stringify(report.report,null,2);
   lastObservation=report.id;$("explainAgent").disabled=false;
   $("explanationResult").hidden=true;
   showMessage(title+" draft investigation generated. Not qualification approval.");
  }catch(e){showMessage(e.message,true);}finally{button.disabled=false;}
 };
 card.append(h,p,button);$("agentCards").append(card);
}
async function loadReviews(){
 try{
  const data=await api("/api/reviews");
  clear("reviewsTable");
  for(const record of data.reviews){
   const row=document.createElement("tr");
   for(const val of [record.agent,record.actor,record.disposition,safeShort(record.id,12)])
    row.append(makeCell(val));
   const cell=document.createElement("td");
   if(record.disposition==="PENDING" && ["qa","admin"].includes(user.role)){
    const button=document.createElement("button");button.className="secondary";button.textContent="Review";
    button.onclick=async()=>{
     const rationale=window.prompt("Review rationale (minimum 8 characters). No release approval:");
     if(!rationale)return;
     const decision=window.prompt("Decision: ACKNOWLEDGED, NEEDS_INVESTIGATION, or DISMISSED","NEEDS_INVESTIGATION");
     if(!decision)return;
     try{
      await api("/api/review",{observation_id:record.id,decision,rationale});
      showMessage("Draft review recorded; no qualification approval.");await loadReviews();
     }catch(e){showMessage(e.message,true);}
    };
    cell.append(button);
   }else cell.textContent="—";
   row.append(cell);$("reviewsTable").append(row);
  }
 }catch(e){showMessage(e.message,true);}
}
async function loadModel(){
 try{
  const m=await api("/api/model");
  $("modelStatus").textContent=m.enabled?
   "Optional Qwen check enabled. Model is not required.":
   "Optional Qwen disabled. All deterministic qualification features still work.";
 }catch(e){showMessage(e.message,true);}
}
$("authForm").addEventListener("submit",async event=>{
 event.preventDefault();$("authError").textContent="";
 const username=$("username").value,password=$("password").value;
 try{
  if(needsSetup){await api("/api/bootstrap",{username,password});needsSetup=false;}
  const session=await api("/api/login",{username,password});
  csrf=session.csrf;user=session.user;$("password").value="";await enterApp();
 }catch(e){$("authError").textContent="Sign-in or setup failed. Check username and password.";}
});
$("logout").onclick=async()=>{
 try{await api("/api/logout",{});}catch{}
 csrf="";user=null;location.reload();
};
$("heroStart").onclick=()=>navigate("journey");
document.querySelectorAll("aside nav button").forEach(b=>b.onclick=()=>navigate(b.dataset.section));
$("runDemo").onclick=async()=>{
 const button=$("runDemo");button.disabled=true;showMessage("Executing synthetic criteria...");
 try{
  const data=await api("/api/demo",{});
  $("demoResult").textContent="Draft technical run completed: "+data.run.summary.PASS+
   " PASS, "+data.run.summary.FAIL+" FAIL. No approval granted.";
  await refresh();showMessage("Synthetic run recorded with evidence refs. View Qualification & evidence.");
  navigate("qualification");
 }catch(e){showMessage(e.message,true);}finally{button.disabled=false;}
};
$("explainAgent").onclick=async()=>{
 if(!lastObservation)return;
 const button=$("explainAgent");button.disabled=true;
 try{
  const result=await api("/api/model-explain",{observation_id:lastObservation});
  $("explanationResult").hidden=false;
  $("explanationResult").textContent=result.text+"\\n\\nUnverified model draft. Human review required.";
  showMessage("Local Qwen explanation generated; original findings unchanged.");
 }catch(e){showMessage("Optional model unavailable: "+e.message,true);}
 finally{button.disabled=false;}
};
$("refreshReviews").onclick=loadReviews;
$("checkModel").onclick=async()=>{
 try{const m=await api("/api/model-check",{});
  $("modelStatus").textContent=m.available?"Local Qwen model detected. Inference has not been validated.":
   "Local model unavailable: "+(m.reason||"not installed")+" — core operation unaffected.";
 }catch(e){showMessage(e.message,true);}
};
init().catch(()=>{$("authError").textContent="Unable to initialize local workspace.";});
