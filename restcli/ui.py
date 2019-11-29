from __future__ import annotations

from typing import Callable, List, Optional

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings, KeyBindingsBase
from prompt_toolkit.key_binding.bindings.focus import (
    focus_next,
    focus_previous,
)
from prompt_toolkit.layout.containers import (
    AnyContainer,
    Container,
    Float,
    VSplit,
)
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Box, Button, Checkbox, Dialog, Frame, Label
from prompt_toolkit.widgets import MenuContainer as _MenuContainer
from prompt_toolkit.widgets import MenuItem as _MenuItem
from prompt_toolkit.widgets import ProgressBar, RadioList, TextArea
from pygments.lexers.data import YamlLexer

from restcli.utils import AttrMap


def handle_quit():
    get_app().exit()


class BaseMenu:
    def __init__(self, menu_items: Optional[List[MenuItem]] = None):
        if menu_items:
            self._item_map = AttrMap(
                *((item.name, item) for item in menu_items if item.name)
            )
            self._item_idx_map = AttrMap(
                *((item.name, i) for i, item in enumerate(menu_items))
            )
        else:
            self._item_map = AttrMap()
            self._item_idx_map = AttrMap()

    def __getitem__(self, name: str) -> MenuItem:
        return self._item_map[name]

    def index_of(self, name: str) -> MenuItem:
        return self._item_idx_map[name]


class MenuContainer(_MenuContainer, BaseMenu):
    def __init__(
        self,
        body: AnyContainer,
        menu_items: List[MenuItem],
        floats: Optional[List[Float]] = None,
        key_bindings: Optional[KeyBindingsBase] = None,
    ):
        super().__init__(body, menu_items, floats, key_bindings)
        BaseMenu.__init__(self, menu_items)
        self._breadcrumb = 0

    def make_toggle_focus(self, item: MenuItem):
        def toggle_focus(event):
            selection = self.get_menu_selection(item.name)
            if (
                event.app.layout.has_focus(self.window)
                and self.selected_menu == selection
            ):
                for _ in range(self._breadcrumb):
                    event.app.layout.focus_last()
            else:
                event.app.layout.focus(self.window)
                self.selected_menu[:] = selection
                self._breadcrumb += 1

        return toggle_focus

    def register_key_bindings(self, kb: KeyBindings):
        for item in self.menu_items:
            if item.name and item.key:
                kb.add(item.key)(self.make_toggle_focus(item))

    def get_menu_selection(self, *chain: str) -> List[int]:
        name, *chain = chain
        selected = [self.index_of(name)]
        item = self[name]
        for name in chain:
            selected.append(item.index_of(name))
            item = item[name]
        return selected


class MenuItem(_MenuItem, BaseMenu):
    """Extends ``prompt_toolkit.widgets.MenuItem``.

    Adds a ``name`` field which can be used to access child MenuItems with
    brackets (i.e. `item[name]`).
    """

    def __init__(
        self,
        text: str = "",
        key: Optional[str] = None,
        name: Optional[str] = None,
        handler: Optional[Callable[[], None]] = None,
        children: Optional[List[MenuItem]] = None,
        disabled: bool = None,
    ):
        self.name = name
        if key:
            text = text.format(key=key)
        self.key = key

        super().__init__(
            text=text, handler=handler, children=children, disabled=disabled,
        )
        BaseMenu.__init__(self, children)

    @classmethod
    def SEPARATOR(cls) -> MenuItem:
        """Return an inactive MenuItem that inserts a horizontal line."""
        return cls("-", disabled=True)


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
                "quit<{key}>", key="c-q", name="quit", handler=handle_quit
            ),
        ],
    )
    menu__edit = MenuItem(
        "edit<{key}>", key="f2", name="edit", children=[MenuItem("(f)ind")]
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
    menu.make_toggle_focus

    key_bindings = kb = KeyBindings()
    kb.add("tab")(focus_next)
    kb.add("s-tab")(focus_previous)

    menu.register_key_bindings(kb)

    @kb.add("c-q")
    def _(event):
        handle_quit()

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
