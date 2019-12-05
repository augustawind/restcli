from __future__ import annotations

from typing import List, Set

from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.layout.containers import (
    AnyContainer,
    HSplit,
    VerticalAlign,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType
from prompt_toolkit.widgets import Frame, TextArea, VerticalLine
from pygments.lexers.data import YamlLexer

from restcli import yaml_utils as yaml
from restcli.ui.menu import MenuContainer, MenuItem
from restcli.workspace import Collection, GroupType, RequestType


class Editor:
    """UI panel where :class:`Collection`s can be edited.

    Attributes
    ----------
    text_area
        Editable text area where Collection Requests are loaded.
    side_menu
        Collapsible menu where the current Collection's Groups and Requests are
        listed hierarchically. Select a Request here to load it into the
        ``text_area``.
    """

    def __init__(self):
        self.text_area = TextArea(
            lexer=PygmentsLexer(YamlLexer),
            width=D(weight=2),
            focus_on_click=True,
            line_numbers=True,
        )
        self.side_menu: AnyContainer = None
        self.container: AnyContainer = None

        self.menu_items: List[Window] = [Window(BufferControl())]
        self.submenu_items: List[List[Window]] = []
        self.expanded_menu_indices: Set[int] = set()

        # TODO: remove this
        self.load_collection(Collection("collection.yaml"))
        self.refresh()

    def __pt_container__(self) -> AnyContainer:
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
        self.menu_items.clear()
        for idx, (group_name, group) in enumerate(collection.items()):
            self.menu_items.append(
                Window(
                    FormattedTextControl(
                        self._gen_menu_fragment(idx, group_name, group),
                        focusable=True,
                    )
                )
            )

            submenu_items = []
            self.submenu_items.append(submenu_items)
            for request_name, request in group.items():
                submenu_items.append(
                    Window(
                        FormattedTextControl(
                            self._gen_submenu_fragment(request_name, request),
                            focusable=True,
                        )
                    )
                )

        self.refresh()

    def _gen_menu_fragment(
        self, index: int, group_name: str, group: GroupType
    ) -> StyleAndTextTuples:
        """Generate a style/text/handler tuple for Groups in the sidebar."""

        def handler(event: MouseEvent):
            if event.event_type == MouseEventType.MOUSE_UP:
                self.expanded_menu_indices.add(index)
                self.refresh()
            else:
                return NotImplemented

        return [("#00ff00", group_name, handler)]

    def _gen_submenu_fragment(
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
