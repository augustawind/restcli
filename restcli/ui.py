from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
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
from prompt_toolkit.widgets import (
    Box,
    Button,
    Checkbox,
    Dialog,
    Frame,
    Label,
    MenuContainer,
    MenuItem,
    ProgressBar,
    RadioList,
    TextArea,
)


def handle_quit():
    get_app().exit()


def new() -> Application:
    collection_text = Label("Open a Collection to see it here")
    collection_frame = Frame(title="Collection view", body=collection_text,)
    environment_text = Label("Open an Environment to see it here")
    environment_frame = Frame(title="Environment view", body=environment_text,)
    body = VSplit([collection_frame, environment_frame], height=D())

    container = MenuContainer(
        body=body,
        floats=[
            Float(
                xcursor=True,
                ycursor=True,
                content=CompletionsMenu(max_height=16, scroll_offset=1),
            ),
        ],
        menu_items=[
            MenuItem(
                "file <F1>",
                children=[
                    MenuItem(
                        "(n)ew file",
                        shortcut=["n"],
                        children=[
                            MenuItem("Collection"),
                            MenuItem("Environment"),
                        ],
                    ),
                    MenuItem(
                        "(o)pen file",
                        shortcut=["o"],
                        children=[
                            MenuItem("Collection"),
                            MenuItem("Environment"),
                        ],
                    ),
                    MenuItem("-", disabled=True),
                    MenuItem(
                        "(s)ave",
                        shortcut=["s"],
                        children=[
                            MenuItem("Save Collection"),
                            MenuItem("Save Environment"),
                        ],
                    ),
                    MenuItem(
                        "save as... <Ctrl+S>",
                        shortcut=["c-s"],
                        children=[
                            MenuItem("Save Collection as..."),
                            MenuItem("Save Environment as..."),
                        ],
                    ),
                    MenuItem("save all"),
                    MenuItem("-", disabled=True),
                    MenuItem(
                        "(c)lose file",
                        shortcut=["c"],
                        children=[
                            MenuItem("Collection"),
                            MenuItem("Environment"),
                        ],
                    ),
                    MenuItem("close all <Ctrl+W>", shortcut=["c-w"]),
                    MenuItem("-", disabled=True),
                    MenuItem("quit <Ctrl+Q>", shortcut=["c-q"], handler=handle_quit),
                ],
            )
        ],
    )

    layout = Layout(container, focused_element=collection_text)

    key_bindings = KeyBindings()
    key_bindings.add("tab")(focus_next)
    key_bindings.add("s-tab")(focus_previous)

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
        # mouse_support=True,
        full_screen=True,
    )
