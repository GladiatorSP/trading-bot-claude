# Versión corregida para Testnet 2026
"""
exchange_connector.py — Conexión con Binance (adaptado a cambios del Testnet)
"""

import logging
import ccxt

import config

logger = logging.getLogger(__name__)


class ExchangeConnector:
    def __init__(self):
        self.exchange = None
        self.is_connected = False
        self.symbol = "BTC/USDT"   # Usamos esta forma más estable

    def connect(self) -> bool:
        try:
            logger.info("Conectando a Binance Futures Testnet...")

            self.exchange = ccxt.binance({
                'apiKey': config.BINANCE_TESTNET_API_KEY,
                'secret': config.BINANCE_TESTNET_SECRET,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',
                }
            })

            if config.USE_TESTNET:
                self.exchange.set_sandbox_mode(True)

            self.exchange.load_markets()
            logger.info("✅ Conexión exitosa con Binance Testnet")

            self.is_connected = True
            return True

        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False

    def get_exchange(self):
        return self.exchange

    def get_balance(self):
        if not self.is_connected:
            return None
        try:
            balance = self.exchange.fetch_balance()
            usdt = balance.get('USDT', {})
            return {
                "total_usdt": float(usdt.get('total', 0)),
                "available_usdt": float(usdt.get('free', 0)),
            }
        except:
            return {"total_usdt": 0, "available_usdt": 0}

    def get_open_positions(self):
        """Método seguro que no rompe el bot"""
        try:
            # Intentamos obtener posiciones de forma más compatible
            positions = self.exchange.fetch_positions([f"{config.SYMBOL.split(':')[0]}"])
            open_pos = []
            for pos in positions:
                contracts = float(pos.get('contracts', 0) or 0)
                if contracts > 0:
                    open_pos.append({
                        "side": pos.get('side', 'unknown'),
                        "size": contracts,
                        "entry_price": float(pos.get('entryPrice', 0)),
                        "unrealized_pnl": float(pos.get('unrealizedPnl', 0)),
                    })
            return open_pos
        except Exception as e:
            logger.warning(f"No se pudieron obtener posiciones: {e}")
            return []   # Devolvemos lista vacía en vez de romper

    def open_position(self, side: str, quantity: float):
        logger.info(f"[SIMULADO] Abrir {side.upper()} de {quantity:.6f} BTC")
        return {"status": "simulated"}

    def close_position(self, position, reason="manual"):
        logger.info(f"[SIMULADO] Cerrar posición - Razón: {reason}")
        return {"status": "simulated"}


def disconnect(self):
        self.is_connected = False
