from __future__ import annotations

ALGORITHM_INFO = {
    "id": "btcusdt_basic",
    "name": "BTCUSDT Basic Micro Scalper",
    "pair": "BTCUSDT",
    "mode": "DRY-RUN",
    "status": "Draft",
    "description": "IF price tick down -> BUY, then TP/SL -> SELL in DRY-RUN.",
}


class BTCUSDTBasicAlgorithm:
    def __init__(self, profile: dict, trade_engine, log_cb) -> None:
        self.profile = profile
        self.trade_engine = trade_engine
        self.log_cb = log_cb
        self.prev_mid = None

    def on_price_update(self, data: dict) -> None:
        mid = float(data.get("last", 0.0))
        if mid <= 0:
            return
        conditions = self.profile.get("conditions", {})
        ticks = float(conditions.get("entry", {}).get("ticks", 1))
        tp = float(conditions.get("exit", {}).get("profit_percent", 0.05))
        sl = float(conditions.get("stop", {}).get("loss_percent", 0.05))
        amount = float(self.profile.get("trade_amount_usdt", 20))

        pos = self.trade_engine.position
        if not pos and self.prev_mid is not None and mid <= (self.prev_mid - ticks):
            result = self.trade_engine.buy_market("BTCUSDT", amount, mid)
            self.log_cb(f"Decision BUY: {result['reason']}")
        elif pos:
            pnl_percent = ((mid - pos["entry_price"]) / pos["entry_price"]) * 100
            pos["unrealized_pnl"] = pnl_percent
            if pnl_percent >= tp:
                result = self.trade_engine.close_position("BTCUSDT", mid)
                self.log_cb(f"Decision TAKE-PROFIT SELL: {result['reason']}")
            elif pnl_percent <= -sl:
                result = self.trade_engine.close_position("BTCUSDT", mid)
                self.log_cb(f"Decision STOP-LOSS SELL: {result['reason']}")

        self.prev_mid = mid
