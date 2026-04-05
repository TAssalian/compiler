from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Iterator

from frontend.lexer.tokens import Token

if TYPE_CHECKING:
    from frontend.semantics.symbols import SymbolEntry, SymbolTable


@dataclass
class Node:
    token: Token
    parent: Node | None = None
    first_child: Node | None = None
    last_child: Node | None = None
    prev_sibling: Node | None = None
    next_sibling: Node | None = None
    symtab: SymbolTable | None = None # Store scope associated with node so we could re-enter scopes easily for the SemanticCheckingVisitor. Without it, semantic checking would have to rediscover the relevant entries or scopes by searching from parent scope, looking at each entry for right name, then get inner scope table
    symtab_entry: SymbolEntry | None = None # Stores declaration records in a symbol table associated with that node, which is used for types checks and id resolution.
    

    def add_child(self, child: Node) -> None:
        child.parent = self
        child.prev_sibling = self.last_child
        child.next_sibling = None

        if self.last_child is None:
            self.first_child = child
        else:
            self.last_child.next_sibling = child

        self.last_child = child

    def iter_children(self) -> Iterator[Node]:
        current = self.first_child
        while current is not None:
            yield current
            current = current.next_sibling

    def accept(self, visitor: Any) -> Any:
        method_name = f"visit_{self.__class__.__name__}" # Get's method name dynamically
        visit_func = getattr(visitor, method_name, None) # Check whether specific visitor subclass has that method or not.
        if visit_func is None:
            return visitor.generic_visit(self)
        return visit_func(self)
