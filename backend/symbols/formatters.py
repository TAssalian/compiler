from __future__ import annotations

from backend.symbols.diagnostic import Diagnostic
from backend.symbols.symbol_table import SymbolTable


# get all the diagnostics found in the table of the <x>CreationVisitor class during the traversal
def format_diagnostics(diagnostics: list[Diagnostic]) -> str:
    lines = []
    for diagnostic in diagnostics:
        lines.append(f"Semantic {diagnostic.severity} at line {diagnostic.line}: {diagnostic.message}")
    return "\n".join(lines)

# print table information, first loop: goes through current table entries, second loop: recursively goes through nested tables and their entries
def format_symbol_table(table: SymbolTable, indent: int = 0) -> str:
    pad = "  " * indent
    lines = [f"{pad}Table: {table.name} ({table.kind})", f"{pad}name | kind | type | link"]
    for entry in table.entries:
        entry_type = entry.type or ""
        if entry.array_dimensions:
            dimension_suffixes = []
            for dim in entry.array_dimensions:
                if dim is None:
                    dimension_suffixes.append("[]")
                else:
                    dimension_suffixes.append(f"[{dim}]")
            entry_type += "".join(dimension_suffixes)
        link_name = ""
        if entry.inner_scope_table:
            link_name = entry.inner_scope_table.name
        lines.append(
            f"{pad}{entry.name} | {entry.kind} | {entry_type} | {link_name}"
        )
    lines.append(f"{pad}" + "-" * 40)
    for entry in table.entries:
        if entry.inner_scope_table is not None:
            lines.append(format_symbol_table(entry.inner_scope_table, indent + 1))
    return "\n".join(lines)
