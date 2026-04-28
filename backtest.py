# backtest.py — Backtest de la estrategia actual
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import config
from strategy import Strategy

print("🚀 Iniciando Backtest...\n")

# =============================================
# CONFIGURACIÓN
# =============================================
SYMBOL = "BTC/USDT"
TIMEFRAME = "5m"
DAYS_BACK = 600                    # Puedes cambiar a 7, 14, 60, etc.
INITIAL_BALANCE = 1000.0

# =============================================
# DESCARGAR DATOS HISTÓRICOS
# =============================================
exchange = ccxt.binance({
    'enableRateLimit': True,
})

print(f"Descargando {DAYS_BACK} días de velas {TIMEFRAME}...")

since = int((datetime.now() - timedelta(days=DAYS_BACK)).timestamp() * 1000)
ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, since=since, limit=1500)

df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

print(f"✅ Datos cargados: {len(df)} velas")
print(f"Desde: {df.index[0]} hasta {df.index[-1]}\n")

# =============================================
# INICIALIZACIÓN
# =============================================
strategy = Strategy()
trades = []
balance = INITIAL_BALANCE
position = None
entry_price = 0
equity = [INITIAL_BALANCE]

print("Ejecutando backtest...\n")

for i in range(50, len(df)):        # Empezamos después de tener suficientes velas
    current_candles = {"5m": df.iloc[:i+1].reset_index()}
    current_price = float(df['close'].iloc[i])

    # Simulación simple de order book
    fake_ob = {"imbalance": 0.55}

    signal = strategy.analyze(current_candles, fake_ob)

    # Abrir posición
    if position is None and signal["valid"]:
        position = signal["direction"]
        entry_price = current_price
        risk_amount = balance * config.RISK_PER_TRADE
        size = risk_amount / (entry_price * config.STOP_LOSS_PCT)   # tamaño según riesgo
        print(f"📍 [{df.index[i].strftime('%Y-%m-%d %H:%M')}] ABRIMOS {position} @ {current_price:,.2f}")

    # Cerrar posición
    elif position is not None:
        should_close = False
        if (position == "LONG" and signal["direction"] == "SHORT") or \
           (position == "SHORT" and signal["direction"] == "LONG"):
            should_close = True
        elif i == len(df)-1:   # Última vela
            should_close = True

        if should_close:
            exit_price = current_price
            pnl_pct = (exit_price - entry_price)/entry_price if position == "LONG" else (entry_price - exit_price)/entry_price
            pnl_usdt = balance * config.RISK_PER_TRADE * (pnl_pct / config.STOP_LOSS_PCT)

            balance += pnl_usdt
            equity.append(balance)

            win = pnl_usdt > 0
            trades.append({
                "time": df.index[i],
                "direction": position,
                "entry": entry_price,
                "exit": exit_price,
                "pnl_usdt": pnl_usdt,
                "win": win
            })

            print(f"✅ CERRAMOS {position} @ {exit_price:,.2f} | PnL: {pnl_usdt:+.2f} USDT")
            position = None

# =============================================
# RESULTADOS
# =============================================
print("\n" + "="*75)
print("📊 RESULTADOS DEL BACKTEST")
print("="*75)
print(f"Período analizado     : {df.index[0].date()}  →  {df.index[-1].date()}")
print(f"Capital inicial       : {INITIAL_BALANCE:,.2f} USDT")
print(f"Capital final         : {balance:,.2f} USDT")
print(f"Beneficio neto        : {balance - INITIAL_BALANCE:+.2f} USDT ({((balance/INITIAL_BALANCE)-1)*100:+.1f}%)")

if trades:
    df_trades = pd.DataFrame(trades)
    winrate = df_trades['win'].mean() * 100
    print(f"\nTotal operaciones     : {len(trades)}")
    print(f"Winrate               : {winrate:.1f}%")
    print(f"Ganancia promedio     : {df_trades['pnl_usdt'].mean():+.2f} USDT")
    print(f"Mejor operación       : {df_trades['pnl_usdt'].max():+.2f} USDT")
    print(f"Peor operación        : {df_trades['pnl_usdt'].min():+.2f} USDT")
else:
    print("\nNo se generaron operaciones durante el período.")

print("\n✅ Backtest finalizado.")
