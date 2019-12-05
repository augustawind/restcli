from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional, Sequence

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import AnyFormattedText, StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import (
    AnyContainer,
    ConditionalContainer,
    HSplit,
    VerticalAlign,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import D, max_layout_dimensions
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType
from prompt_toolkit.widgets import Button, Frame, Label, TextArea, VerticalLine
from pygments.lexers.data import YamlLexer

from restcli import yaml_utils as yaml
from restcli.ui.menu import MenuContainer, MenuItem
from restcli.workspace import Collection

if TYPE_CHECKING:
    from restcli.ui import UI


class Editor:
    def __init__(self, width=None, height=None):
        self.width = width
        self.height = height

        collection = Collection(source="examples/full/collection.yaml")

        self.text_area = TextArea(lexer=PygmentsLexer(YamlLexer), width=D(weight=2))
        self.menu_items = [Window(BufferControl())]
        self.refresh()

        def mktext(text: str):
            def handler(event: MouseEvent):
                if event.event_type == MouseEventType.MOUSE_UP:
                    self.text_area.text = text
                    self.refresh()
                else:
                    return NotImplemented

            return [("bg:#aaaaaa #888888", text, handler)]

        self.menu_items = [
            Window(FormattedTextControl(mktext("lions"), focusable=True)),
            Window(FormattedTextControl(mktext("tigers"), focusable=True)),
            Window(FormattedTextControl(mktext("bears"), focusable=True)),
            Window(FormattedTextControl(mktext("lions"), focusable=True)),
            Window(FormattedTextControl(mktext("tigers"), focusable=True)),
            Window(FormattedTextControl(mktext("bears"), focusable=True)),
            Window(FormattedTextControl(mktext("lions"), focusable=True)),
            Window(FormattedTextControl(mktext("tigers"), focusable=True)),
            Window(FormattedTextControl(mktext("bears"), focusable=True)),
            Window(FormattedTextControl(mktext("lions"), focusable=True)),
            Window(FormattedTextControl(mktext("tigers"), focusable=True)),
            Window(FormattedTextControl(mktext("bears"), focusable=True)),
        ]
        self.refresh()

    def refresh(self):
        self.side_menu = HSplit(self.menu_items, width=D(weight=1), align=VerticalAlign.TOP)
        self.container = Frame(
            VSplit([self.side_menu, VerticalLine(), self.text_area]),
            title="Collection",
            width=self.width,
            height=self.height,
        )

    def __pt_container__(self) -> AnyContainer:
        return self.container
