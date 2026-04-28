# Versión corregida para Colab - Abril 2026
"""
config.py — Configuración del bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==================== CREDENCIALES ====================
BINANCE_TESTNET_API_KEY: str = os.getenv("BINANCE_TESTNET_API_KEY", "")
BINANCE_TESTNET_SECRET: str   = os.getenv("BINANCE_TESTNET_SECRET", "")

# ==================== MODO DE OPERACIÓN ====================
USE_TESTNET: bool = True

# ==================== MERCADO ====================
SYMBOL: str = "BTC/USDT:USDT"
LEVERAGE: int = 5
MARGIN_TYPE: str = "isolated"

# ==================== GESTIÓN DE RIESGO ====================
RISK_PER_TRADE: float = 0.005      # 0.5%
STOP_LOSS_PCT: float = 0.003       # 0.3%
TAKE_PROFIT_PCT: float = 0.006     # 0.6%

# ==================== PARÁMETROS TÉCNICOS ====================
ORDER_BOOK_DEPTH: int = 20
ORDER_BOOK_IMBALANCE_THRESHOLD: float = 0.65

EMA_FAST_PERIOD: int = 9
EMA_SLOW_PERIOD: int = 21
ATR_PERIOD: int = 14

ATR_MIN_MULTIPLIER: float = 0.8
ATR_MAX_MULTIPLIER: float = 3.0

# Timeframes
TIMEFRAMES: list = ["1m", "5m", "15m"]
CANDLES_TO_FETCH: int = 100
MAIN_TIMEFRAME: str = "5m"

# Tiempos del bot
LOOP_INTERVAL_SECONDS: int = 30
API_RATE_LIMIT_SLEEP: float = 0.5

# Archivos
LOG_LEVEL: str = "INFO"


# ==================== FUNCIONES DE VALIDACIÓN ====================
def validate_config() -> bool:
    if not BINANCE_TESTNET_API_KEY or not BINANCE_TESTNET_SECRET:
        print("❌ ERROR: Faltan las API Keys en el archivo .env")
        print("   Ve a https://testnet.binancefuture.com y genera tus keys")
        return False
    
    print("✅ Configuración cargada correctamente (Modo Testnet)")
    return True


def print_config_summary():
    """Muestra resumen de configuración"""
    print("\n" + "="*60)
    print("🚀 CONFIGURACIÓN DEL BOT - BTC/USDT Futures")
    print("="*60)
    print(f"📍 Modo:          TESTNET (Paper Trading)")
    print(f"💱 Par:           {SYMBOL}")
    print(f"⚡ Apalancamiento: {LEVERAGE}x")
    print(f"💰 Riesgo por trade: {RISK_PER_TRADE*100:.1f}%")
    print(f"🎯 Stop Loss:     {STOP_LOSS_PCT*100:.1f}% | Take Profit: {TAKE_PROFIT_PCT*100:.1f}%")
    print(f"📊 Umbral Order Book: {ORDER_BOOK_IMBALANCE_THRESHOLD*100:.0f}%")
    print("="*60 + "\n")
