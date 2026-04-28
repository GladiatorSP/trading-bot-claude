# Versión corregida y más permisiva - Abril 2026
"""
strategy.py — Estrategia simplificada
"""

import logging
import pandas as pd

import config

logger = logging.getLogger(__name__)


class Strategy:
    def __init__(self):
        self.ema_fast = config.EMA_FAST_PERIOD
        self.ema_slow = config.EMA_SLOW_PERIOD
        self.atr_period = config.ATR_PERIOD
        self.ob_threshold = config.ORDER_BOOK_IMBALANCE_THRESHOLD

        logger.info(f"Estrategia cargada → EMA {self.ema_fast}/{self.ema_slow} | OB umbral: {self.ob_threshold*100:.0f}%")

    def analyze(self, candles: dict, order_book: dict) -> dict:
        signal = {
            "direction": "HOLD",
            "valid": False,
            "reason": "Sin datos suficientes",
            "entry_price": 0.0,
            "strength": 0.0
        }

        if not candles or config.MAIN_TIMEFRAME not in candles:
            signal["reason"] = "Sin velas disponibles"
            return signal

        df = candles[config.MAIN_TIMEFRAME]
        if df is None or len(df) < config.EMA_SLOW_PERIOD + 10:
            signal["reason"] = f"Pocas velas en {config.MAIN_TIMEFRAME}"
            return signal

        current_price = float(df["close"].iloc[-1])
        signal["entry_price"] = current_price

        # 1. Order Book
        ob_signal = "neutral"
        if order_book and "imbalance" in order_book:
            imb = order_book["imbalance"]
            if imb >= self.ob_threshold:
                ob_signal = "long"
            elif imb <= (1 - self.ob_threshold):
                ob_signal = "short"

        # 2. EMAs
        ema_signal = "neutral"
        try:
            ema_fast = df["close"].ewm(span=self.ema_fast, adjust=False).mean().iloc[-1]
            ema_slow = df["close"].ewm(span=self.ema_slow, adjust=False).mean().iloc[-1]

            if ema_fast > ema_slow:
                ema_signal = "long"
            else:
                ema_signal = "short"
        except:
            pass

        # 3. Volatilidad (más permisiva para pruebas)
        volatility_ok = True
        volatility_reason = "OK"
        try:
            hl = df["high"] - df["low"]
            hpc = (df["high"] - df["close"].shift(1)).abs()
            lpc = (df["low"] - df["close"].shift(1)).abs()
            tr = pd.concat([hl, hpc, lpc], axis=1).max(axis=1)
            atr = tr.rolling(window=self.atr_period).mean().iloc[-1]
            atr_pct = (atr / current_price * 100) if current_price > 0 else 0

            # Mucho más permisivo para Testnet
            if atr_pct < 0.05:
                volatility_ok = False
                volatility_reason = f"Volatilidad muy baja ({atr_pct:.3f}%)"
            elif atr_pct > 5.0:
                volatility_ok = False
                volatility_reason = f"Volatilidad muy alta ({atr_pct:.3f}%)"
        except Exception as e:
            logger.error(f"Error ATR: {e}")

        # Decisión final
        if volatility_ok and ob_signal == "long" and ema_signal == "long":
            signal["direction"] = "LONG"
            signal["valid"] = True
            signal["reason"] = f"LONG | OB alcista + EMA alcista | Vol OK"
        elif volatility_ok and ob_signal == "short" and ema_signal == "short":
            signal["direction"] = "SHORT"
            signal["valid"] = True
            signal["reason"] = f"SHORT | OB bajista + EMA bajista | Vol OK"
        else:
            signal["reason"] = f"HOLD → {volatility_reason} | OB={ob_signal} | EMA={ema_signal}"

        if signal["valid"]:
            logger.info(f"SEÑAL VÁLIDA → {signal['direction']}")
        else:
            logger.info(f"{signal['reason']}")

        return signal