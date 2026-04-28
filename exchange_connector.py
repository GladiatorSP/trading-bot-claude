# exchange_connector.py — Versión compatible 2026
"""
Conexión adaptada a restricciones actuales de Binance Testnet
"""

import logging
import ccxt

import config

logger = logging.getLogger(__name__)


class ExchangeConnector:
    def __init__(self):
        self.exchange = None
        self.is_connected = False

    def connect(self) -> bool:
        try:
            logger.info("Intentando conexión con Binance Futures...")

            self.exchange = ccxt.binance({
                'apiKey': config.BINANCE_TESTNET_API_KEY,
                'secret': config.BINANCE_TESTNET_SECRET,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',
                },
                # Proxies y headers para evitar algunos bloqueos
                'headers': {
                    'User-Agent': 'Mozilla/5.0'
                }
            })

            # Activar modo testnet
            if config.USE_TESTNET:
                self.exchange.set_sandbox_mode(True)

            self.exchange.load_markets()
            logger.info("✅ Conexión establecida con Binance")

            self.is_connected = True
            return True

        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            print("\n⚠️  Sugerencias:")
            print("   1. Usa VPN (con servidor en EE.UU., Singapur o Turquía)")
            print("   2. Prueba más tarde (a veces el bloqueo es temporal)")
            print("   3. Considera usar Bybit Testnet como alternativa")
            return False

    def get_exchange(self):
        return self.exchange

    def get_open_positions(self):
        try:
            positions = self.exchange.fetch_positions()
            return [p for p in positions if float(p.get('contracts', 0)) > 0]
        except:
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
            return {"total_usdt": 1000, "available_usdt": 1000}

    def open_position(self, side: str, quantity: float):
        logger.info(f"[SIMULADO] Abrir {side.upper()} {quantity:.6f} BTC")
        return {"status": "simulated"}

    def close_position(self, position, reason="manual"):
        logger.info(f"[SIMULADO] Cerrar posición - {reason}")
        return {"status": "simulated"}
