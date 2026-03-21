from __future__ import annotations

from dataclasses import dataclass, field

from backend.symbols.symbol_entry import SymbolEntry


@dataclass
class SymbolTable:
    name: str
    kind: str
    parent_scope: SymbolTable | None = None
    entries: list[SymbolEntry] = field(default_factory=list)
    inherited_class_tables: list[SymbolTable] = field(default_factory=list)

    # Return matching entries in this symbol table and any inherited class tables.
    def lookup(self, name: str | None = None, kinds: set[str] | None = None) -> list[SymbolEntry]:
        matches = []
        for entry in self.entries:
            name_matches = name is None or entry.name == name
            kind_matches = kinds is None or entry.kind in kinds
            if name_matches and kind_matches:
                matches.append(entry)
        for symbol_table in self.inherited_class_tables:
            matches.extend(symbol_table.lookup(name, kinds=kinds))
        return matches
