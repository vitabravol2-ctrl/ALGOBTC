from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
import threading
from typing import Callable

import websockets


class PriceWebSocket:
    def __init__(self, symbol: str, on_update: Callable[[dict], None], on_error: Callable[[str], None]) -> None:
        self.symbol = symbol.lower()
        self.on_update = on_update
        self.on_error = on_error
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive() and not self._stop_event.is_set())

    def _run_loop(self) -> None:
        asyncio.run(self._listen())

    async def _listen(self) -> None:
        url = f"wss://stream.binance.com:9443/ws/{self.symbol}@bookTicker"
        while not self._stop_event.is_set():
            try:
                async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
                    while not self._stop_event.is_set():
                        raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        msg = json.loads(raw)
                        bid = float(msg.get("b", 0.0))
                        ask = float(msg.get("a", 0.0))
                        mid = (bid + ask) / 2 if bid and ask else 0.0
                        spread = ask - bid if bid and ask else 0.0
                        self.on_update(
                            {
                                "bid": bid,
                                "ask": ask,
                                "last": mid,
                                "spread": spread,
                                "time": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S"),
                                "source": "WebSocket",
                            }
                        )
            except Exception as exc:  # noqa: BLE001
                self.on_error(f"WebSocket error: {exc}")
                await asyncio.sleep(2)
