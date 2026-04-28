# backtest.py — Versión usando Bybit (evita bloqueos de Binance)
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import config
from strategy import Strategy

print("🚀 Iniciando Backtest usando Bybit...\n")

# ========================= CONFIGURACIÓN =========================
SYMBOL = "BTCUSDT"          # Formato de Bybit
TIMEFRAME = "5m"
DIAS = 30                   # Cambia a 15, 45, 90 según quieras
CAPITAL_INICIAL = 1000.0

# ========================= DESCARGA DE DATOS =========================
exchange = ccxt.bybit({
    'enableRateLimit': True,
})

print(f"Descargando {DIAS} días de velas {TIMEFRAME} desde Bybit...")

since = int((datetime.now() - timedelta(days=DIAS)).timestamp() * 1000)
ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, since=since, limit=1500)

df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

print(f"✅ Datos cargados: {len(df):,} velas")
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

    # Simulación simple de order book
    fake_ob = {"imbalance": 0.58}

    signal = strategy.analyze(current_candles, fake_ob)

    # Abrir
    if position is None and signal["valid"]:
        position = signal["direction"]
        entry_price = current_price
        print(f"📍 [{df.index[i].strftime('%m-%d %H:%M')}] ABRIMOS {position} @ {current_price:,.1f}")

    # Cerrar
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
print(f"Período          : {df.index[0].date()}  →  {df.index[-1].date()}")
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
    print("\nNo se generaron operaciones en este período.")

print("\n✅ Backtest finalizado.")
