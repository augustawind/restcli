from typing import Sequence

from prompt_toolkit.application import get_app
from prompt_toolkit.completion.filesystem import PathCompleter
from prompt_toolkit.shortcuts import input_dialog

from ..menu import MenuContainer, MenuHandler, MenuItem

__all__ = ["end_program", "toggle_focus", "open_file"]


def end_program(handler=None):
    get_app().exit()


@MenuHandler.register
def toggle_focus(self, menu: MenuContainer, items: Sequence[MenuItem]):
    def handler(event=None):
        layout = get_app().layout
        selection = menu.get_menu_selection(item.name for item in items)
        if layout.has_focus(menu.window) and menu.selected_menu == selection:
            for _ in range(menu._breadcrumb):
                layout.focus_last()
        else:
            layout.focus(menu.window)
            menu.selected_menu[:] = selection
            menu._breadcrumb += 1

    return handler
