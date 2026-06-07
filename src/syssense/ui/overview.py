"""Dashboard principal do SysSense."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from gi.repository import Gtk, Pango


SpeedtestCallback = Callable[[Gtk.Button], None]
DiskSelectionCallback = Callable[[Gtk.Button, str], None]
DiskDrawCallback = Callable[[Gtk.DrawingArea, object, int, int], None]
CardOrderCallback = Callable[[Gtk.Button, str, str], None]
ResetOrderCallback = Callable[[Gtk.Button], None]


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
class OverviewRefs:
    """Referências que a janela principal atualiza durante a coleta."""

    page: Gtk.Widget
    scrolled: Gtk.ScrolledWindow
    flow: Gtk.FlowBox
    card_order_box: Gtk.Box
    cards: list[Gtk.Widget]
    card_widgets: dict[str, Gtk.Widget]
    card_flow_children: dict[str, Gtk.Widget]
    cpu_card: Gtk.Widget
    cpu_label: Gtk.Label
    cpu_progressbar: Gtk.ProgressBar
    cpu_alert_label: Gtk.Revealer
    mem_card: Gtk.Widget
    mem_label: Gtk.Label
    mem_progressbar: Gtk.ProgressBar
    mem_alert_label: Gtk.Revealer
    disk_overview_card: Gtk.Widget
    disk_label: Gtk.Label
    disk_progressbar: Gtk.ProgressBar
    disk_alert_label: Gtk.Revealer
    disk_chart_detail_label: Gtk.Label
    disk_chart: Gtk.DrawingArea
    disk_partition_menu: Gtk.MenuButton
    disk_partition_popover: Gtk.Popover
    disk_partition_options_box: Gtk.Box
    temp_card: Gtk.Widget
    temp_label: Gtk.Label
    net_card: Gtk.Widget
    net_label: Gtk.Label
    load_card: Gtk.Widget
    load_label: Gtk.Label
    uptime_card: Gtk.Widget
    uptime_label: Gtk.Label
    speed_panel: Gtk.Widget
    speed_button: Gtk.Button
    speed_result_label: Gtk.Label


def build_overview_tab(
    card_order: list[str],
    on_speedtest_clicked: SpeedtestCallback,
    on_disk_partition_selected: DiskSelectionCallback,
    on_disk_draw: DiskDrawCallback,
    on_card_order_changed: CardOrderCallback,
    on_card_order_reset: ResetOrderCallback,
) -> OverviewRefs:
    """Cria a aba de Visão Geral e devolve referências dos widgets."""
    page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    page.set_hexpand(True)
    page.set_vexpand(True)

    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
    scrolled.set_hexpand(True)
    scrolled.set_vexpand(True)

    top_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    top_bar.get_style_context().add_class("overview-toolbar")
    top_bar.set_halign(Gtk.Align.FILL)
    spacer = Gtk.Box()
    spacer.set_hexpand(True)
    top_bar.append(spacer)
    order_refs = _create_card_order_menu(card_order, on_card_order_changed, on_card_order_reset)
    top_bar.append(order_refs["button"])

    flow = Gtk.FlowBox()
    flow.get_style_context().add_class("overview-flow")
    flow.set_selection_mode(Gtk.SelectionMode.NONE)
    flow.set_max_children_per_line(3)
    flow.set_min_children_per_line(1)
    flow.set_column_spacing(8)
    flow.set_row_spacing(8)
    flow.set_homogeneous(False)
    flow.set_margin_top(4)
    flow.set_margin_bottom(16)
    flow.set_margin_start(2)
    flow.set_margin_end(2)

    cards: list[Gtk.Widget] = []
    card_widgets: dict[str, Gtk.Widget] = {}
    card_flow_children: dict[str, Gtk.Widget] = {}

    cpu_label = Gtk.Label()
    cpu_progressbar = Gtk.ProgressBar()
    cpu_alert_label = create_inline_alert_label()
    cpu_card = create_metric_card("CPU", cpu_label, cpu_progressbar, "light-card", cpu_alert_label)
    _append_overview_card(flow, cards, card_widgets, card_flow_children, cpu_card, "cpu")

    mem_label = Gtk.Label()
    mem_progressbar = Gtk.ProgressBar()
    mem_alert_label = create_inline_alert_label()
    mem_card = create_metric_card("Memória RAM", mem_label, mem_progressbar, None, mem_alert_label)
    _append_overview_card(flow, cards, card_widgets, card_flow_children, mem_card, "memory")

    disk_label = Gtk.Label()
    disk_progressbar = Gtk.ProgressBar()
    disk_alert_label = create_inline_alert_label()
    disk_refs = _create_disk_overview_card(
        disk_label,
        disk_progressbar,
        disk_alert_label,
        on_disk_partition_selected,
        on_disk_draw,
    )
    _append_overview_card(
        flow,
        cards,
        card_widgets,
        card_flow_children,
        disk_refs["card"],
        "storage",
    )

    temp_label = Gtk.Label()
    temp_card = create_info_card("Temperatura", temp_label)
    _append_overview_card(flow, cards, card_widgets, card_flow_children, temp_card, "temperature")

    net_label = Gtk.Label()
    net_card = create_info_card("Tráfego de Rede", net_label)
    _append_overview_card(flow, cards, card_widgets, card_flow_children, net_card, "network")

    load_label = Gtk.Label()
    load_card = create_info_card("Carga do Sistema", load_label)
    load_card.set_tooltip_text(
        "Carga média do sistema. Compare esses valores com a quantidade de núcleos da CPU."
    )
    _append_overview_card(flow, cards, card_widgets, card_flow_children, load_card, "load")

    uptime_label = Gtk.Label()
    uptime_card = create_info_card("Tempo Ligado", uptime_label, "wide-card")
    _append_overview_card(flow, cards, card_widgets, card_flow_children, uptime_card, "uptime")

    speed_refs = _create_speedtest_card(on_speedtest_clicked)
    _append_overview_card(
        flow,
        cards,
        card_widgets,
        card_flow_children,
        speed_refs["panel"],
        "internet",
    )

    scrolled.set_child(flow)
    page.append(top_bar)
    page.append(scrolled)

    return OverviewRefs(
        page=page,
        scrolled=scrolled,
        flow=flow,
        card_order_box=order_refs["box"],
        cards=cards,
        card_widgets=card_widgets,
        card_flow_children=card_flow_children,
        cpu_card=cpu_card,
        cpu_label=cpu_label,
        cpu_progressbar=cpu_progressbar,
        cpu_alert_label=cpu_alert_label,
        mem_card=mem_card,
        mem_label=mem_label,
        mem_progressbar=mem_progressbar,
        mem_alert_label=mem_alert_label,
        disk_overview_card=disk_refs["card"],
        disk_label=disk_label,
        disk_progressbar=disk_progressbar,
        disk_alert_label=disk_alert_label,
        disk_chart_detail_label=disk_refs["detail_label"],
        disk_chart=disk_refs["chart"],
        disk_partition_menu=disk_refs["menu"],
        disk_partition_popover=disk_refs["popover"],
        disk_partition_options_box=disk_refs["options_box"],
        temp_card=temp_card,
        temp_label=temp_label,
        net_card=net_card,
        net_label=net_label,
        load_card=load_card,
        load_label=load_label,
        uptime_card=uptime_card,
        uptime_label=uptime_label,
        speed_panel=speed_refs["panel"],
        speed_button=speed_refs["button"],
        speed_result_label=speed_refs["result_label"],
    )


def rebuild_card_order_controls(
    box: Gtk.Box,
    card_order: list[str],
    on_card_order_changed: CardOrderCallback,
):
    """Reconstrói controles de ordenação dos cards."""
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()

    total = len(card_order)
    for index, key in enumerate(card_order):
        label = CARD_LABELS.get(key, key)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.get_style_context().add_class("card-order-row")

        text = Gtk.Label(label=label)
        text.set_halign(Gtk.Align.START)
        text.set_hexpand(True)
        row.append(text)

        up_button = Gtk.Button.new_from_icon_name("go-up-symbolic")
        up_button.set_has_frame(False)
        up_button.set_tooltip_text("Mover para cima")
        up_button.set_sensitive(index > 0)
        up_button.get_style_context().add_class("card-order-button")
        up_button.connect("clicked", on_card_order_changed, key, "up")
        row.append(up_button)

        down_button = Gtk.Button.new_from_icon_name("go-down-symbolic")
        down_button.set_has_frame(False)
        down_button.set_tooltip_text("Mover para baixo")
        down_button.set_sensitive(index < total - 1)
        down_button.get_style_context().add_class("card-order-button")
        down_button.connect("clicked", on_card_order_changed, key, "down")
        row.append(down_button)

        box.append(row)


def _create_card_order_menu(
    card_order: list[str],
    on_card_order_changed: CardOrderCallback,
    on_card_order_reset: ResetOrderCallback,
) -> dict[str, Gtk.Widget]:
    """Cria menu discreto de ordenação da dashboard."""
    button = Gtk.MenuButton()
    button.set_has_frame(False)
    button.set_tooltip_text("Organizar cards")
    button.set_property("icon-name", "view-sort-ascending-symbolic")
    button.get_style_context().add_class("overview-order-button")

    popover = Gtk.Popover()
    popover.set_has_arrow(False)
    popover.get_style_context().add_class("overview-order-popover")

    panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    panel.get_style_context().add_class("overview-order-panel")
    title = Gtk.Label(label="Ordem dos cards")
    title.set_halign(Gtk.Align.START)
    title.get_style_context().add_class("alert-guide-title")
    panel.append(title)

    order_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    order_box.get_style_context().add_class("card-order-list")
    panel.append(order_box)
    rebuild_card_order_controls(order_box, card_order, on_card_order_changed)

    reset_button = Gtk.Button(label="Restaurar ordem")
    reset_button.get_style_context().add_class("secondary-action")
    reset_button.connect("clicked", on_card_order_reset)
    panel.append(reset_button)

    popover.set_child(panel)
    button.set_popover(popover)
    return {
        "button": button,
        "box": order_box,
    }


def create_metric_card(
    title: str,
    label: Gtk.Label,
    progress: Gtk.ProgressBar,
    extra_class: str | None = None,
    alert_label: Gtk.Widget | None = None,
) -> Gtk.Widget:
    """Cria card de métrica."""
    card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    card.get_style_context().add_class("card-custom")
    card.get_style_context().add_class("metric-card")
    if extra_class:
        card.get_style_context().add_class(extra_class)
    card.set_size_request(210, 116)

    title_label = Gtk.Label()
    title_label.set_markup(f"<b>{title}</b>")
    title_label.set_halign(Gtk.Align.START)
    card.append(title_label)

    label.set_halign(Gtk.Align.START)
    label.get_style_context().add_class("subtitle-text")
    card.append(label)

    progress.set_hexpand(True)
    card.append(progress)

    if alert_label:
        card.append(alert_label)

    return card


def create_inline_alert_label() -> Gtk.Revealer:
    """Cria um texto curto de alerta para cards."""
    revealer = Gtk.Revealer()
    revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
    revealer.set_transition_duration(160)
    label = Gtk.Label()
    label.set_halign(Gtk.Align.START)
    label.set_xalign(0)
    label.get_style_context().add_class("inline-alert")
    revealer.set_child(label)
    revealer.set_reveal_child(False)
    return revealer


def create_info_card(title: str, label: Gtk.Label, extra_class: str | None = None) -> Gtk.Widget:
    """Cria card de informação."""
    card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    card.get_style_context().add_class("card-custom")
    if extra_class:
        card.get_style_context().add_class(extra_class)
    card.set_size_request(210, 104)

    title_label = Gtk.Label()
    title_label.set_markup(f"<b>{title}</b>")
    title_label.set_halign(Gtk.Align.START)
    card.append(title_label)

    label.set_halign(Gtk.Align.START)
    label.set_wrap(True)
    label.get_style_context().add_class("subtitle-text")
    card.append(label)

    return card


def _append_overview_card(
    flow: Gtk.FlowBox,
    cards: list[Gtk.Widget],
    card_widgets: dict[str, Gtk.Widget],
    card_flow_children: dict[str, Gtk.Widget],
    card: Gtk.Widget,
    key: str,
):
    """Adiciona card à visão geral e guarda referência para responsividade."""
    flow.append(card)
    cards.append(card)
    card_widgets[key] = card
    flow_child = card.get_parent()
    flow_child.syssense_card_key = key
    card_flow_children[key] = flow_child


def _create_disk_overview_card(
    disk_label: Gtk.Label,
    disk_progressbar: Gtk.ProgressBar,
    disk_alert_label: Gtk.Widget,
    on_disk_partition_selected: DiskSelectionCallback,
    on_disk_draw: DiskDrawCallback,
) -> dict[str, Gtk.Widget]:
    """Cria o card de armazenamento com gráfico de partições."""
    card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    card.get_style_context().add_class("card-custom")
    card.get_style_context().add_class("disk-chart-card")
    card.set_size_request(240, 184)

    header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    title = Gtk.Label()
    title.set_markup("<b>Armazenamento</b>")
    title.set_halign(Gtk.Align.START)
    title.set_hexpand(True)
    selector_refs = _create_disk_partition_selector(on_disk_partition_selected)
    header.append(title)
    header.append(selector_refs["menu"])
    card.append(header)

    chart_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    chart_row.get_style_context().add_class("disk-chart-row")
    chart_row.set_size_request(204, 92)
    disk_chart = Gtk.DrawingArea()
    disk_chart.set_size_request(92, 92)
    disk_chart.set_content_width(92)
    disk_chart.set_content_height(92)
    disk_chart.set_draw_func(on_disk_draw)
    chart_row.append(disk_chart)

    info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    info_box.get_style_context().add_class("disk-info-box")
    info_box.set_size_request(118, 86)
    info_box.set_valign(Gtk.Align.CENTER)
    disk_label.set_halign(Gtk.Align.START)
    disk_label.set_xalign(0)
    disk_label.set_wrap(False)
    disk_label.set_width_chars(16)
    disk_label.set_max_width_chars(16)
    disk_label.set_ellipsize(Pango.EllipsizeMode.END)
    disk_label.get_style_context().add_class("subtitle-text")
    disk_chart_detail_label = Gtk.Label(label="Aguardando dados")
    disk_chart_detail_label.set_halign(Gtk.Align.START)
    disk_chart_detail_label.set_xalign(0)
    disk_chart_detail_label.set_wrap(False)
    disk_chart_detail_label.set_width_chars(16)
    disk_chart_detail_label.set_max_width_chars(16)
    disk_chart_detail_label.set_ellipsize(Pango.EllipsizeMode.END)
    disk_chart_detail_label.get_style_context().add_class("subtitle-text")
    disk_progressbar.set_hexpand(True)
    info_box.append(disk_label)
    info_box.append(disk_chart_detail_label)
    info_box.append(disk_progressbar)
    chart_row.append(info_box)
    card.append(chart_row)
    card.append(disk_alert_label)

    return {
        "card": card,
        "detail_label": disk_chart_detail_label,
        "chart": disk_chart,
        **selector_refs,
    }


def _create_disk_partition_selector(
    on_disk_partition_selected: DiskSelectionCallback,
) -> dict[str, Gtk.Widget]:
    """Cria seletor de partições sem usar ComboBoxText."""
    menu_button = Gtk.MenuButton()
    menu_button.get_style_context().add_class("disk-partition-combo")
    menu_button.set_size_request(78, -1)
    menu_button.set_property("label", "Tudo")

    popover = Gtk.Popover()
    popover.set_has_arrow(False)
    popover.get_style_context().add_class("disk-partition-popover")
    options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
    options_box.get_style_context().add_class("disk-partition-options")
    popover.set_child(options_box)
    menu_button.set_popover(popover)
    _rebuild_disk_partition_options(options_box, ("Tudo",), "Tudo", on_disk_partition_selected)
    return {
        "menu": menu_button,
        "popover": popover,
        "options_box": options_box,
    }


def _rebuild_disk_partition_options(
    options_box: Gtk.Box,
    titles: tuple[str, ...],
    selected: str,
    on_disk_partition_selected: DiskSelectionCallback,
):
    """Reconstrói opções iniciais do seletor de armazenamento."""
    child = options_box.get_first_child()
    while child is not None:
        options_box.remove(child)
        child = options_box.get_first_child()
    for title in titles:
        button = Gtk.Button(label=title)
        button.set_has_frame(False)
        button.set_halign(Gtk.Align.FILL)
        button.get_style_context().add_class("disk-partition-option")
        if title == selected:
            button.get_style_context().add_class("active")
        button.connect("clicked", on_disk_partition_selected, title)
        options_box.append(button)


def _create_speedtest_card(on_speedtest_clicked: SpeedtestCallback) -> dict[str, Gtk.Widget]:
    """Cria card de teste de internet."""
    speed_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    speed_panel.get_style_context().add_class("card-custom")
    speed_panel.set_size_request(210, 88)
    speed_title = Gtk.Label(label="Internet")
    speed_title.set_halign(Gtk.Align.START)
    speed_title.get_style_context().add_class("section-title")
    speed_button = Gtk.Button(label="Testar Velocidade")
    speed_button.get_style_context().add_class("suggested-action")
    speed_button.connect("clicked", on_speedtest_clicked)
    speed_result_label = Gtk.Label()
    speed_result_label.set_wrap(False)
    speed_result_label.set_single_line_mode(True)
    speed_result_label.set_width_chars(26)
    speed_result_label.set_max_width_chars(26)
    speed_result_label.set_ellipsize(Pango.EllipsizeMode.END)
    speed_result_label.set_halign(Gtk.Align.START)
    speed_result_label.set_xalign(0)
    speed_result_label.get_style_context().add_class("subtitle-text")
    speed_panel.append(speed_title)
    speed_panel.append(speed_button)
    speed_panel.append(speed_result_label)
    return {
        "panel": speed_panel,
        "button": speed_button,
        "result_label": speed_result_label,
    }
