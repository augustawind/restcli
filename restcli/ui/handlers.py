from __future__ import annotations

from asyncio import ensure_future

from restcli.ui.dialogs import NewFileDialog, OpenFileDialog
from restcli.ui.menu import MenuHandler

__all__ = ["EndProgram", "ToggleFocus", "OpenFile"]


class EndProgram(MenuHandler):
    def __call__(self, event=None):
        self.ui.app.exit()


class ToggleFocus(MenuHandler):
    def __call__(self, event=None):
        layout = self.ui.app.layout
        selection = self.ui.root_container.get_menu_selection(
            item.name for item in self.items
        )
        if (
            layout.has_focus(self.ui.root_container.window)
            and self.ui.root_container.selected_menu == selection
        ):
            for _ in range(self.ui.root_container.breadcrumb):
                layout.focus_last()
        else:
            layout.focus(self.ui.root_container.window)
            self.ui.root_container.selected_menu[:] = selection
            self.ui.root_container.breadcrumb += 1


class NewFile(MenuHandler):
    def __call__(self, event=None):
        ensure_future(self.run_dialog())

    async def run_dialog(self):
        dialog = NewFileDialog(self.ui)
        document = await dialog.run()
        self.ui.editor.load_collection(document)


class OpenFile(MenuHandler):
    def __call__(self, event=None):
        ensure_future(self.run_dialog())

    async def run_dialog(self):
        open_dialog = OpenFileDialog(self.ui)
        document = await open_dialog.run()
        if not document:
            return
        self.ui.editor.load_collection(document)


class SaveActiveTab(MenuHandler):
    def __call__(self, event=None):
        self.ui.editor.content.active_tab.save_changes()
        self.ui.editor.redraw()
