from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.mouse_events import MouseEventType
from prompt_toolkit.widgets import Frame, TextArea
from pygments.lexers.data import YamlLexer

if TYPE_CHECKING:
    from restcli.ui import UI


class Editor(Frame):

    def __init__(self, ui: UI):
        self.ui = ui

        self.tab_arrangement = TabArrangement()

        self.tabs_toolbar = TabsToolbar(self)
        self.text_area = TextArea(lexer=PygmentsLexer(YamlLexer))
        self.content_panel = Frame(title="Workspace", body=self.text_area)

        self.layout = Layout(HSplit([
            self.tabs_toolbar,
            self.content_panel,
        ]))


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


class Tab(Window):

    def __init__(self):
        pass

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
                    result.append(("class:tabbar.tab", f" {caption} ", handler))
                result.append(("class:tabbar", " "))

            return result

        super().__init__(get_tokens, style="class:tabbar")