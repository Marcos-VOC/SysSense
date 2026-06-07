"""Configuração persistente do SysSense."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any


APP_CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "syssense"
CONFIG_FILE = APP_CONFIG_DIR / "config.json"

REFRESH_OPTIONS_SECONDS = (1.0, 2.5, 5.0, 10.0)

DEFAULT_CONFIG: dict[str, Any] = {
    "refresh_interval": 2.5,
    "critical_toasts": True,
    "show_speedtest": True,
    "visible_cards": {
        "cpu": True,
        "memory": True,
        "storage": True,
        "temperature": True,
        "network": True,
        "load": True,
        "uptime": True,
        "internet": True,
    },
}


def _coerce_refresh_interval(value: Any) -> float:
    """Retorna uma opção válida de intervalo."""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return DEFAULT_CONFIG["refresh_interval"]

    return numeric if numeric in REFRESH_OPTIONS_SECONDS else DEFAULT_CONFIG["refresh_interval"]


def normalize_config(raw_config: dict[str, Any] | None) -> dict[str, Any]:
    """Mescla configuração do usuário com defaults e valida valores."""
    config = deepcopy(DEFAULT_CONFIG)
    if not isinstance(raw_config, dict):
        return config

    config["refresh_interval"] = _coerce_refresh_interval(raw_config.get("refresh_interval"))
    config["critical_toasts"] = bool(raw_config.get("critical_toasts", config["critical_toasts"]))
    config["show_speedtest"] = bool(raw_config.get("show_speedtest", config["show_speedtest"]))

    raw_cards = raw_config.get("visible_cards", {})
    if isinstance(raw_cards, dict):
        for key in config["visible_cards"]:
            if key in raw_cards:
                config["visible_cards"][key] = bool(raw_cards[key])

    return config


def load_config(path: Path = CONFIG_FILE) -> dict[str, Any]:
    """Carrega configuração do usuário ou retorna defaults seguros."""
    try:
        with path.open("r", encoding="utf-8") as file:
            raw_config = json.load(file)
    except (OSError, json.JSONDecodeError):
        return deepcopy(DEFAULT_CONFIG)

    return normalize_config(raw_config)


def save_config(config: dict[str, Any], path: Path = CONFIG_FILE) -> dict[str, Any]:
    """Valida e salva configuração do usuário."""
    normalized = normalize_config(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(normalized, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return normalized
