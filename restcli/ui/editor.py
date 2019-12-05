from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional, Sequence

from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import AnyFormattedText, StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import (
    AnyContainer,
    ConditionalContainer,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType
from prompt_toolkit.widgets import Frame, Label, TextArea
from pygments.lexers.data import YamlLexer

from restcli import yaml_utils as yaml
from restcli.workspace import Collection

if TYPE_CHECKING:
    from restcli.ui import UI


class Editor:
    def __init__(self):
        self.sidebar = NavigationFrame(self)

        self.text_area = TextArea(lexer=PygmentsLexer(YamlLexer))
        self.content_panel = Frame(self.text_area, title="Editor")

        self._container = VSplit([self.sidebar, self.content_panel])

        self.current_collection: Collection = None

    def __pt_container__(self) -> AnyContainer:
        return self._container

    def load_collection(self, collection: Collection):
        self.current_collection = collection
        self.sidebar.load_collection(collection)


class NavigationFrame:
    def __init__(self, editor: Editor):
        self.editor = editor
        self.nav_items = []
        self._container = Frame(Window(BufferControl()), title="Collection")

    def __pt_container__(self) -> AnyContainer:
        return self._container

    def load_collection(self, collection: Collection):
        self.nav_items.clear()
        for group_name, group in collection.items():
            self.nav_items.append(
                NavigationItem(self.editor, group_name, group)
            )
        self._container.body = HSplit(self.nav_items)


class NavigationItem:
    def __init__(self, editor: Editor, group_name: str, group: dict):
        self.editor = editor
        self.group_name = group_name
        self.group = group

        request_items = []
        for request_name, request in group.items():
            request_items.append(
                ExpandableButton(
                    request_name, handler=self._get_handler(request)
                )
            )

        self._container = ExpandableButton(group_name, children=request_items)

    def __pt_container__(self) -> AnyContainer:
        return self._container

    def _get_handler(self, request: dict) -> Callable[[], None]:
        def handler():
            self.editor.text_area.text = yaml.dump(request)

        return handler


class ExpandableButton:
    def __init__(
        self,
        text: AnyFormattedText,
        handler: Optional[Callable[[], None]] = None,
        width: int = 12,
        children: Optional[Sequence[AnyContainer]] = None,
        level: int = 0,
    ):
        self.text = text
        self._handler = handler
        self.width = width
        self.sub_items = children

        self.expanded = False
        self.level = level

        self.control = FormattedTextControl(
            self._get_text_fragments,
            key_bindings=self._get_key_bindings(),
            focusable=True,
        )

        def get_style() -> str:
            if get_app().layout.has_focus(self):
                return "class:button.focused"
            else:
                return "class:button"

        self.window = Window(
            self.control,
            align=WindowAlign.CENTER,
            height=1,
            width=width,
            style=get_style,
            dont_extend_width=True,
            dont_extend_height=True,
        )

    def __pt_container__(self) -> AnyContainer:
        if self.expanded:
            return VSplit([self.window, *self.sub_items])
        else:
            return VSplit([self.window])

    def handler(self):
        if self._handler:
            self._handler()
        if self.sub_items:
            self.expanded = not self.expanded

    def _get_text_fragments(self) -> StyleAndTextTuples:
        text = ("{:^%s}" % (self.width - 2)).format(self.text)

        def handler(mouse_event: MouseEvent) -> None:
            if mouse_event.event_type == MouseEventType.MOUSE_UP:
                self.handler()

        return [
            ("class:button.arrow", "<", handler),
            ("[SetCursorPosition]", ""),
            ("class:button.text", text, handler),
            ("class:button.arrow", ">", handler),
        ]

    def _get_key_bindings(self) -> KeyBindings:
        " Key bindings for the Button. "
        kb = KeyBindings()

        @kb.add(" ")
        @kb.add("enter")
        def _(event: KeyPressEvent):
            self.handler()

        return kb


class TabArrangement:
    def __init__(self):
        self.tabs = []
        self.active_tab_idx = None

    @property
    def active_tab(self) -> Optional[Tab]:
        if self.active_tab_idx is not None:
            return self.tabs[self.active_tab_idx]

    def close_tab(self):
        if self.active_tab_idx is None:
            return

        del self.tabs[self.active_tab_idx]
        if len(self.tabs) == 0:
            self.active_tab_idx = None
        else:
            self.active_tab_idx = max(0, self.active_tab_idx - 1)


class Tab:
    def __init__(self):
        # TODO: configure
        self.pt_window = Window()

    def get_display_name(self) -> str:
        """Return the display name for this tab."""
        # TODO
        return "my-tab"

    def has_unsaved_changes(self) -> bool:
        """Return whether this tab has unsaved changes."""
        # TODO
        return False


class TabsToolbar(ConditionalContainer):
    """Container for the :class:`TabsControl`."""

    def __init__(self, editor: Editor):
        super(TabsToolbar, self).__init__(
            Window(TabsControl(editor), height=1),
            filter=Condition(
                lambda: True
                # Only show when there are multiple tabs:
                # lambda: len(editor.window_arrangement.tab_pages) > 1
            ),
        )


class TabsControl(FormattedTextControl):
    """Displays the tabs at the top of the editor."""

    def __init__(self, editor: Editor):
        def location_for_tab(tab: Tab):
            return tab.get_display_name()

        def create_tab_handler(idx: int):
            """Return a mouse handler for this tab. Select the tab on click."""

            def handler(app, mouse_event):
                if mouse_event.event_type == MouseEventType.MOUSE_DOWN:
                    editor.window_arrangement.active_tab_index = idx
                    editor.sync_with_prompt_toolkit()
                else:
                    return NotImplemented

            return handler

        def get_tokens():
            """Return the tokens displayed on the tab."""
            selected_tab_idx = editor.tab_arrangement.active_tab_idx

            result = []

            for i, tab in enumerate(editor.tab_arrangement.tabs):
                caption = location_for_tab(tab)
                if tab.has_unsaved_changes():
                    caption = f" + {caption}"

                handler = create_tab_handler(i)

                if i == selected_tab_idx:
                    result.append(
                        ("class:tabbar.tab.active", f" {caption} ", handler)
                    )
                else:
                    result.append(
                        ("class:tabbar.tab", f" {caption} ", handler)
                    )
                result.append(("class:tabbar", " "))

            return result

        super().__init__(get_tokens, style="class:tabbar")
