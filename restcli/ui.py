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

from restcli.utils import AttrMap, is_non_str_iterable


def handle_quit():
    get_app().exit()


class MenuContainer(_MenuContainer):
    def __init__(
        self,
        body: AnyContainer,
        menu_items: List["MenuItem"],
        floats: Optional[List[Float]] = None,
        key_bindings: Optional[KeyBindingsBase] = None,
    ):
        self._menu_item_map = AttrMap(
            *(
                (item.name, (i, item))
                for i, item in enumerate(menu_items)
                if item.name
            )
        )
        super().__init__(body, menu_items, floats, key_bindings)

    def focus_item_by_name(self, *chain: str):
        chain = iter(chain)
        i, item = self._menu_item_map[next(chain)]
        self.selected_menu[:] = [i]
        for name in chain:
            self.selected_menu.append(item.index_of(name))
            item = item[name]


class MenuItem(_MenuItem):
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
        children: Optional[List["MenuItem"]] = None,
        disabled: bool = None,
    ):
        self.name = name
        if key:
            text = text.format(key=key)
        self.key = key

        if children:
            self._child_map = AttrMap(
                *((item.name, item) for item in children if item.name)
            )
            self._child_idx_map = AttrMap(
                *((item.name, i) for i, item in enumerate(children))
            )
        else:
            self._child_map = AttrMap()
            self._child_idx_map = AttrMap()

        super().__init__(
            text=text, handler=handler, children=children, disabled=disabled,
        )

    def __getitem__(self, name: str) -> "MenuItem":
        return self._child_map[name]

    def index_of(self, name: str) -> "MenuItem":
        return self._child_idx_map[name]

    @classmethod
    def SEPARATOR(cls) -> "MenuItem":
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
                children=[MenuItem("Collection"), MenuItem("Environment"),],
            ),
            MenuItem(
                "({key})pen file",
                key="o",
                name="open",
                children=[MenuItem("Collection"), MenuItem("Environment"),],
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
    menu__edit = MenuItem("edit <F2>", children=[MenuItem("(f)ind")],)
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

    @kb.add("f1")
    def _(event):
        if layout.has_focus(menu.window):
            event.app.layout.focus_last()
        else:
            layout.focus(menu.window)
            menu.focus_item_by_name("file")

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
