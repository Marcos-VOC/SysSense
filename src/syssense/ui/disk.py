"""Tela de disco do SysSense."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from gi.repository import Gtk


@dataclass
class DiskRefs:
    """Referências da aba de disco usadas pela janela principal."""

    page: Gtk.Widget
    partitions_box: Gtk.Box


def build_disk_tab() -> DiskRefs:
    """Cria a aba de Disco."""
    scrolled = Gtk.ScrolledWindow()

    content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    content.set_margin_start(12)
    content.set_margin_end(12)
    content.set_margin_top(12)
    content.set_margin_bottom(12)

    partitions_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    content.append(partitions_box)

    scrolled.set_child(content)
    return DiskRefs(page=scrolled, partitions_box=partitions_box)


def update_disk_tab(partitions_box: Gtk.Box, disk_data: dict[str, Any]):
    """Atualiza cards de partições montadas."""
    _clear_box(partitions_box)

    for part in disk_data.get("partitions", []):
        partitions_box.append(_create_partition_card(part))


def _create_partition_card(part: dict[str, Any]) -> Gtk.Widget:
    """Cria card de uma partição."""
    card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    card.get_style_context().add_class("card-custom")

    name_label = Gtk.Label()
    name_label.set_markup(f"<b>{part['device']}</b> • {part['mountpoint']}")
    name_label.set_halign(Gtk.Align.START)
    card.append(name_label)

    total_gb = part["total"] / (1024**3)
    used_gb = part["used"] / (1024**3)
    free_gb = part["free"] / (1024**3)
    pct = part["percent"]

    info_label = Gtk.Label()
    info_label.set_text(
        f"Usado: {used_gb:.1f} GB / {total_gb:.1f} GB ({pct:.1f}%) | "
        f"Livre: {free_gb:.1f} GB | {part.get('fstype', 'fs')}"
    )
    info_label.set_halign(Gtk.Align.START)
    info_label.get_style_context().add_class("subtitle-text")
    card.append(info_label)

    progressbar = Gtk.ProgressBar()
    progressbar.set_fraction(pct / 100)
    card.append(progressbar)

    if pct > 70:
        alert_label = Gtk.Label(label="⚠️ Espaço em disco limitado")
        alert_label.get_style_context().add_class("alert-medium")
        alert_label.set_halign(Gtk.Align.START)
        card.append(alert_label)

    return card


def _clear_box(box: Gtk.Box):
    """Remove todos os filhos de um Gtk.Box no GTK 4."""
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()
