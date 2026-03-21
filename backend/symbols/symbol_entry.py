from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.symbols.symbol_table import SymbolTable


@dataclass
class SymbolEntry:
    name: str
    kind: str
    type: str | None = None
    
    parameter_types: list[str] = field(default_factory=list)
    array_dimensions: list[int | None] = field(default_factory=list)
    inner_scope_table: SymbolTable | None = None
    line: int | None = None
    owner_class: str | None = None
    node: object | None = None
    is_definition: bool = False
