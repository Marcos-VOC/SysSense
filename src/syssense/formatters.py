"""Formatadores de texto usados pela interface do SysSense."""

from __future__ import annotations

from typing import Any


def format_refresh_option(seconds: float) -> str:
    """Formata opção de intervalo de atualização."""
    return f"{int(seconds)}s" if float(seconds).is_integer() else f"{seconds:.1f}s"


def format_disk_size(value: int | float) -> str:
    """Formata bytes de disco sem esconder partições pequenas."""
    value = float(value or 0)
    gib = value / (1024**3)
    if gib >= 1:
        return f"{gib:.1f}G"
    mib = value / (1024**2)
    return f"{mib:.0f}M"


def format_rate(bytes_per_second: float) -> str:
    """Formata uma taxa de rede em unidades legíveis."""
    value = max(float(bytes_per_second or 0), 0)
    if value >= 1024**2:
        return f"{value / (1024**2):.1f} MB/s"
    if value >= 1024:
        return f"{value / 1024:.0f} KB/s"
    return f"{value:.0f} B/s"


def format_total_transfer(value: int | float) -> str:
    """Formata total acumulado de rede."""
    value = float(value or 0)
    if value >= 1024**3:
        return f"{value / (1024**3):.2f} GB"
    if value >= 1024**2:
        return f"{value / (1024**2):.1f} MB"
    return f"{value / 1024:.0f} KB"


def format_network_tooltip(bytes_recv: int | float, bytes_sent: int | float) -> str:
    """Formata tooltip com acumulado de rede."""
    return (
        f"Acumulado recebido: {format_total_transfer(bytes_recv)}\n"
        f"Acumulado enviado: {format_total_transfer(bytes_sent)}"
    )


def format_network_rates(down_rate: float, up_rate: float) -> str:
    """Formata velocidades atuais de download e upload."""
    return f"↓ {format_rate(down_rate)} | ↑ {format_rate(up_rate)}"


def format_load_average(load: dict[str, Any]) -> str:
    """Formata carga média do sistema."""
    return (
        f"1min: {load.get('1min', 0):.2f} | "
        f"5min: {load.get('5min', 0):.2f} | "
        f"15min: {load.get('15min', 0):.2f}"
    )


def format_uptime(uptime: dict[str, Any]) -> str:
    """Formata o tempo ligado mesmo quando só há segundos disponíveis."""
    if uptime.get("uptime_formatted"):
        return uptime["uptime_formatted"]
    seconds = uptime.get("uptime_seconds")
    if seconds is None:
        return "N/A"
    days = int(seconds) // 86400
    hours = (int(seconds) % 86400) // 3600
    minutes = (int(seconds) % 3600) // 60
    return f"{days}d {hours}h {minutes}m"
