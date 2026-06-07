"""
Módulo de interface gráfica do SysSense.
Versão GTK 4.0 com libadwaita.
Construir janela com design moderno e minimalista.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, GLib, Gdk, Adw
from importlib import resources
import threading
import math
import time
from typing import Dict, Any

from . import collectors, diagnostics, config, formatters
from .ui.sidebar import build_sidebar
from .ui.preferences import build_preferences_panel
from .ui.overview import build_overview_tab, rebuild_card_order_controls
from .ui.processes import (
    append_process_row,
    build_processes_tab,
    clear_process_list,
    set_active_process_tab,
)
from .ui.disk import build_disk_tab, update_disk_tab
from .ui.services import build_services_tab, update_services_tab

class SysSenseWindow(Adw.ApplicationWindow):
    """Janela principal do SysSense com interface minimalista em GTK 4.0."""
    
    def __init__(self, app):
        super().__init__(application=app, title="SysSense - Monitor do Sistema")
        self.set_default_size(1120, 720)
        self.set_resizable(True)
        
        # Dados coletados (cache global para threading)
        self.dados_cache = {}
        self.lock = threading.Lock()
        self.previous_network_sample = None
        self.last_critical_alerts = set()
        self.toast_overlay = None
        self.user_config = config.load_config()
        self.refresh_timer_id = None
        
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        
        # Setup CSS
        self._setup_css()
        
        # Build UI
        self._build_ui()
        
        # Conecta sinal de show para iniciar coleta
        self.connect('map', self._on_show)
    
    def _setup_css(self):
        """Aplica CSS customizado."""
        css_provider = Gtk.CssProvider()
        css_text = resources.files("syssense.resources").joinpath("styles.css").read_text(encoding="utf-8")
        css_provider.load_from_data(css_text.encode())
        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            display,
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def _build_ui(self):
        """Constrói interface principal."""
        # Header bar com estilo
        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle(title="SysSense", subtitle="Monitor do Sistema"))
        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header)
        
        # Box principal (vertical)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Stack para transição entre loading e conteúdo
        self.main_stack = Gtk.Stack()
        self.main_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.main_stack.set_transition_duration(300)
        
        # Página de loading
        loading_page = self._create_loading_page()
        self.main_stack.add_named(loading_page, "loading")
        
        # Página de conteúdo
        content_page = self._create_content_page()
        self.main_stack.add_named(content_page, "content")
        
        # Mostra loading inicialmente
        self.main_stack.set_visible_child_name("loading")
        
        self.main_stack.set_hexpand(True)
        self.main_stack.set_vexpand(True)
        vbox.append(self.main_stack)
        self.toast_overlay = Adw.ToastOverlay()
        self.toast_overlay.set_child(vbox)
        toolbar_view.set_content(self.toast_overlay)
        self.set_content(toolbar_view)
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key_controller)
    
    def _create_loading_page(self) -> Gtk.Widget:
        """Página de loading com spinner."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        
        spinner = Gtk.Spinner()
        spinner.start()
        box.append(spinner)
        
        label = Gtk.Label(label="Coletando dados do sistema...")
        box.append(label)
        
        return box
    
    def _create_content_page(self) -> Gtk.Widget:
        """Página com conteúdo principal em estilo dashboard."""
        overlay = Gtk.Overlay()
        overlay.set_hexpand(True)
        overlay.set_vexpand(True)

        shell = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        shell.get_style_context().add_class("dashboard-shell")
        shell.set_hexpand(True)
        shell.set_vexpand(True)
        
        # Stack usado como navegação principal; a sidebar controla as páginas.
        self.page_stack = Gtk.Stack()
        self.page_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.page_stack.set_transition_duration(180)
        
        # Cria abas
        self._create_tabs()
        
        shell.append(self._create_sidebar())
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content.get_style_context().add_class("content-pane")
        content.set_hexpand(True)
        content.set_vexpand(True)
        
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        kicker = Gtk.Label(label="MONITOR DO SISTEMA")
        kicker.set_halign(Gtk.Align.START)
        kicker.get_style_context().add_class("page-kicker")
        title = Gtk.Label(label="SysSense")
        title.set_halign(Gtk.Align.START)
        title.get_style_context().add_class("page-title")
        title_box.append(kicker)
        title_box.append(title)
        content.append(title_box)
        
        self.page_stack.set_hexpand(True)
        self.page_stack.set_vexpand(True)
        content.append(self.page_stack)
        shell.append(content)

        overlay.set_child(shell)
        overlay.add_overlay(self._create_panel_dismiss_layer())
        overlay.add_overlay(self._create_alert_overlay_panel())
        overlay.add_overlay(self._create_preferences_overlay_panel())
        return overlay

    def _create_panel_dismiss_layer(self) -> Gtk.Widget:
        """Cria área invisível para fechar painéis internos ao clicar fora."""
        layer = Gtk.Box()
        layer.set_hexpand(True)
        layer.set_vexpand(True)
        layer.set_halign(Gtk.Align.FILL)
        layer.set_valign(Gtk.Align.FILL)
        layer.set_can_target(False)
        layer.get_style_context().add_class("panel-dismiss-layer")
        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self._on_panel_dismiss_pressed)
        layer.add_controller(gesture)
        self.panel_dismiss_layer = layer
        return layer

    def _create_sidebar(self) -> Gtk.Widget:
        """Cria a barra lateral de navegação."""
        refs = build_sidebar(
            self._on_nav_clicked,
            self._toggle_alert_panel,
            self._toggle_preferences_panel,
        )
        self.sidebar = refs.container
        self.nav_buttons = refs.nav_buttons
        self.nav_labels = refs.nav_labels
        self.nav_icons = refs.nav_icons
        self.alert_indicator = refs.alert_indicator
        self.preferences_button = refs.preferences_button
        self.nav_footer = refs.footer
        self._set_active_nav(0)
        GLib.timeout_add(350, self._update_responsive_sidebar)
        
        return self.sidebar

    def _create_alert_overlay_panel(self) -> Gtk.Widget:
        """Cria painel interno de alertas sem popup externo."""
        self.alert_panel_revealer = Gtk.Revealer()
        self.alert_panel_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        self.alert_panel_revealer.set_transition_duration(150)
        self.alert_panel_revealer.set_halign(Gtk.Align.START)
        self.alert_panel_revealer.set_valign(Gtk.Align.END)
        self.alert_panel_revealer.set_margin_start(self._overlay_panel_start_margin())
        self.alert_panel_revealer.set_margin_bottom(18)
        self.alert_panel_revealer.set_can_target(False)

        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        panel.get_style_context().add_class("alert-popover")
        panel.get_style_context().add_class("alert-overlay-panel")
        panel.set_size_request(260, -1)
        self.alert_popover_box = panel
        self.alert_popover_title = Gtk.Label(label="Status do Sistema")
        self.alert_popover_title.set_halign(Gtk.Align.START)
        self.alert_popover_title.get_style_context().add_class("alert-guide-title")
        panel.append(self.alert_popover_title)
        self.alert_popover_subtitle = Gtk.Label(label="Nenhum alerta ativo.")
        self.alert_popover_subtitle.set_wrap(True)
        self.alert_popover_subtitle.set_xalign(0)
        self.alert_popover_subtitle.set_halign(Gtk.Align.START)
        self.alert_popover_subtitle.set_width_chars(28)
        self.alert_popover_subtitle.set_max_width_chars(28)
        self.alert_popover_subtitle.get_style_context().add_class("alert-guide-subtitle")
        panel.append(self.alert_popover_subtitle)
        self.alert_popover_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        panel.append(self.alert_popover_list)
        self.alert_panel_revealer.set_child(panel)

        return self.alert_panel_revealer

    def _toggle_alert_panel(self, _button: Gtk.Button):
        """Alterna o painel interno de riscos."""
        if hasattr(self, "alert_panel_revealer"):
            if hasattr(self, "preferences_panel_revealer"):
                self.preferences_panel_revealer.set_can_target(False)
                self.preferences_panel_revealer.set_reveal_child(False)
            will_open = not self.alert_panel_revealer.get_reveal_child()
            self.alert_panel_revealer.set_can_target(will_open)
            self.alert_panel_revealer.set_reveal_child(will_open)
            self._set_panel_dismiss_active(will_open)

    def _create_preferences_overlay_panel(self) -> Gtk.Widget:
        """Cria painel interno de preferências sem popup externo."""
        refs = build_preferences_panel(
            self.user_config,
            self._overlay_panel_start_margin(),
            self._on_refresh_preference_changed,
            self._on_bool_preference_changed,
            self._on_card_visibility_changed,
        )
        self.preferences_panel_revealer = refs.revealer
        self.refresh_combo = refs.refresh_combo
        self.card_switches = refs.card_switches
        return self.preferences_panel_revealer

    def _toggle_preferences_panel(self, _button: Gtk.Button):
        """Abre ou fecha o painel interno de preferências."""
        if hasattr(self, "preferences_panel_revealer"):
            if hasattr(self, "alert_panel_revealer"):
                self.alert_panel_revealer.set_can_target(False)
                self.alert_panel_revealer.set_reveal_child(False)
            will_open = not self.preferences_panel_revealer.get_reveal_child()
            self.preferences_panel_revealer.set_can_target(will_open)
            self.preferences_panel_revealer.set_reveal_child(will_open)
            self._set_panel_dismiss_active(will_open)

    def _on_panel_dismiss_pressed(self, _gesture: Gtk.GestureClick, _n_press: int, _x: float, _y: float):
        """Fecha painéis internos quando o clique ocorre fora deles."""
        self._close_overlay_panels()

    def _on_key_pressed(
        self,
        _controller: Gtk.EventControllerKey,
        keyval: int,
        _keycode: int,
        _state: Gdk.ModifierType,
    ) -> bool:
        """Fecha painéis internos com Escape."""
        if keyval == Gdk.KEY_Escape:
            return self._close_overlay_panels()
        return False

    def _close_overlay_panels(self) -> bool:
        """Fecha painéis flutuantes internos e informa se algo foi fechado."""
        closed = False
        if hasattr(self, "alert_panel_revealer") and self.alert_panel_revealer.get_reveal_child():
            self.alert_panel_revealer.set_can_target(False)
            self.alert_panel_revealer.set_reveal_child(False)
            closed = True
        if hasattr(self, "preferences_panel_revealer") and self.preferences_panel_revealer.get_reveal_child():
            self.preferences_panel_revealer.set_can_target(False)
            self.preferences_panel_revealer.set_reveal_child(False)
            closed = True
        self._set_panel_dismiss_active(False)
        return closed

    def _set_panel_dismiss_active(self, active: bool):
        """Ativa ou desativa camada invisível de clique fora dos painéis."""
        if hasattr(self, "panel_dismiss_layer"):
            self.panel_dismiss_layer.set_can_target(active)

    def _format_refresh_option(self, seconds: float) -> str:
        """Formata opção de intervalo."""
        return formatters.format_refresh_option(seconds)

    def _save_user_config(self):
        """Persiste preferências do usuário."""
        self.user_config = config.save_config(self.user_config)

    def _on_refresh_preference_changed(self, combo: Gtk.ComboBoxText):
        """Atualiza intervalo de refresh."""
        active = combo.get_active()
        if active < 0:
            return
        self.user_config["refresh_interval"] = config.REFRESH_OPTIONS_SECONDS[active]
        self._save_user_config()
        self._restart_refresh_timer()
        self._refresh_footer_mode()
        GLib.idle_add(self._release_widget_focus, combo)
        GLib.idle_add(self._close_preferences_panel)

    def _close_preferences_panel(self) -> bool:
        """Fecha o painel de preferências quando uma ação discreta termina."""
        if hasattr(self, "preferences_panel_revealer"):
            self.preferences_panel_revealer.set_can_target(False)
            self.preferences_panel_revealer.set_reveal_child(False)
        self._set_panel_dismiss_active(False)
        return False

    def _on_bool_preference_changed(self, switch: Gtk.Switch, _pspec, key: str):
        """Atualiza preferências booleanas."""
        self.user_config[key] = switch.get_active()
        self._save_user_config()
        if key == "show_speedtest":
            self._apply_card_visibility()

    def _on_card_visibility_changed(self, switch: Gtk.Switch, _pspec, key: str):
        """Atualiza visibilidade de cards."""
        self.user_config["visible_cards"][key] = switch.get_active()
        self._save_user_config()
        self._apply_card_visibility()

    def _on_card_order_changed(self, _button: Gtk.Button, key: str, direction: str):
        """Move um card na ordem persistida da dashboard."""
        card_order = list(self.user_config.get("card_order", config.DEFAULT_CARD_ORDER))
        if key not in card_order:
            return
        index = card_order.index(key)
        offset = -1 if direction == "up" else 1
        new_index = index + offset
        if new_index < 0 or new_index >= len(card_order):
            return
        card_order[index], card_order[new_index] = card_order[new_index], card_order[index]
        self.user_config["card_order"] = card_order
        self._save_user_config()
        self._apply_card_order()
        self._refresh_card_order_controls()

    def _on_card_order_reset(self, _button: Gtk.Button):
        """Restaura ordem padrão dos cards."""
        self.user_config["card_order"] = list(config.DEFAULT_CARD_ORDER)
        self._save_user_config()
        self._apply_card_order()
        self._refresh_card_order_controls()

    def _refresh_card_order_controls(self):
        """Atualiza lista de controles de ordenação na Visão Geral."""
        if hasattr(self, "card_order_box"):
            rebuild_card_order_controls(
                self.card_order_box,
                self.user_config["card_order"],
                self._on_card_order_changed,
            )

    def _restart_refresh_timer(self):
        """Reinicia timer de atualização automática."""
        if self.refresh_timer_id is not None:
            GLib.source_remove(self.refresh_timer_id)
        interval_ms = int(self.user_config["refresh_interval"] * 1000)
        self.refresh_timer_id = GLib.timeout_add(interval_ms, self._on_auto_refresh)

    def _on_nav_clicked(self, button: Gtk.Button, page: int):
        """Alterna páginas pelo menu lateral."""
        self.page_stack.set_visible_child_name(self.page_names[page])
        self._set_active_nav(page)

    def _set_active_nav(self, page: int):
        """Marca visualmente a página ativa."""
        for i, button in enumerate(getattr(self, 'nav_buttons', [])):
            if i == page:
                button.get_style_context().add_class("active")
            else:
                button.get_style_context().remove_class("active")

    def _update_responsive_sidebar(self) -> bool:
        """Compacta a sidebar quando a janela fica estreita."""
        compact = self.get_width() < 760
        self.sidebar.set_size_request(50 if compact else 132, -1)
        if compact:
            self.sidebar.get_style_context().add_class("sidebar-compact")
        else:
            self.sidebar.get_style_context().remove_class("sidebar-compact")
        panel_margin = self._overlay_panel_start_margin(compact)
        if hasattr(self, "alert_panel_revealer"):
            self.alert_panel_revealer.set_margin_start(panel_margin)
        if hasattr(self, "preferences_panel_revealer"):
            self.preferences_panel_revealer.set_margin_start(panel_margin)
        for label in self.nav_labels:
            label.set_visible(not compact)
        self.nav_footer.set_visible(not compact)
        return True

    def _overlay_panel_start_margin(self, compact: bool | None = None) -> int:
        """Alinha painéis internos com a borda esquerda dos cards."""
        if compact is None:
            compact = getattr(self, "sidebar", None) is not None and self.get_width() < 760
        return 74 if compact else 162
    
    def _create_tabs(self):
        """Cria todas as abas do aplicativo."""
        self.page_names = ["overview", "processes", "disk", "services"]

        # Aba 1: Visão Geral
        overview_box = self._create_overview_tab()
        self.page_stack.add_named(overview_box, "overview")
        
        # Aba 2: Processos
        processes_box = self._create_processes_tab()
        self.page_stack.add_named(processes_box, "processes")
        
        # Aba 3: Disco
        disk_box = self._create_disk_tab()
        self.page_stack.add_named(disk_box, "disk")
        
        # Aba 4: Serviços
        services_box = self._create_services_tab()
        self.page_stack.add_named(services_box, "services")
        
    def _create_overview_tab(self) -> Gtk.Widget:
        """Aba de Visão Geral."""
        refs = build_overview_tab(
            self.user_config["card_order"],
            self._on_speedtest_clicked,
            self._on_disk_partition_selected,
            self._draw_disk_chart,
            self._on_card_order_changed,
            self._on_card_order_reset,
        )
        self.overview_scrolled = refs.scrolled
        self.overview_flow = refs.flow
        self.card_order_box = refs.card_order_box
        self.overview_cards = refs.cards
        self.overview_card_widgets = refs.card_widgets
        self.overview_card_flow_children = refs.card_flow_children
        self.cpu_card = refs.cpu_card
        self.cpu_label = refs.cpu_label
        self.cpu_progressbar = refs.cpu_progressbar
        self.cpu_alert_label = refs.cpu_alert_label
        self.mem_card = refs.mem_card
        self.mem_label = refs.mem_label
        self.mem_progressbar = refs.mem_progressbar
        self.mem_alert_label = refs.mem_alert_label
        self.disk_overview_card = refs.disk_overview_card
        self.disk_label = refs.disk_label
        self.disk_progressbar = refs.disk_progressbar
        self.disk_alert_label = refs.disk_alert_label
        self.disk_chart_detail_label = refs.disk_chart_detail_label
        self.disk_chart = refs.disk_chart
        self.disk_partition_menu = refs.disk_partition_menu
        self.disk_partition_popover = refs.disk_partition_popover
        self.disk_partition_options_box = refs.disk_partition_options_box
        self.temp_card = refs.temp_card
        self.temp_label = refs.temp_label
        self.net_card = refs.net_card
        self.net_label = refs.net_label
        self.load_card = refs.load_card
        self.load_label = refs.load_label
        self.uptime_card = refs.uptime_card
        self.uptime_label = refs.uptime_label
        self.speed_panel = refs.speed_panel
        self.speed_button = refs.speed_button
        self.speed_result_label = refs.speed_result_label
        self.disk_partitions_data = []
        self.disk_partitions_signature = None
        self.selected_disk_partition = "Tudo"
        self.overview_flow.set_sort_func(self._compare_overview_cards)
        self._apply_cards_overview_layout()
        self._apply_card_order()
        self._apply_card_visibility()
        return refs.page

    def _apply_cards_overview_layout(self):
        """Mantém a visão geral sempre no modo cards compactos."""
        self.overview_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        self.overview_flow.get_style_context().add_class("compact-overview")
        self.overview_flow.set_max_children_per_line(4)
        for card in self.overview_cards:
            card.set_size_request(168, 88)
        self.disk_overview_card.set_size_request(192, 140)

    def _compare_overview_cards(
        self,
        child_a: Gtk.FlowBoxChild,
        child_b: Gtk.FlowBoxChild,
        _user_data=None,
    ) -> int:
        """Ordena cards conforme preferência persistida."""
        order = self.user_config.get("card_order", config.DEFAULT_CARD_ORDER)
        positions = {key: index for index, key in enumerate(order)}
        key_a = getattr(child_a, "syssense_card_key", "")
        key_b = getattr(child_b, "syssense_card_key", "")
        return positions.get(key_a, 999) - positions.get(key_b, 999)

    def _apply_card_order(self):
        """Aplica ordenação manual salva aos cards da dashboard."""
        if hasattr(self, "overview_flow"):
            self.overview_flow.invalidate_sort()

    def _apply_card_visibility(self):
        """Aplica preferências de visibilidade dos cards."""
        if not hasattr(self, "overview_card_widgets"):
            return

        visible_cards = self.user_config.get("visible_cards", {})
        for key, card in self.overview_card_widgets.items():
            visible = bool(visible_cards.get(key, True))
            if key == "internet" and not self.user_config.get("show_speedtest", True):
                visible = False
            flow_child = self.overview_card_flow_children.get(key)
            if flow_child is None:
                flow_child = card.get_parent()
                self.overview_card_flow_children[key] = flow_child
            if flow_child is not None:
                flow_child.set_visible(visible)
            card.set_visible(visible)

    def _create_processes_tab(self) -> Gtk.Widget:
        """Aba de Processos com navegação animada entre visões."""
        refs = build_processes_tab(self._on_process_tab_clicked)
        self.process_runtime_notice = refs.runtime_notice
        self.process_tab_buttons = refs.tab_buttons
        self.process_stack = refs.stack
        self.mem_list = refs.mem_list
        self.cpu_proc_list = refs.cpu_proc_list
        self.compare_mem_list = refs.compare_mem_list
        self.compare_cpu_list = refs.compare_cpu_list
        self._set_active_process_tab("memory")
        return refs.page

    def _on_process_tab_clicked(self, _button: Gtk.Button, page_name: str):
        """Alterna visão interna de processos com transição."""
        self.process_stack.set_visible_child_name(page_name)
        self._set_active_process_tab(page_name)

    def _set_active_process_tab(self, page_name: str):
        """Marca botão ativo da navegação interna de Processos."""
        set_active_process_tab(getattr(self, "process_tab_buttons", []), page_name)
    
    def _create_disk_tab(self) -> Gtk.Widget:
        """Aba de Disco."""
        refs = build_disk_tab()
        self.disk_partitions_box = refs.partitions_box
        return refs.page
    
    def _create_services_tab(self) -> Gtk.Widget:
        """Aba de Serviços."""
        refs = build_services_tab(self._on_refresh_services)
        self.services_refresh_button = refs.refresh_button
        self.services_status_label = refs.status_label
        self.services_box = refs.services_box
        return refs.page
    
    def _on_disk_partition_selected(self, _button: Gtk.Button, title: str):
        """Atualiza o gráfico quando a partição selecionada muda."""
        self.selected_disk_partition = title or "Tudo"
        self.disk_partition_menu.set_property("label", self.selected_disk_partition)
        self._rebuild_disk_partition_options(self._disk_partition_titles(), self.selected_disk_partition)
        self.disk_partition_popover.popdown()
        self._update_disk_overview_card()
        GLib.idle_add(self._release_widget_focus, self.disk_partition_menu)

    def _release_widget_focus(self, widget: Gtk.Widget) -> bool:
        """Solta foco após seleção para evitar cliques presos."""
        root = widget.get_root()
        if isinstance(root, Gtk.Window):
            root.set_focus(None)
        return False

    def _disk_partition_titles(self) -> tuple[str, ...]:
        """Retorna títulos disponíveis para o seletor de armazenamento."""
        partitions = getattr(self, 'disk_partitions_data', [])
        return ("Tudo",) + tuple(self._disk_partition_title(part) for part in partitions)

    def _rebuild_disk_partition_options(self, titles: tuple[str, ...], selected: str):
        """Reconstrói opções do seletor de armazenamento."""
        self._clear_box(self.disk_partition_options_box)
        for title in titles:
            button = Gtk.Button(label=title)
            button.set_has_frame(False)
            button.set_halign(Gtk.Align.FILL)
            button.get_style_context().add_class("disk-partition-option")
            if title == selected:
                button.get_style_context().add_class("active")
            button.connect("clicked", self._on_disk_partition_selected, title)
            self.disk_partition_options_box.append(button)

    def _update_disk_overview_card(self):
        """Atualiza texto e gráfico do card de armazenamento."""
        partitions = getattr(self, 'disk_partitions_data', [])
        if not partitions:
            self.disk_label.set_text("Nenhuma partição encontrada")
            self.disk_chart_detail_label.set_text("")
            self.disk_progressbar.set_fraction(0)
            self.disk_chart.queue_draw()
            return

        selected = getattr(self, 'selected_disk_partition', "Tudo")
        if selected == "Tudo":
            total = sum(part.get('total', 0) for part in partitions)
            used = sum(part.get('used', 0) for part in partitions)
            free = sum(part.get('free', 0) for part in partitions)
            pct = (used / total * 100) if total else 0
            self.disk_label.set_text(f"{pct:.1f}% usado")
            self.disk_chart_detail_label.set_text(f"{formatters.format_disk_size(used)} / {formatters.format_disk_size(total)}")
            self.disk_progressbar.set_fraction(min(pct / 100, 1))
        else:
            part = next((p for p in partitions if self._disk_partition_title(p) == selected), partitions[0])
            pct = part.get('percent', 0)
            used = part.get('used', 0)
            total = part.get('total', 0)
            self.disk_label.set_text(f"{pct:.1f}% usado")
            self.disk_chart_detail_label.set_text(f"{formatters.format_disk_size(used)} / {formatters.format_disk_size(total)}")
            self.disk_progressbar.set_fraction(min(pct / 100, 1))
        self.disk_chart.queue_draw()

    def _format_network_text(self, rede: Dict[str, Any]) -> tuple[str, str]:
        """Calcula velocidade atual de rede e tooltip com acumulado."""
        now = time.monotonic()
        sent = rede.get('bytes_sent', 0)
        recv = rede.get('bytes_recv', 0)
        tooltip = formatters.format_network_tooltip(recv, sent)

        previous = self.previous_network_sample
        self.previous_network_sample = {
            'time': now,
            'bytes_sent': sent,
            'bytes_recv': recv,
        }
        if not previous:
            return formatters.format_network_rates(0, 0), tooltip

        elapsed = max(now - previous.get('time', now), 0.1)
        down_rate = max(recv - previous.get('bytes_recv', recv), 0) / elapsed
        up_rate = max(sent - previous.get('bytes_sent', sent), 0) / elapsed
        return formatters.format_network_rates(down_rate, up_rate), tooltip

    def _sync_disk_partition_selector(self, partitions: list):
        """Sincroniza opções do seletor de partições."""
        signature = tuple(self._disk_partition_title(part) for part in partitions)
        if signature == self.disk_partitions_signature:
            return
        current = getattr(self, 'selected_disk_partition', "Tudo")
        selected = current if current in signature else "Tudo"
        titles = ("Tudo",) + signature
        self._rebuild_disk_partition_options(titles, selected)
        self.disk_partition_menu.set_property("label", selected)
        self.disk_partitions_signature = signature
        self.selected_disk_partition = selected

    def _disk_partition_title(self, part: Dict[str, Any]) -> str:
        """Nome curto para exibição no seletor de partição."""
        mountpoint = part.get('mountpoint') or part.get('device') or "Partição"
        device = part.get('device') or ""
        if mountpoint == "/":
            return "/"
        return mountpoint if not device else f"{mountpoint}"

    def _draw_disk_chart(self, area: Gtk.DrawingArea, cr, width: int, height: int):
        """Desenha uma rosca de duas cores: usado e livre."""
        partitions = getattr(self, 'disk_partitions_data', [])
        cx = width / 2
        cy = height / 2
        radius = max(min(width, height) / 2 - 8, 10)
        line_width = max(radius * 0.28, 6)
        start = -math.pi / 2

        cr.set_line_width(line_width)
        cr.set_line_cap(0)

        used, total = self._get_selected_disk_usage(partitions)
        used_fraction = min((used / total) if total else 0, 1)

        # Livre: trilha cinza completa.
        cr.set_source_rgba(0.91, 0.89, 0.85, 0.16)
        cr.arc(cx, cy, radius, 0, math.tau)
        cr.stroke()

        if used_fraction <= 0:
            return

        # Usado: fatia clara sobre a trilha.
        cr.set_source_rgb(0.91, 0.89, 0.85)
        cr.arc(cx, cy, radius, start, start + (used_fraction * math.tau))
        cr.stroke()

    def _get_selected_disk_usage(self, partitions: list) -> tuple[int, int]:
        """Retorna bytes usados e totais para Tudo ou partição selecionada."""
        if not partitions:
            return 0, 0

        selected = getattr(self, 'selected_disk_partition', "Tudo")
        if selected == "Tudo":
            return (
                sum(part.get('used', 0) for part in partitions),
                sum(part.get('total', 0) for part in partitions),
            )

        part = next((p for p in partitions if self._disk_partition_title(p) == selected), partitions[0])
        return part.get('used', 0), part.get('total', 0)

    def _clear_box(self, box: Gtk.Box):
        """Remove todos os filhos de um Gtk.Box no GTK 4."""
        child = box.get_first_child()
        while child is not None:
            box.remove(child)
            child = box.get_first_child()
    
    # ========== Callbacks de Threading ==========
    
    def _on_show(self, widget):
        """Inicia coleta inicial em thread."""
        thread = threading.Thread(target=self._initial_load, daemon=True)
        thread.start()
    
    def _initial_load(self):
        """Carrega dados iniciais."""
        all_data = self._collect_all_data()
        GLib.idle_add(self._on_initial_data_ready, all_data)
    
    def _collect_all_data(self) -> Dict[str, Any]:
        """Coleta todos os dados."""
        return {
            'runtime': collectors.get_runtime_info(),
            'cpu': collectors.get_cpu_info(),
            'memoria': collectors.get_memory_info(),
            'disco': collectors.get_disk_info(),
            'processos': collectors.get_top_processes(),
            'rede': collectors.get_network_info(),
            'temperatura': collectors.get_temperature(),
            'uptime': collectors.get_uptime(),
            'servicos': collectors.get_failed_services()
        }
    
    def _on_initial_data_ready(self, data: Dict[str, Any]) -> bool:
        """Dados iniciais prontos."""
        self.dados_cache = data
        
        self._update_overview(data)
        self._update_automatic_alerts(data)
        self._update_runtime_notice(data)
        self._update_processes(data)
        self._update_disk(data)
        
        self.main_stack.set_visible_child_name("content")
        
        self._restart_refresh_timer()
        
        return False
    
    def _on_auto_refresh(self) -> bool:
        """Atualização automática conforme preferências."""
        thread = threading.Thread(target=self._refresh_fast_data, daemon=True)
        thread.start()
        return True
    
    def _refresh_fast_data(self):
        """Atualiza dados rápidos."""
        data = {
            'cpu': collectors.get_cpu_info(),
            'memoria': collectors.get_memory_info(),
            'disco': collectors.get_disk_info(),
            'rede': collectors.get_network_info(),
            'temperatura': collectors.get_temperature(),
            'processos': collectors.get_top_processes(),
            'uptime': collectors.get_uptime(),
        }
        
        with self.lock:
            self.dados_cache.update(data)
        
        GLib.idle_add(self._on_fast_data_updated, data)
    
    def _on_fast_data_updated(self, data: Dict[str, Any]) -> bool:
        """Atualiza widgets."""
        with self.lock:
            merged_data = self.dados_cache.copy()
        self._update_overview(data)
        self._update_automatic_alerts(merged_data)
        self._update_processes(data)
        self._update_disk(data)
        return False

    def _update_runtime_notice(self, data: Dict[str, Any]):
        """Atualiza avisos de modo nativo/sandbox."""
        runtime = data.get('runtime', {})
        is_flatpak = runtime.get('is_flatpak', False)
        if hasattr(self, 'process_runtime_notice'):
            self.process_runtime_notice.set_visible(is_flatpak)
            if is_flatpak:
                self.process_runtime_notice.set_text(
                    "Modo sandbox: a lista de processos mostra apenas o ambiente Flatpak. "
                    "Use a instalação nativa para monitorar os processos reais do Fedora."
                )
        if hasattr(self, 'nav_footer'):
            self.current_runtime_is_flatpak = is_flatpak
            self._refresh_footer_mode()

    def _refresh_footer_mode(self):
        """Atualiza rodapé da sidebar."""
        if not hasattr(self, 'nav_footer'):
            return
        is_flatpak = getattr(self, "current_runtime_is_flatpak", False)
        mode = "Sandbox" if is_flatpak else "Nativo"
        interval = self._format_refresh_option(self.user_config["refresh_interval"])
        self.nav_footer.set_text(f"Auto refresh: {interval}\nModo: {mode}")
    
    def _on_refresh_services(self, button: Gtk.Button):
        """Botão Atualizar em Serviços."""
        button.set_sensitive(False)
        button.set_label("Atualizando...")
        self.services_status_label.set_text("Consultando systemd e logs")
        thread = threading.Thread(target=self._fetch_services, daemon=True)
        thread.start()
    
    def _fetch_services(self):
        """Coleta serviços e logs."""
        data = collectors.get_failed_services()
        logs = collectors.get_recent_logs(50)
        GLib.idle_add(self._on_services_updated, data, logs)
    
    def _on_services_updated(self, services: Dict[str, Any], logs: Dict[str, Any]) -> bool:
        """Atualiza aba de serviços."""
        with self.lock:
            self.dados_cache['servicos'] = services
        self._update_services(services, logs)
        self._update_automatic_alerts(self.dados_cache.copy())
        self.services_refresh_button.set_sensitive(True)
        self.services_refresh_button.set_label("Atualizar")
        self.services_status_label.set_text("Atualização concluída")
        return False
    
    def _on_speedtest_clicked(self, button: Gtk.Button):
        """Botão Testar Velocidade."""
        button.set_sensitive(False)
        button.set_label("Testando...")
        self.speed_result_label.set_text("Executando teste")
        self.speed_result_label.set_tooltip_text(None)
        thread = threading.Thread(target=self._run_speedtest, daemon=True)
        thread.start()
    
    def _run_speedtest(self):
        """Executa speedtest."""
        result = collectors.speedtest()
        GLib.idle_add(self._on_speedtest_complete, result)
    
    def _on_speedtest_complete(self, result: Dict[str, Any]) -> bool:
        """Exibe resultado do speedtest."""
        self.speed_button.set_sensitive(True)
        self.speed_button.set_label("Testar Velocidade")
        
        if result.get('success'):
            text = f"↓ {result['download_mbps']:.1f} Mbps | ↑ {result['upload_mbps']:.1f} Mbps"
            self.speed_result_label.set_tooltip_text(
                f"Ping: {result['ping_ms']:.1f} ms\nServidor: {result.get('server', 'Desconhecido')}"
            )
        else:
            error = result.get('error', 'Desconhecido')
            text = "Teste indisponível"
            self.speed_result_label.set_tooltip_text(error)
        
        self.speed_result_label.set_text(text)
        self.speed_panel.set_size_request(210, 88)
        
        return False
    
    # ========== Atualização de Widgets ==========
    
    def _update_overview(self, data: Dict[str, Any]):
        """Atualiza Visão Geral."""
        cpu = data.get('cpu', {})
        mem = data.get('memoria', {})
        disco = data.get('disco', {})
        temp = data.get('temperatura', {})
        rede = data.get('rede', {})
        uptime = data.get('uptime', {})
        
        cpu_pct = cpu.get('percent', 0)
        self.cpu_label.set_text(f"{cpu_pct:.1f}%")
        self.cpu_progressbar.set_fraction(cpu_pct / 100)
        
        mem_pct = mem.get('percent', 0)
        mem_gb = mem.get('used', 0) / (1024**3)
        mem_total = mem.get('total', 0) / (1024**3)
        self.mem_label.set_text(f"{mem_pct:.1f}% ({mem_gb:.1f} / {mem_total:.1f} GB)")
        self.mem_progressbar.set_fraction(mem_pct / 100)
        
        self.disk_partitions_data = disco.get('partitions', [])
        self._sync_disk_partition_selector(self.disk_partitions_data)
        self._update_disk_overview_card()
        
        if temp.get('disponivel'):
            temp_c = temp.get('celsius', 'N/A')
            self.temp_label.set_text(f"{temp_c} °C")
        else:
            self.temp_label.set_text("Sensor não disponível")
        
        bytes_sent = rede.get('bytes_sent', 0)
        bytes_recv = rede.get('bytes_recv', 0)
        net_text, net_tooltip = self._format_network_text(rede)
        self.net_label.set_text(net_text)
        self.net_label.set_tooltip_text(net_tooltip)
        
        load = cpu.get('load_avg', {})
        self.load_label.set_text(formatters.format_load_average(load))
        
        self.uptime_label.set_text(formatters.format_uptime(uptime))

    def _update_automatic_alerts(self, data: Dict[str, Any]):
        """Atualiza o diagnóstico automático e os alertas visuais."""
        alertas = diagnostics.diagnosticar_por_regras(data)
        self._update_alert_indicator(alertas)
        self._update_card_alerts(alertas)
        self._show_important_toasts(alertas)

    def _update_alert_indicator(self, alertas: list[dict]):
        """Atualiza ícone, tooltip e popover de alertas."""
        if not hasattr(self, 'alert_indicator'):
            return

        highest = self._highest_alert_severity(alertas)
        context = self.alert_indicator.get_style_context()
        for css_class in ("alert-indicator-ok", "alert-indicator-medium", "alert-indicator-high"):
            context.remove_class(css_class)

        if highest == "alta":
            context.add_class("alert-indicator-high")
            self.alert_indicator.set_icon_name("dialog-error-symbolic")
            title = "Alerta crítico"
        elif highest == "media":
            context.add_class("alert-indicator-medium")
            self.alert_indicator.set_icon_name("dialog-warning-symbolic")
            title = "Atenção"
        else:
            context.add_class("alert-indicator-ok")
            self.alert_indicator.set_icon_name("emblem-ok-symbolic")
            title = "Sistema OK"

        self.alert_indicator.set_tooltip_text(None)
        self._update_alert_guide(title, alertas)

    def _update_alert_guide(self, title: str, alertas: list[dict]):
        """Preenche o painel-guia de alertas."""
        if not hasattr(self, 'alert_popover_list'):
            return

        self.alert_popover_title.set_text(title)
        self._clear_box(self.alert_popover_list)

        if not alertas:
            self.alert_popover_box.set_size_request(260, -1)
            self.alert_popover_subtitle.set_width_chars(28)
            self.alert_popover_subtitle.set_max_width_chars(28)
            self.alert_popover_subtitle.set_text("Nenhum alerta ativo no momento.")
            return

        self.alert_popover_box.set_size_request(520, -1)
        self.alert_popover_subtitle.set_width_chars(58)
        self.alert_popover_subtitle.set_max_width_chars(58)
        self.alert_popover_subtitle.set_text(
            f"{len(alertas)} alerta(s) detectado(s). Passe pelos cards destacados para ver detalhes."
        )
        for alerta in alertas[:5]:
            self.alert_popover_list.append(self._create_alert_guide_row(alerta))

        if len(alertas) > 5:
            more = Gtk.Label(label=f"+ {len(alertas) - 5} alerta(s) oculto(s)")
            more.set_halign(Gtk.Align.START)
            more.get_style_context().add_class("alert-guide-subtitle")
            self.alert_popover_list.append(more)

    def _create_alert_guide_row(self, alerta: dict) -> Gtk.Widget:
        """Cria uma linha compacta no painel-guia."""
        severity = alerta.get('severidade', 'media')
        row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        row.get_style_context().add_class("alert-guide-row")
        row.get_style_context().add_class("high" if severity == "alta" else "medium")

        chip = Gtk.Label(label="CRÍTICO" if severity == "alta" else "ATENÇÃO")
        chip.set_halign(Gtk.Align.START)
        chip.get_style_context().add_class("alert-guide-chip")
        chip.get_style_context().add_class("high" if severity == "alta" else "medium")
        row.append(chip)

        message = Gtk.Label(label=alerta.get('mensagem', 'Alerta sem descrição.'))
        message.set_wrap(True)
        message.set_xalign(0)
        message.set_halign(Gtk.Align.START)
        message.set_width_chars(58)
        message.set_max_width_chars(58)
        message.get_style_context().add_class("subtitle-text")
        row.append(message)

        return row

    def _update_card_alerts(self, alertas: list[dict]):
        """Marca os cards diretamente afetados por alertas."""
        self._set_card_alert(self.cpu_card, self.cpu_alert_label, None, "")
        self._set_card_alert(self.mem_card, self.mem_alert_label, None, "")
        self._set_card_alert(self.disk_overview_card, self.disk_alert_label, None, "")
        self.disk_label.set_tooltip_text(None)

        fields = {}
        for alerta in alertas:
            fields.setdefault(alerta.get('campo'), alerta)

        if 'cpu_percent' in fields:
            self._set_card_alert(
                self.cpu_card,
                self.cpu_alert_label,
                fields['cpu_percent']['severidade'],
                "CPU alta"
            )
        if 'mem_percent' in fields:
            self._set_card_alert(
                self.mem_card,
                self.mem_alert_label,
                fields['mem_percent']['severidade'],
                "Memória alta"
            )
        elif 'swap_percent' in fields:
            self._set_card_alert(
                self.mem_card,
                self.mem_alert_label,
                fields['swap_percent']['severidade'],
                "Swap em uso"
            )
        if 'disco_percent' in fields:
            alerta = fields['disco_percent']
            self._set_card_alert(
                self.disk_overview_card,
                self.disk_alert_label,
                alerta['severidade'],
                "Espaço limitado"
            )
            self.disk_label.set_tooltip_text(alerta['mensagem'])

    def _set_card_alert(
        self,
        card: Gtk.Widget,
        label: Gtk.Widget,
        severity: str | None,
        text: str
    ):
        """Aplica ou remove borda e texto curto de alerta em um card."""
        text_label = label.get_child() if isinstance(label, Gtk.Revealer) else label
        context = card.get_style_context()
        context.remove_class("alert-card-medium")
        context.remove_class("alert-card-high")
        text_label.get_style_context().remove_class("alert-medium")
        text_label.get_style_context().remove_class("alert-high")

        if not severity:
            if isinstance(label, Gtk.Revealer):
                label.set_reveal_child(False)
            else:
                label.set_visible(False)
            text_label.set_text("")
            return

        if severity == "alta":
            context.add_class("alert-card-high")
            text_label.get_style_context().add_class("alert-high")
            text_label.set_text(f"Crítico: {text}")
        else:
            context.add_class("alert-card-medium")
            text_label.get_style_context().add_class("alert-medium")
            text_label.set_text(f"Atenção: {text}")
        if isinstance(label, Gtk.Revealer):
            label.set_reveal_child(True)
        else:
            label.set_visible(True)

    def _show_important_toasts(self, alertas: list[dict]):
        """Mostra toast apenas para alertas críticos novos."""
        if not self.user_config.get("critical_toasts", True):
            self.last_critical_alerts = {
                alerta.get('campo')
                for alerta in alertas
                if alerta.get('severidade') == 'alta'
            }
            return

        critical_alerts = [
            alerta for alerta in alertas
            if alerta.get('severidade') == 'alta'
        ]
        current = {alerta.get('campo') for alerta in critical_alerts}
        new_alerts = current - self.last_critical_alerts
        self.last_critical_alerts = current

        if not self.toast_overlay or not new_alerts:
            return

        field = next(iter(new_alerts))
        message = next(
            alerta.get('mensagem', 'Alerta crítico ativo.')
            for alerta in critical_alerts
            if alerta.get('campo') == field
        )
        toast = Adw.Toast.new(message)
        toast.set_timeout(5)
        self.toast_overlay.add_toast(toast)

    def _highest_alert_severity(self, alertas: list[dict]) -> str | None:
        """Retorna a maior severidade ativa."""
        if any(alerta.get('severidade') == 'alta' for alerta in alertas):
            return "alta"
        if any(alerta.get('severidade') == 'media' for alerta in alertas):
            return "media"
        return None

    def _update_processes(self, data: Dict[str, Any]):
        """Atualiza Processos."""
        procs = data.get('processos', {})
        
        clear_process_list(self.mem_list)
        for proc in procs.get('by_memory', []):
            append_process_row(self.mem_list, [
                proc['name'],
                proc['pid'],
                f"{proc.get('cpu_percent', 0):.1f}",
                f"{proc.get('memory_percent', 0):.1f}",
            ])
        
        clear_process_list(self.cpu_proc_list)
        for proc in procs.get('by_cpu', []):
            append_process_row(self.cpu_proc_list, [
                proc['name'],
                proc['pid'],
                f"{proc.get('cpu_percent', 0):.1f}",
                f"{proc.get('memory_percent', 0):.1f}",
            ])
        
        clear_process_list(self.compare_mem_list)
        for proc in procs.get('by_memory', [])[:10]:
            append_process_row(self.compare_mem_list, [proc['name'], f"{proc.get('memory_percent', 0):.1f}"])
        
        clear_process_list(self.compare_cpu_list)
        for proc in procs.get('by_cpu', [])[:10]:
            append_process_row(self.compare_cpu_list, [proc['name'], f"{proc.get('cpu_percent', 0):.1f}"])
    
    def _update_disk(self, data: Dict[str, Any]):
        """Atualiza Disco."""
        update_disk_tab(self.disk_partitions_box, data.get('disco', {}))
        
    
    def _update_services(self, services: Dict[str, Any], logs: Dict[str, Any]):
        """Atualiza Serviços."""
        update_services_tab(self.services_box, services, logs)
        
