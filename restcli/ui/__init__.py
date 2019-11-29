"""Interactive TUI application for restcli."""

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import (
    focus_next,
    focus_previous,
)
from prompt_toolkit.layout.containers import Container, Float, VSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame, TextArea
from pygments.lexers.data import YamlLexer

from .menu import MenuContainer, MenuItem, handlers


class UI:
    """Holds all the user interface application logic.

    Attributes
    ----------
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

    def __init__(self):
        self.body = self._init_body()
        self.menu = self._init_menu()
        self.key_bindings = self._init_key_bindings()
        self.style = self._init_style()
        self.layout = self._init_layout()
        self.application = Application(
            layout=self.layout,
            key_bindings=self.key_bindings,
            style=self.style,
            mouse_support=True,
            full_screen=True,
        )

    def run(self):
        self.application.run()

    def _init_layout(self) -> Layout:
        element = self.body.get_children()[0]
        return Layout(self.menu, focused_element=element)

    def _init_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add("tab")(focus_next)
        kb.add("s-tab")(focus_previous)
        self.menu.register_key_bindings(kb)
        return kb

    def _init_menu(self) -> MenuContainer:
        return MenuContainer(
            body=self.body,
            menu_items=[
                MenuItem(
                    "file<{key}>",
                    key="f1",
                    name="file",
                    handler=handlers.toggle_focus,
                    children=[
                        MenuItem(
                            "({key})ew file",
                            key="n",
                            name="new",
                            children=[
                                MenuItem("Collection"),
                                MenuItem("Environment"),
                            ],
                        ),
                        MenuItem(
                            "({key})pen file",
                            key="o",
                            name="open",
                            children=[
                                MenuItem("Collection"),
                                MenuItem("Environment"),
                            ],
                        ),
                        MenuItem.SEPARATOR(),
                        MenuItem(
                            "({key})ave",
                            key="s",
                            name="save",
                            children=[
                                MenuItem("Save Collection"),
                                MenuItem("Save Environment"),
                            ],
                        ),
                        MenuItem(
                            "({key})ave as...",
                            key="S",
                            name="save_as",
                            children=[
                                MenuItem("Save Collection as..."),
                                MenuItem("Save Environment as..."),
                            ],
                        ),
                        MenuItem(
                            "save all<{key}>", key="c-s", name="save_all"
                        ),
                        MenuItem.SEPARATOR(),
                        MenuItem(
                            "({key})lose file",
                            key="c",
                            name="close",
                            children=[
                                MenuItem("Collection"),
                                MenuItem("Environment"),
                            ],
                        ),
                        MenuItem(
                            "close all<{key}>", key="c-w", name="close_all"
                        ),
                        MenuItem.SEPARATOR(),
                        MenuItem(
                            "quit<{key}>",
                            key="c-q",
                            name="quit",
                            handler=handlers.exit,
                        ),
                    ],
                ),
                MenuItem(
                    "edit<{key}>",
                    key="f2",
                    name="edit",
                    handler=handlers.toggle_focus,
                    children=[MenuItem("(f)ind")],
                ),
            ],
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(max_height=16, scroll_offset=1),
                ),
            ],
        )

    def _init_body(self) -> Container:
        panel__collection__text = TextArea(lexer=PygmentsLexer(YamlLexer))
        panel__collection = Frame(
            title="Untitled Collection", body=panel__collection__text,
        )
        panel__environment__text = TextArea(lexer=PygmentsLexer(YamlLexer))
        panel__environment = Frame(
            title="Environment view", body=panel__environment__text,
        )
        return VSplit([panel__collection, panel__environment], height=D())

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
