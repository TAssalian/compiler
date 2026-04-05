from __future__ import annotations

from dataclasses import dataclass, field

from frontend.semantics.symbols.symbol_entry import SymbolEntry


@dataclass
class SymbolTable:
    name: str
    kind: str
    parent_scope: SymbolTable | None = None # To walk back up to parent scope to know whether function belongs to a class or if local var shadows class data member
    entries: list[SymbolEntry] = field(default_factory=list)
    inherited_class_tables: list[SymbolTable] = field(default_factory=list)

    # Return matching entries in this symbol table and any inherited class tables.
    def lookup(self, 
        name: str | None = None, 
        kinds: set[str] | None = None, 
        visited: set[int] | None = None,
    ) -> list[SymbolEntry]:
        
        # Prevent infinite recursion if we have circular inheritance    
        if visited is None:
            visited = set()
        table_id = id(self)
        if table_id in visited:
            return []
        visited.add(table_id)

        matches = []
        for entry in self.entries:
            name_matches = name is None or entry.name == name
            kind_matches = kinds is None or entry.kind in kinds
            if name_matches and kind_matches:
                matches.append(entry)
        for symbol_table in self.inherited_class_tables:
            matches.extend(symbol_table.lookup(name, kinds=kinds, visited=visited))
        return matches
