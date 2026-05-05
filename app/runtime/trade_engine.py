from __future__ import annotations

from datetime import datetime, timezone
import json

from app.core.config import load_json_safe, save_json
from app.risk.risk_guard import validate_order
from app.storage.paths import TRADES_PATH


class TradeEngine:
    def __init__(self) -> None:
        self.position = None

    def buy_market(self, symbol: str, usdt_amount: float, price: float) -> dict:
        qty = usdt_amount / price if price > 0 else 0
        check = validate_order(symbol, "BUY", qty, price, "DRY-RUN")
        if not check["ok"]:
            return check
        self.position = {
            "symbol": symbol,
            "qty": qty,
            "entry_price": price,
            "entry_time": datetime.now(timezone.utc).isoformat(),
            "side": "LONG",
            "unrealized_pnl": 0.0,
        }
        self._record("BUY", symbol, qty, price)
        return {"ok": True, "reason": "BUY executed in DRY-RUN."}

    def sell_market(self, symbol: str, quantity: float, price: float) -> dict:
        check = validate_order(symbol, "SELL", quantity, price, "DRY-RUN")
        if not check["ok"]:
            return check
        self._record("SELL", symbol, quantity, price)
        self.position = None
        return {"ok": True, "reason": "SELL executed in DRY-RUN."}

    def close_position(self, symbol: str, price: float) -> dict:
        if not self.position:
            return {"ok": False, "reason": "No open position."}
        return self.sell_market(symbol, self.position["qty"], price)

    def _record(self, side: str, symbol: str, qty: float, price: float) -> None:
        payload = load_json_safe(TRADES_PATH, {"trades": [], "last_trade": None})
        trade = {
            "time": datetime.now(timezone.utc).isoformat(),
            "side": side,
            "symbol": symbol,
            "qty": qty,
            "price": price,
            "mode": "DRY-RUN",
        }
        payload["trades"].append(trade)
        payload["last_trade"] = trade
        save_json(TRADES_PATH, payload)
