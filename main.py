# Versión Ultra-Simple para primera prueba - Abril 2026
"""
main.py — Versión mínima para probar el bot
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

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("main")


def main():
    print("\n" + "="*65)
    print("🤖 TRADING BOT CLAUDE - Versión Ultra Simple (Prueba)")
    print("="*65)
    print(f"Par: {config.SYMBOL} | Modo: TESTNET")
    print("="*65 + "\n")

    # Validar configuración
    if not validate_config():
        print("❌ Error en configuración. Revisa el archivo .env")
        sys.exit(1)

    print_config_summary()

    # Inicializar componentes
    try:
        connector = ExchangeConnector()
        if not connector.connect():
            print("❌ No se pudo conectar con Binance Testnet")
            sys.exit(1)

        exchange = connector.get_exchange()
        data_hub = DataHub(exchange)
        strategy = Strategy()

        logger.info("✅ Bot inicializado correctamente\n")
        print("🚀 Iniciando prueba del bot... (presiona Ctrl+C para detener)\n")

    except Exception as e:
        logger.error(f"Error al inicializar: {e}")
        sys.exit(1)

    cycle = 0

    try:
        while True:
            cycle += 1
            print(f"\n{'─'*60}")
            print(f"CICLO #{cycle}  |  {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'─'*60}")

            try:
                # Obtener datos
                candles = data_hub.get_all_candles()
                order_book = data_hub.get_order_book()

                if not candles:
                    print("⚠️ No se obtuvieron velas. Esperando...")
                    time.sleep(config.LOOP_INTERVAL_SECONDS)
                    continue

                # Analizar estrategia
                signal = strategy.analyze(candles, order_book)

                # Mostrar contexto cada 3 ciclos
                if cycle % 3 == 0:
                    data_hub.print_market_context()

                # Mostrar señal
                if signal["valid"]:
                    print(f"🎯 SEÑAL VÁLIDA → {signal['direction']}")
                    print(f"   Razón: {signal['reason']}")
                    print(f"   Precio: {signal['entry_price']:,.2f} USDT")
                else:
                    print(f"⏸️  HOLD → {signal['reason']}")

            except Exception as e:
                logger.error(f"Error en ciclo {cycle}: {e}")

            print(f"⏳ Esperando {config.LOOP_INTERVAL_SECONDS} segundos...")
            time.sleep(config.LOOP_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n\n⏹️ Bot detenido manualmente.")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
    finally:
        print("\n👋 Prueba finalizada.")


if __name__ == "__main__":
    main()