# backtest.py — Versión Realista 2026
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config
from strategy import Strategy

print("🚀 Backtest Realista (con mercado lateral + tendencias mixtas)\n")

# ========================= CONFIG =========================
DIAS = 45
CAPITAL_INICIAL = 1000.0

# ========================= DATOS MÁS REALISTAS =========================
np.random.seed(123)
dates = pd.date_range(end=datetime.now(), periods=DIAS*288, freq='5min')

# Precio con fases: lateral → subida → bajada → lateral
base = 76000
phase1 = np.linspace(0, 800, len(dates)//3)           # subida suave
phase2 = np.linspace(800, -1200, len(dates)//3)       # bajada fuerte
phase3 = np.linspace(-1200, 400, len(dates) - 2*len(dates)//3) 

trend = np.concatenate([phase1, phase2, phase3])
noise = np.random.normal(0, 1100, len(dates))
price = base + trend + noise

df = pd.DataFrame({
    'timestamp': dates,
    'open': price * (1 + np.random.normal(0, 0.0015, len(dates))),
    'high': price * (1 + np.abs(np.random.normal(0, 0.004, len(dates)))),
    'low': price * (1 - np.abs(np.random.normal(0, 0.004, len(dates)))),
    'close': price,
    'volume': np.random.lognormal(9.5, 1.2, len(dates))
})
df.set_index('timestamp', inplace=True)

print(f"✅ Datos realistas generados: {len(df):,} velas")
print(f"Período: {df.index[0].date()} → {df.index[-1].date()}\n")

# ========================= BACKTEST =========================
strategy = Strategy()
trades = []
balance = CAPITAL_INICIAL
position = None
entry_price = 0

print("Ejecutando backtest realista...\n")

for i in range(100, len(df)):
    current_candles = {"5m": df.iloc[:i+1].reset_index()}
    current_price = float(df['close'].iloc[i])

    fake_ob = {"imbalance": np.random.uniform(0.42, 0.78)}

    signal = strategy.analyze(current_candles, fake_ob)

    if position is None and signal["valid"]:
        position = signal["direction"]
        entry_price = current_price
        print(f"📍 [{df.index[i].strftime('%m-%d %H:%M')}] ABRIMOS {position} @ {current_price:,.1f}")

    elif position is not None:
        should_close = False
        if (position == "LONG" and signal["direction"] == "SHORT") or \
           (position == "SHORT" and signal["direction"] == "LONG"):
            should_close = True
        # Stop-loss y take-profit más realistas
        if position == "LONG":
            if current_price <= entry_price * 0.993:   # -0.7%
                should_close = True
            elif current_price >= entry_price * 1.015: # +1.5%
                should_close = True
        else:  # SHORT
            if current_price >= entry_price * 1.007:
                should_close = True
            elif current_price <= entry_price * 0.985:
                should_close = True

        if should_close or i == len(df)-1:
            exit_price = current_price
            pnl_pct = (exit_price - entry_price) / entry_price if position == "LONG" else (entry_price - exit_price) / entry_price
            pnl_usdt = balance * config.RISK_PER_TRADE * (pnl_pct / config.STOP_LOSS_PCT * 1.8)

            balance += pnl_usdt

            trades.append({
                "fecha": df.index[i],
                "direccion": position,
                "entrada": entry_price,
                "salida": exit_price,
                "pnl": pnl_usdt,
                "win": pnl_usdt > 0
            })

            print(f"✅ CERRAMOS {position} @ {exit_price:,.1f} | PnL: {pnl_usdt:+.2f} USDT")
            position = None

# ========================= RESULTADOS =========================
print("\n" + "="*85)
print("📊 RESULTADOS DEL BACKTEST REALISTA")
print("="*85)
print(f"Capital inicial : ${CAPITAL_INICIAL:,.2f}")
print(f"Capital final   : ${balance:,.2f}")
print(f"Beneficio neto  : ${balance - CAPITAL_INICIAL:+.2f} ({((balance/CAPITAL_INICIAL)-1)*100:+.1f}%)")

if trades:
    df_trades = pd.DataFrame(trades)
    winrate = df_trades['win'].mean() * 100
    print(f"\nOperaciones totales : {len(trades)}")
    print(f"Winrate             : {winrate:.1f}%")
    print(f"Ganancia media      : ${df_trades['pnl'].mean():+.2f}")
    print(f"Mejor operación     : ${df_trades['pnl'].max():+.2f}")
    print(f"Peor operación      : ${df_trades['pnl'].min():+.2f}")
    print(f"Max Drawdown aprox : -{(min(df_trades['pnl']) / CAPITAL_INICIAL * 100):.1f}%")
else:
    print("No se generaron operaciones.")

print("\n✅ Backtest finalizado.")
