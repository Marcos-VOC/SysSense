"""Tela de processos do SysSense."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from gi.repository import Gtk, Pango


ProcessTabCallback = Callable[[Gtk.Button, str], None]


@dataclass
class ProcessRefs:
    """Referências da aba de processos usadas pela janela principal."""

    page: Gtk.Widget
    runtime_notice: Gtk.Label
    tab_buttons: list[Gtk.Button]
    stack: Gtk.Stack
    mem_list: Gtk.Widget
    cpu_proc_list: Gtk.Widget
    compare_mem_list: Gtk.Widget
    compare_cpu_list: Gtk.Widget


def build_processes_tab(on_tab_clicked: ProcessTabCallback) -> ProcessRefs:
    """Cria a aba de Processos com navegação interna."""
    page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    page.get_style_context().add_class("process-page")

    runtime_notice = Gtk.Label()
    runtime_notice.set_halign(Gtk.Align.START)
    runtime_notice.set_xalign(0)
    runtime_notice.set_wrap(True)
    runtime_notice.get_style_context().add_class("runtime-notice")
    runtime_notice.set_visible(False)
    page.append(runtime_notice)

    tab_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    tab_bar.get_style_context().add_class("process-tab-bar")
    tab_buttons: list[Gtk.Button] = []
    for label, page_name in (
        ("Por Memória", "memory"),
        ("Por CPU", "cpu"),
        ("Comparar", "compare"),
    ):
        button = _create_process_tab_button(label, page_name, on_tab_clicked)
        tab_buttons.append(button)
        tab_bar.append(button)
    page.append(tab_bar)

    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
    stack.set_transition_duration(160)

    mem_list = create_process_list(["Processo", "PID", "CPU %", "Memória %"], [3, 1, 1, 1])
    stack.add_named(create_table_scroller(mem_list), "memory")

    cpu_proc_list = create_process_list(["Processo", "PID", "CPU %", "Memória %"], [3, 1, 1, 1])
    stack.add_named(create_table_scroller(cpu_proc_list), "cpu")

    compare_mem_list = create_process_list(["Processo", "Memória %"], [2, 1], base_width=72)
    compare_cpu_list = create_process_list(["Processo", "CPU %"], [2, 1], base_width=72)
    stack.add_named(_create_compare_page(compare_mem_list, compare_cpu_list), "compare")

    stack.set_visible_child_name("memory")
    stack.set_hexpand(True)
    stack.set_vexpand(True)
    page.append(stack)

    return ProcessRefs(
        page=page,
        runtime_notice=runtime_notice,
        tab_buttons=tab_buttons,
        stack=stack,
        mem_list=mem_list,
        cpu_proc_list=cpu_proc_list,
        compare_mem_list=compare_mem_list,
        compare_cpu_list=compare_cpu_list,
    )


def set_active_process_tab(tab_buttons: list[Gtk.Button], page_name: str):
    """Marca botão ativo da navegação interna de Processos."""
    names = ("memory", "cpu", "compare")
    for button, name in zip(tab_buttons, names):
        if name == page_name:
            button.get_style_context().add_class("active")
        else:
            button.get_style_context().remove_class("active")


def create_process_list(headers: list[str], weights: list[int], base_width: int = 94) -> Gtk.Widget:
    """Cria lista de processos com hover unificado por linha."""
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    outer.get_style_context().add_class("process-list")
    outer.process_weights = weights
    outer.process_base_width = base_width

    header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    header.get_style_context().add_class("process-header")
    for title, weight in zip(headers, weights):
        label = Gtk.Label(label=title)
        label.set_xalign(0 if title == "Processo" else 0.5)
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


def append_process_row(process_list: Gtk.Widget, values: list[str]):
    """Adiciona uma linha de processo a uma lista."""
    row = Gtk.ListBoxRow()
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    box.get_style_context().add_class("process-row")
    weights = getattr(process_list, "process_weights", [1] * len(values))
    base_width = getattr(process_list, "process_base_width", 94)
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


def clear_process_list(process_list: Gtk.Widget):
    """Remove todas as linhas de uma lista de processos."""
    child = process_list.process_listbox.get_first_child()
    while child is not None:
        process_list.process_listbox.remove(child)
        child = process_list.process_listbox.get_first_child()


def create_table_scroller(child: Gtk.Widget, min_height: int = 420) -> Gtk.Widget:
    """Cria uma área de tabela com respiro visual."""
    scrolled = Gtk.ScrolledWindow()
    scrolled.get_style_context().add_class("process-card")
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled.set_min_content_height(min_height)
    scrolled.set_child(child)
    return scrolled


def _create_process_tab_button(
    label: str,
    page_name: str,
    on_tab_clicked: ProcessTabCallback,
) -> Gtk.Widget:
    """Cria botão de navegação interna da aba Processos."""
    button = Gtk.Button(label=label)
    button.set_has_frame(False)
    button.get_style_context().add_class("process-tab-button")
    button.connect("clicked", on_tab_clicked, page_name)
    return button


def _create_compare_page(mem_list: Gtk.Widget, cpu_list: Gtk.Widget) -> Gtk.Widget:
    """Cria página comparativa de memória e CPU."""
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
    left_box.append(create_table_scroller(mem_list, min_height=400))

    right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    right_box.get_style_context().add_class("compare-panel")
    right_box.set_margin_start(4)
    right_box.set_margin_end(8)
    right_label = Gtk.Label(label="Por CPU")
    right_label.get_style_context().add_class("section-title")
    right_box.append(right_label)
    right_box.append(create_table_scroller(cpu_list, min_height=400))

    left_box.set_hexpand(True)
    left_box.set_vexpand(True)
    right_box.set_hexpand(True)
    right_box.set_vexpand(True)
    compare_flow.append(left_box)
    compare_flow.append(right_box)
    return compare_flow
