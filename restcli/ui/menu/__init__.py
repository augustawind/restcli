from __future__ import annotations

import abc
from typing import Callable, List, Optional, Union

from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings, KeyBindingsBase
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import AnyContainer, Float
from prompt_toolkit.widgets import MenuContainer as _MenuContainer
from prompt_toolkit.widgets import MenuItem as _MenuItem

from restcli.utils import AttrMap


class MenuHandler(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(
        self, menu: MenuContainer, item: MenuItem
    ) -> Callable[[Optional[KeyPressEvent]], None]:
        """Should return a function that responds to user interaction.

        This function be used to respond to clicks (if mouse is enabled) and to
        key presses (if a keyboard shortcut is provided). The returned function
        must _optionally_ accept a single :class:`KeyPressEvent` - in the event
        of a mouse click, the function will be called with no parameters. This
        requirement allows us to reuse the same function for both event types.
        """

    @classmethod
    def register(cls, func):
        return type(func.__name__, (cls,), {"__call__": func})()


class BaseMenu(metaclass=abc.ABCMeta):
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

    @property
    @abc.abstractmethod
    def items(self) -> List[MenuItem]:
        """Should return the list of all child :class:`MenuItem`s."""

    def register_key_bindings(self, kb: KeyBindings):
        for item in self.items:
            if item.key and item.handler:
                kb.add(item.key)(item.handler)
            item.register_key_bindings(kb)

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
        key_bindings: Optional[KeyBindingsBase] = None,  # TODO: figure dis out
    ):
        super().__init__(body, menu_items, floats, key_bindings)
        BaseMenu.__init__(self, menu_items)
        self.init_handlers(menu_items)
        self._breadcrumb = 0

    @property
    def items(self) -> List[MenuItem]:
        return self.menu_items

    def init_handlers(self, menu_items):
        for item in menu_items:
            if item.handler:
                if isinstance(item.handler, MenuHandler):
                    item.handler = item.handler(self, item)
                elif not isinstance(item.handler, Callable):
                    raise TypeError(
                        f"handler={item.handler} for {item} is not callable"
                    )
            self.init_handlers(item.items)

    def get_menu_selection(self, *chain: str) -> List[int]:
        name, *chain = chain
        selected = [self.index_of(name)]
        item = self[name]
        for name in chain:
            selected.append(item.index_of(name))
            item = item[name]
        return selected


class MenuItem(_MenuItem, BaseMenu):
    """Extends ``prompt_toolkit.widgets.MenuItem`` using :class:`BaseMenu`.

    Adds a ``name`` field which can be used to access child MenuItems with
    brackets (i.e. `item[name]`).
    """

    def __init__(
        self,
        text: str = "",
        key: Optional[str] = None,
        name: Optional[str] = None,
        handler: Optional[Union[MenuHandler, Callable[[], None]]] = None,
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

    @property
    def items(self) -> List[MenuItem]:
        return self.children

    def __str__(self):
        fields = self.text
        for attr in ("key", "name"):
            value = getattr(self, attr)
            if value:
                fields += f", {attr}={value}"
        if self.disabled:
            fields += f", disabled=True"
        return f"{type(self).__name__}({fields})"

    @classmethod
    def SEPARATOR(cls) -> MenuItem:
        """Return an inactive MenuItem that inserts a horizontal line."""
        return cls("-", disabled=True)
