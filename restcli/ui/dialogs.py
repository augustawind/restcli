from __future__ import annotations

from asyncio import Future
from typing import TYPE_CHECKING

from prompt_toolkit.completion.filesystem import PathCompleter
from prompt_toolkit.layout.containers import Float, HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Label, RadioList, TextArea

from restcli.workspace import Collection, Environment

if TYPE_CHECKING:
    from restcli.ui import UI


# noinspection PyTypeChecker
class OpenDocumentDialog(Dialog):
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
        self.ui.app.layout.focus(self.ok_button)
        buf.complete_state = None
        return True

    async def run(self):
        float_ = Float(self)
        self.ui.root_container.floats.insert(0, float_)

        self.ui.app.layout.focus(self)
        result = await self.future
        self.ui.app.layout.focus_last()

        if float_ in self.ui.root_container.floats:
            self.ui.root_container.floats.remove(float_)

        return result
