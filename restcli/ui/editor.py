from __future__ import annotations

from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.layout.containers import (
    AnyContainer,
    HSplit,
    VerticalAlign,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType
from prompt_toolkit.widgets import Frame, TextArea, VerticalLine
from pygments.lexers.data import YamlLexer

from restcli import yaml_utils as yaml
from restcli.ui.menu import MenuContainer, MenuItem
from restcli.workspace import Collection, GroupType, RequestType


class Editor:
    def __init__(self, width=None, height=None):
        self.width = width
        self.height = height

        collection = Collection(source="examples/full/collection.yaml")

        self.text_area = TextArea(
            lexer=PygmentsLexer(YamlLexer),
            width=D(weight=2),
            focus_on_click=True,
            line_numbers=True,
        )
        self.menu_items = []
        self.child_menu_items = []
        self.expanded_menu_indices = set()

        def mktext(text: str):
            def handler(event: MouseEvent):
                if event.event_type == MouseEventType.MOUSE_UP:
                    self.text_area.text = text
                    self.refresh()
                else:
                    return NotImplemented

            return [("#00ff00", text, handler)]

        # Create some dummy data
        for i, group_name in enumerate(("lions", "tigers", "bears",)):
            self.menu_items.append(
                Window(
                    FormattedTextControl(
                        self.make_group_nav(i, group_name, {}), focusable=True
                    )
                )
            )
            self.child_menu_items.append([])
            for n in range(0, len(group_name) * 3, len(group_name)):
                label = f"{group_name}{n}"
                self.child_menu_items[-1].append(
                    Window(FormattedTextControl(mktext(label), focusable=True))
                )
        self.refresh()

    def __pt_container__(self) -> AnyContainer:
        return self.container

    def refresh(self):
        menu_items = []
        for i, menu_item in enumerate(self.menu_items):
            menu_items.append(menu_item)
            if i in self.expanded_menu_indices:
                child_menu_items = self.child_menu_items[i]
                menu_items.extend(child_menu_items)

        self.side_menu = HSplit(
            menu_items, width=D(weight=1), align=VerticalAlign.TOP,
        )
        self.container = Frame(
            VSplit([self.side_menu, VerticalLine(), self.text_area]),
            title="Collection",
            width=self.width,
            height=self.height,
        )

    def make_group_nav(
        self, index: int, group_name: str, group: GroupType
    ) -> StyleAndTextTuples:
        def handler(event: MouseEvent):
            if event.event_type == MouseEventType.MOUSE_UP:
                self.expanded_menu_indices.add(index)
                self.refresh()
            else:
                return NotImplemented

        return [("#00ff00", group_name, handler)]

    def make_request_nav(
        self, request_name: str, request: RequestType
    ) -> StyleAndTextTuples:
        def handler(event: MouseEvent):
            if event.event_type == MouseEventType.MOUSE_UP:
                self.text_area.text = yaml.dump(request)
                self.refresh()
            else:
                return NotImplemented

        label_text = f"\t{request_name}"
        return [("#00ff00", label_text, handler)]
