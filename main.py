# Versión simplificada por Grok - Abril 2026
"""
main.py — Bot de Trading Simple para Testnet
Versión básica para empezar a probar desde el móvil.
"""

import time
import logging
import sys
from datetime import datetime

import config
from config import validate_config, print_config_summary
from exchange_connector import ExchangeConnector
from data_hub import DataHub
from strategy import Strategy
from risk_manager import RiskManager
from journal import TradeJournal

# Configurar logging simple
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("main")


def main():
    print("\n" + "="*60)
    print("🤖 TRADING BOT CLAUDE - Versión Simplificada")
    print("="*60)
    print(f"Par: {config.SYMBOL} | Modo: {'TESTNET' if config.USE_TESTNET else 'REAL'}")
    print("="*60 + "\n")

    # 1. Validar configuración
    if not validate_config():
        print("❌ Error en la configuración. Revisa el archivo .env")
        sys.exit(1)

    print_config_summary()

    # 2. Inicializar componentes
    try:
        connector = ExchangeConnector()
        if not connector.connect():
            print("❌ No se pudo conectar con Binance Testnet")
            sys.exit(1)

        exchange = connector.get_exchange()
        data_hub = DataHub(exchange)
        strategy = Strategy()
        risk_manager = RiskManager()
        journal = TradeJournal()

        logger.info("✅ Todos los componentes inicializados correctamente\n")

    except Exception as e:
        logger.error(f"Error durante la inicialización: {e}")
        sys.exit(1)

    # 3. Bucle principal simple
    cycle = 0
    print("🚀 Bot iniciado. Presiona Ctrl+C para detener.\n")

    try:
        while True:
            cycle += 1
            print(f"\n{'─' * 50}")
            print(f"CICLO #{cycle} — {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'─' * 50}")

            try:
                # Obtener datos del mercado
                candles = data_hub.get_all_candles()
                order_book = data_hub.get_order_book()

                if not candles:
                    print("⚠️  No se pudieron obtener velas. Esperando...")
                    time.sleep(config.LOOP_INTERVAL_SECONDS)
                    continue

                # Analizar estrategia
                signal = strategy.analyze(candles, order_book)

                # Mostrar contexto del mercado
                if cycle % 3 == 0:   # Cada 3 ciclos mostramos resumen
                    data_hub.print_market_context()

                print(f"📊 Señal: {signal['direction']} | {signal['reason']}")

                # Si hay señal válida → evaluamos riesgo y mostramos
                if signal["valid"]:
                    print(f"🎯 ¡SEÑAL VÁLIDA! → {signal['direction']}")
                    print(f"   Razón: {signal['reason']}")
                    print(f"   Precio sugerido: {signal['entry_price']:,.2f} USDT")

                    # Aquí más adelante abriremos posición (por ahora solo mostramos)
                    journal.log_signal(signal)

                else:
                    print("⏸️  Sin señal válida esta vez.")

            except Exception as e:
                logger.error(f"Error en ciclo {cycle}: {e}")

            print(f"⏳ Esperando {config.LOOP_INTERVAL_SECONDS} segundos...")
            time.sleep(config.LOOP_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n\n⏹️  Bot detenido manualmente por el usuario.")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
    finally:
        print("\n👋 Bot finalizado.")


if __name__ == "__main__":
    main()