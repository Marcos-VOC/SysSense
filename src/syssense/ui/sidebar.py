"""Construção da barra lateral do SysSense."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from gi.repository import Gtk, Pango


NavCallback = Callable[[Gtk.Button, int], None]
ButtonCallback = Callable[[Gtk.Button], None]


@dataclass
class SidebarRefs:
    """Referências da sidebar que a janela principal precisa atualizar."""

    container: Gtk.Box
    nav_buttons: list[Gtk.Button]
    nav_labels: list[Gtk.Label]
    nav_icons: list[Gtk.Image]
    alert_indicator: Gtk.Button
    preferences_button: Gtk.Button
    footer: Gtk.Label


NAV_ITEMS = (
    ("Visão Geral", "view-grid-symbolic", 0),
    ("Processos", "view-list-symbolic", 1),
    ("Disco", "drive-harddisk-symbolic", 2),
    ("Serviços", "applications-system-symbolic", 3),
)


def build_sidebar(
    on_nav_clicked: NavCallback,
    on_alert_clicked: ButtonCallback,
    on_preferences_clicked: ButtonCallback,
) -> SidebarRefs:
    """Cria a sidebar e devolve as referências necessárias para atualização."""
    sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    sidebar.get_style_context().add_class("sidebar")
    sidebar.set_size_request(132, -1)
    sidebar.set_hexpand(False)
    sidebar.set_halign(Gtk.Align.START)

    nav_buttons: list[Gtk.Button] = []
    nav_labels: list[Gtk.Label] = []
    nav_icons: list[Gtk.Image] = []

    for title, icon_name, page in NAV_ITEMS:
        button = _create_nav_button(title, icon_name, page, on_nav_clicked, nav_labels, nav_icons)
        sidebar.append(button)
        nav_buttons.append(button)

    spacer = Gtk.Box()
    spacer.set_vexpand(True)
    sidebar.append(spacer)

    alert_indicator = _create_alert_indicator(on_alert_clicked)
    preferences_button = _create_preferences_button(on_preferences_clicked)
    status_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    status_row.append(alert_indicator)
    status_row.append(preferences_button)
    sidebar.append(status_row)

    footer = Gtk.Label(label="Auto refresh: 2.5s")
    footer.set_wrap(True)
    footer.set_halign(Gtk.Align.START)
    footer.get_style_context().add_class("brand-subtitle")
    sidebar.append(footer)

    return SidebarRefs(
        container=sidebar,
        nav_buttons=nav_buttons,
        nav_labels=nav_labels,
        nav_icons=nav_icons,
        alert_indicator=alert_indicator,
        preferences_button=preferences_button,
        footer=footer,
    )


def _create_nav_button(
    title: str,
    icon_name: str,
    page: int,
    on_nav_clicked: NavCallback,
    nav_labels: list[Gtk.Label],
    nav_icons: list[Gtk.Image],
) -> Gtk.Button:
    """Cria um botão de navegação da sidebar."""
    button = Gtk.Button()
    button.get_style_context().add_class("nav-item")
    button.set_has_frame(False)
    button.set_hexpand(True)
    button.set_tooltip_text(title)
    button.connect("clicked", on_nav_clicked, page)

    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    row.set_halign(Gtk.Align.START)
    icon = Gtk.Image.new_from_icon_name(icon_name)
    icon.set_pixel_size(16)
    icon.get_style_context().add_class("nav-icon")
    nav_icons.append(icon)

    label = Gtk.Label(label=title)
    label.set_halign(Gtk.Align.START)
    label.set_xalign(0)
    label.set_hexpand(True)
    label.set_width_chars(8)
    label.set_max_width_chars(10)
    label.set_ellipsize(Pango.EllipsizeMode.END)
    nav_labels.append(label)

    row.append(icon)
    row.append(label)
    button.set_child(row)
    return button


def _create_alert_indicator(on_alert_clicked: ButtonCallback) -> Gtk.Button:
    """Cria indicador automático de alertas na sidebar."""
    button = Gtk.Button.new_from_icon_name("emblem-ok-symbolic")
    button.set_has_frame(False)
    button.set_has_tooltip(False)
    button.get_style_context().add_class("alert-indicator")
    button.get_style_context().add_class("alert-indicator-ok")
    button.connect("clicked", on_alert_clicked)
    return button


def _create_preferences_button(on_preferences_clicked: ButtonCallback) -> Gtk.Button:
    """Cria botão de preferências mínimas."""
    button = Gtk.Button.new_from_icon_name("emblem-system-symbolic")
    button.set_has_frame(False)
    button.get_style_context().add_class("prefs-button")
    button.connect("clicked", on_preferences_clicked)
    return button
