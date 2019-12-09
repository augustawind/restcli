from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Callable, List, Optional, Sequence, Union

from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings, KeyBindingsBase
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import AnyContainer, Float
from prompt_toolkit.widgets import MenuContainer as _MenuContainer
from prompt_toolkit.widgets import MenuItem as _MenuItem

from restcli.utils import AttrMap

if TYPE_CHECKING:
    from restcli.ui import UI


class MenuHandler(metaclass=abc.ABCMeta):
    """Base class for handlers that respond to user interaction.

    Attributes
    ----------

    ui
        The UI object this handler is attached to.
    items
        The chain of :class:`restcli.ui.menu.MenuItem`s from the root menu
        all the way to the current ``MenuItem`.

    Implementor classes can be passed to :class:`MenuItem` via the
    ``handler`` parameter. When the ``MenuItem`` is triggered, either by a
    mouse click or a key press, an instance of the MenuHandler class passed
    to ``handler`` will be created and then called.
    """

    def __init__(self, ui: UI, items: Sequence[MenuItem]):
        self.ui = ui
        self.items = items

    @abc.abstractmethod
    def __call__(self, event: Optional[KeyPressEvent] = None):
        """Execute the handler.

        This function be used to respond to clicks (if mouse is enabled) and
        to key presses (if a keyboard shortcut is provided). Implementors
        must _optionally_ accept a single :class:`KeyPressEvent` parameter.
        It must be optional so that it can respond to both mouse clicks
        _and_ key presses, since only key presses generate a
        ``KeyPressEvent``.
        """


class MenuItemsMixin(metaclass=abc.ABCMeta):
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
        """Should return the list of all child :class:`MenuItem` objects."""

    def register_key_bindings(self, kb: KeyBindings):
        for item in self.items:
            if item.key and item.handler:
                kb.add(item.key)(item.handler)
            item.register_key_bindings(kb)

    def __getitem__(self, name: str) -> MenuItem:
        return self._item_map[name]

    def index_of(self, name: str) -> MenuItem:
        return self._item_idx_map[name]


class MenuContainer(_MenuContainer, MenuItemsMixin):
    def __init__(
        self,
        ui: UI,
        body: AnyContainer,
        menu_items: List[MenuItem],
        floats: Optional[List[Float]] = None,
        key_bindings: Optional[KeyBindingsBase] = None,  # TODO: figure dis out
    ):
        super().__init__(body, menu_items, floats, key_bindings)
        MenuItemsMixin.__init__(self, menu_items)

        self.ui = ui
        self.breadcrumb = 0
        self._init_items(menu_items)

    @property
    def items(self) -> List[MenuItem]:
        return self.menu_items

    def _init_items(self, menu_items, chain=()):
        for item in menu_items:
            # Pass UI instance down for convenience
            if not item.ui:
                item.ui = self.ui

            # Instantiate MenuHandlers into normal handler funcs
            item_chain = chain + (item,)
            if item.handler:
                if not issubclass(item.handler, MenuHandler):
                    raise TypeError(
                        f"{item}: MenuItem.handler must be a subclass of"
                        " MenuHandler"
                    )
                item.handler = item.handler(self.ui, item_chain)

            # Initialize grandchildren
            self._init_items(item.items, chain=item_chain)

    def get_menu_selection(self, chain: Sequence[str]) -> List[int]:
        name, *chain = chain
        selected = [self.index_of(name)]
        item = self[name]
        for name in chain:
            selected.append(item.index_of(name))
            item = item[name]
        return selected


class MenuItem(_MenuItem, MenuItemsMixin):
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
        disabled: bool = False,
        ui: Optional[UI] = None,
    ):
        self.name = name
        if key:
            text = text.format(key=key)
        self.key = key

        self.ui = ui

        super().__init__(
            text=text, handler=handler, children=children, disabled=disabled
        )
        MenuItemsMixin.__init__(self, children)

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
