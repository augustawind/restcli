from prompt_toolkit.application import get_app

from ..menu import MenuHandler


def exit(handler=None):
    get_app().exit()


@MenuHandler.register
def toggle_focus(self, menu, item):
    def handler(event=None):
        layout = get_app().layout
        selection = menu.get_menu_selection(item.name)
        if layout.has_focus(menu.window) and menu.selected_menu == selection:
            for _ in range(menu._breadcrumb):
                layout.focus_last()
        else:
            layout.focus(menu.window)
            menu.selected_menu[:] = selection
            menu._breadcrumb += 1

    return handler
