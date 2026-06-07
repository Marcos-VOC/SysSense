"""Painel interno de preferências do SysSense."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from gi.repository import Gtk

from syssense import config, formatters


RefreshCallback = Callable[[Gtk.ComboBoxText], None]
SwitchCallback = Callable[[Gtk.Switch, object, str], None]


CARD_LABELS = {
    "cpu": "CPU",
    "memory": "Memória",
    "storage": "Armazenamento",
    "temperature": "Temperatura",
    "network": "Rede",
    "load": "Carga",
    "uptime": "Tempo ligado",
    "internet": "Internet",
}


@dataclass
class PreferencesRefs:
    """Referências que a janela principal precisa controlar."""

    revealer: Gtk.Revealer
    refresh_combo: Gtk.ComboBoxText
    card_switches: dict[str, Gtk.Switch]


def build_preferences_panel(
    user_config: dict[str, Any],
    start_margin: int,
    on_refresh_changed: RefreshCallback,
    on_bool_changed: SwitchCallback,
    on_card_visibility_changed: SwitchCallback,
) -> PreferencesRefs:
    """Cria painel interno de preferências."""
    revealer = Gtk.Revealer()
    revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
    revealer.set_transition_duration(150)
    revealer.set_halign(Gtk.Align.START)
    revealer.set_valign(Gtk.Align.END)
    revealer.set_margin_start(start_margin)
    revealer.set_margin_bottom(18)
    revealer.set_can_target(False)

    panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    panel.get_style_context().add_class("prefs-popover")
    panel.get_style_context().add_class("prefs-overlay-panel")

    title = Gtk.Label(label="Preferências")
    title.set_halign(Gtk.Align.START)
    title.get_style_context().add_class("alert-guide-title")
    panel.append(title)

    refresh_combo = _create_refresh_combo(user_config, on_refresh_changed)
    refresh_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    refresh_row.get_style_context().add_class("prefs-row")
    refresh_label = Gtk.Label(label="Atualização")
    refresh_label.set_halign(Gtk.Align.START)
    refresh_label.set_hexpand(True)
    refresh_row.append(refresh_label)
    refresh_row.append(refresh_combo)
    panel.append(refresh_row)

    toast_switch = Gtk.Switch()
    toast_switch.set_active(user_config["critical_toasts"])
    toast_switch.connect("notify::active", on_bool_changed, "critical_toasts")
    panel.append(_create_switch_row("Toasts críticos", toast_switch))

    cards_title = Gtk.Label(label="Cards da dashboard")
    cards_title.set_halign(Gtk.Align.START)
    cards_title.get_style_context().add_class("alert-guide-subtitle")
    panel.append(cards_title)

    card_switches: dict[str, Gtk.Switch] = {}
    for key, label in CARD_LABELS.items():
        switch = Gtk.Switch()
        switch.set_active(user_config["visible_cards"][key])
        switch.connect("notify::active", on_card_visibility_changed, key)
        card_switches[key] = switch
        panel.append(_create_switch_row(label, switch))

    revealer.set_child(panel)
    return PreferencesRefs(
        revealer=revealer,
        refresh_combo=refresh_combo,
        card_switches=card_switches,
    )


def _create_refresh_combo(
    user_config: dict[str, Any],
    on_refresh_changed: RefreshCallback,
) -> Gtk.ComboBoxText:
    """Cria seletor de intervalo de atualização."""
    combo = Gtk.ComboBoxText()
    for value in config.REFRESH_OPTIONS_SECONDS:
        combo.append_text(formatters.format_refresh_option(value))
    active_index = config.REFRESH_OPTIONS_SECONDS.index(user_config["refresh_interval"])
    combo.set_active(active_index)
    combo.connect("changed", on_refresh_changed)
    return combo


def _create_switch_row(label_text: str, switch: Gtk.Switch) -> Gtk.Widget:
    """Cria linha de preferência com switch."""
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    row.get_style_context().add_class("prefs-row")
    label = Gtk.Label(label=label_text)
    label.set_halign(Gtk.Align.START)
    label.set_hexpand(True)
    row.append(label)
    row.append(switch)
    return row
