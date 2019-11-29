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


def new() -> Application:
    panel__collection__text = TextArea(lexer=PygmentsLexer(YamlLexer))
    panel__collection = Frame(
        title="Untitled Collection", body=panel__collection__text,
    )
    panel__environment__text = TextArea(lexer=PygmentsLexer(YamlLexer))
    panel__environment = Frame(
        title="Environment view", body=panel__environment__text,
    )
    body = VSplit([panel__collection, panel__environment], height=D())

    menu__file = MenuItem(
        "file<{key}>",
        key="f1",
        name="file",
        handler=handlers.toggle_focus,
        children=[
            MenuItem(
                "({key})ew file",
                key="n",
                name="new",
                children=[MenuItem("Collection"), MenuItem("Environment")],
            ),
            MenuItem(
                "({key})pen file",
                key="o",
                name="open",
                children=[MenuItem("Collection"), MenuItem("Environment")],
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
            MenuItem("save all<{key}>", key="c-s", name="save_all"),
            MenuItem.SEPARATOR(),
            MenuItem(
                "({key})lose file",
                key="c",
                name="close",
                children=[MenuItem("Collection"), MenuItem("Environment"),],
            ),
            MenuItem("close all<{key}>", key="c-w", name="close_all"),
            MenuItem.SEPARATOR(),
            MenuItem(
                "quit<{key}>", key="c-q", name="quit", handler=handlers.exit,
            ),
        ],
    )
    menu__edit = MenuItem(
        "edit<{key}>",
        key="f2",
        name="edit",
        handler=handlers.toggle_focus,
        children=[MenuItem("(f)ind")],
    )
    menu = MenuContainer(
        body=body,
        menu_items=[menu__file, menu__edit],
        floats=[
            Float(
                xcursor=True,
                ycursor=True,
                content=CompletionsMenu(max_height=16, scroll_offset=1),
            ),
        ],
    )

    layout = Layout(menu, focused_element=panel__collection__text)

    key_bindings = kb = KeyBindings()
    kb.add("tab")(focus_next)
    kb.add("s-tab")(focus_previous)

    menu.register_key_bindings(kb)

    style = Style.from_dict(
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

    return Application(
        layout=layout,
        key_bindings=key_bindings,
        style=style,
        mouse_support=True,
        full_screen=True,
    )
