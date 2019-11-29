from asyncio import Future, ensure_future
from typing import Sequence

from prompt_toolkit.application import get_app
from prompt_toolkit.completion.filesystem import PathCompleter
from prompt_toolkit.layout.containers import Float, HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.shortcuts import input_dialog
from prompt_toolkit.widgets import Button, Dialog, Label, TextArea

from restcli.ui.menu import MenuHandler, MenuItem

__all__ = ["end_program", "toggle_focus", "open_file"]


def end_program(handler=None):
    get_app().exit()


@MenuHandler.register
def toggle_focus(self, ui: "UI", items: Sequence[MenuItem]):
    def handler(event=None):
        layout = get_app().layout
        selection = ui.menu.get_menu_selection(item.name for item in items)
        if (
            layout.has_focus(ui.menu.window)
            and ui.menu.selected_menu == selection
        ):
            for _ in range(ui.menu._breadcrumb):
                layout.focus_last()
        else:
            layout.focus(ui.menu.window)
            ui.menu.selected_menu[:] = selection
            ui.menu._breadcrumb += 1

    return handler
