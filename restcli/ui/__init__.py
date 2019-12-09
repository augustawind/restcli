"""Interactive TUI application for restcli."""
import os.path
from dataclasses import dataclass
from typing import List

from prompt_toolkit.application import Application
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import (
    focus_next,
    focus_previous,
)
from prompt_toolkit.layout.containers import Float, VSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame, TextArea
from pygments.lexers.data import YamlLexer

from restcli.ui import handlers
from restcli.ui.editor import Editor
from restcli.ui.menu import MenuContainer, MenuItem
from restcli.workspace import Collection, Document, Environment


@dataclass(init=False)
class AppState:
    current_document: Document
    active_collection: Collection
    active_env: Environment


class UI:
    """Holds all the user interface application logic.

    Attributes
    ----------
    state : :class:`AppState`
        Holds application state.
    editor : :class:`Editor`
        UI component where data is edited by the user.
    output : :class:`prompt_toolkit.widgets.TextArea`
        UI component where various output is displayed.
    body : :class:`prompt_toolkit.layout.containers.Container`
        UI component where data will be displayed.
    menu : :class:`MenuContainer`
        UI component that wraps `body` with a context menu.
    key_bindings : :class:`prompt_toolkit.key_binding.KeyBindings`
        Application-wide key bindings.
    style : :class:`prompt_toolkit.styles.Style`
        Styling information for display.
    layout : :class:`prompt_toolkit.layout.Layout`
        UI component that holds all other components.
    """

    # noinspection PyTypeChecker
    def __init__(self):
        self.state = AppState()

        def update_editor_title(collection: Collection):
            self._editor_frame.title = os.path.basename(collection.source)

        self.editor = Editor(update_title=update_editor_title)
        self._editor_frame = Frame(
            self.editor, title="Collection", width=D(weight=5)
        )

        self.output = TextArea(lexer=PygmentsLexer(YamlLexer), read_only=True)
        self._output_frame = Frame(
            self.output, title="Output", width=D(weight=4)
        )

        self.body = VSplit(
            [self._editor_frame, self._output_frame], height=D()
        )

        self.menu = MenuContainer(
            self,
            body=self.body,
            menu_items=self._init_menu_items(),
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(max_height=16, scroll_offset=1),
                )
            ],
        )

        self.key_bindings = self._init_key_bindings()
        self.style = self._init_style()

        self.layout = Layout(self.menu, focused_element=self.editor.side_menu)

        self.app = Application(
            layout=self.layout,
            key_bindings=self.key_bindings,
            style=self.style,
            mouse_support=True,
            full_screen=True,
            editing_mode=EditingMode.VI,
        )

        # NOTE: this is here for convenience while developing
        self.editor.load_collection(Collection("collection.yaml"))

    def run(self):
        self.app.run()

    def _init_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        self.menu.register_key_bindings(kb)

        kb.add("c-x")(lambda _: self.app.exit())
        kb.add("tab")(focus_next)
        kb.add("s-tab")(focus_previous)

        return kb

    def _init_menu_items(self) -> List[MenuItem]:
        return [
            MenuItem(
                "file<{key}>",
                key="f1",
                name="file",
                handler=handlers.ToggleFocus,
                children=[
                    MenuItem("new file <{key}>", key="c-n", name="new"),
                    MenuItem(
                        "open file <{key}>",
                        key="c-o",
                        name="open",
                        handler=handlers.OpenFile,
                    ),
                    MenuItem.SEPARATOR(),
                    MenuItem("save <{key}>", key="c-s", name="save"),
                    MenuItem("save as...", name="save_as"),
                    MenuItem("save all", name="save_all"),
                    MenuItem.SEPARATOR(),
                    MenuItem("close file <{key}>", key="c-w", name="close"),
                    MenuItem("close all", name="close_all"),
                    MenuItem.SEPARATOR(),
                    MenuItem(
                        "quit <{key}>",
                        key="c-q",
                        name="quit",
                        handler=handlers.EndProgram,
                    ),
                ],
            ),
            MenuItem(
                "edit<{key}>",
                key="f2",
                name="edit",
                handler=handlers.ToggleFocus,
                children=[MenuItem("(f)ind")],
            ),
        ]

    def _init_style(self) -> Style:
        return Style.from_dict(
            {
                "window.border": "#888888",
                "shadow": "bg:#222222",
                "menu-bar": "bg:#aaaaaa #888888",
                "menu-bar.selected-item": "bg:#ffffff #000000",
                "menu": "bg:#888888 #ffffff",
                "menu.border": "#aaaaaa",
                "window.border shadow": "#444444",
                "focused  button": "bg:#880000 #ffffff noinherit",
                # Styling for Dialog widgets.
                "radiolist focused": "noreverse",
                "radiolist focused radio.selected": "reverse",
                "button-bar": "bg:#aaaaff",
            }
        )
