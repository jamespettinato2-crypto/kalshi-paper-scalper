# Kalshi Paper Scalper

A mobile-friendly paper trading dashboard with a FastAPI backend proxy for Kalshi's public market data.

## Deploy on Render
1. Sign in to Render and choose **New → Web Service**.
2. Connect this GitHub repository.
3. Runtime: **Python**.
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Deploy. Open the Render URL and tap **Load markets**.

## Run locally
`pip install -r requirements.txt`
`uvicorn main:app --host 0.0.0.0 --port 8000`

## Notes
- Uses public Kalshi market data only; no API key required.
- Paper account and simulated orders are client-side and never place real orders.
- Reset balance accepts any positive amount.
- Simplified simulated fills; does not model order queue, slippage or all fees.
- Live trading is not implemented. Profit is not guaranteed.

## Server scanner

The dashboard includes a server-side scanner API:
- `POST /api/scanner/start` starts scanning Kalshi's public open markets.
- `POST /api/scanner/stop` stops it.
- `GET /api/scanner/status` returns scanner status, latest signals, errors, and scan interval.
- Scanner enabled state and recent price baselines are stored in SQLite.

Set `DATABASE_PATH` to a persistent disk path on a paid Render service to retain scanner settings and baselines across restarts. Render Free services can sleep and have ephemeral filesystems, so they cannot guarantee 24/7 scanning or durable paper-account history. The scanner currently reports momentum signals; it does not place server-side paper trades. Paper positions and balance remain browser-local until a persistent paper-account API is implemented.
