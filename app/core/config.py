from __future__ import annotations

from copy import deepcopy
import json
import logging
from typing import Any

from app.algorithms.algorithm_profile import DEFAULT_PROFILE
from app.storage.paths import ALGORITHMS_PATH, CONFIG_PATH, TRADES_PATH, ensure_directories

DEFAULT_CONFIG: dict[str, Any] = {
    "binance": {"api_key": "", "api_secret": "", "use_testnet": False},
    "app": {"default_pair": "BTCUSDT"},
    "trading": {"mode": "DRY-RUN", "max_trade_usdt": 20, "emergency_stop": False},
}


def save_json(path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


def load_json_safe(path, default_payload: Any) -> Any:
    ensure_directories()
    if not path.exists() or path.stat().st_size == 0:
        save_json(path, default_payload)
        return deepcopy(default_payload)
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:  # noqa: BLE001
        backup = path.with_suffix(path.suffix + ".bak")
        path.replace(backup)
        logging.error("Corrupted file moved to backup: %s", backup)
        save_json(path, default_payload)
        return deepcopy(default_payload)


def bootstrap_files() -> None:
    ensure_directories()
    load_json_safe(CONFIG_PATH, deepcopy(DEFAULT_CONFIG))
    load_json_safe(ALGORITHMS_PATH, [deepcopy(DEFAULT_PROFILE)])
    load_json_safe(TRADES_PATH, {"trades": [], "last_trade": None})


def load_config() -> dict[str, Any]:
    config = load_json_safe(CONFIG_PATH, deepcopy(DEFAULT_CONFIG))
    merged = deepcopy(DEFAULT_CONFIG)
    merged["binance"].update(config.get("binance", {}))
    merged["app"].update(config.get("app", {}))
    merged["trading"].update(config.get("trading", {}))
    if merged["trading"].get("mode") != "DRY-RUN":
        merged["trading"]["mode"] = "DRY-RUN"
        logging.error("LIVE mode requested in config, forced to DRY-RUN")
        save_json(CONFIG_PATH, merged)
    return merged


def save_keys(api_key: str, api_secret: str) -> None:
    config = load_config()
    config["binance"]["api_key"] = api_key.strip()
    config["binance"]["api_secret"] = api_secret.strip()
    save_json(CONFIG_PATH, config)


def load_algorithms() -> list[dict[str, Any]]:
    return load_json_safe(ALGORITHMS_PATH, [deepcopy(DEFAULT_PROFILE)])


def save_algorithms(items: list[dict[str, Any]]) -> None:
    save_json(ALGORITHMS_PATH, items)
