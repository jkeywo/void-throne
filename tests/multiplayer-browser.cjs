const {chromium}=require('C:/Users/jkeyw/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {PeerServer}=require(process.env.PEER_SERVER_MODULE||'peer');
const {spawn}=require('child_process');const fs=require('fs');const path=require('path');const assert=require('assert');
const root=path.resolve(__dirname,'..'),base='http://127.0.0.1:8880';
const actions=JSON.parse(fs.readFileSync(root+'/design/experiments/replay-config.json','utf8')).plugin_config.actions;
const options=JSON.stringify({host:'127.0.0.1',port:9001,path:'/',secure:false,config:{iceServers:[]}});
const save=path.resolve('.playtrace/multiplayer-test-session-'+Date.now()+'.json');
let browser,server,signal;
async function waitServer(){for(let i=0;i<40;i++){try{const r=await fetch(base+'/multiplayer.html');if(r.ok)return;}catch{}await new Promise(r=>setTimeout(r,150));}throw Error('Test server did not start');}
async function fill(page,form,data){for(const[k,v]of Object.entries(data)){const el=page.locator(form+' [name="'+k+'"]');if(!await el.count())continue;const tag=await el.evaluate(e=>e.tagName);if(typeof v==='boolean')await el.setChecked(v);else if(tag==='SELECT')await el.selectOption(v);else await el.fill(v);}}
function row(a,r){const s=a.stage,o={note:a.notes?.[r]||''};if(s==='draft')Object.assign(o,a.proposals[r]);if(s==='vision')o.choice=a.choice;if(s==='commit'){if(r==='A')Object.assign(o,{reserve:a.reserve,disclose:a.disclose});else Object.assign(o,a.assignments[r],{sign:a.signatures[r]});}if(s==='council'){for(const k of ['navigation','security'])if(r in a[k])o[k]=a[k][r];if(r==='A')o.warrant=a.warrant;}if(s==='trial-vote'){Object.assign(o,a.votes[r]);o.pledge=!!a.votes[r][r.startsWith('G')?'Guild':'Janissariat'];}if(s==='ceremony-vote')o.approve=a.approvals[r];return o;}
(async()=>{
 signal=PeerServer({port:9001,path:'/',host:'127.0.0.1'});
 server=spawn('C:/Coding/playtrace/.venv/Scripts/python.exe',['launch.py','--no-open','--port','8880','--mp-save',save],{cwd:root,windowsHide:true,stdio:['ignore','pipe','pipe']});server.stderr.on('data',b=>process.stderr.write(b));await waitServer();
 browser=await chromium.launch({headless:true,executablePath:'C:/Users/jkeyw/AppData/Local/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-win64/chrome-headless-shell.exe'});
 const errors=[];const host=await(await browser.newContext({viewport:{width:1440,height:1000}})).newPage();host.on('pageerror',e=>errors.push('host: '+e));await host.goto(base+'/multiplayer.html');await host.locator('.network summary').click();await host.locator('#peer-options').fill(options);await host.locator('#host-start').click();await host.waitForFunction(()=>document.querySelector('#connection-status').textContent.includes('Room open'));
 const room=await host.locator('#room-code').textContent();const players={};
 for(const r of ['GN','GS','JN','JS','A']){const p=await(await browser.newContext({viewport:{width:1200,height:950}})).newPage();p.on('pageerror',e=>errors.push(r+': '+e));await p.goto('file:///'+root+'/web/multiplayer-player.html');await p.locator('.network summary').click();await p.locator('#peer-options').fill(options);await fill(p,'#join-form',{room,name:'Human '+r,role:r});await p.locator('#join-form button').first().click();await host.waitForFunction(r=>Object.values(current.pending).some(x=>x.name==='Human '+r),r);const cid=await host.evaluate(r=>Object.entries(current.pending).find(([,x])=>x.name==='Human '+r)[0],r);await host.locator('[data-admit="'+cid+'"]').click();await p.waitForFunction(()=>current?.role);players[r]=p;}
 await players.GN.locator('[data-channel="guild"]').click();await players.GN.locator('#chat-text').fill('PRIVATE GUILD TEST');await players.GN.locator('#chat-form button').click();await players.GS.waitForFunction(()=>current.chat.some(c=>c.text==='PRIVATE GUILD TEST'));
 assert(!(await players.JN.evaluate(()=>JSON.stringify(current))).includes('PRIVATE GUILD TEST'));
 // An edit survives a teammate’s submission and incoming chat updates.
 await players.GN.locator('#sheet [name=note]').fill('Unsaved typing survives');await players.GS.locator('#chat-text').fill('Public conversation');await players.GS.locator('#chat-form button').click();await host.waitForFunction(()=>current.chat.length===2);assert.equal(await players.GN.locator('#sheet [name=note]').inputValue(),'Unsaved typing survives');
 for(let i=0;i<actions.length;i++){
   const a=actions[i],old=await host.evaluate(()=>current.epoch);
   if(['trial-proposal','ceremony-proposal'].includes(a.stage)){
     const f={...(a.articles||a.package),plan:a.plan||''};for(const q of a.pledges||[]){f[q.owner+'-asset']=q.asset;f[q.owner+'-assignment']=q.assignment;f[q.owner+'-domain']=Object.keys(a.articles).find(d=>a.articles[d]===q.article);}await fill(host,'#advance',f);
   }else{
     const required=await host.evaluate(()=>current.required);
     for(const r of required){await fill(players[r],'#sheet',row(a,r));await players[r].locator('#sheet button[type=submit]').click();}
     await host.waitForFunction(()=>current.required.every(r=>current.sheets[r]));
   }
   await host.locator('#advance button').click();await host.waitForFunction(old=>current.epoch!==old,old);
   const epoch=await host.evaluate(()=>current.epoch);for(const [seat,p] of Object.entries(players)){try{await p.waitForFunction(e=>current.epoch===e,epoch);}catch(e){console.log('Waiting for',seat,epoch,'errors',errors);for(const [r,q]of Object.entries(players))console.log(r,await q.evaluate(()=>({epoch:current?.epoch,status:document.querySelector('#connection-status').textContent,error:document.querySelector('#error').textContent})));throw e;}}
   if(i===1){
     assert(await players.A.locator('.vision').count());assert.equal(await players.GN.locator('.vision').count(),0);
     assert(!(await players.GN.evaluate(()=>JSON.stringify(current))).includes('total Raid cost Stability'));
     await players.A.locator('.vision summary').click();await players.A.screenshot({path:'.playtrace/ascendant.png'});
     // Refresh on a portable file page: rejoin with the saved seat token, no new admission.
     const p=players.GN;await p.reload();await p.locator('.network summary').click();await p.locator('#peer-options').fill(options);await fill(p,'#join-form',{room,name:'Human GN',role:'GN'});await p.locator('#join-form button').first().click();await p.waitForFunction(e=>current?.epoch===e,epoch);assert.equal(await p.evaluate(()=>current.role),'GN');
   }
   if(i===3){await host.screenshot({path:'.playtrace/host-result.png'});await players.GN.screenshot({path:'.playtrace/player-result.png'});}
 }
 const expected=JSON.parse(fs.readFileSync(root+'/tests/fixtures/expected-ending.json','utf8'));
 assert.deepStrictEqual(await host.evaluate(()=>current.game.state),expected.physical);assert(await host.evaluate(()=>current.game.settlement.ratified));
 await players.GN.setViewportSize({width:390,height:844});assert(!await players.GN.evaluate(()=>document.documentElement.scrollWidth>innerWidth));await players.GN.screenshot({path:'.playtrace/mobile.png'});
 const report=await(await fetch(base+'/api/mp/report')).text();assert(report.includes('PRIVATE GUILD TEST'));assert(report.includes('Human-seat multiplayer record'));fs.writeFileSync('.playtrace/qa-report.html',report);
 assert.deepStrictEqual(errors,[]);console.log('PASS: six isolated browsers, real PeerJS/WebRTC, private faction chat and vision, reconnect, all 13 sheets, exact ending, report and narrow screen.');
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();if(server)server.kill();if(signal)signal.close?.();setTimeout(()=>process.exit(process.exitCode||0),200);});
