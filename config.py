# Versión mejorada por Grok - Abril 2026
"""
============================================================
config.py — Configuración central del bot de trading
============================================================
Este archivo contiene TODOS los parámetros del bot.
No modifiques nada aquí si no estás seguro.
Las credenciales van en el archivo .env
"""

import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# ============================================================
# CREDENCIALES BINANCE TESTNET
# ============================================================

BINANCE_TESTNET_API_KEY: str = os.getenv("BINANCE_TESTNET_API_KEY", "")
BINANCE_TESTNET_SECRET: str   = os.getenv("BINANCE_TESTNET_SECRET", "")

# ============================================================
# MODO DE OPERACIÓN
# ============================================================

USE_TESTNET: bool = True                    # ← Cambia a False solo cuando estés listo para real

# ============================================================
# CONFIGURACIÓN DEL MERCADO
# ============================================================

SYMBOL: str = "BTC/USDT:USDT"
LEVERAGE: int = 5
MARGIN_TYPE: str = "isolated"

# ============================================================
# GESTIÓN DE RIESGO (Muy conservadora)
# ============================================================

RISK_PER_TRADE: float = 0.005      # 0.5% del balance por operación
STOP_LOSS_PCT: float = 0.003       # 0.3%
TAKE_PROFIT_PCT: float = 0.006     # 0.6% → Ratio 1:2
MAX_DAILY_DRAWDOWN: float = 0.05   # 5% máximo de pérdida diaria
MAX_OPEN_POSITIONS: int = 1
MAX_POSITION_SIZE_PCT: float = 0.20

# ============================================================
# INDICADORES Y PARÁMETROS
# ============================================================

ORDER_BOOK_DEPTH: int = 20
ORDER_BOOK_IMBALANCE_THRESHOLD: float = 0.55   # 55%

EMA_FAST_PERIOD: int = 9
EMA_SLOW_PERIOD: int = 21
ATR_PERIOD: int = 14
ATR_MIN_MULTIPLIER: float = 0.3
ATR_MAX_MULTIPLIER: float = 4.0

# Timeframes
MAIN_TIMEFRAME: str = "5m"
CONFIRMATION_TIMEFRAME: str = "15m"
CANDLES_TO_FETCH: int = 100

# Tiempos
LOOP_INTERVAL_SECONDS: int = 30
ERROR_WAIT_SECONDS: int = 30
API_RATE_LIMIT_SLEEP: float = 0.5

# Archivos
JOURNAL_FILE: str = "trades_journal.jsonl"
LOG_FILE: str = "bot.log"
LOG_LEVEL: str = "INFO"

# CoinGlass (opcional)
COINGLASS_API_KEY: str = os.getenv("COINGLASS_API_KEY", "")
USE_COINGLASS: bool = False   # Lo dejamos en False por ahora (API limitada gratis)

# ============================================================
# FUNCIÓN DE VALIDACIÓN
# ============================================================

def validate_config() -> bool:
    """Verifica que la configuración sea válida"""
    if not BINANCE_TESTNET_API_KEY or not BINANCE_TESTNET_SECRET:
        print("❌ ERROR: Faltan las API Keys de Binance Testnet en el archivo .env")
        print("   → Crea el archivo .env usando .env.example como guía")
        return False
    
    print("✅ Configuración cargada correctamente (Modo Testnet)")
    return True


def print_config_summary():
    """Muestra resumen de la configuración"""
    print("\n" + "="*60)
    print("🚀 CONFIGURACIÓN DEL BOT - BTC/USDT Futures")
    print("="*60)
    print(f"📍 Modo:          {'TESTNET (Paper Trading)' if USE_TESTNET else 'REAL'}")
    print(f"💱 Par:           {SYMBOL}")
    print(f"⚡ Apalancamiento: {LEVERAGE}x")
    print(f"💰 Riesgo por trade: {RISK_PER_TRADE*100:.1f}%")
    print(f"🎯 Stop Loss:     {STOP_LOSS_PCT*100:.1f}% | Take Profit: {TAKE_PROFIT_PCT*100:.1f}%")
    print(f"📊 Umbral Order Book: {ORDER_BOOK_IMBALANCE_THRESHOLD*100:.0f}%")
    print("="*60 + "\n")