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
