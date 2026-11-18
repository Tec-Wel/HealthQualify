/* Actual browser checks and screenshot capture for static site and local application.
 * Runs only against loopback servers with synthetic fixtures.
 */
import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import { spawn } from 'node:child_process';
import { mkdtempSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { setTimeout as sleep } from 'node:timers/promises';

const root=process.cwd();
const output=join(root,'website','screenshots-preview');
mkdirSync(output,{recursive:true});
const site=process.env.SITE_URL||'http://127.0.0.1:8765/';
const local='http://127.0.0.1:8899/';
const errors=[];
function assert(cond,msg){if(!cond)throw Error(msg);}
async function ready(url,timeoutMs=20000){
  const start=Date.now();
  while(Date.now()-start<timeoutMs){
    try { const res=await fetch(url); if(res.ok)return; } catch {}
    await sleep(350);
  }
  throw Error('Server not reachable: '+url);
}
const browser=await chromium.launch({headless:true});
let application;
try{
  for(const viewport of [{width:390,height:844,name:'mobile'},{width:768,height:1024,name:'tablet'},{width:1440,height:900,name:'desktop'}]){
    const context=await browser.newContext({viewport:{width:viewport.width,height:viewport.height},deviceScaleFactor:1});
    const page=await context.newPage();
    page.on('pageerror',e=>errors.push(viewport.name+': '+e.message));
    await page.goto(site,{waitUntil:'networkidle'});
    assert(await page.locator('h1').count()===1,'Homepage needs exactly one H1');
    assert(await page.locator('a[href*="demo/"]').count()>0,'Demo link missing');
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2);
    assert(!overflow,'Horizontal layout overflow at '+viewport.name);
    const audit=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
    const high=audit.violations.filter(v=>v.impact==='serious'||v.impact==='critical');
    if (high.length) {
      for (const violation of high) {
        console.error('AXE ',viewport.name,violation.id,violation.nodes.slice(0,40).map(n=>({target:n.target,summary:n.failureSummary?.slice(0,190),html:n.html?.slice(0,160)})));
      }
    }
    assert(high.length===0,'Accessibility issues at '+viewport.name+': '+high.map(v=>v.id+'('+v.nodes.length+')').join(', '));
    await page.screenshot({path:join(output,'website-'+viewport.name+'.png'),fullPage:true});
    await page.goto(site+'demo/',{waitUntil:'networkidle'});
    await page.locator('#tour-next').click();
    assert((await page.locator('#tour-count').innerText()).includes('02'),'Tour did not advance');
    await page.locator('[data-tour-step="3"]').click();
    assert((await page.locator('#tour-state').innerText()).includes('NOT APPROVED'),'Tour final state missing');
    await page.screenshot({path:join(output,'tour-'+viewport.name+'.png'),fullPage:true});
    await page.goto(site+'architecture/',{waitUntil:'networkidle'});
    await page.locator('[data-component="qwen"]').click();
    assert((await page.locator('#arch-title').innerText()).includes('Ollama'),'Architecture explorer did not update');
    await page.screenshot({path:join(output,'architecture-'+viewport.name+'.png'),fullPage:true});
    await page.close();
    await context.close();
  }

  const scratch=mkdtempSync(join(tmpdir(),'healthqualify-synthetic-browser-'));
  const db=join(scratch,'developer-alpha.db');
  application=spawn('python',['-m','healthqualify.local_edition_v08','--no-browser','--db',db,'--port','8899'],
    {cwd:root,stdio:['ignore','pipe','pipe'],env:{...process.env,PYTHONUNBUFFERED:'1'}});
  let stderr='';
  application.stderr.on('data',data=>{stderr+=data.toString()});
  await ready(local+'api/health');
  const page=await browser.newPage({viewport:{width:1365,height:850}});
  page.on('pageerror',e=>errors.push('local: '+e.message));
  await page.goto(local,{waitUntil:'networkidle'});
  assert((await page.locator('#authTitle').innerText()).includes('Set up'),'Expected first run admin setup');
  await page.locator('#username').fill('synthetic_admin');
  await page.locator('#password').fill('Synthetic-Only-Admin-Passphrase-2026');
  await page.locator('#authButton').click();
  await page.locator('#overview.active').waitFor();
  await page.screenshot({path:join(output,'actual-local-overview.png'),fullPage:true});
  await page.locator('#heroStart').click();
  await page.locator('#runDemo').click();
  await page.locator('#qualification.active').waitFor({timeout:30000});
  assert((await page.locator('#runsTable tr').count())>0,'No qualification run visible');
  await page.screenshot({path:join(output,'actual-local-qualification.png'),fullPage:true});
  await page.locator('[data-section="agents"]').click();
  await page.screenshot({path:join(output,'actual-local-agents.png'),fullPage:true});
  await page.close();
  assert(errors.length===0,'Browser console errors: '+errors.join(' | '));
  console.log('Browser QA passed. Three screen sizes, tour, architecture and synthetic local app captures.');
}finally{
  if(application&&!application.killed){application.kill('SIGTERM');await sleep(300);}
  await browser.close();
}
