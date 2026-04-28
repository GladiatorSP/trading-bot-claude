# Versión simplificada y mejorada por Grok - Abril 2026
"""
strategy.py — Estrategia de Trading (Versión Simple)

Combina 3 filtros:
1. Order Book Imbalance
2. Cruce / Tendencia de EMAs (5m)
3. Volatilidad (ATR)

Solo genera señal cuando los 3 filtros están alineados.
"""

import logging
import pandas as pd

import config

logger = logging.getLogger(__name__)


class Strategy:
    """Estrategia simple para day trading / scalping en BTC/USDT"""

    def __init__(self):
        self.ema_fast = config.EMA_FAST_PERIOD
        self.ema_slow = config.EMA_SLOW_PERIOD
        self.atr_period = config.ATR_PERIOD
        self.ob_threshold = config.ORDER_BOOK_IMBALANCE_THRESHOLD

        logger.info(f"Estrategia cargada → EMA {self.ema_fast}/{self.ema_slow} | OB umbral: {self.ob_threshold*100:.0f}%")

    def analyze(self, candles: dict, order_book: dict) -> dict:
        """
        Analiza el mercado y retorna una señal.

        Retorna un diccionario con:
            direction: "LONG", "SHORT" o "HOLD"
            valid: True/False
            reason: explicación
            entry_price: precio sugerido
        """
        signal = {
            "direction": "HOLD",
            "valid": False,
            "reason": "Sin datos suficientes",
            "entry_price": 0.0,
            "strength": 0.0
        }

        # Verificar que tengamos velas del timeframe principal
        if not candles or config.MAIN_TIMEFRAME not in candles:
            signal["reason"] = "Sin velas disponibles"
            return signal

        df = candles[config.MAIN_TIMEFRAME]
        if df is None or len(df) < config.EMA_SLOW_PERIOD + 10:
            signal["reason"] = f"Pocas velas en {config.MAIN_TIMEFRAME}"
            return signal

        # Precio actual
        current_price = float(df["close"].iloc[-1])
        signal["entry_price"] = current_price

        # =============================================
        # 1. ANÁLISIS ORDER BOOK
        # =============================================
        ob_signal = "neutral"
        ob_strength = 0.0

        if order_book and "imbalance" in order_book:
            imb = order_book["imbalance"]
            if imb >= self.ob_threshold:
                ob_signal = "long"
                ob_strength = (imb - 0.5) * 2
            elif imb <= (1 - self.ob_threshold):
                ob_signal = "short"
                ob_strength = ((1 - imb) - 0.5) * 2

        # =============================================
        # 2. ANÁLISIS EMAs
        # =============================================
        ema_signal = "neutral"
        try:
            ema_fast = df["close"].ewm(span=self.ema_fast, adjust=False).mean().iloc[-1]
            ema_slow = df["close"].ewm(span=self.ema_slow, adjust=False).mean().iloc[-1]

            prev_ema_fast = df["close"].ewm(span=self.ema_fast, adjust=False).mean().iloc[-2]
            prev_ema_slow = df["close"].ewm(span=self.ema_slow, adjust=False).mean().iloc[-2]

            # Cruce fresco
            bullish_cross = (prev_ema_fast <= prev_ema_slow) and (ema_fast > ema_slow)
            bearish_cross = (prev_ema_fast >= prev_ema_slow) and (ema_fast < ema_slow)

            if bullish_cross:
                ema_signal = "long"
            elif bearish_cross:
                ema_signal = "short"
            elif ema_fast > ema_slow:
                ema_signal = "long_trend"
            else:
                ema_signal = "short_trend"

        except Exception as e:
            logger.error(f"Error calculando EMAs: {e}")

        # =============================================
        # 3. VOLATILIDAD (ATR)
        # =============================================
        volatility_ok = False
        try:
            hl = df["high"] - df["low"]
            hpc = (df["high"] - df["close"].shift(1)).abs()
            lpc = (df["low"] - df["close"].shift(1)).abs()
            tr = pd.concat([hl, hpc, lpc], axis=1).max(axis=1)
            atr = tr.rolling(window=self.atr_period).mean().iloc[-1]
            atr_pct = (atr / current_price * 100) if current_price > 0 else 0

            min_atr = current_price * config.STOP_LOSS_PCT * config.ATR_MIN_MULTIPLIER
            max_atr = current_price * config.STOP_LOSS_PCT * config.ATR_MAX_MULTIPLIER

            volatility_ok = min_atr <= atr <= max_atr

        except Exception as e:
            logger.error(f"Error calculando ATR: {e}")

        # =============================================
        # COMBINAR SEÑALES
        # =============================================
        if volatility_ok:
            if ob_signal == "long" and ema_signal in ["long", "long_trend"]:
                signal["direction"] = "LONG"
                signal["valid"] = True
                signal["strength"] = 0.7
                signal["reason"] = f"✅ LONG | OB alcista + EMA alcista | Volatilidad OK"

            elif ob_signal == "short" and ema_signal in ["short", "short_trend"]:
                signal["direction"] = "SHORT"
                signal["valid"] = True
                signal["strength"] = 0.7
                signal["reason"] = f"✅ SHORT | OB bajista + EMA bajista | Volatilidad OK"

            else:
                signal["reason"] = f"HOLD - Señales no alineadas (OB={ob_signal}, EMA={ema_signal})"
        else:
            signal["reason"] = "HOLD - Volatilidad fuera de rango"

        if signal["valid"]:
            logger.info(f"SEÑAL GENERADA → {signal['direction']} | {signal['reason']}")

        return signal