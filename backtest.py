# backtest.py — Versión ligera (usa datos públicos)
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config
from strategy import Strategy

print("🚀 Iniciando Backtest (versión sin API keys)...\n")

# ========================= CONFIGURACIÓN =========================
DIAS = 30
CAPITAL_INICIAL = 1000.0
TIMEFRAME = "5m"

print(f"Generando datos simulados de {DIAS} días para BTC/USDT...\n")

# Generamos datos históricos simulados (precio realista con tendencia + ruido)
np.random.seed(42)
dates = pd.date_range(end=datetime.now(), periods=DIAS*288, freq='5min')  # 288 velas por día en 5m

# Precio base con tendencia ligera
base_price = 76000
trend = np.linspace(0, 3000, len(dates))   # tendencia alcista leve
noise = np.random.normal(0, 800, len(dates))
price = base_price + trend + noise

df = pd.DataFrame({
    'timestamp': dates,
    'open': price * (1 + np.random.normal(0, 0.001, len(dates))),
    'high': price * (1 + np.abs(np.random.normal(0, 0.003, len(dates)))),
    'low': price * (1 - np.abs(np.random.normal(0, 0.003, len(dates)))),
    'close': price,
    'volume': np.random.lognormal(10, 1, len(dates))
})
df.set_index('timestamp', inplace=True)

print(f"✅ Datos simulados generados: {len(df):,} velas")
print(f"Período: {df.index[0].date()} → {df.index[-1].date()}\n")

# ========================= BACKTEST =========================
strategy = Strategy()
trades = []
balance = CAPITAL_INICIAL
position = None
entry_price = 0

print("Ejecutando backtest...\n")

for i in range(50, len(df)):
    current_candles = {"5m": df.iloc[:i+1].reset_index()}
    current_price = float(df['close'].iloc[i])

    fake_ob = {"imbalance": np.random.uniform(0.45, 0.75)}   # simulación realista

    signal = strategy.analyze(current_candles, fake_ob)

    if position is None and signal["valid"]:
        position = signal["direction"]
        entry_price = current_price
        print(f"📍 [{df.index[i].strftime('%m-%d %H:%M')}] ABRIMOS {position} @ {current_price:,.1f}")

    elif position is not None:
        if (position == "LONG" and signal["direction"] == "SHORT") or \
           (position == "SHORT" and signal["direction"] == "LONG") or i == len(df)-1:
            
            exit_price = current_price
            pnl_pct = (exit_price - entry_price) / entry_price if position == "LONG" else (entry_price - exit_price) / entry_price
            pnl_usdt = balance * config.RISK_PER_TRADE * (pnl_pct / config.STOP_LOSS_PCT)

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
print("\n" + "="*80)
print("📊 RESULTADOS DEL BACKTEST")
print("="*80)
print(f"Capital inicial  : ${CAPITAL_INICIAL:,.2f}")
print(f"Capital final    : ${balance:,.2f}")
print(f"Beneficio neto   : ${balance - CAPITAL_INICIAL:+.2f} ({((balance/CAPITAL_INICIAL)-1)*100:+.1f}%)")

if trades:
    df_trades = pd.DataFrame(trades)
    winrate = df_trades['win'].mean() * 100
    print(f"\nOperaciones totales : {len(trades)}")
    print(f"Winrate             : {winrate:.1f}%")
    print(f"Ganancia media      : ${df_trades['pnl'].mean():+.2f}")
    print(f"Mejor operación     : ${df_trades['pnl'].max():+.2f}")
    print(f"Peor operación      : ${df_trades['pnl'].min():+.2f}")
else:
    print("\nNo se generaron operaciones.")

print("\n✅ Backtest finalizado.")
