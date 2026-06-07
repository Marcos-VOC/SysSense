"""
Módulo de interface gráfica do SysSense.
Versão GTK 4.0 com libadwaita.
Construir janela com design moderno e minimalista.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, GLib, Gdk, Adw, Pango
import threading
import math
import html
import time
from typing import Dict, Any

from . import collectors, diagnostics, config


# CSS customizável para design minimalista moderno
SYSSENSE_CSS = """
@define-color ss-bg #0f0f10;
@define-color ss-surface #171719;
@define-color ss-surface-2 #202124;
@define-color ss-surface-3 #2a2b2f;
@define-color ss-card #ddd9cf;
@define-color ss-card-dark #1f2023;
@define-color ss-card-hover #2c2d31;
@define-color ss-text #e8e4d8;
@define-color ss-muted #aaa69c;
@define-color ss-ink #191a1d;
@define-color ss-border rgba(232, 228, 216, 0.10);
@define-color ss-accent #e8e4d8;
@define-color ss-danger #ff7b72;
@define-color ss-warning #e5c07b;
@define-color ss-success #9ece6a;

window,
.dashboard-root {
    background: @ss-bg;
    color: @ss-text;
}

headerbar {
    background: @ss-bg;
    color: @ss-text;
    box-shadow: none;
    border: none;
}

.dashboard-shell {
    background: @ss-bg;
    padding: 10px;
}

.sidebar {
    background: @ss-surface;
    border: 1px solid @ss-border;
    border-radius: 16px;
    padding: 10px 8px;
    margin: 0 10px 0 0;
}

.sidebar-compact {
    padding: 12px 8px;
}

.brand-subtitle,
.subtitle-text {
    color: @ss-muted;
    font-size: 13px;
}

.runtime-notice {
    background: rgba(232, 228, 216, 0.06);
    color: @ss-muted;
    border: 1px solid @ss-border;
    border-radius: 12px;
    padding: 10px 12px;
    margin: 8px 0 10px 0;
}

.status-pill {
    color: @ss-muted;
    font-size: 12px;
    margin-top: 4px;
}

.nav-item {
    background: transparent;
    color: @ss-muted;
    border: none;
    border-radius: 11px;
    padding: 9px 9px;
    margin: 2px 0;
}

.nav-item:hover {
    background: @ss-card-hover;
    color: @ss-text;
}

.nav-item.active {
    background: @ss-card;
    color: @ss-ink;
}

.nav-icon {
    color: inherit;
}

button.nav-item label,
button.nav-item image,
button.nav-item .nav-icon {
    color: inherit;
}

button.nav-item.active label,
button.nav-item.active image,
button.nav-item.active .nav-icon,
.nav-item.active .nav-icon {
    color: @ss-ink;
}

.content-pane {
    padding: 2px 0 0 0;
}

.page-title {
    color: @ss-text;
    font-size: 50px;
    font-weight: 800;
}

.page-kicker {
    color: @ss-muted;
    font-size: 12px;
    font-weight: 700;
}

.overview-flow {
    background: transparent;
}

.overview-flow flowboxchild {
    padding: 0;
    border-radius: 16px;
}

.overview-flow flowboxchild:hover {
    border-radius: 16px;
    background: transparent;
}



.compact-overview .metric-card,
.compact-overview .card-custom {
    min-width: 168px;
    min-height: 88px;
    padding: 14px;
    margin: 5px;
}

.compact-overview .wide-card {
    min-width: 168px;
}

.card-custom,
.panel-card {
    border-radius: 18px;
    padding: 18px;
    margin: 7px;
    background: @ss-card-dark;
    color: @ss-text;
    border: 1px solid @ss-border;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.20);
}

.metric-card {
    min-width: 200px;
    min-height: 112px;
}

.wide-card {
    min-width: 414px;
}

.light-card {
    background: @ss-card;
    color: @ss-ink;
}

.light-card .subtitle-text {
    color: rgba(25, 26, 29, 0.62);
}

.light-card.alert-card-medium {
    border-color: rgba(145, 107, 21, 0.70);
}

.light-card.alert-card-high {
    border-color: rgba(164, 49, 42, 0.72);
}

.section-title {
    font-size: 17px;
    font-weight: 700;
    margin-top: 8px;
    margin-bottom: 6px;
    color: @ss-text;
}

button {
    border-radius: 12px;
}

button.suggested-action {
    background: @ss-card;
    color: @ss-ink;
    font-weight: 700;
}


.disk-chart-card {
    min-width: 240px;
    min-height: 184px;
}

.disk-chart-row {
    margin-top: 4px;
}

.disk-partition-combo {
    min-width: 78px;
}

.disk-info-box {
    min-width: 118px;
}

.disk-chart-center {
    font-size: 12px;
    color: @ss-muted;
}

progressbar trough {
    min-height: 8px;
    border-radius: 999px;
    background: rgba(232, 228, 216, 0.13);
}

progressbar progress {
    border-radius: 999px;
    background: @ss-accent;
}

.light-card progressbar trough {
    background: rgba(0, 0, 0, 0.14);
}

.light-card progressbar progress {
    background: @ss-ink;
}

notebook,
notebook > stack,
scrolledwindow {
    background: transparent;
    border: none;
}

notebook tab {
    padding: 10px 18px;
    margin: 0 6px 8px 0;
    border-radius: 12px;
    border-bottom: 3px solid transparent;
    box-shadow: none;
    color: @ss-muted;
}

