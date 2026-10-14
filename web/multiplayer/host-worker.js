// Only the facilitator starts this worker. Player messages use the fixed
// Multiplayer.receive entry point; no peer can submit Python or host actions.
let engine;
let chain = Promise.resolve();
self.onmessage = ({data}) => {
  chain = chain.then(async () => {
    try {
      if (data.action === 'init') {
        const {loadPyodide} = await import('https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs');
        engine = await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/'});
        for (const [path, content] of Object.entries(data.files)) {
          const full = '/game/' + path;
          engine.FS.mkdirTree(full.slice(0, full.lastIndexOf('/')));
          engine.FS.writeFile(full, content);
        }
        engine.globals.set('saved_json', JSON.stringify(data.backup));
        engine.runPython("import sys, json\nsys.path.insert(0, '/game/src')\nfrom void_throne.browser_host import BrowserHost\nbrowser_host = BrowserHost(json.loads(saved_json))");
        self.postMessage({id:data.id, result:{ready:true}});
      } else {
        if (!engine) throw Error('The game has not loaded yet.');
        engine.globals.set('request_json', JSON.stringify({action:data.action, payload:data.payload}));
        const result = engine.runPython("request = json.loads(request_json)\njson.dumps(browser_host.request(request['action'], request['payload']), ensure_ascii=False)");
        self.postMessage({id:data.id, result:JSON.parse(result)});
      }
    } catch (e) {
      self.postMessage({id:data.id, error:e.message || String(e)});
    }
  });
};
