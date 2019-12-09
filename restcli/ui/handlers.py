from __future__ import annotations

from asyncio import Future, ensure_future
from typing import TYPE_CHECKING

from prompt_toolkit.completion.filesystem import PathCompleter
from prompt_toolkit.layout.containers import Float, HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Label, RadioList, TextArea

from restcli.ui.menu import MenuHandler
from restcli.workspace import Collection, Environment

if TYPE_CHECKING:
    from restcli.ui import UI

__all__ = ["EndProgram", "ToggleFocus", "OpenFile"]


class EndProgram(MenuHandler):
    def __call__(self, event=None):
        self.ui.app.exit()


class ToggleFocus(MenuHandler):
    def __call__(self, event=None):
        layout = self.ui.layout
        selection = self.ui.menu.get_menu_selection(
            item.name for item in self.items
        )
        if (
            layout.has_focus(self.ui.menu.window)
            and self.ui.menu.selected_menu == selection
        ):
            for _ in range(self.ui.menu.breadcrumb):
                layout.focus_last()
        else:
            layout.focus(self.ui.menu.window)
            self.ui.menu.selected_menu[:] = selection
            self.ui.menu.breadcrumb += 1


class OpenFile(MenuHandler):
    def __call__(self, event=None):
        ensure_future(self.run_dialog())

    async def run_dialog(self):
        open_dialog = OpenFileDialog(self.ui)
        document = await open_dialog.run()
        if not document:
            return
        self.ui.editor.load_collection(document)


# noinspection PyTypeChecker
class OpenFileDialog(Dialog):
    def __init__(
        self,
        ui: UI,
        title: str = "Open file",
        text: str = "File path",
        ok_text: str = "OK",
        cancel_text: str = "Cancel",
    ):
        self.future = Future()
        self.ui = ui

        self.radio_list = RadioList(
            [(Collection, "Collection"), (Environment, "Environment")]
        )

        self.ok_button = Button(ok_text, self.handle_ok)
        self.cancel_button = Button(cancel_text, self.handle_cancel)

        self.text_area = TextArea(
            text="collection.yaml",
            multiline=False,
            completer=PathCompleter(),
            accept_handler=self.handle_accept_text,
        )

        super().__init__(
            title=title,
            body=HSplit(
                [
                    HSplit(
                        [
                            Label(text="File type", dont_extend_height=True),
                            self.radio_list,
                        ],
                        padding=D(preferred=1, max=1),
                    ),
                    HSplit(
                        [
                            Label(text=text, dont_extend_height=True),
                            self.text_area,
                        ],
                        padding=D(preferred=1, max=1),
                    ),
                ],
                width=D(preferred=80),
                padding=1,
            ),
            buttons=[self.ok_button, self.cancel_button],
            modal=True,
            with_background=True,
        )

    def handle_ok(self):
        document_cls = self.radio_list.current_value
        source = self.text_area.text
        self.future.set_result(document_cls(source))

    def handle_cancel(self):
        self.future.set_result(None)

    def handle_accept_text(self, buf):
        self.ui.layout.focus(self.ok_button)
        buf.complete_state = None
        return True

    async def run(self):
        float_ = Float(self)
        self.ui.menu.floats.insert(0, float_)

        self.ui.layout.focus(self)
        result = await self.future
        self.ui.layout.focus_last()

        if float_ in self.ui.menu.floats:
            self.ui.menu.floats.remove(float_)

        return result
