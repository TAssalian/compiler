from __future__ import annotations

from abc import ABC


class Visitor(ABC):
    def visit_children(self, node):
        for child in node.iter_children():
            child.accept(self)
        return node.symtab
