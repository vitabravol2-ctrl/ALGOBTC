from __future__ import annotations

import httpx

from app.core.config import load_config


class BinanceClient:
    def __init__(self) -> None:
        self.config = load_config()
        self.base_url = "https://api.binance.com"

    @property
    def api_key(self) -> str:
        return self.config["binance"].get("api_key", "")

    @property
    def api_secret(self) -> str:
        return self.config["binance"].get("api_secret", "")

    def keys_present(self) -> bool:
        return bool(self.api_key and self.api_secret)

    def test_connection(self) -> tuple[bool, str]:
        if not self.keys_present():
            return False, "API keys are missing. Save API Key and API Secret first."

        try:
            response = httpx.get(f"{self.base_url}/api/v3/time", timeout=10.0)
            response.raise_for_status()
            return True, "Binance connection OK (server time endpoint)."
        except Exception as exc:  # noqa: BLE001
            return False, f"Binance connection failed: {exc}"
