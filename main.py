import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response

app = FastAPI(title="Kalshi Paper Scalper")
from scanner_api import router as scanner_router
app.include_router(scanner_router)
KALSHI = "https://api.elections.kalshi.com/trade-api/v2"

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#070b12"><link rel="manifest" href="/manifest.webmanifest"><link rel="icon" href="/app-icon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/app-icon.svg">
<title>Kalshi Paper Scalper</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{color-scheme:dark;--bg:#070b12;--panel:#0e1724;--panel2:#111e2e;--line:#223249;--text:#edf4ff;--muted:#8193ad;--green:#49e2ac;--red:#ff7185;--blue:#6baeff;--gold:#f5c66a}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(ellipse at 12% -10%,rgba(39,111,178,.2),transparent 42%),radial-gradient(ellipse at 90% 0%,rgba(45,197,150,.08),transparent 32%),var(--bg);color:var(--text);font:14px 'Manrope',system-ui,Arial;min-height:100vh}
header{padding:22px max(4vw,18px);border-bottom:1px solid rgba(99,139,187,.18);display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;background:rgba(7,11,18,.82);backdrop-filter:blur(18px);position:sticky;top:0;z-index:10}
h1{font-size:22px;letter-spacing:-.8px;margin:0;font-weight:800}h1:first-letter{color:var(--green)}main{max-width:1500px;margin:auto;padding:26px max(4vw,18px) 48px}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:18px}
.panel,.metric{background:linear-gradient(145deg,rgba(17,30,46,.97),rgba(12,21,33,.98));border:1px solid var(--line);border-radius:17px;padding:19px;margin-bottom:16px;box-shadow:0 10px 32px rgba(0,0,0,.12)}
.metric{position:relative;overflow:hidden;margin:0;min-height:112px}.metric:after{content:"";position:absolute;width:100px;height:100px;border-radius:50%;right:-40px;top:-42px;background:rgba(73,226,172,.06);filter:blur(1px)}.metric label{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:1.1px;font-weight:700}.metric strong{display:block;font:500 27px 'DM Mono',monospace;margin-top:13px;letter-spacing:-1px}
.row,.split{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.split{justify-content:space-between}section.panel>b,.panel .split>b{font-size:14px;font-weight:800;letter-spacing:-.2px}
button,input,select{font:inherit;color:var(--text);background:#101d2d;border:1px solid #2a3d56;border-radius:10px;padding:10px 12px;outline:none;transition:border-color .18s,transform .18s,background .18s}input:focus,select:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(107,174,255,.1)}button{cursor:pointer;font-weight:700;font-size:12px;letter-spacing:.1px}button:hover{border-color:#6baeff;transform:translateY(-1px)}button:disabled{opacity:.35;cursor:not-allowed;transform:none}button.primary{background:linear-gradient(135deg,#2f83e8,#2764bd);border-color:#5799ef;box-shadow:0 5px 18px rgba(47,131,232,.18)}button.danger{background:#311b28;border-color:#6b3548;color:#ff9cad}
.status{font:500 10px 'DM Mono',monospace;letter-spacing:.45px;text-transform:uppercase;padding:7px 10px;border-radius:7px;background:#202d3f;color:#a6b5c9;border:1px solid #2b3c52}.good{color:var(--green);background:rgba(18,78,60,.3);border-color:rgba(73,226,172,.24)}.bad{color:var(--red);background:rgba(90,27,43,.3);border-color:rgba(255,113,133,.28)}
.tablewrap{overflow:auto;border-radius:10px;margin-top:14px}table{border-collapse:collapse;width:100%;min-width:700px}th,td{text-align:left;padding:13px 12px;border-bottom:1px solid rgba(60,82,109,.35);font-size:12px;white-space:nowrap}th{color:#91a4bd;text-transform:uppercase;font-size:10px;letter-spacing:.8px;font-weight:800;background:rgba(4,10,17,.25)}tbody tr{transition:background .15s}tbody tr:hover{background:rgba(95,143,194,.055)}td:first-child{font-weight:700;max-width:300px;overflow:hidden;text-overflow:ellipsis}td button{padding:7px 9px;font-size:10px}
.note{font-size:11px;color:var(--muted);line-height:1.65;margin-bottom:0}.good,.pos{color:var(--green)}.bad,.neg{color:var(--red)}.empty{text-align:center;color:var(--muted);padding:30px 18px!important;font-size:12px!important}
section.panel:nth-of-type(2){border-color:#263b53}#chart{margin-top:12px;border-radius:12px;background:linear-gradient(180deg,rgba(73,226,172,.035),transparent);overflow:visible}
@media(max-width:900px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.metric strong{font-size:23px}}
@media(max-width:600px){header{padding:16px;position:static}h1{font-size:19px}main{padding:18px 12px 32px}.panel{padding:14px;border-radius:14px}.grid{gap:9px}.metric{padding:13px;min-height:98px}.metric strong{font-size:19px;margin-top:10px}.metric label{font-size:9px;letter-spacing:.6px}.row{gap:7px}.split{align-items:flex-start}.status{font-size:9px}button,input,select{padding:9px;font-size:11px}}
</style></head><body>
<header><div><h1>◈ Kalshi Paper Scalper</h1><div class="note">Public Kalshi market data · simulated trades only</div></div><div class="row"><span id="status" class="status">Not connected</span><button class="primary" id="load">Load markets</button></div></header>
<main>
<div class="grid"><div class="metric"><label>Paper balance</label><strong id="balance">$10,000.00</strong></div><div class="metric"><label>Realized P&amp;L</label><strong id="pnl">$0.00</strong></div><div class="metric"><label>Open positions</label><strong id="open">0</strong></div><div class="metric"><label>Closed trades</label><strong id="closed">0</strong></div></div>
<section class="panel"><div class="split"><b>Paper account controls</b><span class="status">PAPER ONLY · LIVE ORDERS DISABLED</span></div><div class="row" style="margin-top:12px"><label>Reset balance $ <input id="resetAmount" type="number" min=".01" step="any" value="10000" style="width:140px"></label><button class="danger" id="reset">Reset account</button><label>Contracts <input id="qty" type="number" min="1" value="1" style="width:80px"></label><label>Max position $ <input id="maxPos" type="number" min="1" value="250" style="width:110px"></label></div><p class="note">Reset accepts any positive amount and clears positions, history and P&amp;L. It does not change your Kalshi account.</section>
<section class="panel"><div class="split"><b>Market scanner</b><div class="row"><select id="filter"><option value="all">All markets</option><option value="sports">Sports</option><option value="economics">Economics / finance</option><option value="weather">Weather</option></select><span id="updated" class="note">Waiting for data</span><span id="scanStatus" class="status good">Auto-refresh every 15 seconds</span><button id="scanToggle">Pause scanning</button></div></div><div class="tablewrap"><table><thead><tr><th>Market</th><th>Ticker</th><th>YES bid / ask</th><th>NO bid / ask*</th><th>Spread</th><th>Paper order</th></tr></thead><tbody id="markets"><tr><td colspan="6" class="empty">Tap Load markets to fetch Kalshi prices.</td></tr></tbody></table></div><p class="note">*NO quotes are derived from YES prices where applicable. Quotes may be missing or stale. Paper fills are simplified and do not model queue priority or all fees.</p></section>
<section class="panel"><div class="split"><b>Opportunity signals (paper strategy)</b><span id="signalSummary" class="status">Building price baseline…</span></div><div class="tablewrap"><table><thead><tr><th>Market</th><th>Direction</th><th>Move since prior scan</th><th>Current quote</th><th>Signal</th></tr></thead><tbody id="signals"><tr><td colspan="5" class="empty">Waiting for multiple scans to establish a baseline.</td></tr></tbody></table></div><p class="note">Starter rule: short-term price momentum at least 2¢ with YES bid/ask spread no more than 5¢. This is a heuristic—not a fair-value model. Fees, liquidity, and fill quality can make it unprofitable. Auto entries are simulated paper trades.</p></section><section class="panel"><b>Open paper positions</b><div class="tablewrap"><table><thead><tr><th>Market</th><th>Side</th><th>Entry</th><th>Qty</th><th>Cost</th><th>Action</th></tr></thead><tbody id="positions"><tr><td colspan="6" class="empty">No open positions.</td></tr></tbody></table></div></section>
<section class="panel"><b>Closed trades</b><div class="tablewrap"><table><thead><tr><th>Market</th><th>Side</th><th>Entry → Exit</th><th>Qty</th><th>Net P&amp;L</th><th>Closed</th></tr></thead><tbody id="history"><tr><td colspan="6" class="empty">No closed trades.</td></tr></tbody></table></div></section>
<section class="panel"><b>Equity history</b><svg id="chart" viewBox="0 0 700 150" style="width:100%;height:150px"></svg><p class="note">This is a paper-trading prototype. No guaranteed profits. Live trading is not implemented.</p></section>
</main>
<script>
const STORAGE_KEY='kalshiPaperScalperStateV1';
let markets=[],positions=[],history=[],balance=10000,pnl=0,equity=[10000],previousQuotes={},seenSignals=new Set(),signals=[];
function saveState(){try{localStorage.setItem(STORAGE_KEY,JSON.stringify({balance,pnl,positions,history,equity,previousQuotes,seenSignals:[...seenSignals]}))}catch(e){console.warn('Could not save paper account state',e)}}
function restoreState(){try{const raw=localStorage.getItem(STORAGE_KEY);if(!raw)return;const s=JSON.parse(raw);if(!s||typeof s!=='object')return;if(Number.isFinite(s.balance)&&s.balance>=0)balance=s.balance;if(Number.isFinite(s.pnl))pnl=s.pnl;if(Array.isArray(s.positions))positions=s.positions;if(Array.isArray(s.history))history=s.history;if(Array.isArray(s.equity)&&s.equity.length)equity=s.equity;if(s.previousQuotes&&typeof s.previousQuotes==='object')previousQuotes=s.previousQuotes;if(Array.isArray(s.seenSignals))seenSignals=new Set(s.seenSignals)}catch(e){console.warn('Could not restore paper account state',e)}}
const $=x=>document.getElementById(x), money=n=>'$'+Number(n||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}), cents=n=>n==null?'—':Number(n).toFixed(1)+'¢';
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function quote(m,k){let v=m[k];if(v==null&&m[k+'_dollars']!=null)v=Number(m[k+'_dollars'])*100;return v==null||!Number.isFinite(Number(v))?null:Number(v)}
function normalize(m){return {...m,b:quote(m,'yes_bid'),a:quote(m,'yes_ask')}}
function cat(m){let s=((m.title||'')+' '+(m.ticker||'')).toLowerCase();if(/weather|rain|snow|temperature/.test(s))return'weather';if(/cpi|fed|interest|gdp|stock|econom|finance|inflation/.test(s))return'economics';if(/nba|nfl|mlb|nhl|soccer|football|tennis|sport/.test(s))return'sports';return'other'}
function renderMarkets(){let f=$('filter').value,ls=markets.filter(m=>f==='all'||cat(m)===f);$('markets').innerHTML=ls.length?ls.map(m=>{let sp=m.a!=null&&m.b!=null?m.a-m.b:null;return '<tr><td>'+esc(m.title||m.ticker)+'</td><td>'+esc(m.ticker)+'</td><td>'+cents(m.b)+' / '+cents(m.a)+'</td><td>'+cents(m.a==null?null:100-m.a)+' / '+cents(m.b==null?null:100-m.b)+'</td><td>'+cents(sp)+'</td><td><button '+(m.a==null?'disabled':'')+' onclick="trade(\''+encodeURIComponent(m.ticker)+'\',\'yes\')">Buy YES</button> <button '+(m.b==null?'disabled':'')+' onclick="trade(\''+encodeURIComponent(m.ticker)+'\',\'no\')">Buy NO</button></td></tr>'}).join(''):'<tr><td colspan="6" class="empty">No matching markets.</td></tr>'}
async function load(){ $('load').disabled=true;$('status').textContent='Fetching…';$('status').className='status';try{let r=await fetch('/api/markets?status=open&limit=1000');let d=await r.json();if(!r.ok)throw Error(d.detail||('HTTP '+r.status));if(!Array.isArray(d.markets))throw Error('Unexpected API response');markets=d.markets.map(normalize);evaluateSignals();renderMarkets();$('updated').textContent='Updated '+new Date().toLocaleTimeString();$('status').textContent='Market data loaded';$('status').className='status good'}catch(e){$('status').textContent='Market data error';$('status').className='status bad';$('markets').innerHTML='<tr><td colspan="6" class="empty">'+esc(e.message)+'</td></tr>'}finally{$('load').disabled=false}}
function evaluateSignals(){
 const found=[];
 for(const m of markets){
  if(m.b==null||m.a==null||m.a<m.b)continue;
  const mid=(m.a+m.b)/2,old=previousQuotes[m.ticker],move=old==null?null:mid-old;
  previousQuotes[m.ticker]=mid;
  if(move===null||Math.abs(move)<2||(m.a-m.b)>5)continue;
  const side=move>0?'yes':'no',price=side==='yes'?m.a:100-m.b;
  found.push({m,move,side,price});
  if(!seenSignals.has(m.ticker+':'+side)&&!positions.some(p=>p.ticker===m.ticker)){
   seenSignals.add(m.ticker+':'+side);
   const q=Math.max(1,Math.floor(Number($('qty').value)||1)),cost=price/100*q,max=Number($('maxPos').value)||250;
   if(cost>0&&cost<=max&&cost<=balance){balance-=cost;positions.push({id:Date.now()+Math.random(),ticker:m.ticker,title:m.title||m.ticker,side,entry:price,qty:q,cost,auto:true});render();saveState();}
  }
 }
 signals=found.sort((a,b)=>Math.abs(b.move)-Math.abs(a.move)).slice(0,50);
 $('signalSummary').textContent=found.length+' qualifying signal(s) this scan';
 $('signals').innerHTML=signals.length?signals.map(s=>'<tr><td>'+esc(s.m.title||s.m.ticker)+'</td><td>'+s.side.toUpperCase()+'</td><td class="'+(s.move>0?'pos':'neg')+'">'+(s.move>0?'+':'')+s.move.toFixed(1)+'¢</td><td>'+cents(s.price)+'</td><td>Momentum · spread '+cents(s.m.a-s.m.b)+'</td></tr>').join(''):'<tr><td colspan="5" class="empty">No qualifying momentum signals on this scan.</td></tr>';
}
function trade(t,side){let m=markets.find(x=>x.ticker===decodeURIComponent(t));if(!m)return;let price=side==='yes'?m.a:100-m.b,q=Math.max(1,Math.floor(Number($('qty').value)||1)),cost=price/100*q,max=Number($('maxPos').value)||250;if(!Number.isFinite(price)||price<=0||price>=100)return;if(cost>max)return alert('Order exceeds max position size');if(cost>balance)return alert('Insufficient paper balance');balance-=cost;positions.push({id:Date.now()+Math.random(),ticker:m.ticker,title:m.title||m.ticker,side,entry:price,qty:q,cost});render();saveState()}
function closePos(id){let p=positions.find(x=>x.id===id);if(!p)return;let m=markets.find(x=>x.ticker===p.ticker);if(!p||!m)return;let exit=p.side==='yes'?m.b:100-m.a;if(!Number.isFinite(exit)||exit<0)return alert('No current quote to close; reload markets.');let proceeds=exit/100*p.qty,profit=proceeds-p.cost;balance+=proceeds;pnl+=profit;history.unshift({...p,exit,profit,closed:new Date().toLocaleTimeString()});positions=positions.filter(x=>x.id!==id);equity.push(balance);render();saveState()}
function render(){ $('balance').textContent=money(balance);$('pnl').textContent=money(pnl);$('pnl').className=pnl>=0?'pos':'neg';$('open').textContent=positions.length;$('closed').textContent=history.length;$('positions').innerHTML=positions.length?positions.map(p=>'<tr><td>'+esc(p.title)+'</td><td>'+p.side.toUpperCase()+'</td><td>'+cents(p.entry)+'</td><td>'+p.qty+'</td><td>'+money(p.cost)+'</td><td><button onclick="closePos('+p.id+')">Close</button></td></tr>').join(''):'<tr><td colspan="6" class="empty">No open positions.</td></tr>';$('history').innerHTML=history.length?history.map(p=>'<tr><td>'+esc(p.title)+'</td><td>'+p.side.toUpperCase()+'</td><td>'+cents(p.entry)+' → '+cents(p.exit)+'</td><td>'+p.qty+'</td><td class="'+(p.profit>=0?'pos':'neg')+'">'+money(p.profit)+'</td><td>'+p.closed+'</td></tr>').join(''):'<tr><td colspan="6" class="empty">No closed trades.</td></tr>';draw()}
function draw(){let v=equity.concat([balance]),lo=Math.min(...v),hi=Math.max(...v);if(lo===hi){lo--;hi++}let points=v.map((n,i)=>(i/(Math.max(1,v.length-1))*690+5)+','+(145-(n-lo)/(hi-lo)*135)).join(' ');$('chart').innerHTML='<polyline points="'+points+'" fill="none" stroke="#43d39e" stroke-width="3"/>'}
let scannerTimer=null,scannerOn=true;
async function setScanner(on){
 scannerOn=on;
 $('scanToggle').textContent=on?'Pause scanning':'Resume scanning';
 $('scanStatus').textContent=on?'Server scanner enabled':'Scanner paused';
 $('scanStatus').className='status '+(on?'good':'');
 try{await fetch('/api/scanner/'+(on?'start':'stop'),{method:'POST'});}catch(e){console.warn('Server scanner control failed',e)}
 if(scannerTimer)clearInterval(scannerTimer);
 scannerTimer=on?setInterval(()=>{if(!document.hidden)load()},15000):null;
}
async function refreshScannerStatus(){
 try{const r=await fetch('/api/scanner/status');const s=await r.json();
 scannerOn=!!s.enabled;
 $('scanToggle').textContent=scannerOn?'Pause scanning':'Resume scanning';
 $('scanStatus').textContent=scannerOn?'Server scan every '+s.interval_seconds+'s':'Scanner paused';
 $('scanStatus').className='status '+(scannerOn?'good':'');
 }catch(e){$('scanStatus').textContent='Scanner status unavailable'}
}
$('load').onclick=load;$('scanToggle').onclick=()=>setScanner(!scannerOn);$('filter').onchange=renderMarkets;$('reset').onclick=()=>{let n=Number($('resetAmount').value);if(!(n>0&&Number.isFinite(n)))return alert('Enter a positive amount');if(!confirm('Reset paper account to '+money(n)+'? This clears trades and positions.'))return;balance=n;pnl=0;positions=[];history=[];equity=[n];previousQuotes={};seenSignals=new Set();render();saveState()};restoreState();render();setScanner(true);load();
</script></body></html>"""


@app.get("/manifest.webmanifest")
async def web_manifest():
    return {
        "id": "/",
        "name": "Kalshi Paper Scalper",
        "short_name": "Paper Scalper",
        "description": "Kalshi market scanner and simulated paper-trading dashboard.",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#070b12",
        "theme_color": "#070b12",
        "icons": [
            {"src": "/app-icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}
        ]
    }

@app.get("/app-icon.svg")
async def app_icon():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="112" fill="#070b12"/><rect x="32" y="32" width="448" height="448" rx="88" fill="#101e2d" stroke="#29425a" stroke-width="8"/><path d="M256 90 390 166 390 318 256 394 122 318 122 166Z" fill="none" stroke="#49e2ac" stroke-width="20" stroke-linejoin="round"/><path d="M162 282 218 224 258 256 340 172" fill="none" stroke="#6baeff" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/><circle cx="340" cy="172" r="17" fill="#f5c66a"/></svg>"""
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(PAGE)

@app.get("/api/health")
async def health():
    return {"ok": True, "provider": "Kalshi public market data"}

@app.get("/api/markets")
async def get_markets(status: str = "open", limit: int = 1000):
    # Kalshi returns markets in cursor-paginated pages. A single request only
    # returns the first page, so keep following cursors to scan broadly.
    page_size = max(1, min(limit, 1000))
    max_pages = 20  # bounded scan: up to 20,000 markets per refresh
    markets = []
    cursor = None
    pages_scanned = 0
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            for _ in range(max_pages):
                params = {"status": status, "limit": page_size}
                if cursor:
                    params["cursor"] = cursor
                response = await client.get(
                    f"{KALSHI}/markets",
                    params=params,
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                payload = response.json()
                batch = payload.get("markets", [])
                markets.extend(batch)
                pages_scanned += 1
                cursor = payload.get("cursor")
                if not cursor or not batch:
                    break
        return {
            "markets": markets,
            "pages_scanned": pages_scanned,
            "scan_complete": not bool(cursor),
            "next_cursor": cursor,
        }
    except httpx.HTTPStatusError as exc:
        raise HTTPException(502, f"Kalshi API returned HTTP {exc.response.status_code}")
    except httpx.TimeoutException:
        raise HTTPException(504, "Timed out contacting Kalshi public market data")
    except httpx.RequestError as exc:
        raise HTTPException(502, f"Could not reach Kalshi API: {type(exc).__name__}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
