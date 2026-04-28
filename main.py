# Versión Mejorada con mejor visualización - Abril 2026
"""
main.py — Bot de prueba mejorado
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("main")


def main():
    print("\n" + "="*75)
    print("🤖 TRADING BOT CLAUDE - Versión Mejorada para Pruebas")
    print("="*75)

    if not validate_config():
        print("❌ Error en la configuración")
        sys.exit(1)

    print_config_summary()

    # Inicialización
    connector = ExchangeConnector()
    if not connector.connect():
        print("❌ Falló la conexión con Binance Testnet")
        sys.exit(1)

    data_hub = DataHub(connector.get_exchange())
    strategy = Strategy()

    print("🚀 Bot iniciado correctamente. Comenzando análisis...\n")

    cycle = 0

    try:
        while True:
            cycle += 1
            print(f"\n{'─'*75}")
            print(f"CICLO #{cycle}  —  {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'─'*75}")

            # Obtener datos
            candles = data_hub.get_all_candles()
            order_book = data_hub.get_order_book()

            if not candles:
                print("⚠️ No se pudieron obtener velas. Esperando...")
                time.sleep(config.LOOP_INTERVAL_SECONDS)
                continue

            # Analizar estrategia
            signal = strategy.analyze(candles, order_book)

            # Mostrar contexto del mercado
            data_hub.print_market_context()

            # Mostrar señal
            if signal["valid"]:
                print(f"\n🎯 ¡SEÑAL VÁLIDA DETECTADA!")
                print(f"   Dirección : {signal['direction']}")
                print(f"   Precio    : {signal['entry_price']:,.2f} USDT")
                print(f"   Razón     : {signal['reason']}")
            else:
                print(f"\n⏸️  HOLD - {signal['reason']}")

            print(f"\n⏳ Esperando {config.LOOP_INTERVAL_SECONDS} segundos para el siguiente ciclo...")
            time.sleep(config.LOOP_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n\n⏹️  Bot detenido manualmente por ti.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
    finally:
        print("\n👋 Prueba finalizada.")


if __name__ == "__main__":
    main()
