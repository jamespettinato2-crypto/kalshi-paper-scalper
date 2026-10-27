import asyncio
import json
import os
import sqlite3
import time
import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter()
KALSHI = "https://api.elections.kalshi.com/trade-api/v2"
DB_PATH = os.environ.get("DATABASE_PATH", "paper_scalper.db")
INTERVAL = max(30, int(os.environ.get("SCANNER_INTERVAL_SECONDS", "60")))
enabled = True
task = None
last_scan = None
last_error = None
market_count = 0
signals = []
previous = {}

def connect():
    con = sqlite3.connect(DB_PATH)
    con.execute("CREATE TABLE IF NOT EXISTS scanner_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    return con

def save(key, value):
    with connect() as con:
        con.execute("INSERT INTO scanner_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (key, json.dumps(value)))

def load(key, default=None):
    with connect() as con:
        row = con.execute("SELECT value FROM scanner_settings WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

enabled = bool(load('enabled', True))

async def fetch_markets():
    result, cursor = [], None
    async with httpx.AsyncClient(timeout=25) as client:
        for _ in range(20):
            params = {"status":"open", "limit":1000}
            if cursor: params["cursor"] = cursor
            r = await client.get(f"{KALSHI}/markets", params=params, headers={"Accept":"application/json"})
            r.raise_for_status()
            payload = r.json()
            batch = payload.get("markets", [])
            result.extend(batch)
            cursor = payload.get("cursor")
            if not cursor or not batch: break
    return result

async def loop():
    global last_scan, last_error, market_count, signals, previous
    while enabled:
        try:
            markets = await fetch_markets()
            current_signals = []
            for m in markets:
                ticker = m.get("ticker")
                bid, ask = m.get("yes_bid"), m.get("yes_ask")
                if not ticker or bid is None or ask is None: continue
                try:
                    bid, ask = float(bid), float(ask)
                    mid = (bid + ask) / 2
                except (TypeError, ValueError):
                    continue
                old = previous.get(ticker)
                previous[ticker] = mid
                if old is not None and abs(mid-float(old)) >= 2 and ask >= bid and ask-bid <= 5:
                    current_signals.append({"ticker":ticker, "title":m.get("title",ticker),
                        "direction":"YES momentum" if mid>float(old) else "NO momentum",
                        "move_cents":round(mid-float(old),2), "yes_bid":bid, "yes_ask":ask})
            signals = sorted(current_signals, key=lambda x:abs(x["move_cents"]), reverse=True)[:100]
            market_count = len(markets)
            last_scan = time.time()
            last_error = None
            save("previous", previous)
            save("last_scan", last_scan)
            save("market_count", market_count)
            save("signals", signals)
        except Exception as e:
            last_error = f"{type(e).__name__}: {str(e)[:250]}"
        await asyncio.sleep(INTERVAL)

@router.get("/api/scanner/status")
async def status():
    global task, previous
    if enabled and (task is None or task.done()):
        previous = load("previous", {})
        task = asyncio.create_task(loop())
    return {"enabled":enabled, "last_scan":last_scan, "markets_scanned":market_count,
            "signals":signals, "last_error":last_error, "interval_seconds":INTERVAL,
            "note":"Server-side scanner only runs while Render service is awake. Signals are informational; this endpoint does not place trades."}

@router.post("/api/scanner/{action}")
async def control(action: str):
    global enabled, task, previous
    if action not in ("start","stop"):
        raise HTTPException(400, "Action must be start or stop")
    enabled = action == "start"
    save("enabled", enabled)
    if task:
        task.cancel()
        task = None
    if enabled:
        previous = load("previous", {})
        task = asyncio.create_task(loop())
    return await status()
