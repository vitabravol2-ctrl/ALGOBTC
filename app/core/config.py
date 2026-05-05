from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from app.storage.paths import CONFIG_PATH, ALGORITHMS_PATH, ensure_directories

DEFAULT_CONFIG: dict[str, Any] = {
    "binance": {
        "api_key": "",
        "api_secret": "",
        "use_testnet": False,
    },
    "app": {
        "default_pair": "BTCUSDT",
    },
}

DEFAULT_ALGORITHMS: list[dict[str, Any]] = [
    {
        "id": "btcusdt_basic",
        "name": "BTCUSDT Basic Micro Scalper",
        "pair": "BTCUSDT",
        "mode": "DRY-RUN",
        "status": "Draft",
        "description": "First BTCUSDT IF-THEN micro scalping algorithm",
    }
]


def _write_json(path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


def bootstrap_files() -> None:
    ensure_directories()
    if not CONFIG_PATH.exists():
        _write_json(CONFIG_PATH, deepcopy(DEFAULT_CONFIG))
    if not ALGORITHMS_PATH.exists():
        _write_json(ALGORITHMS_PATH, deepcopy(DEFAULT_ALGORITHMS))


def load_config() -> dict[str, Any]:
    bootstrap_files()
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = json.load(file)

    merged = deepcopy(DEFAULT_CONFIG)
    merged["binance"].update(config.get("binance", {}))
    merged["app"].update(config.get("app", {}))
    return merged


def save_keys(api_key: str, api_secret: str) -> None:
    config = load_config()
    config["binance"]["api_key"] = api_key.strip()
    config["binance"]["api_secret"] = api_secret.strip()
    _write_json(CONFIG_PATH, config)


def load_algorithms() -> list[dict[str, Any]]:
    bootstrap_files()
    with ALGORITHMS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)
