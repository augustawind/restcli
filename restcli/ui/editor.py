from __future__ import annotations

import os.path
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Set

from prompt_toolkit.layout.containers import (
    Container,
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
from restcli.workspace import Collection, GroupType, RequestType

if TYPE_CHECKING:
    from restcli.ui import UI


class RequestTab:

    group_name: Optional[str]
    request_name: Optional[str]
    request_body: Optional[RequestType]
    on_save: Optional[Callable[[RequestTab], None]]

    DEFAULT_NAME = "[Empty]"

    def __init__(
        self,
        group_name: Optional[str] = None,
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

        if group_name or request_name or request_body:
            assert group_name and request_name and request_body
            self.set_request(group_name, request_name, request_body)
            self.saved_text = self.text_area.text
        else:
            self.group_name = None
            self.request_name = self.DEFAULT_NAME
            self.request_body = None

        self.on_save = None

    def __pt_container__(self):
        return self.text_area

    def is_empty(self) -> bool:
        return len(self.text_area.text) == 0 and len(self.saved_text) == 0

    @property
    def is_populated(self) -> bool:
        return bool(
            self.group_name
            and self.request_name
            and self.request_body
            and self.on_save
        )

    @property
    def has_unsaved_changed(self) -> bool:
        return bool(self.text_area.text != self.saved_text)

    def set_request(
        self, group_name: str, request_name: str, request_body: RequestType
    ):
        self.group_name = group_name
        self.request_name = request_name
        self.request_body = request_body
        self.text_area.text = yaml.dump(request_body)

    def save_changes(self):
        assert self.is_populated

        self.saved_text = self.text_area.text
        self.request_body = yaml.load(self.saved_text)
        self.on_save(self)


class TabbedRequestWindow:
    editor: Editor
    width: D
    tabs: List[RequestTab]
    active_tab_idx: int

    state: Dict[str, GroupType]

    tab_bar: Container
    container: Container

    def __init__(self, editor: Editor, width: D = None):
        self.editor = editor
        self.width = width

        self.tabs = [RequestTab(width=width)]
        self.active_tab_idx = 0

        self.state = {}

        self.redraw()

    def __pt_container__(self):
        return self.container

    def redraw(self):
        self.tab_bar = self.get_tab_controls()
        self.container = HSplit(
            [self.tab_bar, HorizontalLine(), self.active_tab]
        )

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
                text = f"+{text}"

            handler = self._one_tab_handler(i)

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

    def _one_tab_handler(self, index: int):
        # noinspection PyTypeChecker
        def handler(event: MouseEvent):
            if event.event_type == MouseEventType.MOUSE_UP:
                self.active_tab_idx = index
                self.editor.redraw()
                self.editor.ui.redraw_layout(self.active_tab)
            else:
                return NotImplemented

        return handler

    def add_tab(self, tab: RequestTab, active: bool = True) -> bool:
        """Add the given tab.

        If `active` is True, make it the active tab. Returns True if it was
        added successfully. Returns False if a tab already exists with the same
         `group_name` and `request_name`.
        """
        if any(
            (tab.group_name, tab.request_name)
            == (t.group_name, t.request_name)
            for t in self.tabs
        ):
            return False

        # Add hook to update state with changes saved in the tab
        tab.on_save = self.on_tab_save

        # If there is only one tab and it's empty, replace it
        if len(self.tabs) == 1 and self.active_tab.is_empty():
            self.tabs[0] = tab
        else:
            self.tabs.append(tab)
            if active:
                self.active_tab_idx = len(self.tabs) - 1

        return True

    def remove_tab(self, index: int) -> Optional[RequestTab]:
        """Remove the tab at the given index.

        If it was the active tab, make the next tab active. If there's only one
        tab left, replace it with an empty tab. Returns the removed tab, or
        None if there was no tab at that index.
        """
        try:
            tab = self.tabs.pop(index)
        except IndexError:
            return None

        if len(self.tabs) == 0:
            self.tabs.append(RequestTab(width=self.width))

        if self.active_tab_idx == index:
            self.active_tab_idx = min(index + 1, len(self.tabs) - 1)

        return tab

    def remove_active_tab(self) -> RequestTab:
        """Remove and return the currently active tab."""
        return self.remove_tab(self.active_tab_idx)

    def on_tab_save(self, tab: RequestTab):
        """Called by RequestTabs to save changes to the Collection."""
        group_state = self.state.setdefault(tab.group_name, {})
        request_state = group_state.setdefault(tab.request_name, {})
        request_state.update(tab.request_body)


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

    ui: UI

    content: TabbedRequestWindow
    side_menu: Container
    container: Container

    menu_items: List[Window]
    submenu_items: List[List[Window]]
    expanded_menu_indices: Set[int]

    collection: Optional[Collection]

    DEFAULT_TITLE = "Untitled collection"

    def __init__(self, ui: UI):
        self.ui = ui

        self.content = TabbedRequestWindow(self, width=D(weight=3))

        self.menu_items = []
        self.submenu_items = []
        self.expanded_menu_indices = set()

        self.collection = None

        self.redraw()

    def __pt_container__(self):
        return self.container

    def redraw(self):
        self.content.redraw()

        menu_items = []
        for i, menu_item in enumerate(self.menu_items):
            menu_items.append(menu_item)
            if i in self.expanded_menu_indices:
                submenu_items = self.submenu_items[i]
                menu_items.extend(submenu_items)

        self.side_menu = HSplit(
            menu_items or [Window(BufferControl())],  # placeholder
            width=D(weight=1),
            align=VerticalAlign.TOP,
        )
        self.container = VSplit([self.side_menu, VerticalLine(), self.content])

    def load_collection(self, collection: Collection):
        self.menu_items.clear()
        self.submenu_items.clear()
        self.expanded_menu_indices.clear()

        # Set sidebar menu items
        for idx, (group_name, group) in enumerate(collection.items()):
            self.menu_items.append(self._side_menu_item(group_name, idx))

            submenu_items = []
            self.submenu_items.append(submenu_items)
            for request_name, request in group.items():
                submenu_items.append(
                    self._side_menu_subitem(group_name, request_name, request)
                )

        # Set frame title
        if collection.source:
            self.ui.editor_frame.title = os.path.basename(collection.source)
        else:
            self.ui.editor_frame.title = self.DEFAULT_TITLE

        self.collection = collection

        self.redraw()

        # Layout must be redrawn for the side menu to function properly
        self.ui.redraw_layout(focus=self.content)

    def _side_menu_item(self, group_name: str, index: int) -> Window:
        """Generate a style/text/handler tuple for Groups in the sidebar."""
        if index in self.expanded_menu_indices:
            text = f"{chr(0x25BC)} {group_name}"  # down triangle (expanded)
        else:
            text = f"{chr(0x25B6)} {group_name}"  # right triangle (collapsed)

        def handler(event: MouseEvent):
            if event.event_type == MouseEventType.MOUSE_UP:
                # Toggle submenu - expand if collapsed, collapse if expanded
                if index in self.expanded_menu_indices:
                    self.expanded_menu_indices.remove(index)
                else:
                    self.expanded_menu_indices.add(index)

                self.menu_items[index] = self._side_menu_item(
                    group_name, index
                )

                self.redraw()

                # Layout must be redrawn to display
                self.ui.redraw_layout(self.menu_items[index])
            else:
                return NotImplemented

        return Window(
            FormattedTextControl([("#00ff00", text, handler)], focusable=True),
            height=1,
        )

    def _side_menu_subitem(
        self, group_name: str, request_name: str, request: RequestType
    ) -> Window:
        def handler(event: MouseEvent):
            if event.event_type == MouseEventType.MOUSE_UP:
                self.content.add_tab(
                    RequestTab(group_name, request_name, request, width=D())
                )
                self.redraw()
            else:
                return NotImplemented

        return Window(
            FormattedTextControl(
                [
                    ("", " " * 4, handler),
                    ("[SetCursorPosition]", "", handler),
                    ("#00ff00", request_name, handler),
                ],
                focusable=True,
            ),
            height=1,
        )
