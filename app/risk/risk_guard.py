from __future__ import annotations

from app.core.config import load_config


def validate_order(symbol: str, side: str, quantity: float, price: float, mode: str) -> dict:
    config = load_config()
    trading = config.get("trading", {})

    if trading.get("emergency_stop", False):
        return {"ok": False, "reason": "Emergency stop is enabled."}
    if mode != "DRY-RUN":
        return {"ok": False, "reason": "LIVE mode is forbidden. DRY-RUN only."}
    if quantity <= 0:
        return {"ok": False, "reason": "Quantity must be > 0."}
    if price <= 0:
        return {"ok": False, "reason": "Price must be > 0."}
    notional = quantity * price
    if notional > float(trading.get("max_trade_usdt", 20)):
        return {"ok": False, "reason": "Order exceeds max_trade_usdt limit."}
    if not symbol or side not in {"BUY", "SELL"}:
        return {"ok": False, "reason": "Invalid symbol or side."}
    return {"ok": True, "reason": "OK"}