notebook tab:checked {
    background: @ss-card;
    border-bottom-color: @ss-muted;
    box-shadow: inset 0 -3px @ss-muted;
    color: @ss-ink;
}

.process-page {
    margin: 4px 0 0 0;
}

.process-card {
    background: @ss-card-dark;
    color: @ss-text;
    border-radius: 18px;
    border: 1px solid @ss-border;
    padding: 8px;
    margin: 12px 0 10px 0;
}

treeview {
    background: @ss-card-dark;
    color: @ss-text;
    border-radius: 12px;
    padding: 6px;
}

treeview header button {
    background: @ss-surface-2;
    color: @ss-muted;
    border: none;
    padding: 8px;
}

treeview header button:hover {
    background: @ss-surface-3;
    color: @ss-text;
}

treeview:selected,
treeview.view:selected {
    background: @ss-surface-3;
    color: @ss-text;
}

.process-list {
    background: transparent;
}

.compare-flow {
    background: transparent;
}

.compare-flow flowboxchild {
    background: transparent;
    border: none;
    box-shadow: none;
    outline: none;
    padding: 0;
}

.compare-flow flowboxchild:hover,
.compare-flow flowboxchild:selected,
.compare-flow flowboxchild:focus,
.compare-flow flowboxchild:focus-visible {
    background: transparent;
    border: none;
    box-shadow: none;
    outline: none;
}

.compare-panel {
    min-width: 300px;
    margin-top: 10px;
}

.process-header {
    color: @ss-muted;
    font-size: 12px;
    font-weight: 700;
    padding: 8px 10px;
}

.process-list row {
    background: transparent;
    border-radius: 12px;
    margin: 2px 0;
    padding: 0;
}

.process-row {
    padding: 9px 12px;
    color: @ss-text;
    border-radius: 10px;
}

.process-list row:hover .process-row {
    background: @ss-surface-3;
}

.alert-high {
    color: @ss-danger;
    font-weight: 700;
}

.alert-medium {
    color: @ss-warning;
    font-weight: 700;
}

.inline-alert {
    font-size: 11px;
    font-weight: 700;
    margin-top: 1px;
}

.alert-card-medium {
    border-color: rgba(229, 192, 123, 0.48);
}

.alert-card-high {
    border-color: rgba(255, 123, 114, 0.58);
}

.alert-indicator {
    border-radius: 12px;
    padding: 8px;
    color: @ss-muted;
    background: rgba(232, 228, 216, 0.05);
}

.alert-indicator-ok {
    color: @ss-success;
}

.alert-indicator-medium {
    color: @ss-warning;
}

.alert-indicator-high {
    color: @ss-danger;
}

.prefs-button {
    border-radius: 12px;
    padding: 8px;
    color: @ss-muted;
    background: rgba(232, 228, 216, 0.05);
}

.prefs-button:hover {
    background: @ss-card-hover;
    color: @ss-text;
}

.prefs-popover {
    padding: 14px;
    min-width: 260px;
    background: @ss-surface;
    color: @ss-text;
    border: 1px solid rgba(232, 228, 216, 0.10);
    border-radius: 16px;
    box-shadow: 0 14px 34px rgba(0, 0, 0, 0.28);
}

.prefs-row {
    padding: 6px 0;
}

popover.alert-guide-popover > contents {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
}

.alert-popover {
    padding: 14px;
    min-width: 240px;
    background: @ss-surface;
    color: @ss-text;
    border: 1px solid rgba(232, 228, 216, 0.10);
    border-radius: 16px;
    box-shadow: 0 14px 34px rgba(0, 0, 0, 0.28);
}

.alert-guide-title {
    color: @ss-text;
    font-size: 15px;
    font-weight: 800;
}

.alert-guide-subtitle {
    color: @ss-muted;
    font-size: 12px;
}

.alert-guide-row {
    background: @ss-card-dark;
    border: 1px solid @ss-border;
    border-radius: 12px;
    padding: 10px;
}

.alert-guide-row.high {
    border-color: rgba(255, 123, 114, 0.42);
}

.alert-guide-row.medium {
    border-color: rgba(229, 192, 123, 0.36);
}

.alert-guide-chip {
    font-size: 10px;
    font-weight: 800;
    border-radius: 999px;
    padding: 2px 7px;
}

.alert-guide-chip.high {
    color: @ss-danger;
    background: rgba(255, 123, 114, 0.12);
}

