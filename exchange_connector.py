# Versión simplificada por Grok - Abril 2026
"""
exchange_connector.py — Conexión con Binance Futures (Testnet)
Versión simple y estable para principiantes.
"""

import logging
import ccxt

import config

logger = logging.getLogger(__name__)


class ExchangeConnector:
    """Maneja la conexión y operaciones básicas con Binance Futures."""

    def __init__(self):
        self.exchange = None
        self.is_connected = False
        self.symbol = config.SYMBOL

    def connect(self) -> bool:
        """Conecta con Binance Testnet"""
        try:
            logger.info(f"Conectando a Binance Futures {'TESTNET' if config.USE_TESTNET else 'REAL'}...")

            if not config.BINANCE_TESTNET_API_KEY or not config.BINANCE_TESTNET_SECRET:
                logger.error("❌ Faltan API Keys en el archivo .env")
                return False

            # Crear conexión con ccxt
            self.exchange = ccxt.binanceusdm({
                'apiKey': config.BINANCE_TESTNET_API_KEY,
                'secret': config.BINANCE_TESTNET_SECRET,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',
                }
            })

            # Activar modo Testnet
            if config.USE_TESTNET:
                self.exchange.set_sandbox_mode(True)
                logger.info("✅ Modo Testnet activado (dinero ficticio)")

            # Probar conexión
            self.exchange.load_markets()
            logger.info("✅ Conexión exitosa con Binance Testnet")

            # Configurar apalancamiento y margen
            self._setup_leverage_and_margin()

            self.is_connected = True
            return True

        except Exception as e:
            logger.error(f"❌ Error al conectar: {e}")
            return False

    def _setup_leverage_and_margin(self):
        """Configura apalancamiento y tipo de margen"""
        try:
            # ccxt suele necesitar el símbolo sin ":USDT" para algunas operaciones
            symbol_for_setup = "BTC/USDT"

            self.exchange.set_leverage(config.LEVERAGE, symbol_for_setup)
            logger.info(f"⚡ Leverage configurado: {config.LEVERAGE}x")

            self.exchange.set_margin_mode(config.MARGIN_TYPE, symbol_for_setup)
            logger.info(f"📌 Margen configurado: {config.MARGIN_TYPE}")

        except Exception as e:
            logger.warning(f"No se pudo configurar leverage/margen automáticamente: {e}")

    def get_exchange(self):
        """Devuelve el objeto exchange para que lo use DataHub"""
        return self.exchange

    def get_balance(self):
        """Obtiene balance en USDT"""
        if not self.is_connected:
            return None

        try:
            balance = self.exchange.fetch_balance()
            usdt = balance.get('USDT', {})

            return {
                "total_usdt": float(usdt.get('total', 0)),
                "available_usdt": float(usdt.get('free', 0)),
                "unrealized_pnl": float(balance.get('info', {}).get('totalUnrealizedProfit', 0))
            }
        except Exception as e:
            logger.error(f"Error obteniendo balance: {e}")
            return None

    def get_open_positions(self):
        """Obtiene posiciones abiertas"""
        if not self.is_connected:
            return []

        try:
            positions = self.exchange.fetch_positions([self.symbol])
            open_pos = []

            for pos in positions:
                contracts = float(pos.get('contracts', 0) or 0)
                if contracts > 0:
                    open_pos.append({
                        "symbol": pos.get('symbol'),
                        "side": pos.get('side'),           # "long" o "short"
                        "size": contracts,
                        "entry_price": float(pos.get('entryPrice', 0)),
                        "unrealized_pnl": float(pos.get('unrealizedPnl', 0)),
                    })
            return open_pos
        except Exception as e:
            logger.error(f"Error obteniendo posiciones: {e}")
            return []

    # Por ahora solo mostramos lo que haríamos (no ejecutamos órdenes reales)
    def open_position(self, side: str, quantity: float):
        """Simulación de apertura de posición (por ahora)"""
        logger.info(f"[SIMULACIÓN] Se abriría posición {side.upper()} de {quantity:.6f} BTC")
        return {"status": "simulated", "side": side, "amount": quantity}

    def close_position(self, position, reason="manual"):
        """Simulación de cierre de posición"""
        logger.info(f"[SIMULACIÓN] Se cerraría posición {position.get('side')} - Razón: {reason}")
        return {"status": "simulated", "reason": reason}

    def disconnect(self):
        self.is_connected = False
        logger.info("Desconectado del exchange")