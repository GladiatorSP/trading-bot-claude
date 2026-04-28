# Versión con control de posiciones - Abril 2026
"""
main.py — Bot con control básico de posiciones
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
    print("\n" + "="*80)
    print("🤖 TRADING BOT CLAUDE - Control de Posiciones")
    print("="*80)

    if not validate_config():
        sys.exit(1)

    print_config_summary()

    connector = ExchangeConnector()
    if not connector.connect():
        print("❌ Falló la conexión")
        sys.exit(1)

    data_hub = DataHub(connector.get_exchange())
    strategy = Strategy()

    print("🚀 Bot iniciado. Monitoreando mercado...\n")

    cycle = 0
    in_position = False

    try:
        while True:
            cycle += 1
            print(f"\n{'─'*80}")
            print(f"CICLO #{cycle} — {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'─'*80}")

            # Verificar si ya tenemos posición abierta
            positions = connector.get_open_positions()
            if positions:
                in_position = True
                pos = positions[0]
                print(f"📍 POSICIÓN ABIERTA: {pos['side'].upper()} | Tamaño: {pos['size']:.6f} BTC | PnL: {pos.get('unrealized_pnl', 0):+.2f} USDT")
            else:
                in_position = False

            # Obtener datos y señal
            candles = data_hub.get_all_candles()
            order_book = data_hub.get_order_book()

            if not candles:
                print("⚠️ No se obtuvieron velas")
                time.sleep(config.LOOP_INTERVAL_SECONDS)
                continue

            signal = strategy.analyze(candles, order_book)

            data_hub.print_market_context()

            if in_position:
                print("⏸️  Ya tienes una posición abierta → No se abren nuevas")
            elif signal["valid"]:
                print(f"\n🎯 ¡SEÑAL VÁLIDA! → {signal['direction']}")
                print(f"   Precio : {signal['entry_price']:,.2f} USDT")
                print(f"   Razón  : {signal['reason']}")
                print("\n⚠️  En esta versión aún NO abrimos posiciones automáticamente.")
            else:
                print(f"⏸️  HOLD → {signal['reason']}")

            print(f"⏳ Esperando {config.LOOP_INTERVAL_SECONDS} segundos...")
            time.sleep(config.LOOP_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n\n⏹️ Bot detenido manualmente.")
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
