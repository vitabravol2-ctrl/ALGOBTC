from __future__ import annotations

DEFAULT_PROFILE = {
    "id": "btcusdt_basic",
    "name": "BTCUSDT Basic Micro Scalper",
    "pair": "BTCUSDT",
    "mode": "DRY-RUN",
    "enabled": False,
    "trade_amount_usdt": 20,
    "conditions": {
        "entry": {"type": "price_tick_down", "ticks": 1},
        "exit": {"type": "take_profit_percent", "profit_percent": 0.05},
        "stop": {"type": "stop_loss_percent", "loss_percent": 0.05},
    },
}
