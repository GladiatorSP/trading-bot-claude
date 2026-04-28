# backtest.py — Versión Equilibrada y Más Realista
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config
from strategy import Strategy

print("🚀 Backtest Versión Equilibrada (Mejor Calidad de Señales)\n")

# ========================= CONFIG =========================
DIAS = 30
CAPITAL_INICIAL = 1000.0

# ========================= DATOS =========================
np.random.seed(42)
dates = pd.date_range(end=datetime.now(), periods=DIAS*288, freq='5min')

base_price = 76500
trend = np.linspace(0, 5000, len(dates))
noise = np.random.normal(0, 900, len(dates))
price = base_price + trend + noise

df = pd.DataFrame({
    'timestamp': dates,
    'open': price * (1 + np.random.normal(0, 0.002, len(dates))),
    'high': price * (1 + np.abs(np.random.normal(0, 0.004, len(dates)))),
    'low': price * (1 - np.abs(np.random.normal(0, 0.004, len(dates)))),
    'close': price,
    'volume': np.random.lognormal(10, 1, len(dates))
})
df.set_index('timestamp', inplace=True)

print(f"✅ {len(df):,} velas generadas\n")

# ========================= BACKTEST =========================
strategy = Strategy()
trades = []
balance = CAPITAL_INICIAL
position = None

print("Ejecutando backtest equilibrado...\n")

for i in range(100, len(df)):
    current_candles = {"5m": df.iloc[:i+1].reset_index()}
    current_price = float(df['close'].iloc[i])

    fake_ob = {"imbalance": np.random.uniform(0.48, 0.82)}

    signal = strategy.analyze(current_candles, fake_ob)

    if position is None and signal["valid"]:
        position = signal["direction"]
        entry_price = current_price
        print(f"📍 [{df.index[i].strftime('%m-%d %H:%M')}] ABRIMOS {position} @ {current_price:,.1f} | {signal['reason']}")

    elif position is not None:
        should_close = False
        if (position == "LONG" and signal["direction"] == "SHORT") or \
           (position == "SHORT" and signal["direction"] == "LONG"):
            should_close = True
        elif position == "LONG" and current_price >= entry_price * 1.012:   # +1.2%
            should_close = True
        elif position == "SHORT" and current_price <= entry_price * 0.988: # -1.2%
            should_close = True

        if should_close or i == len(df)-1:
            exit_price = current_price
            pnl_pct = (exit_price - entry_price) / entry_price if position == "LONG" else (entry_price - exit_price) / entry_price
            pnl_usdt = balance * config.RISK_PER_TRADE * (pnl_pct / config.STOP_LOSS_PCT * 2)

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
print("📊 RESULTADOS DEL BACKTEST EQUILIBRADO")
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
else:
    print("No se generaron operaciones.")

print("\n✅ Backtest finalizado.")
