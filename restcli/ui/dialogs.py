from __future__ import annotations

import abc
from asyncio import Future
from typing import TYPE_CHECKING

from prompt_toolkit.completion.filesystem import PathCompleter
from prompt_toolkit.layout.containers import Float, HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Label, RadioList, TextArea

from restcli import yaml_utils as yaml
from restcli.workspace import Collection, Environment

if TYPE_CHECKING:
    from restcli.ui import UI

OK_TEXT = "OK"
CANCEL_TEXT = "Cancel"


class BaseFileDialog(Dialog, metaclass=abc.ABCMeta):
    def __init__(self, ui: UI, title: str, text: str):
        self.future = Future()
        self.ui = ui

        self.ok_button = Button(OK_TEXT, self.handle_ok)
        self.cancel_button = Button(CANCEL_TEXT, self.handle_cancel)

        self.text_area = TextArea(
            multiline=False,
            completer=PathCompleter(),
            accept_handler=self.handle_accept_text,
        )

        # noinspection PyTypeChecker
        super().__init__(
            title=title,
            body=HSplit(
                [Label(text=text, dont_extend_height=True), self.text_area],
                width=D(preferred=80),
                padding=D(preferred=1, max=1),
            ),
            buttons=[self.ok_button, self.cancel_button],
            modal=True,
            with_background=True,
        )

    @abc.abstractmethod
    def handle_ok(self):
        """What to do when the OK button is pressed.

        This should perform any validation required, and if successful it
        should call `self.future.set_result` with the result of the Dialog.
        """

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


class BaseRadioFileDialog(BaseFileDialog, metaclass=abc.ABCMeta):
    """Abstract base class for dialogs that open files."""

    def __init__(self, ui: UI, title: str, text: str):
        super().__init__(ui, title, text)

        self.radio_list = RadioList(
            [(Collection, "Collection"), (Environment, "Environment")]
        )

        # noinspection PyTypeChecker
        self.body = HSplit(
            [
                HSplit(
                    [
                        Label(text="Type", dont_extend_height=True),
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
        )

    @abc.abstractmethod
    def handle_ok(self):
        """Same as :method:`BaseFileDialog.handle_ok`."""


class NewFileDialog(BaseRadioFileDialog):
    def __init__(self, ui: UI):
        super().__init__(ui, title="New File", text="File name")

    def handle_ok(self):
        """Create a new Document of the selected type (Collection or Env)."""
        document_cls = self.radio_list.current_value
        name = self.text_area.text
        result = document_cls()
        result.source = name
        self.future.set_result(result)


class OpenFileDialog(BaseRadioFileDialog):
    def __init__(self, ui: UI):
        super().__init__(ui, title="Open File", text="Path to open file")
        self.text_area.text = "collection.yaml"

    def handle_ok(self):
        """Load the Document of the selected type (Collection or Env)."""
        # TODO: handle bad paths here
        document_cls = self.radio_list.current_value
        source = self.text_area.text
        self.future.set_result(document_cls(source))


class ExportFileDialog(BaseFileDialog):
    def __init__(self, ui: UI, title="Export File"):
        super().__init__(ui, title=title, text="Path to save file")

    def handle_ok(self):
        """Save the file to the filesystem."""
        # Assimilate saved changes into the Collection
        for group_name, group_data in self.ui.editor.content.state.items():
            group = self.ui.editor.collection.setdefault(group_name, {})
            group.update(group_data)

        # Save the Collection to the given path
        path = self.text_area.text.strip()
        self.ui.editor.collection.source = path
        self.ui.editor.collection.save()

        self.future.set_result(path)
