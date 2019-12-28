from __future__ import annotations

import abc
import asyncio
from asyncio import Future
from contextlib import asynccontextmanager
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from prompt_toolkit.completion.filesystem import PathCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import (
    AnyContainer,
    ConditionalContainer,
    Float,
    HSplit,
)
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Label, RadioList, TextArea

from restcli import yaml_utils as yaml
from restcli.workspace import Collection, Environment

if TYPE_CHECKING:
    from restcli.ui import UI

TEXT_OK = "OK"
TEXT_CANCEL = "Cancel"


class AsyncDialog(Dialog):
    """Base class for floating Dialogs that await a result from a Future."""

    def __init__(self, ui: UI, title: str, body: AnyContainer, **kwargs):
        self.future = Future()
        self.ui = ui
        self.float_ = None

        super().__init__(title=title, body=body, **kwargs)

    async def run(self):
        async with self.render():
            self.ui.app.layout.focus(self)
            result = await self.future
            self.ui.app.layout.focus_last()

        return result

    async def run_from_dialog(self, dialog: AsyncDialog):
        self.ui.root_container.floats.remove(dialog.float_)

        async with self.render():
            self.ui.app.layout.focus(self)
            result = await self.future
            self.ui.app.layout.focus(dialog)

        return result

    @asynccontextmanager
    async def render(self):
        self.float_ = Float(self)
        self.ui.root_container.floats.insert(0, self.float_)

        yield

        if self.float_ in self.ui.root_container.floats:
            self.ui.root_container.floats.remove(self.float_)


class BaseTextInputDialog(AsyncDialog, metaclass=abc.ABCMeta):
    """Abstract base class for Dialogs that prompt the user for text."""

    def __init__(self, ui: UI, title: str, text: str):
        self.ok_button = Button(TEXT_OK, self.handle_ok)
        self.cancel_button = Button(TEXT_CANCEL, self.handle_cancel)

        self.text_area = TextArea(
            multiline=False,
            completer=PathCompleter(),
            accept_handler=self.handle_accept_text,
        )
        self.message_box = TextArea(
            read_only=True, focusable=False, style="bg:#ffffff #ff0000"
        )

        # noinspection PyTypeChecker
        super().__init__(
            ui=ui,
            title=title,
            body=HSplit(
                [
                    Label(text=text, dont_extend_height=True),
                    self.text_area,
                    ConditionalContainer(
                        self.message_box,
                        Condition(lambda: bool(self.message_box.text)),
                    ),
                ],
                width=D(preferred=80),
                padding=D(preferred=1, max=1),
            ),
            buttons=[self.ok_button, self.cancel_button],
            modal=True,
            with_background=True,
        )

    def set_message(self, text: str):
        self.message_box.text = text

    def handle_ok(self):
        """What to do when the OK button is pressed.

        This should perform any validation required, and if successful
        it should call `self.future.set_result` with the result of the
        Dialog.
        """

    def handle_cancel(self):
        self.future.set_result(None)

    def handle_accept_text(self, buf):
        self.ui.app.layout.focus(self.ok_button)
        buf.complete_state = None
        return True


class BaseDocumentInputDialog(BaseTextInputDialog, metaclass=abc.ABCMeta):
    """Adds a Document-type prompt to BaseTextInputDialog."""

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
                        ConditionalContainer(
                            self.message_box,
                            Condition(lambda: bool(self.message_box.text)),
                        ),
                    ],
                    padding=D(preferred=1, max=1),
                ),
            ],
            width=D(preferred=80),
            padding=1,
        )

    @abc.abstractmethod
    def handle_ok(self):
        """Same as :method:`BaseTextInputDialog.handle_ok`."""


class NewFileDialog(BaseDocumentInputDialog):
    def __init__(self, ui: UI):
        super().__init__(ui, title="New File", text="File name")

    def handle_ok(self):
        """Create a new Document of the selected type (Collection or Env)."""
        document_cls = self.radio_list.current_value
        name = self.text_area.text
        result = document_cls()
        result.source = name
        self.future.set_result(result)


class OpenFileDialog(BaseDocumentInputDialog):
    def __init__(self, ui: UI):
        super().__init__(ui, title="Open File", text="Path to open file")
        self.text_area.text = "collection.yaml"

    def handle_ok(self):
        """Load the Document of the selected type (Collection or Env)."""
        # TODO: handle bad paths here
        document_cls = self.radio_list.current_value
        source = self.text_area.text
        self.future.set_result(document_cls(source))


class ExportFileDialog(BaseTextInputDialog):
    def __init__(self, ui: UI, title="Export File"):
        super().__init__(ui, title=title, text="Path to save file")

    def handle_ok(self):
        """Save the file to the filesystem."""
        # Assimilate saved changes into the Collection
        for group_name, group_data in self.ui.editor.content.state.items():
            group = self.ui.editor.collection.setdefault(group_name, {})
            group.update(group_data)

        path = Path(self.text_area.text.strip())

        # If existing directory, show error message
        if path.is_dir():
            self.set_message(f'Invalid path: "{path.name}" is a directory')
            return

        # If existing file, run confirmation dialog
        if path.is_file():
            confirmation = ConfirmationDialog(
                self.ui,
                title="Overwrite file",
                text=(
                    f'"{path.name}" already exists.'
                    " Do you want to replace it?"
                ),
            )
            task = asyncio.create_task(confirmation.run_from_dialog(self))

            def do_if_confirmed(confirmed):
                if confirmed.result():
                    self.do_export(path)

            task.add_done_callback(do_if_confirmed)
        else:
            self.do_export(path)

    def do_export(self, path: Path):
        """Save the Collection to the given path."""
        self.ui.editor.collection.source = path
        self.ui.editor.collection.save()
        self.future.set_result(path)


class ConfirmationDialog(AsyncDialog):
    def __init__(
        self,
        ui: UI,
        title: str,
        text: str,
        ok_text: str = TEXT_OK,
        cancel_text: str = TEXT_CANCEL,
    ):
        super().__init__(
            ui=ui,
            title=title,
            body=Label(text=text, dont_extend_height=True),
            buttons=[
                Button(text=ok_text, handler=self.handle_ok),
                Button(text=cancel_text, handler=self.handle_cancel),
            ],
            with_background=True,
        )

    def handle_ok(self):
        self.future.set_result(True)

    def handle_cancel(self):
        self.future.set_result(False)
