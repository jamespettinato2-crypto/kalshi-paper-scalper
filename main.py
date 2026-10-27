import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="Kalshi Paper Scalper")
KALSHI = "https://api.elections.kalshi.com/trade-api/v2"

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kalshi Paper Scalper</title>
<style>
:root{color-scheme:dark;--bg:#080d14;--panel:#111a27;--line:#283548;--text:#e9eff8;--muted:#8fa0b7;--green:#43d39e;--red:#ff6878;--blue:#63a8ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px system-ui,Arial}header{padding:20px 4vw;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap}h1{font-size:22px;margin:0}main{max-width:1400px;margin:auto;padding:22px 4vw}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.panel,.metric{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px;margin-bottom:14px}.metric label{color:var(--muted);font-size:12px}.metric strong{display:block;font-size:25px;margin-top:5px}.row,.split{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.split{justify-content:space-between}button,input,select{font:inherit;color:var(--text);background:#182334;border:1px solid #34455e;border-radius:9px;padding:10px 12px}button{cursor:pointer}button.primary{background:#225db0;border-color:#3978ce}button.danger{background:#49212a;border-color:#73313d}.status{font-size:12px;padding:6px 10px;border-radius:20px;background:#273344;color:var(--muted)}.good{color:var(--green);background:#12372d}.bad{color:var(--red);background:#3c2028}.tablewrap{overflow:auto}table{border-collapse:collapse;width:100%;min-width:700px}th,td{text-align:left;padding:11px;border-bottom:1px solid var(--line);font-size:13px}th{color:var(--muted)}td button{padding:6px 9px;font-size:12px}.note{font-size:12px;color:var(--muted);line-height:1.5}.empty{text-align:center;color:var(--muted);padding:22px}.pos{color:var(--green)}.neg{color:var(--red)}@media(max-width:700px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}main{padding:14px}.metric strong{font-size:20px}}
</style></head><body>
<header><div><h1>◈ Kalshi Paper Scalper</h1><div class="note">Public Kalshi market data · simulated trades only</div></div><div class="row"><span id="status" class="status">Not connected</span><button class="primary" id="load">Load markets</button></div></header>
<main>
<div class="grid"><div class="metric"><label>Paper balance</label><strong id="balance">$10,000.00</strong></div><div class="metric"><label>Realized P&amp;L</label><strong id="pnl">$0.00</strong></div><div class="metric"><label>Open positions</label><strong id="open">0</strong></div><div class="metric"><label>Closed trades</label><strong id="closed">0</strong></div></div>
<section class="panel"><div class="split"><b>Paper account controls</b><span class="status">PAPER ONLY · LIVE ORDERS DISABLED</span></div><div class="row" style="margin-top:12px"><label>Reset balance $ <input id="resetAmount" type="number" min=".01" step="any" value="10000" style="width:140px"></label><button class="danger" id="reset">Reset account</button><label>Contracts <input id="qty" type="number" min="1" value="1" style="width:80px"></label><label>Max position $ <input id="maxPos" type="number" min="1" value="250" style="width:110px"></label></div><p class="note">Reset accepts any positive amount and clears positions, history and P&amp;L. It does not change your Kalshi account.</section>
<section class="panel"><div class="split"><b>Market scanner</b><div class="row"><select id="filter"><option value="all">All markets</option><option value="sports">Sports</option><option value="economics">Economics / finance</option><option value="weather">Weather</option></select><span id="updated" class="note">Waiting for data</span><span id="scanStatus" class="status good">Auto-refresh every 15 seconds</span><button id="scanToggle">Pause scanning</button></div></div><div class="tablewrap"><table><thead><tr><th>Market</th><th>Ticker</th><th>YES bid / ask</th><th>NO bid / ask*</th><th>Spread</th><th>Paper order</th></tr></thead><tbody id="markets"><tr><td colspan="6" class="empty">Tap Load markets to fetch Kalshi prices.</td></tr></tbody></table></div><p class="note">*NO quotes are derived from YES prices where applicable. Quotes may be missing or stale. Paper fills are simplified and do not model queue priority or all fees.</p></section>
<section class="panel"><b>Open paper positions</b><div class="tablewrap"><table><thead><tr><th>Market</th><th>Side</th><th>Entry</th><th>Qty</th><th>Cost</th><th>Action</th></tr></thead><tbody id="positions"><tr><td colspan="6" class="empty">No open positions.</td></tr></tbody></table></div></section>
<section class="panel"><b>Closed trades</b><div class="tablewrap"><table><thead><tr><th>Market</th><th>Side</th><th>Entry → Exit</th><th>Qty</th><th>Net P&amp;L</th><th>Closed</th></tr></thead><tbody id="history"><tr><td colspan="6" class="empty">No closed trades.</td></tr></tbody></table></div></section>
<section class="panel"><b>Equity history</b><svg id="chart" viewBox="0 0 700 150" style="width:100%;height:150px"></svg><p class="note">This is a paper-trading prototype. No guaranteed profits. Live trading is not implemented.</p></section>
</main>
<script>
let markets=[],positions=[],history=[],balance=10000,pnl=0,equity=[10000];
const $=x=>document.getElementById(x), money=n=>'$'+Number(n||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}), cents=n=>n==null?'—':Number(n).toFixed(1)+'¢';
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function quote(m,k){let v=m[k];if(v==null&&m[k+'_dollars']!=null)v=Number(m[k+'_dollars'])*100;return v==null||!Number.isFinite(Number(v))?null:Number(v)}
function normalize(m){return {...m,b:quote(m,'yes_bid'),a:quote(m,'yes_ask')}}
function cat(m){let s=((m.title||'')+' '+(m.ticker||'')).toLowerCase();if(/weather|rain|snow|temperature/.test(s))return'weather';if(/cpi|fed|interest|gdp|stock|econom|finance|inflation/.test(s))return'economics';if(/nba|nfl|mlb|nhl|soccer|football|tennis|sport/.test(s))return'sports';return'other'}
function renderMarkets(){let f=$('filter').value,ls=markets.filter(m=>f==='all'||cat(m)===f);$('markets').innerHTML=ls.length?ls.map(m=>{let sp=m.a!=null&&m.b!=null?m.a-m.b:null;return '<tr><td>'+esc(m.title||m.ticker)+'</td><td>'+esc(m.ticker)+'</td><td>'+cents(m.b)+' / '+cents(m.a)+'</td><td>'+cents(m.a==null?null:100-m.a)+' / '+cents(m.b==null?null:100-m.b)+'</td><td>'+cents(sp)+'</td><td><button '+(m.a==null?'disabled':'')+' onclick="trade(\''+encodeURIComponent(m.ticker)+'\',\'yes\')">Buy YES</button> <button '+(m.b==null?'disabled':'')+' onclick="trade(\''+encodeURIComponent(m.ticker)+'\',\'no\')">Buy NO</button></td></tr>'}).join(''):'<tr><td colspan="6" class="empty">No matching markets.</td></tr>'}
async function load(){ $('load').disabled=true;$('status').textContent='Fetching…';$('status').className='status';try{let r=await fetch('/api/markets?status=open&limit=1000');let d=await r.json();if(!r.ok)throw Error(d.detail||('HTTP '+r.status));if(!Array.isArray(d.markets))throw Error('Unexpected API response');markets=d.markets.map(normalize);renderMarkets();$('updated').textContent='Updated '+new Date().toLocaleTimeString();$('status').textContent='Market data loaded';$('status').className='status good'}catch(e){$('status').textContent='Market data error';$('status').className='status bad';$('markets').innerHTML='<tr><td colspan="6" class="empty">'+esc(e.message)+'</td></tr>'}finally{$('load').disabled=false}}
function trade(t,side){let m=markets.find(x=>x.ticker===decodeURIComponent(t));if(!m)return;let price=side==='yes'?m.a:100-m.b,q=Math.max(1,Math.floor(Number($('qty').value)||1)),cost=price/100*q,max=Number($('maxPos').value)||250;if(!Number.isFinite(price)||price<=0||price>=100)return;if(cost>max)return alert('Order exceeds max position size');if(cost>balance)return alert('Insufficient paper balance');balance-=cost;positions.push({id:Date.now()+Math.random(),ticker:m.ticker,title:m.title||m.ticker,side,entry:price,qty:q,cost});render()}
function closePos(id){let p=positions.find(x=>x.id===id),m=markets.find(x=>x.ticker===p.ticker);if(!p||!m)return;let exit=p.side==='yes'?m.b:100-m.a;if(!Number.isFinite(exit)||exit<0)return alert('No current quote to close; reload markets.');let proceeds=exit/100*p.qty,profit=proceeds-p.cost;balance+=proceeds;pnl+=profit;history.unshift({...p,exit,profit,closed:new Date().toLocaleTimeString()});positions=positions.filter(x=>x.id!==id);equity.push(balance);render()}
function render(){ $('balance').textContent=money(balance);$('pnl').textContent=money(pnl);$('pnl').className=pnl>=0?'pos':'neg';$('open').textContent=positions.length;$('closed').textContent=history.length;$('positions').innerHTML=positions.length?positions.map(p=>'<tr><td>'+esc(p.title)+'</td><td>'+p.side.toUpperCase()+'</td><td>'+cents(p.entry)+'</td><td>'+p.qty+'</td><td>'+money(p.cost)+'</td><td><button onclick="closePos('+p.id+')">Close</button></td></tr>').join(''):'<tr><td colspan="6" class="empty">No open positions.</td></tr>';$('history').innerHTML=history.length?history.map(p=>'<tr><td>'+esc(p.title)+'</td><td>'+p.side.toUpperCase()+'</td><td>'+cents(p.entry)+' → '+cents(p.exit)+'</td><td>'+p.qty+'</td><td class="'+(p.profit>=0?'pos':'neg')+'">'+money(p.profit)+'</td><td>'+p.closed+'</td></tr>').join(''):'<tr><td colspan="6" class="empty">No closed trades.</td></tr>';draw()}
function draw(){let v=equity.concat([balance]),lo=Math.min(...v),hi=Math.max(...v);if(lo===hi){lo--;hi++}let points=v.map((n,i)=>(i/(Math.max(1,v.length-1))*690+5)+','+(145-(n-lo)/(hi-lo)*135)).join(' ');$('chart').innerHTML='<polyline points="'+points+'" fill="none" stroke="#43d39e" stroke-width="3"/>'}
let scannerTimer=null,scannerOn=true;function setScanner(on){scannerOn=on;$('scanToggle').textContent=on?'Pause scanning':'Resume scanning';$('scanStatus').textContent=on?'Auto-refresh every 15 seconds':'Scanner paused';$('scanStatus').className='status '+(on?'good':'');if(scannerTimer)clearInterval(scannerTimer);scannerTimer=on?setInterval(()=>{if(!document.hidden)load()},15000):null}
$('load').onclick=load;$('scanToggle').onclick=()=>setScanner(!scannerOn);$('filter').onchange=renderMarkets;$('reset').onclick=()=>{let n=Number($('resetAmount').value);if(!(n>0&&Number.isFinite(n)))return alert('Enter a positive amount');if(!confirm('Reset paper account to '+money(n)+'? This clears trades and positions.'))return;balance=n;pnl=0;positions=[];history=[];equity=[n];render()};render();setScanner(true);load();
</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(PAGE)

@app.get("/api/health")
async def health():
    return {"ok": True, "provider": "Kalshi public market data"}

@app.get("/api/markets")
async def get_markets(status: str = "open", limit: int = 1000):
    limit = max(1, min(limit, 1000))
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{KALSHI}/markets",
                params={"status": status, "limit": limit},
                headers={"Accept": "application/json"},
            )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(502, f"Kalshi API returned HTTP {exc.response.status_code}")
    except httpx.TimeoutException:
        raise HTTPException(504, "Timed out contacting Kalshi public market data")
    except httpx.RequestError as exc:
        raise HTTPException(502, f"Could not reach Kalshi API: {type(exc).__name__}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
