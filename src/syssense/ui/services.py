"""Tela de serviços systemd do SysSense."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
import html

from gi.repository import Gtk


RefreshCallback = Callable[[Gtk.Button], None]


@dataclass
class ServicesRefs:
    """Referências da aba de serviços usadas pela janela principal."""

    page: Gtk.Widget
    refresh_button: Gtk.Button
    status_label: Gtk.Label
    services_box: Gtk.Box


def build_services_tab(on_refresh_services: RefreshCallback) -> ServicesRefs:
    """Cria a aba de Serviços."""
    page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    page.set_margin_start(12)
    page.set_margin_end(12)
    page.set_margin_top(12)
    page.set_margin_bottom(12)

    controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    refresh_button = Gtk.Button(label="Atualizar")
    refresh_button.connect("clicked", on_refresh_services)
    controls.append(refresh_button)

    status_label = Gtk.Label(label="Atualizado sob demanda")
    status_label.set_halign(Gtk.Align.START)
    status_label.get_style_context().add_class("status-pill")
    controls.append(status_label)
    page.append(controls)

    scrolled = Gtk.ScrolledWindow()
    services_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    scrolled.set_child(services_box)
    scrolled.set_hexpand(True)
    scrolled.set_vexpand(True)
    page.append(scrolled)

    return ServicesRefs(
        page=page,
        refresh_button=refresh_button,
        status_label=status_label,
        services_box=services_box,
    )


def update_services_tab(
    services_box: Gtk.Box,
    services: dict[str, Any],
    logs: dict[str, Any],
):
    """Atualiza Serviços."""
    _clear_box(services_box)

    failed_count = services.get("count", 0)
    service_error = services.get("error")
    logs_error = logs.get("error")

    if service_error:
        state_label = Gtk.Label()
        state_label.set_markup("<b>Indisponível</b>")
        state_label.set_halign(Gtk.Align.START)
        services_box.append(state_label)
        error_label = Gtk.Label(label=f"Serviços indisponíveis: {service_error}")
        error_label.set_wrap(True)
        error_label.set_halign(Gtk.Align.START)
        error_label.get_style_context().add_class("alert-medium")
        services_box.append(error_label)

    if failed_count == 0 and not service_error:
        state_label = Gtk.Label()
        state_label.set_markup("<b>Tudo certo</b>")
        state_label.set_halign(Gtk.Align.START)
        services_box.append(state_label)
        label = Gtk.Label(label="Nenhum serviço systemd com falha foi encontrado.")
        label.get_style_context().add_class("subtitle-text")
        label.set_halign(Gtk.Align.START)
        services_box.append(label)
    else:
        title = Gtk.Label()
        title.set_markup(f"<b>Falhas detectadas</b> • {failed_count} serviço(s)")
        title.set_halign(Gtk.Align.START)
        if failed_count:
            services_box.append(title)

        for service in services.get("failed_services", []):
            service_label = Gtk.Label()
            name = html.escape(service.get("name", "Serviço desconhecido"))
            state = html.escape(service.get("state", "estado desconhecido"))
            service_label.set_markup(f"<b>{name}</b> [{state}]")
            service_label.set_halign(Gtk.Align.START)
            services_box.append(service_label)

    logs_title = Gtk.Label()
    logs_title.set_markup("<b>Logs Recentes</b>")
    logs_title.set_halign(Gtk.Align.START)
    logs_title.set_margin_top(16)
    services_box.append(logs_title)

    log_lines = logs.get("logs", [])[-20:]
    if logs_error:
        log_error_label = Gtk.Label(label=f"Logs indisponíveis: {logs_error}")
        log_error_label.set_wrap(True)
        log_error_label.set_halign(Gtk.Align.START)
        log_error_label.get_style_context().add_class("alert-medium")
        services_box.append(log_error_label)
    elif not log_lines:
        empty_logs_label = Gtk.Label(label="Nenhum log recente retornado.")
        empty_logs_label.set_halign(Gtk.Align.START)
        empty_logs_label.get_style_context().add_class("subtitle-text")
        services_box.append(empty_logs_label)

    for log_line in log_lines:
        log_label = Gtk.Label(label=log_line.strip())
        log_label.set_wrap(True)
        log_label.set_halign(Gtk.Align.START)
        log_label.get_style_context().add_class("subtitle-text")
        services_box.append(log_label)


def _clear_box(box: Gtk.Box):
    """Remove todos os filhos de um Gtk.Box no GTK 4."""
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()
