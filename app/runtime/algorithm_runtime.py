from __future__ import annotations

from app.algorithms.btcusdt_basic import BTCUSDTBasicAlgorithm
from app.runtime.trade_engine import TradeEngine


class AlgorithmRuntime:
    def __init__(self, log_cb) -> None:
        self.status = "STOPPED"
        self.active = None
        self.log_cb = log_cb
        self.trade_engine = TradeEngine()

    def start_algorithm(self, profile: dict) -> None:
        self.active = BTCUSDTBasicAlgorithm(profile, self.trade_engine, self.log_cb)
        self.status = "RUNNING"
        self.log_cb("Algorithm started in DRY-RUN")

    def stop_algorithm(self, algo_id: str) -> None:
        if self.active and self.active.profile.get("id") == algo_id:
            self.active = None
        self.status = "STOPPED"
        self.log_cb("Algorithm stopped")

    def on_price_update(self, price_data: dict) -> None:
        if self.status != "RUNNING" or not self.active:
            return
        try:
            self.active.on_price_update(price_data)
        except Exception as exc:  # noqa: BLE001
            self.status = "ERROR"
            self.log_cb(f"Algorithm error: {exc}")
