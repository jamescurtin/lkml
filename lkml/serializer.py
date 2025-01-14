from copy import deepcopy
from typing import Any, Dict, Iterator, Sequence

from lkml.keys import (
    EXPR_BLOCK_KEYS,
    KEYS_WITH_NAME_FIELDS,
    PLURAL_KEYS,
    QUOTED_LITERAL_KEYS,
)


class Serializer:
    def __init__(self):
        self.parent_key: str = None
        self.level = 0
        self.field_counter = 0
        self.base_indent = " " * 2
        self.indent = ""
        self.newline_indent = "\n"

    def increase_level(self) -> None:
        self.field_counter = 0
        self.level += 1
        self.update_indent()

    def decrease_level(self) -> None:
        self.field_counter = 0
        self.level -= 1
        self.update_indent()

    def update_indent(self) -> None:
        self.indent = self.base_indent * self.level
        self.newline_indent = "\n" + self.indent

    def is_plural_key(self, key) -> bool:
        if key.endswith("s"):
            singular_key = key.rstrip("s")
            return (
                singular_key in PLURAL_KEYS
                # `allowed_values` can be a set or a plural key depending on the parent
                and not (
                    singular_key == "allowed_value"
                    and self.parent_key.rstrip("s") == "access_grant"
                )
            )
        else:
            return False

    def serialize(self, obj: Dict) -> str:
        def chain_with_newline():
            for key, value in deepcopy(obj).items():
                yield from self.write_any(key, value)
                yield "\n"

        return "".join(chain_with_newline())

    def expand_list(self, key: str, values: Sequence) -> Iterator[str]:
        modified_key = key.rstrip("s") if key not in ("filters") else key
        for i, value in enumerate(values):
            if i > 0:
                yield "\n"
            yield from self.write_any(modified_key, value)

    def write_any(self, key: str, value: Any) -> Iterator[str]:
        if isinstance(value, str):
            yield from self.write_pair(key, value)

        if isinstance(value, (list, tuple)):
            if self.is_plural_key(key):
                yield from self.expand_list(key, value)
            else:
                yield from self.write_set(key, value)

        if isinstance(value, dict):
            if key in KEYS_WITH_NAME_FIELDS or "name" not in value.keys():
                name = None
            else:
                name = value.pop("name")
            yield from self.write_block(key, value, name)

        self.field_counter += 1

    def write_block(
        self, key: str, fields: Dict[str, Any], name: str = None
    ) -> Iterator[str]:
        if self.field_counter > 0:
            yield "\n"

        yield from self.write_key(key)
        if name:
            yield f"{name} " + "{"
        else:
            yield "{"

        if fields:
            self.parent_key = key
            self.increase_level()
            yield "\n"
            for i, (key, value) in enumerate(fields.items()):
                if i > 0:
                    yield "\n"
                yield from self.write_any(key, value)
            self.decrease_level()
            yield self.newline_indent

        yield "}"

    def write_set(self, key: str, values: Sequence[str]) -> Iterator[str]:
        # `suggestions` is only quoted when it's a set, so override the default
        force_quote = True if key == "suggestions" else False

        yield from self.write_key(key)
        yield "["

        if values:
            if len(values) > 5:
                self.increase_level()
                yield self.newline_indent
                for i, value in enumerate(values):
                    if i > 0:
                        yield f",{self.newline_indent}"
                    yield from self.write_value(key, value, force_quote)
                self.decrease_level()
                yield self.newline_indent
            else:
                for i, value in enumerate(values):
                    if i > 0:
                        yield f", "
                    yield from self.write_value(key, value, force_quote)
        yield "]"

    def write_pair(self, key: str, value: str) -> Iterator[str]:
        yield from self.write_key(key)
        yield from self.write_value(key, value)

    def write_key(self, key: str) -> Iterator[str]:
        yield f"{self.indent}{key}: "

    def write_value(
        self, key: str, value: str, force_quote: bool = False
    ) -> Iterator[str]:
        if force_quote or key in QUOTED_LITERAL_KEYS:
            yield '"'
            yield value
            yield '"'
        elif key in EXPR_BLOCK_KEYS:
            yield value
            yield " ;;"
        else:
            yield value
