from __future__ import annotations

from asyncio import Future, ensure_future
from typing import TYPE_CHECKING, Sequence

from prompt_toolkit.application import get_app
from prompt_toolkit.completion.filesystem import PathCompleter
from prompt_toolkit.layout.containers import Float, HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.shortcuts import input_dialog
from prompt_toolkit.widgets import Button, Dialog, Label, RadioList, TextArea

from restcli.ui.menu import MenuHandler, MenuItem

if TYPE_CHECKING:
    from restcli.ui import UI

__all__ = ["end_program", "toggle_focus", "open_file"]


def end_program(handler=None):
    get_app().exit()


@MenuHandler.register
def toggle_focus(self, ui: UI, items: Sequence[MenuItem]):
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


@MenuHandler.register
def open_file(self, ui: UI, items: Sequence[MenuItem]):
    def handler(event=None):
        async def coroutine():
            open_dialog = OpenFileDialog(ui)
            file_type, path = await open_dialog.run()
            if file_type == "collection":
                ui.state.active_collection_path = path
                with open(path) as fh:
                    ui.state.raw_collection = fh.read()
                with open("log.txt", "a") as fh:
                    print(
                        f"{ui.state.active_collection_path=}, {ui.state.raw_collection=}",
                        file=fh,
                    )
            else:
                ui.state.active_env_path = path
                with open(path) as fh:
                    ui.state.raw_env = fh.read()
                with open("log.txt", "a") as fh:
                    print(
                        f"{ui.state.active_env_path=}, {ui.state.raw_env=}",
                        file=fh,
                    )

        ensure_future(coroutine())

    return handler


class OpenFileDialog(Dialog):
    def __init__(
        self,
        ui: UI,
        title: str = "Open file",
        text: str = "idk what to put here",
        ok_text: str = "OK",
        cancel_text: str = "Cancel",
    ):
        self.future = Future()
        self.ui = ui

        self.radio_list = RadioList(
            [("collection", "Collection"), ("environment", "Environment"),]
        )

        self.ok_button = Button(ok_text, self.handle_ok)
        self.cancel_button = Button(cancel_text, self.handle_cancel)

        self.text_area = TextArea(
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
                padding=1,
            ),
            buttons=[self.ok_button, self.cancel_button],
            modal=True,
            with_background=True,
        )

    def handle_ok(self):
        self.future.set_result(
            (self.radio_list.current_value, self.text_area.text)
        )

    def handle_cancel(self):
        self.future.set_result(None)

    def handle_accept_text(self, buf):
        self.ui.layout.focus(self.ok_button)
        buf.complete_state = None
        return True

    async def run(self):
        float_ = Float(self)
        self.ui.menu.floats.insert(0, float_)

        focused_before = self.ui.layout.current_window
        self.ui.layout.focus(self)
        result = await self.future
        self.ui.layout.focus(focused_before)

        if float_ in self.ui.menu.floats:
            self.ui.menu.floats.remove(float_)

        return result
