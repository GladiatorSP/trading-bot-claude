# Versión corregida para Colab - Abril 2026
"""
data_hub.py — Centro de datos (corregido)
"""

import time
import logging
import pandas as pd
from datetime import datetime

import config

logger = logging.getLogger(__name__)


class DataHub:
    """Obtiene datos de mercado desde Binance"""

    def __init__(self, exchange):
        self.exchange = exchange
        self.symbol = config.SYMBOL
        logger.info(f"DataHub iniciado para {self.symbol}")

    def get_candles(self, timeframe: str = "5m", limit: int = None) -> pd.DataFrame | None:
        """Obtiene velas para un timeframe específico"""
        if limit is None:
            limit = config.CANDLES_TO_FETCH

        try:
            raw = self.exchange.fetch_ohlcv(
                symbol=self.symbol,
                timeframe=timeframe,
                limit=limit
            )

            if not raw:
                logger.warning(f"No se recibieron velas para {timeframe}")
                return None

            df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = pd.to_numeric(df[col])

            logger.debug(f"✅ {len(df)} velas [{timeframe}] obtenidas")
            time.sleep(config.API_RATE_LIMIT_SLEEP)
            return df

        except Exception as e:
            logger.error(f"❌ Error velas {timeframe}: {e}")
            return None

    def get_all_candles(self) -> dict:
        """Obtiene velas para todos los timeframes configurados"""
        candles = {}
        for tf in config.TIMEFRAMES:
            df = self.get_candles(tf)
            if df is not None:
                candles[tf] = df
        return candles

    def get_order_book(self, depth: int = None) -> dict | None:
        """Obtiene order book y calcula imbalance"""
        if depth is None:
            depth = config.ORDER_BOOK_DEPTH

        try:
            ob = self.exchange.fetch_order_book(symbol=self.symbol, limit=depth)
            bids = ob.get("bids", [])
            asks = ob.get("asks", [])

            if not bids or not asks:
                return None

            bid_vol = sum(qty for _, qty in bids)
            ask_vol = sum(qty for _, qty in asks)
            total_vol = bid_vol + ask_vol or 1

            imbalance = bid_vol / total_vol

            return {
                "imbalance": imbalance,
                "imbalance_pct": imbalance * 100,
                "best_bid": bids[0][0],
                "best_ask": asks[0][0]
            }

        except Exception as e:
            logger.error(f"❌ Error order book: {e}")
            return None

    def get_ticker(self):
        """Obtiene precio actual"""
        try:
            t = self.exchange.fetch_ticker(self.symbol)
            return {
                "price": float(t.get("last", 0)),
                "pct_change_24h": float(t.get("percentage", 0))
            }
        except:
            return None

    def print_market_context(self):
        """Imprime resumen simple del mercado"""
        ticker = self.get_ticker()
        ob = self.get_order_book()
        candles = self.get_candles("5m")

        print(f"\n📊 CONTEXTO DE MERCADO - {self.symbol}")
        if ticker:
            print(f"💰 Precio: {ticker['price']:,.2f} USDT ({ticker['pct_change_24h']:+.2f}%)")

        if ob:
            print(f"📖 Imbalance: {ob['imbalance_pct']:.1f}% {'🟢 Comprador' if ob['imbalance'] > 0.5 else '🔴 Vendedor'}")

        if candles is not None and len(candles) > 0:
            price = candles["close"].iloc[-1]
            print(f"📈 Último precio vela 5m: {price:,.2f} USDT")

        print("-" * 50)