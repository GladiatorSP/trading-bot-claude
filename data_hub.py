# Versión simplificada y mejorada por Grok - Abril 2026
"""
data_hub.py — Centro de datos del bot (versión simple y estable)
Obtiene: velas, order book, precio actual y resumen del mercado.
"""

import time
import logging
import pandas as pd
from datetime import datetime

import config

logger = logging.getLogger(__name__)


class DataHub:
    """Clase responsable de obtener todos los datos de mercado desde Binance."""

    def __init__(self, exchange):
        self.exchange = exchange
        self.symbol = config.SYMBOL
        logger.info(f"DataHub iniciado para {self.symbol}")

    # ====================== VELAS (KLINES) ======================
    def get_candles(self, timeframe: str = "5m", limit: int = None) -> pd.DataFrame | None:
        """Obtiene velas OHLCV"""
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

            logger.debug(f"✅ {len(df)} velas [{timeframe}] obtenidas | Último precio: {df['close'].iloc[-1]:,.2f}")
            time.sleep(config.API_RATE_LIMIT_SLEEP)
            return df

        except Exception as e:
            logger.error(f"❌ Error al obtener velas {timeframe}: {e}")
            return None

    # ====================== ORDER BOOK ======================
    def get_order_book(self, depth: int = None) -> dict | None:
        """Obtiene el libro de órdenes y calcula el imbalance"""
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

            best_bid = bids[0][0]
            best_ask = asks[0][0]
            spread = best_ask - best_bid

            return {
                "imbalance": imbalance,
                "imbalance_pct": imbalance * 100,
                "bid_volume": bid_vol,
                "ask_volume": ask_vol,
                "best_bid": best_bid,
                "best_ask": best_ask,
                "spread": spread,
                "spread_pct": (spread / ((best_bid + best_ask)/2)) * 100 if best_bid else 0,
                "top_bids": bids[:5],
                "top_asks": asks[:5]
            }

        except Exception as e:
            logger.error(f"❌ Error al obtener order book: {e}")
            return None

    # ====================== PRECIO ACTUAL ======================
    def get_ticker(self) -> dict | None:
        """Obtiene precio actual"""
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            return {
                "price": float(ticker.get("last", 0)),
                "bid": float(ticker.get("bid", 0)),
                "ask": float(ticker.get("ask", 0)),
                "pct_change_24h": float(ticker.get("percentage", 0))
            }
        except Exception as e:
            logger.error(f"❌ Error al obtener ticker: {e}")
            return None

    # ====================== CONTEXTO COMPLETO (Para Claude) ======================
    def get_market_context(self) -> dict:
        """Genera un resumen claro del mercado para análisis humano o Claude"""
        context = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": self.symbol,
            "ticker": None,
            "order_book": None,
            "indicators": {},
            "summary": ""
        }

        # Precio actual
        context["ticker"] = self.get_ticker()

        # Order Book
        context["order_book"] = self.get_order_book()

        # Velas + EMAs + ATR (solo en 5m por simplicidad)
        df = self.get_candles("5m")
        if df is not None and len(df) >= config.EMA_SLOW_PERIOD + 10:
            ema_fast = df["close"].ewm(span=config.EMA_FAST_PERIOD, adjust=False).mean().iloc[-1]
            ema_slow = df["close"].ewm(span=config.EMA_SLOW_PERIOD, adjust=False).mean().iloc[-1]
            last_price = df["close"].iloc[-1]

            # ATR simple
            tr = pd.concat([
                df["high"] - df["low"],
                (df["high"] - df["close"].shift(1)).abs(),
                (df["low"] - df["close"].shift(1)).abs()
            ], axis=1).max(axis=1)
            atr = tr.rolling(config.ATR_PERIOD).mean().iloc[-1]

            context["indicators"]["5m"] = {
                "price": float(last_price),
                "ema_fast": float(ema_fast),
                "ema_slow": float(ema_slow),
                "atr": float(atr),
                "trend": "ALCISTA" if ema_fast > ema_slow else "BAJISTA"
            }

        # Construir resumen legible
        lines = [f"\n📊 CONTEXTO DE MERCADO — {self.symbol} | {context['timestamp']}"]
        lines.append("=" * 60)

        if context["ticker"]:
            t = context["ticker"]
            lines.append(f"💰 Precio actual:     {t['price']:,.2f} USDT  ({t['pct_change_24h']:+.2f}% 24h)")

        if context["order_book"]:
            ob = context["order_book"]
            lines.append(f"📖 Order Book Imbalance: {ob['imbalance_pct']:.1f}% {'🟢 Comprador' if ob['imbalance'] > 0.5 else '🔴 Vendedor'}")

        if context["indicators"].get("5m"):
            ind = context["indicators"]["5m"]
            lines.append(f"📈 EMA {config.EMA_FAST_PERIOD}/{config.EMA_SLOW_PERIOD}:   {ind['ema_fast']:.2f} / {ind['ema_slow']:.2f} → {ind['trend']}")
            lines.append(f"🌡️  ATR:               {ind['atr']:.2f} USDT")

        lines.append("=" * 60)
        context["summary"] = "\n".join(lines)

        return context

    def print_market_context(self):
        """Imprime el contexto en pantalla"""
        ctx = self.get_market_context()
        print(ctx["summary"])
        return ctx