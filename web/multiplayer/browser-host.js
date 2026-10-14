// Durable host saves live in this browser, never in a player peer's state.
const BrowserTable = (() => {
  let db, worker, releaseLock, locked=false, serial=0, failed=false;
  const pending=new Map();
  const openDB=()=>db?Promise.resolve(db):new Promise((resolve,reject)=>{
    const q=indexedDB.open('void-throne-host',1);
    q.onupgradeneeded=()=>{q.result.createObjectStore('games');q.result.createObjectStore('archives');};
    q.onsuccess=()=>{db=q.result;resolve(db);};q.onerror=()=>reject(Error('Browser storage is unavailable. Allow site storage before hosting.'));
  });
  async function saved(){const d=await openDB();return new Promise((resolve,reject)=>{const q=d.transaction('games').objectStore('games').get('current');q.onsuccess=()=>resolve(q.result||null);q.onerror=()=>reject(q.error);});}
  async function persist(backup,archive=false){const d=await openDB();return new Promise((resolve,reject)=>{
    const tx=d.transaction(['games','archives'],'readwrite');const games=tx.objectStore('games');
    if(archive){const q=games.get('current');q.onsuccess=()=>{if(q.result)tx.objectStore('archives').put(q.result,q.result.room+'-'+Date.now());};}
    games.put(backup,'current');tx.oncomplete=resolve;tx.onabort=tx.onerror=()=>reject(Error('The browser could not save this game. Stop play and download a recovery backup.'));
  });}
  async function lock(){if(locked)return;
    if(!navigator.locks)throw Error('Hosting needs a browser with secure storage and Web Locks. Open the online page in a current browser.');
    await new Promise((resolve,reject)=>{
      navigator.locks.request('void-throne-facilitator',{ifAvailable:true},async lease=>{
        if(!lease){reject(Error('Another tab in this browser is hosting. Close it before resuming here.'));return;}
        locked=true;resolve();await new Promise(r=>releaseLock=r);locked=false;
      }).catch(reject);
    });
  }
  function call(action,payload={}){return new Promise((resolve,reject)=>{
    const id=++serial;
    const timer=setTimeout(()=>{pending.delete(id);failed=true;if(worker)worker.terminate();reject(Error('The game took too long to respond. Reload and resume the saved game.'));},120000);
    pending.set(id,{resolve,reject,timer});worker.postMessage({id,action,...(action==='init'?payload:{payload})});
  });}
  function stop(){if(worker)worker.terminate();worker=null;for(const p of pending.values()){clearTimeout(p.timer);p.reject(Error('The host was stopped.'));}pending.clear();if(releaseLock)releaseLock();releaseLock=null;locked=false;}
  async function start(fresh){
    if(worker&&!failed)return;
    await lock();failed=false;
    try{
      const backup=await saved();
      if(fresh&&backup&&!confirm('Archive the saved game and start a new one? You can resume it instead.'))throw Error('New game cancelled. Use Resume saved game.');
      const url=URL.createObjectURL(new Blob([HOST_WORKER],{type:'text/javascript'}));
      worker=new Worker(url,{type:'module'});URL.revokeObjectURL(url);
      worker.onmessage=({data})=>{const p=pending.get(data.id);if(!p)return;pending.delete(data.id);clearTimeout(p.timer);data.error?p.reject(Error(data.error)):p.resolve(data.result);};
      worker.onerror=()=>{failed=true;for(const p of pending.values()){clearTimeout(p.timer);p.reject(Error('The browser game engine could not load. Check your connection, then reload and resume.'));}pending.clear();};
      // Start from the durable save even for a new room so it can be archived atomically.
      await call('init',{files:HOST_FILES,backup});
      let result=await call('host');
      if(fresh&&backup)result=await call('new',{host_key:result.envelope.host_key});
      // 'new' retains the host key but its envelope does not include it.
      if(fresh&&backup){const lease=await call('host');result.envelope.host_key=lease.envelope.host_key;}
      await persist(result.backup,fresh&&!!backup);
      return result.envelope;
    }catch(e){stop();throw e;}
  }
  let recovery=null;
  async function request(action,payload){
    if(failed)throw Error('Autosave stopped. Download a recovery backup, then reload and resume.');
    const result=await call(action,payload);
    if(result.backup){recovery=result.backup;try{await persist(result.backup,action==='new');}catch(e){failed=true;window.dispatchEvent(new CustomEvent('host-save-failed',{detail:e.message}));throw e;}}
    return result;
  }
  function download(name,content,type){const u=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
  async function backup(){const b=recovery||await saved();if(!b)throw Error('No saved game yet.');download('void-throne-host-backup.json',JSON.stringify(b,null,2),'application/json');}
  async function archives(){const d=await openDB();const rows=await new Promise((resolve,reject)=>{const q=d.transaction('archives').objectStore('archives').getAll();q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error);});if(!rows.length)throw Error('No earlier games have been archived in this browser.');download('void-throne-archived-backups.json',JSON.stringify(rows,null,2),'application/json');}
  return {start,request,saved,stop,download,backup,archives};
})();