.alert-guide-chip.medium {
    color: @ss-warning;
    background: rgba(229, 192, 123, 0.12);
}
"""


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
        css_provider.load_from_data(SYSSENSE_CSS.encode())
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
        shell = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        shell.get_style_context().add_class("dashboard-shell")
        shell.set_hexpand(True)
        shell.set_vexpand(True)
        
        # Notebook usado como stack de páginas; a navegação visual fica na sidebar.
        self.notebook = Gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        
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
        
        self.notebook.set_hexpand(True)
        self.notebook.set_vexpand(True)
        content.append(self.notebook)
        shell.append(content)
        
        return shell

    def _create_sidebar(self) -> Gtk.Widget:
        """Cria a barra lateral de navegação."""
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sidebar.get_style_context().add_class("sidebar")
        sidebar.set_size_request(132, -1)
        sidebar.set_hexpand(False)
        sidebar.set_halign(Gtk.Align.START)
        self.sidebar = sidebar
        self.nav_labels = []
        self.nav_icons = []
        
        self.nav_buttons = []
        items = [
            ("Visão Geral", "view-grid-symbolic", 0),
            ("Processos", "view-list-symbolic", 1),
            ("Disco", "drive-harddisk-symbolic", 2),
            ("Serviços", "applications-system-symbolic", 3),
        ]
        for title, icon_name, page in items:
            button = self._create_nav_button(title, icon_name, page)
            sidebar.append(button)
            self.nav_buttons.append(button)
        
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        sidebar.append(spacer)

        status_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        status_row.append(self._create_alert_indicator())
        status_row.append(self._create_preferences_button())
        sidebar.append(status_row)
        
        footer = Gtk.Label(label="Auto refresh: 2.5s")
        footer.set_wrap(True)
        footer.set_halign(Gtk.Align.START)
        footer.get_style_context().add_class("brand-subtitle")
        sidebar.append(footer)
        self.nav_footer = footer
        self._set_active_nav(0)
        GLib.timeout_add(350, self._update_responsive_sidebar)
        
        return sidebar

    def _create_alert_indicator(self) -> Gtk.Widget:
        """Cria indicador automático de alertas na sidebar."""
        button = Gtk.MenuButton()
        button.set_icon_name("emblem-ok-symbolic")
        button.set_has_tooltip(False)
        button.get_style_context().add_class("alert-indicator")
        button.get_style_context().add_class("alert-indicator-ok")
        self.alert_indicator = button

        popover = Gtk.Popover()
        popover.get_style_context().add_class("alert-guide-popover")
        popover.set_position(Gtk.PositionType.RIGHT)
        popover_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        popover_box.get_style_context().add_class("alert-popover")
        popover_box.set_size_request(260, -1)
        self.alert_popover_box = popover_box
        self.alert_popover_title = Gtk.Label(label="Status do Sistema")
        self.alert_popover_title.set_halign(Gtk.Align.START)
        self.alert_popover_title.get_style_context().add_class("alert-guide-title")
        popover_box.append(self.alert_popover_title)
        self.alert_popover_subtitle = Gtk.Label(label="Nenhum alerta ativo.")
        self.alert_popover_subtitle.set_wrap(True)
        self.alert_popover_subtitle.set_xalign(0)
        self.alert_popover_subtitle.set_halign(Gtk.Align.START)
        self.alert_popover_subtitle.set_width_chars(28)
        self.alert_popover_subtitle.set_max_width_chars(28)
        self.alert_popover_subtitle.get_style_context().add_class("alert-guide-subtitle")
        popover_box.append(self.alert_popover_subtitle)
        self.alert_popover_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        popover_box.append(self.alert_popover_list)
        popover.set_child(popover_box)
        button.set_popover(popover)

        return button

    def _create_preferences_button(self) -> Gtk.Widget:
        """Cria popover de preferências mínimas."""
        button = Gtk.Button.new_from_icon_name("emblem-system-symbolic")
        button.set_has_frame(False)
        button.get_style_context().add_class("prefs-button")
        self.preferences_button = button

        popover = Gtk.Popover()
        popover.set_position(Gtk.PositionType.RIGHT)
        popover.set_autohide(True)
        if hasattr(popover, "set_cascade_popdown"):
            popover.set_cascade_popdown(True)
        popover_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        popover_box.get_style_context().add_class("prefs-popover")

        title = Gtk.Label(label="Preferências")
        title.set_halign(Gtk.Align.START)
        title.get_style_context().add_class("alert-guide-title")
        popover_box.append(title)

        refresh_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        refresh_row.get_style_context().add_class("prefs-row")
        refresh_label = Gtk.Label(label="Atualização")
        refresh_label.set_halign(Gtk.Align.START)
        refresh_label.set_hexpand(True)
        refresh_row.append(refresh_label)
        self.refresh_combo = Gtk.ComboBoxText()
        for value in config.REFRESH_OPTIONS_SECONDS:
            self.refresh_combo.append_text(self._format_refresh_option(value))
        active_index = config.REFRESH_OPTIONS_SECONDS.index(self.user_config["refresh_interval"])
        self.refresh_combo.set_active(active_index)
        self.refresh_combo.connect("changed", self._on_refresh_preference_changed)
        refresh_row.append(self.refresh_combo)
        popover_box.append(refresh_row)

        toast_switch = Gtk.Switch()
        toast_switch.set_active(self.user_config["critical_toasts"])
        toast_switch.connect("notify::active", self._on_bool_preference_changed, "critical_toasts")
        popover_box.append(self._create_switch_row("Toasts críticos", toast_switch))

        cards_title = Gtk.Label(label="Cards da dashboard")
        cards_title.set_halign(Gtk.Align.START)
        cards_title.get_style_context().add_class("alert-guide-subtitle")
        popover_box.append(cards_title)

        self.card_switches = {}
        card_labels = {
            "cpu": "CPU",
            "memory": "Memória",
            "storage": "Armazenamento",
            "temperature": "Temperatura",
            "network": "Rede",
            "load": "Carga",
            "uptime": "Tempo ligado",
            "internet": "Internet",
        }
        for key, label in card_labels.items():
            switch = Gtk.Switch()
            switch.set_active(self.user_config["visible_cards"][key])
            switch.connect("notify::active", self._on_card_visibility_changed, key)
            self.card_switches[key] = switch
            popover_box.append(self._create_switch_row(label, switch))

        popover.set_child(popover_box)
        popover.set_parent(button)
        button.connect("clicked", self._toggle_preferences_popover)
        self.preferences_popover = popover
        return button

    def _toggle_preferences_popover(self, _button: Gtk.Button):
        """Abre ou fecha o popover de preferências."""
        if self.preferences_popover.get_visible():
            self.preferences_popover.popdown()
        else:
            self.preferences_popover.popup()

    def _create_switch_row(self, label_text: str, switch: Gtk.Switch) -> Gtk.Widget:
        """Cria linha de preferência com switch."""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.get_style_context().add_class("prefs-row")
        label = Gtk.Label(label=label_text)
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        row.append(label)
        row.append(switch)
        return row

    def _format_refresh_option(self, seconds: float) -> str:
        """Formata opção de intervalo."""
        return f"{int(seconds)}s" if seconds.is_integer() else f"{seconds:.1f}s"

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
        GLib.idle_add(self._close_preferences_popover)

    def _close_preferences_popover(self) -> bool:
        """Fecha o popover de preferências quando uma ação discreta termina."""
        if hasattr(self, "preferences_popover"):
            self.preferences_popover.popdown()
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

    def _restart_refresh_timer(self):
        """Reinicia timer de atualização automática."""
        if self.refresh_timer_id is not None:
            GLib.source_remove(self.refresh_timer_id)
        interval_ms = int(self.user_config["refresh_interval"] * 1000)
        self.refresh_timer_id = GLib.timeout_add(interval_ms, self._on_auto_refresh)

    def _create_nav_button(self, title: str, icon_name: str, page: int) -> Gtk.Widget:
        """Cria um botão de navegação da sidebar."""
        button = Gtk.Button()
        button.get_style_context().add_class("nav-item")
        button.set_has_frame(False)
        button.set_hexpand(True)
        button.set_tooltip_text(title)
        button.connect('clicked', self._on_nav_clicked, page)
        
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.set_halign(Gtk.Align.START)
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(16)
        icon.get_style_context().add_class("nav-icon")
        self.nav_icons.append(icon)
        label = Gtk.Label(label=title)
        label.set_halign(Gtk.Align.START)
        label.set_xalign(0)
        label.set_hexpand(True)
        label.set_width_chars(8)
        label.set_max_width_chars(10)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        row.append(icon)
        row.append(label)
        button.set_child(row)
        self.nav_labels.append(label)
        
        return button

    def _on_nav_clicked(self, button: Gtk.Button, page: int):
        """Alterna páginas pelo menu lateral."""
        self.notebook.set_current_page(page)
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
        for label in self.nav_labels:
            label.set_visible(not compact)
        self.nav_footer.set_visible(not compact)
        return True
    
    def _create_tabs(self):
        """Cria todas as abas do aplicativo."""
        # Aba 1: Visão Geral
        overview_box = self._create_overview_tab()
        overview_label = Gtk.Label(label="Visão Geral")
        self.notebook.append_page(overview_box, overview_label)
        
        # Aba 2: Processos
        processes_box = self._create_processes_tab()
        processes_label = Gtk.Label(label="Processos")
        self.notebook.append_page(processes_box, processes_label)
        
        # Aba 3: Disco
        disk_box = self._create_disk_tab()
        disk_label = Gtk.Label(label="Disco")
        self.disk_tab_label = disk_label
        self.notebook.append_page(disk_box, disk_label)
        
        # Aba 4: Serviços
        services_box = self._create_services_tab()
        services_label = Gtk.Label(label="Serviços")
        self.notebook.append_page(services_box, services_label)
        
    def _create_overview_tab(self) -> Gtk.Widget:
        """Aba de Visão Geral."""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        page.set_hexpand(True)
        page.set_vexpand(True)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        self.overview_scrolled = scrolled

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
        self.overview_flow = flow
        self.overview_cards = []
        self.overview_card_widgets = {}
        self.overview_card_flow_children = {}
        
        # CPU
        self.cpu_label = Gtk.Label()
        self.cpu_progressbar = Gtk.ProgressBar()
        self.cpu_alert_label = self._create_inline_alert_label()
        self.cpu_card = self._create_metric_card(
            "CPU",
            self.cpu_label,
            self.cpu_progressbar,
            "light-card",
            self.cpu_alert_label
        )
        self._append_overview_card(self.cpu_card, "cpu")
        
        # Memória
        self.mem_label = Gtk.Label()
        self.mem_progressbar = Gtk.ProgressBar()
        self.mem_alert_label = self._create_inline_alert_label()
        self.mem_card = self._create_metric_card(
            "Memória RAM",
            self.mem_label,
            self.mem_progressbar,
            None,
            self.mem_alert_label
        )
        self._append_overview_card(self.mem_card, "memory")
        
        # Disco
        self.disk_label = Gtk.Label()
        self.disk_progressbar = Gtk.ProgressBar()
        self.disk_alert_label = self._create_inline_alert_label()
        self.disk_overview_card = self._create_disk_overview_card()
        self._append_overview_card(self.disk_overview_card, "storage")
        
        # Temperatura
        self.temp_label = Gtk.Label()
        self.temp_card = self._create_info_card("Temperatura", self.temp_label)
        self._append_overview_card(self.temp_card, "temperature")
        
        # Rede
        self.net_label = Gtk.Label()
        self.net_card = self._create_info_card("Tráfego de Rede", self.net_label)
        self._append_overview_card(self.net_card, "network")
        
        # Load Average
        self.load_label = Gtk.Label()
        self.load_card = self._create_info_card("Carga do Sistema", self.load_label)
        self.load_card.set_tooltip_text("Carga média do sistema. Compare esses valores com a quantidade de núcleos da CPU.")
        self._append_overview_card(self.load_card, "load")
        
        # Uptime
        self.uptime_label = Gtk.Label()
        self.uptime_card = self._create_info_card("Tempo Ligado", self.uptime_label, "wide-card")
        self._append_overview_card(self.uptime_card, "uptime")
        
        speed_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        speed_panel.get_style_context().add_class("card-custom")
        speed_panel.set_size_request(210, 88)
        self.speed_panel = speed_panel
        speed_title = Gtk.Label(label="Internet")
        speed_title.set_halign(Gtk.Align.START)
        speed_title.get_style_context().add_class("section-title")
        speed_button = Gtk.Button(label="Testar Velocidade")
        speed_button.get_style_context().add_class("suggested-action")
        speed_button.connect('clicked', self._on_speedtest_clicked)
        self.speed_button = speed_button
        self.speed_result_label = Gtk.Label()
        self.speed_result_label.set_wrap(False)
        self.speed_result_label.set_single_line_mode(True)
        self.speed_result_label.set_width_chars(26)
        self.speed_result_label.set_max_width_chars(26)
        self.speed_result_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.speed_result_label.set_halign(Gtk.Align.START)
        self.speed_result_label.set_xalign(0)
        self.speed_result_label.get_style_context().add_class("subtitle-text")
        speed_panel.append(speed_title)
        speed_panel.append(speed_button)
        speed_panel.append(self.speed_result_label)
        self._append_overview_card(speed_panel, "internet")
        
        scrolled.set_child(flow)
        page.append(scrolled)
        self._apply_cards_overview_layout()
        self._apply_card_visibility()
        return page

    def _append_overview_card(self, card: Gtk.Widget, key: str):
        """Adiciona card à visão geral e guarda referência para responsividade."""
        self.overview_flow.append(card)
        self.overview_cards.append(card)
        self.overview_card_widgets[key] = card
        self.overview_card_flow_children[key] = card.get_parent()

    def _apply_cards_overview_layout(self):
        """Mantém a visão geral sempre no modo cards compactos."""
        self.overview_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        self.overview_flow.get_style_context().add_class("compact-overview")
        self.overview_flow.set_max_children_per_line(4)
        for card in self.overview_cards:
            card.set_size_request(168, 88)
        self.disk_overview_card.set_size_request(192, 140)

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
        """Aba de Processos com notebook de 3 abas."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.get_style_context().add_class("process-page")

        self.process_runtime_notice = Gtk.Label()
        self.process_runtime_notice.set_halign(Gtk.Align.START)
        self.process_runtime_notice.set_xalign(0)
        self.process_runtime_notice.set_wrap(True)
        self.process_runtime_notice.get_style_context().add_class("runtime-notice")
        self.process_runtime_notice.set_visible(False)
        vbox.append(self.process_runtime_notice)
        
        notebook = Gtk.Notebook()
        
        self.mem_list = self._create_process_list(['Processo', 'PID', 'CPU %', 'Memória %'], [3, 1, 1, 1])
        notebook.append_page(self._create_table_scroller(self.mem_list), Gtk.Label(label="Por Memória"))
        
        self.cpu_proc_list = self._create_process_list(['Processo', 'PID', 'CPU %', 'Memória %'], [3, 1, 1, 1])
        notebook.append_page(self._create_table_scroller(self.cpu_proc_list), Gtk.Label(label="Por CPU"))
        
        compare_flow = Gtk.FlowBox()
        compare_flow.get_style_context().add_class("compare-flow")
        compare_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        compare_flow.set_min_children_per_line(1)
        compare_flow.set_max_children_per_line(2)
        compare_flow.set_column_spacing(10)
        compare_flow.set_row_spacing(10)
        compare_flow.set_homogeneous(True)
        
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        left_box.get_style_context().add_class("compare-panel")
        left_box.set_margin_start(8)
        left_box.set_margin_end(4)
        left_label = Gtk.Label(label="Por Memória")
        left_label.get_style_context().add_class("section-title")
        left_box.append(left_label)
        self.compare_mem_list = self._create_process_list(['Processo', 'Memória %'], [2, 1], base_width=72)
        left_box.append(self._create_table_scroller(self.compare_mem_list, min_height=400))
        
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        right_box.get_style_context().add_class("compare-panel")
        right_box.set_margin_start(4)
        right_box.set_margin_end(8)
        right_label = Gtk.Label(label="Por CPU")
        right_label.get_style_context().add_class("section-title")
        right_box.append(right_label)
        self.compare_cpu_list = self._create_process_list(['Processo', 'CPU %'], [2, 1], base_width=72)
        right_box.append(self._create_table_scroller(self.compare_cpu_list, min_height=400))
        
        left_box.set_hexpand(True)
        left_box.set_vexpand(True)
        right_box.set_hexpand(True)
        right_box.set_vexpand(True)
        compare_flow.append(left_box)
        compare_flow.append(right_box)
        
        notebook.append_page(compare_flow, Gtk.Label(label="Comparar"))
        
        notebook.set_hexpand(True)
        notebook.set_vexpand(True)
        vbox.append(notebook)
        return vbox
    
    def _create_disk_tab(self) -> Gtk.Widget:
        """Aba de Disco."""
        scrolled = Gtk.ScrolledWindow()
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        
        self.disk_partitions_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.append(self.disk_partitions_box)
        
        scrolled.set_child(vbox)
        return scrolled
    
    def _create_services_tab(self) -> Gtk.Widget:
        """Aba de Serviços."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        refresh_button = Gtk.Button(label="Atualizar")
        refresh_button.connect('clicked', self._on_refresh_services)
        controls.append(refresh_button)
        self.services_refresh_button = refresh_button
        self.services_status_label = Gtk.Label(label="Atualizado sob demanda")
        self.services_status_label.set_halign(Gtk.Align.START)
        self.services_status_label.get_style_context().add_class("status-pill")
        controls.append(self.services_status_label)
        vbox.append(controls)
        
        scrolled = Gtk.ScrolledWindow()
        self.services_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scrolled.set_child(self.services_box)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        vbox.append(scrolled)
        
        return vbox
    
    def _create_disk_overview_card(self) -> Gtk.Widget:
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
        self.disk_partition_combo = Gtk.ComboBoxText()
        self.disk_partition_combo.get_style_context().add_class("disk-partition-combo")
        self.disk_partition_combo.set_size_request(78, -1)
        self.disk_partition_combo.append_text("Tudo")
        self.disk_partition_combo.set_active(0)
        self.disk_partition_combo.connect('changed', self._on_disk_partition_changed)
        header.append(title)
        header.append(self.disk_partition_combo)
        card.append(header)

        chart_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        chart_row.get_style_context().add_class("disk-chart-row")
        chart_row.set_size_request(204, 92)
        self.disk_chart = Gtk.DrawingArea()
        self.disk_chart.set_size_request(92, 92)
        self.disk_chart.set_content_width(92)
        self.disk_chart.set_content_height(92)
        self.disk_chart.set_draw_func(self._draw_disk_chart)
        chart_row.append(self.disk_chart)

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info_box.get_style_context().add_class("disk-info-box")
        info_box.set_size_request(118, 86)
        info_box.set_valign(Gtk.Align.CENTER)
        self.disk_label.set_halign(Gtk.Align.START)
        self.disk_label.set_xalign(0)
        self.disk_label.set_wrap(False)
        self.disk_label.set_width_chars(16)
        self.disk_label.set_max_width_chars(16)
        self.disk_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.disk_label.get_style_context().add_class("subtitle-text")
        self.disk_chart_detail_label = Gtk.Label(label="Aguardando dados")
        self.disk_chart_detail_label.set_halign(Gtk.Align.START)
        self.disk_chart_detail_label.set_xalign(0)
        self.disk_chart_detail_label.set_wrap(False)
        self.disk_chart_detail_label.set_width_chars(16)
        self.disk_chart_detail_label.set_max_width_chars(16)
        self.disk_chart_detail_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.disk_chart_detail_label.get_style_context().add_class("subtitle-text")
        self.disk_progressbar.set_hexpand(True)
        info_box.append(self.disk_label)
        info_box.append(self.disk_chart_detail_label)
        info_box.append(self.disk_progressbar)
        chart_row.append(info_box)
        card.append(chart_row)
        card.append(self.disk_alert_label)

        self.disk_partitions_data = []
        self.disk_partitions_signature = None
        self.selected_disk_partition = "Tudo"
        return card

    def _on_disk_partition_changed(self, combo: Gtk.ComboBoxText):
        """Atualiza o gráfico quando a partição selecionada muda."""
        self.selected_disk_partition = combo.get_active_text() or "Tudo"
        self._update_disk_overview_card()

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
            self.disk_chart_detail_label.set_text(f"{self._format_disk_size(used)} / {self._format_disk_size(total)}")
            self.disk_progressbar.set_fraction(min(pct / 100, 1))
        else:
            part = next((p for p in partitions if self._disk_partition_title(p) == selected), partitions[0])
            pct = part.get('percent', 0)
            used = part.get('used', 0)
            total = part.get('total', 0)
            self.disk_label.set_text(f"{pct:.1f}% usado")
            self.disk_chart_detail_label.set_text(f"{self._format_disk_size(used)} / {self._format_disk_size(total)}")
            self.disk_progressbar.set_fraction(min(pct / 100, 1))
        self.disk_chart.queue_draw()

    def _format_disk_size(self, value: int | float) -> str:
        """Formata bytes de disco sem esconder partições pequenas."""
        value = float(value or 0)
        gib = value / (1024**3)
        if gib >= 1:
            return f"{gib:.1f}G"
        mib = value / (1024**2)
        return f"{mib:.0f}M"

    def _format_rate(self, bytes_per_second: float) -> str:
        """Formata uma taxa de rede em unidades legíveis."""
        value = max(float(bytes_per_second or 0), 0)
        if value >= 1024**2:
            return f"{value / (1024**2):.1f} MB/s"
        if value >= 1024:
            return f"{value / 1024:.0f} KB/s"
        return f"{value:.0f} B/s"

    def _format_total_transfer(self, value: int | float) -> str:
        """Formata total acumulado de rede."""
        value = float(value or 0)
        if value >= 1024**3:
            return f"{value / (1024**3):.2f} GB"
        if value >= 1024**2:
            return f"{value / (1024**2):.1f} MB"
        return f"{value / 1024:.0f} KB"

    def _format_network_text(self, rede: Dict[str, Any]) -> tuple[str, str]:
        """Calcula velocidade atual de rede e tooltip com acumulado."""
        now = time.monotonic()
        sent = rede.get('bytes_sent', 0)
        recv = rede.get('bytes_recv', 0)
        tooltip = (
            f"Acumulado recebido: {self._format_total_transfer(recv)}\n"
            f"Acumulado enviado: {self._format_total_transfer(sent)}"
        )

        previous = self.previous_network_sample
        self.previous_network_sample = {
            'time': now,
            'bytes_sent': sent,
            'bytes_recv': recv,
        }
        if not previous:
            return "↓ 0 B/s | ↑ 0 B/s", tooltip

        elapsed = max(now - previous.get('time', now), 0.1)
        down_rate = max(recv - previous.get('bytes_recv', recv), 0) / elapsed
        up_rate = max(sent - previous.get('bytes_sent', sent), 0) / elapsed
        return f"↓ {self._format_rate(down_rate)} | ↑ {self._format_rate(up_rate)}", tooltip

    def _sync_disk_partition_combo(self, partitions: list):
        """Sincroniza opções do seletor de partições."""
        signature = tuple(self._disk_partition_title(part) for part in partitions)
        if signature == self.disk_partitions_signature:
            return
        current = getattr(self, 'selected_disk_partition', "Tudo")
        self.disk_partition_combo.remove_all()
        self.disk_partition_combo.append_text("Tudo")
        for title in signature:
            self.disk_partition_combo.append_text(title)
        active = 0
        if current in signature:
            active = list(signature).index(current) + 1
        self.disk_partition_combo.set_active(active)
        self.disk_partitions_signature = signature
        self.selected_disk_partition = self.disk_partition_combo.get_active_text() or "Tudo"

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

    def _create_metric_card(
        self,
        title: str,
        label: Gtk.Label,
        progress: Gtk.ProgressBar,
        extra_class: str | None = None,
        alert_label: Gtk.Label | None = None
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

    def _create_inline_alert_label(self) -> Gtk.Label:
        """Cria um texto curto de alerta para cards."""
        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_xalign(0)
        label.get_style_context().add_class("inline-alert")
        label.set_visible(False)
        return label
    
    def _create_info_card(self, title: str, label: Gtk.Label, extra_class: str | None = None) -> Gtk.Widget:
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
    
    def _create_process_list(self, headers: list[str], weights: list[int], base_width: int = 94) -> Gtk.Widget:
        """Cria lista de processos com hover unificado por linha."""
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        outer.get_style_context().add_class("process-list")
        outer.process_weights = weights
        outer.process_base_width = base_width

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.get_style_context().add_class("process-header")
        for title, weight in zip(headers, weights):
            label = Gtk.Label(label=title)
            label.set_xalign(0 if title == 'Processo' else 0.5)
            label.set_hexpand(True)
            label.set_size_request(base_width * weight, -1)
            header.append(label)
        outer.append(header)

        listbox = Gtk.ListBox()
        listbox.get_style_context().add_class("process-list")
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        outer.process_listbox = listbox
        outer.append(listbox)
        return outer

    def _append_process_row(self, process_list: Gtk.Widget, values: list[str]):
        """Adiciona uma linha de processo a uma lista."""
        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.get_style_context().add_class("process-row")
        weights = getattr(process_list, 'process_weights', [1] * len(values))
        base_width = getattr(process_list, 'process_base_width', 94)
        for i, (value, weight) in enumerate(zip(values, weights)):
            label = Gtk.Label(label=str(value))
            label.set_xalign(0 if i == 0 else 0.5)
            label.set_ellipsize(Pango.EllipsizeMode.END)
            label.set_tooltip_text(str(value))
            label.set_hexpand(True)
            label.set_size_request(base_width * weight, -1)
            box.append(label)
        row.set_child(box)
        process_list.process_listbox.append(row)

    def _clear_process_list(self, process_list: Gtk.Widget):
        """Remove todas as linhas de uma lista de processos."""
        self._clear_box(process_list.process_listbox)

    def _create_table_scroller(self, child: Gtk.Widget, min_height: int = 420) -> Gtk.Widget:
        """Cria uma área de tabela com respiro visual."""
        scrolled = Gtk.ScrolledWindow()
        scrolled.get_style_context().add_class("process-card")
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(min_height)
        scrolled.set_child(child)
        return scrolled

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
            text = "Erro no teste"
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
        self._sync_disk_partition_combo(self.disk_partitions_data)
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
        self.load_label.set_text(f"1min: {load.get('1min', 0):.2f} | 5min: {load.get('5min', 0):.2f} | 15min: {load.get('15min', 0):.2f}")
        
        self.uptime_label.set_text(self._format_uptime(uptime))
    
    def _format_uptime(self, uptime: Dict[str, Any]) -> str:
        """Formata o tempo ligado mesmo quando só há segundos disponíveis."""
        if uptime.get('uptime_formatted'):
            return uptime['uptime_formatted']
        seconds = uptime.get('uptime_seconds')
        if seconds is None:
            return 'N/A'
        days = int(seconds) // 86400
        hours = (int(seconds) % 86400) // 3600
        minutes = (int(seconds) % 3600) // 60
        return f"{days}d {hours}h {minutes}m"

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
        label: Gtk.Label,
        severity: str | None,
        text: str
    ):
        """Aplica ou remove borda e texto curto de alerta em um card."""
        context = card.get_style_context()
        context.remove_class("alert-card-medium")
        context.remove_class("alert-card-high")
        label.get_style_context().remove_class("alert-medium")
        label.get_style_context().remove_class("alert-high")

        if not severity:
            label.set_visible(False)
            label.set_text("")
            return

        if severity == "alta":
            context.add_class("alert-card-high")
            label.get_style_context().add_class("alert-high")
            label.set_text(f"Crítico: {text}")
        else:
            context.add_class("alert-card-medium")
            label.get_style_context().add_class("alert-medium")
            label.set_text(f"Atenção: {text}")
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
        
        self._clear_process_list(self.mem_list)
        for proc in procs.get('by_memory', []):
            self._append_process_row(self.mem_list, [
                proc['name'],
                proc['pid'],
                f"{proc.get('cpu_percent', 0):.1f}",
                f"{proc.get('memory_percent', 0):.1f}",
            ])
        
        self._clear_process_list(self.cpu_proc_list)
        for proc in procs.get('by_cpu', []):
            self._append_process_row(self.cpu_proc_list, [
                proc['name'],
                proc['pid'],
                f"{proc.get('cpu_percent', 0):.1f}",
                f"{proc.get('memory_percent', 0):.1f}",
            ])
        
        self._clear_process_list(self.compare_mem_list)
        for proc in procs.get('by_memory', [])[:10]:
            self._append_process_row(self.compare_mem_list, [proc['name'], f"{proc.get('memory_percent', 0):.1f}"])
        
        self._clear_process_list(self.compare_cpu_list)
        for proc in procs.get('by_cpu', [])[:10]:
            self._append_process_row(self.compare_cpu_list, [proc['name'], f"{proc.get('cpu_percent', 0):.1f}"])
    
    def _update_disk(self, data: Dict[str, Any]):
        """Atualiza Disco."""
        self._clear_box(self.disk_partitions_box)
        
        disco = data.get('disco', {})
        
        for part in disco.get('partitions', []):
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            card.get_style_context().add_class("card-custom")
            
            name_label = Gtk.Label()
            name_label.set_markup(f"<b>{part['device']}</b> • {part['mountpoint']}")
            name_label.set_halign(Gtk.Align.START)
            card.append(name_label)
            
            total_gb = part['total'] / (1024**3)
            used_gb = part['used'] / (1024**3)
            free_gb = part['free'] / (1024**3)
            pct = part['percent']
            
            info_label = Gtk.Label()
            info_label.set_text(
                f"Usado: {used_gb:.1f} GB / {total_gb:.1f} GB ({pct:.1f}%) | "
                f"Livre: {free_gb:.1f} GB | {part.get('fstype', 'fs')}"
            )
            info_label.set_halign(Gtk.Align.START)
            info_label.get_style_context().add_class("subtitle-text")
            card.append(info_label)
            
            pbar = Gtk.ProgressBar()
            pbar.set_fraction(pct / 100)
            card.append(pbar)
            
            if pct > 70:
                alert_label = Gtk.Label()
                alert_label.set_text("⚠️ Espaço em disco limitado")
                alert_label.get_style_context().add_class("alert-medium")
                alert_label.set_halign(Gtk.Align.START)
                card.append(alert_label)
            
            self.disk_partitions_box.append(card)
        
    
    def _update_services(self, services: Dict[str, Any], logs: Dict[str, Any]):
        """Atualiza Serviços."""
        self._clear_box(self.services_box)
        
        failed_count = services.get('count', 0)
        service_error = services.get('error')
        logs_error = logs.get('error')

        if service_error:
            state_label = Gtk.Label()
            state_label.set_markup("<b>Indisponível</b>")
            state_label.set_halign(Gtk.Align.START)
            self.services_box.append(state_label)
            error_label = Gtk.Label(label=f"Serviços indisponíveis: {service_error}")
            error_label.set_wrap(True)
            error_label.set_halign(Gtk.Align.START)
            error_label.get_style_context().add_class("alert-medium")
            self.services_box.append(error_label)
        
        if failed_count == 0 and not service_error:
            state_label = Gtk.Label()
            state_label.set_markup("<b>Tudo certo</b>")
            state_label.set_halign(Gtk.Align.START)
            self.services_box.append(state_label)
            label = Gtk.Label(label="Nenhum serviço systemd com falha foi encontrado.")
            label.get_style_context().add_class("subtitle-text")
            label.set_halign(Gtk.Align.START)
            self.services_box.append(label)
        else:
            title = Gtk.Label()
            title.set_markup(f"<b>Falhas detectadas</b> • {failed_count} serviço(s)")
            title.set_halign(Gtk.Align.START)
            if failed_count:
                self.services_box.append(title)
            
            for service in services.get('failed_services', []):
                service_label = Gtk.Label()
                name = html.escape(service.get('name', 'Serviço desconhecido'))
                state = html.escape(service.get('state', 'estado desconhecido'))
                service_label.set_markup(f"<b>{name}</b> [{state}]")
                service_label.set_halign(Gtk.Align.START)
                self.services_box.append(service_label)
        
        logs_title = Gtk.Label()
        logs_title.set_markup(f"<b>Logs Recentes</b>")
        logs_title.set_halign(Gtk.Align.START)
        logs_title.set_margin_top(16)
        self.services_box.append(logs_title)

        log_lines = logs.get('logs', [])[-20:]
        if logs_error:
            log_error_label = Gtk.Label(label=f"Logs indisponíveis: {logs_error}")
            log_error_label.set_wrap(True)
            log_error_label.set_halign(Gtk.Align.START)
            log_error_label.get_style_context().add_class("alert-medium")
            self.services_box.append(log_error_label)
        elif not log_lines:
            empty_logs_label = Gtk.Label(label="Nenhum log recente retornado.")
            empty_logs_label.set_halign(Gtk.Align.START)
            empty_logs_label.get_style_context().add_class("subtitle-text")
            self.services_box.append(empty_logs_label)

        for log_line in log_lines:
            log_label = Gtk.Label(label=log_line.strip())
            log_label.set_wrap(True)
            log_label.set_halign(Gtk.Align.START)
            log_label.get_style_context().add_class("subtitle-text")
            self.services_box.append(log_label)
        
