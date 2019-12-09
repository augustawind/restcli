from __future__ import annotations

import os.path
from typing import TYPE_CHECKING, List, Optional, Set

from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.layout.containers import (
    Container,
    DynamicContainer,
    HorizontalAlign,
    HSplit,
    VerticalAlign,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import AnyDimension, D
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType
from prompt_toolkit.widgets import HorizontalLine, TextArea, VerticalLine
from pygments.lexers.data import YamlLexer

from restcli import yaml_utils as yaml
from restcli.workspace import Collection, RequestType

if TYPE_CHECKING:
    from restcli.ui import UI


class RequestTab:

    request_name: Optional[str]
    request_body: Optional[RequestType]

    DEFAULT_NAME = "[Empty]"

    def __init__(
        self,
        request_name: Optional[str] = None,
        request_body: Optional[RequestType] = None,
        width: AnyDimension = None,
    ):
        self.saved_text = ""

        self.text_area = TextArea(
            width=width,
            lexer=PygmentsLexer(YamlLexer),
            line_numbers=True,
            scrollbar=True,
            focus_on_click=True,
        )

        if request_name or request_body:
            assert request_name and request_body, "Incomplete data provided"
            self.set_request(request_name, request_body)
        else:
            self.request_name = self.DEFAULT_NAME
            self.request_body = None

    def __pt_container__(self):
        return self.text_area

    def is_empty(self) -> bool:
        return (
            len(self.text_area.text.strip()) == 0 and len(self.saved_text) == 0
        )

    @property
    def has_unsaved_changed(self) -> bool:
        return bool(self.text_area.text.strip() != self.saved_text)

    def set_request(self, request_name: str, request_body: RequestType):
        self.request_name = request_name
        self.request_body = request_body
        self.text_area.text = yaml.dump(request_body)

    def save_changes(self):
        self.saved_text = self.text_area.text.strip()


class TabbedRequestWindow:
    def __init__(self, editor: Editor, width: AnyDimension = None):
        self.editor = editor
        self.width = width

        self.tabs = [RequestTab(width=width)]
        self.active_tab_idx = 0

        self.tab_bar = DynamicContainer(self.get_tab_controls)

    def __pt_container__(self):
        return HSplit([self.tab_bar, HorizontalLine(), self.active_tab])

    @property
    def active_tab(self) -> RequestTab:
        return self.tabs[self.active_tab_idx]

    def get_tab_controls(self) -> Container:
        controls = []
        for i, tab in enumerate(self.tabs):
            style = "class:tabbar.tab"
            if i == self.active_tab_idx:
                style += ".active"

            text = tab.request_name
            if tab.has_unsaved_changed:
                text = f"+ {text}"

            def handler(event: MouseEvent):
                if event.event_type == MouseEventType.MOUSE_UP:
                    self.active_tab_idx = i
                    self.editor.redraw()
                    self.editor.ui.redraw_layout(self.active_tab)
                else:
                    return NotImplemented

            controls.append(
                Window(
                    FormattedTextControl(
                        [(style, text, handler)], focusable=True
                    ),
                    width=D(min=3, max=len(text), preferred=len(text)),
                )
            )
        return VSplit(
            controls,
            height=1,
            width=self.width,
            padding=D.exact(1),
            align=HorizontalAlign.LEFT,
        )

    def add_tab(self, tab: RequestTab, active: bool = True):
        """Add the given tab.

        If `active` is True, make it the active tab.
        """
        # If there is only one tab and it's empty, replace it
        if len(self.tabs) == 1 and self.active_tab.is_empty():
            self.tabs[0] = tab
        else:
            self.tabs.append(tab)
            if active:
                self.active_tab_idx = len(self.tabs) - 1

    def remove_tab(self, index: int) -> Optional[RequestTab]:
        """Remove the tab at the given index.

        If it was the active tab, make the next tab active. Returns the removed
        tab, or None if there was no tab at that index.
        """
        try:
            return self.tabs.pop(index)
        except IndexError:
            return None


class Editor:
    """UI panel where :class:`Collection`s can be edited.

    Attributes
    ----------
    content
        Editable text area where Collection Requests are loaded.
    side_menu
        Collapsible menu where the current Collection's Groups and Requests are
        listed hierarchically. Select a Request here to load it into the
        ``text_area``.
    """

    content: TabbedRequestWindow
    side_menu: Container
    container: Container

    menu_items: List[Window]
    submenu_items: List[List[Window]]
    expanded_menu_indices: Set[int]

    ui: UI

    DEFAULT_TITLE = "Untitled collection"

    def __init__(self, ui: UI):
        self.content = TabbedRequestWindow(self, width=D(weight=2))

        self.menu_items = [Window(BufferControl())]
        self.submenu_items = []
        self.expanded_menu_indices = set()

        self.ui = ui

        self.redraw()

    def __pt_container__(self):
        return self.container

    def redraw(self):
        menu_items = []
        for i, menu_item in enumerate(self.menu_items):
            menu_items.append(menu_item)
            if i in self.expanded_menu_indices:
                submenu_items = self.submenu_items[i]
                menu_items.extend(submenu_items)

        self.side_menu = HSplit(
            menu_items,
            width=D(weight=1),
            padding=D(max=1, preferred=1),
            align=VerticalAlign.TOP,
        )
        self.container = VSplit([self.side_menu, VerticalLine(), self.content])

    def load_collection(self, collection: Collection):
        self.menu_items.clear()
        self.submenu_items.clear()
        self.expanded_menu_indices.clear()

        # Set sidebar menu items
        for idx, (group_name, group) in enumerate(collection.items()):
            self.menu_items.append(
                Window(
                    FormattedTextControl(
                        self._side_menu_item(group_name, idx), focusable=True
                    ),
                    height=1,
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
                        ),
                        height=1,
                    )
                )

        # Set frame title
        if collection.source:
            self.ui.editor_frame.title = os.path.basename(collection.source)
        else:
            self.ui.editor_frame.title = self.DEFAULT_TITLE

        self.redraw()

        # Layout must be redrawn for the side menu to function properly
        self.ui.redraw_layout(focus=self.side_menu)

    def _side_menu_item(
        self, group_name: str, index: int
    ) -> StyleAndTextTuples:
        """Generate a style/text/handler tuple for Groups in the sidebar."""

        def handler(event: MouseEvent):
            if event.event_type == MouseEventType.MOUSE_UP:
                # Toggle submenu - expand if collapsed, collapse if expanded
                if index in self.expanded_menu_indices:
                    self.expanded_menu_indices.remove(index)
                else:
                    self.expanded_menu_indices.add(index)

                self.redraw()

                # Layout must be redrawn to display
                self.ui.redraw_layout(self.menu_items[index])
            else:
                return NotImplemented

        return [("#00ff00", group_name, handler)]

    def _side_menu_subitem(
        self, request_name: str, request: RequestType
    ) -> StyleAndTextTuples:
        def handler(event: MouseEvent):
            if event.event_type == MouseEventType.MOUSE_UP:
                self.content.add_tab(
                    RequestTab(request_name, request, width=D())
                )
                self.redraw()
            else:
                return NotImplemented

        return [
            ("", " " * 8, handler),
            ("[SetCursorPosition]", "", handler),
            ("#00ff00", request_name, handler),
        ]
