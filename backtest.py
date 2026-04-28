# backtest.py — Backtest simple de la estrategia actual
import time
import pandas as pd
import ccxt
from datetime import datetime, timedelta

import config
from strategy import Strategy
from data_hub import DataHub   # Usamos el mismo DataHub

print("🚀 Iniciando Backtest de la estrategia...")

# =============================================
# CONFIGURACIÓN DEL BACKTEST
# =============================================
SYMBOL = "BTC/USDT:USDT"
TIMEFRAME = "5m"
DAYS_BACK = 30                    # Últimos 30 días
INITIAL_BALANCE = 1000.0          # Capital inicial ficticio (USDT)

# =============================================
# CONEXIÓN PARA DATOS HISTÓRICOS
# =============================================
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

print(f"Descargando datos históricos de {DAYS_BACK} días ({TIMEFRAME})...")

since = int((datetime.now() - timedelta(days=DAYS_BACK)).timestamp() * 1000)
ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, since=since, limit=1000)

df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

print(f"✅ Datos cargados: {len(df)} velas desde {df.index[0]} hasta {df.index[-1]}")

# =============================================
# INICIALIZACIÓN
# =============================================
strategy = Strategy()
trades = []
equity_curve = [INITIAL_BALANCE]
position = None
entry_price = 0
balance = INITIAL_BALANCE

print("\nEjecutando backtest...\n")

for i in range(config.EMA_SLOW_PERIOD + 10, len(df)):
    # Tomamos solo las velas hasta el momento actual del bucle
    current_candles = {"5m": df.iloc[:i+1].reset_index()}
    
    # Simulamos order book con el precio actual (aproximación)
    current_price = float(df['close'].iloc[i])
    fake_order_book = {"imbalance": 0.55}  # valor neutro, la estrategia usará principalmente EMAs

    signal = strategy.analyze(current_candles, fake_order_book)

    # Si no hay posición y hay señal válida → abrimos
    if position is None and signal["valid"]:
        position = signal["direction"]
        entry_price = current_price
        size = (balance * config.RISK_PER_TRADE) / (entry_price * 0.003)   # riesgo 0.5%
        print(f"📍 [{df.index[i]}] ABRIMOS {position} @ {current_price:,.2f}")

    # Si tenemos posición → verificamos salida (simple: cierre por señal contraria o final)
    elif position is not None:
        # Salida simple: señal contraria o fin del backtest
        if (position == "LONG" and signal["direction"] == "SHORT") or \
           (position == "SHORT" and signal["direction"] == "LONG") or \
           (i == len(df)-1):

            exit_price = current_price
            pnl_pct = (exit_price - entry_price) / entry_price if position == "LONG" else (entry_price - exit_price) / entry_price
            pnl_usdt = balance * config.RISK_PER_TRADE * (pnl_pct / 0.003)   # según riesgo

            balance += pnl_usdt
            equity_curve.append(balance)

            win = pnl_usdt > 0
            trades.append({
                "entry_time": df.index[i - (i % 10)],  # aproximación
                "direction": position,
                "entry": entry_price,
                "exit": exit_price,
                "pnl_usdt": pnl_usdt,
                "win": win
            })

            print(f"✅ [{df.index[i]}] CERRAMOS {position} | PnL: {pnl_usdt:+.2f} USDT")

            position = None

# =============================================
# RESULTADOS FINALES
# =============================================
print("\n" + "="*70)
print("📊 RESULTADOS DEL BACKTEST")
print("="*70)
print(f"Período: {df.index[0].date()} → {df.index[-1].date()}")
print(f"Capital inicial : {INITIAL_BALANCE:,.2f} USDT")
print(f"Capital final   : {balance:,.2f} USDT")
print(f"Beneficio neto  : {balance - INITIAL_BALANCE:+.2f} USDT ({(balance/INITIAL_BALANCE-1)*100:+.1f}%)")

if trades:
    df_trades = pd.DataFrame(trades)
    winrate = (df_trades['win'].mean() * 100)
    total_trades = len(df_trades)
    wins = df_trades['win'].sum()
    print(f"\nOperaciones     : {total_trades}")
    print(f"Winrate         : {winrate:.1f}% ({wins}/{total_trades})")
    print(f"Mejor trade     : {df_trades['pnl_usdt'].max():+.2f} USDT")
    print(f"Peor trade      : {df_trades['pnl_usdt'].min():+.2f} USDT")
else:
    print("\nNo se generaron operaciones en este período.")

print("\n✅ Backtest finalizado. Revisa los resultados arriba.")
