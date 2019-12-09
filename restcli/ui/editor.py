from __future__ import annotations

from typing import Callable, List, Set

from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.layout.containers import (
    Container,
    HSplit,
    VerticalAlign,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType
from prompt_toolkit.widgets import TextArea, VerticalLine
from pygments.lexers.data import YamlLexer

from restcli import yaml_utils as yaml
from restcli.workspace import Collection, RequestType


class Editor:
    """UI panel where :class:`Collection`s can be edited.

    Parameters
    ----------
    update_title : callable
        A callable that takes a :class :`Collection` and sets the Editor's
        title appropriately. This is necessary because the title is stored on
        the Editor's parent container.

    Attributes
    ----------
    text_area
        Editable text area where Collection Requests are loaded.
    side_menu
        Collapsible menu where the current Collection's Groups and Requests are
        listed hierarchically. Select a Request here to load it into the
        ``text_area``.
    """

    update_title: Callable[[Collection], None]

    text_area: TextArea
    side_menu: Container
    container: Container

    menu_items: List[Window]
    submenu_items: List[List[Window]]
    expanded_menu_indices: Set[int]

    def __init__(self, update_title: Callable[[Collection], None]):
        self.update_title = update_title

        self.text_area = TextArea(
            lexer=PygmentsLexer(YamlLexer),
            width=D(weight=2),
            focus_on_click=True,
            line_numbers=True,
        )

        self.menu_items = [Window(BufferControl())]
        self.submenu_items = []
        self.expanded_menu_indices = set()

        self.refresh()

    def __pt_container__(self) -> Container:
        return self.container

    def refresh(self):
        menu_items = []
        for i, menu_item in enumerate(self.menu_items):
            menu_items.append(menu_item)
            if i in self.expanded_menu_indices:
                submenu_items = self.submenu_items[i]
                menu_items.extend(submenu_items)

        self.side_menu = HSplit(
            menu_items, width=D(weight=1), align=VerticalAlign.TOP
        )
        self.container = VSplit(
            [self.side_menu, VerticalLine(), self.text_area]
        )

    def load_collection(self, collection: Collection):
        # Set sidebar menu items
        self.menu_items.clear()
        for idx, (group_name, group) in enumerate(collection.items()):
            self.menu_items.append(
                Window(
                    FormattedTextControl(
                        self._side_menu_item(group_name, idx), focusable=True,
                    )
                )
            )

            submenu_items = []
            self.submenu_items.append(submenu_items)
            for request_name, request in group.items():
                submenu_items.append(
                    Window(
                        FormattedTextControl(
                            self._side_menu_subitem(request_name, request),
                            focusable=True,
                        )
                    )
                )

        # Set frame title
        self.update_title(collection)

        self.refresh()

    def _side_menu_item(
        self, group_name: str, index: int
    ) -> StyleAndTextTuples:
        """Generate a style/text/handler tuple for Groups in the sidebar."""

        def handler(event: MouseEvent):
            if event.event_type == MouseEventType.MOUSE_UP:
                self.expanded_menu_indices.add(index)
                self.refresh()
            else:
                return NotImplemented

        return [("#00ff00", group_name, handler)]

    def _side_menu_subitem(
        self, request_name: str, request: RequestType
    ) -> StyleAndTextTuples:
        def handler(event: MouseEvent):
            if event.event_type == MouseEventType.MOUSE_UP:
                self.text_area.text = yaml.dump(request)
                self.refresh()
            else:
                return NotImplemented

        return [
            ("", " " * 8, handler),
            ("[SetCursorPosition]", "", handler),
            ("#00ff00", request_name, handler),
        ]
