# exchange_connector.py — Bybit Testnet (versión estable 2026)
"""
Conexión con Bybit Testnet
"""

import logging
import ccxt

import config

logger = logging.getLogger(__name__)


class ExchangeConnector:
    def __init__(self):
        self.exchange = None
        self.is_connected = False
        self.symbol = "BTC/USDT:USDT"

    def connect(self) -> bool:
        try:
            logger.info("Conectando a Bybit Testnet...")

            self.exchange = ccxt.bybit({
                'apiKey': config.BINANCE_TESTNET_API_KEY,
                'secret': config.BINANCE_TESTNET_SECRET,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',
                }
            })

            # Activar Testnet
            self.exchange.set_sandbox_mode(True)

            self.exchange.load_markets()
            logger.info("✅ Conexión exitosa con Bybit Testnet")

            self.is_connected = True
            return True

        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False

    def get_exchange(self):
        return self.exchange

    def get_open_positions(self):
        try:
            positions = self.exchange.fetch_positions([self.symbol])
            return [p for p in positions if float(p.get('contracts', 0) or 0) > 0]
        except Exception as e:
            logger.warning(f"No se pudieron obtener posiciones: {e}")
            return []

    def get_balance(self):
        try:
            balance = self.exchange.fetch_balance()
            usdt = balance.get('USDT', {})
            return {
                "total_usdt": float(usdt.get('total', 0)),
                "available_usdt": float(usdt.get('free', 0))
            }
        except:
            return {"total_usdt": 10000, "available_usdt": 10000}

    def open_position(self, side: str, quantity: float):
        logger.info(f"[SIMULADO] Abrir {side.upper()} {quantity:.6f} BTC")
        return {"status": "simulated"}

    def close_position(self, position, reason="manual"):
        logger.info(f"[SIMULADO] Cerrar posición - {reason}")
        return {"status": "simulated"}
