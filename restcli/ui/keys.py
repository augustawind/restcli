from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import (
    focus_next,
    focus_previous,
)


def tab_focus(key_bindings: KeyBindings):
    key_bindings.add("tab")(focus_next)
    key_bindings.add("s-tab")(focus_previous)
