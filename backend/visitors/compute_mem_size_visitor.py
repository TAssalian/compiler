from __future__ import annotations

from frontend.ast.nodes import (
    AddOpNode,
    ClassDeclNode,
    FloatNumNode,
    FParamNode,
    FuncBodyNode,
    FuncDefNode,
    IdNode,
    IndexNode,
    IntNumNode,
    MinusNode,
    MultOpNode,
    NotNode,
    PlusNode,
    ProgNode,
    ProgramBlockNode,
    RelOpNode,
    StartNode,
    VarDeclNode,
    VariableNode,
)
from frontend.semantics.symbols import SymbolEntry, SymbolTable
from frontend.semantics.visitors.visitor import Visitor


class ComputeMemSizeVisitor(Visitor):
    INTEGER_SIZE = 4
    FLOAT_SIZE = 8
    ADDRESS_SIZE = 4

    def __init__(self, global_table: SymbolTable | None = None) -> None:
        self.global_table = global_table
        self.current_scope: SymbolTable | None = global_table
        self.current_offset = 0
        self.literal_counter = 0
        self.temp_counter = 0
        self._computed_class_tables: set[int] = set()
        self._active_class_tables: set[int] = set()

    def visit_ProgNode(self, node: ProgNode):
        self.global_table = node.symtab
        self.current_scope = self.global_table
        self.visit_children(node)

    def visit_ClassDeclNode(self, node: ClassDeclNode):
        class_table = node.symtab
        table_id = id(class_table)
        if table_id in self._computed_class_tables:
            return None

        self._active_class_tables.add(table_id)
        previous_scope = self.current_scope

        self.current_scope = class_table
        self.current_offset = 0
        class_table.inherited_class_offsets.clear()

        for inherits_node in node.inherits:
            parent_entry = self._lookup_class(inherits_node.id_node.token.lexeme)
            parent_table = parent_entry.inner_scope_table
            parent_table_id = id(parent_table)
            if parent_table_id not in self._computed_class_tables and parent_table_id not in self._active_class_tables:
                parent_entry.node.accept(self)
            class_table.inherited_class_offsets[parent_table.name] = self.current_offset
            self.current_offset += parent_table.size

        for member in node.members:
            if isinstance(member, VarDeclNode):
                member.accept(self)

        class_table.size = self.current_offset
        self._active_class_tables.remove(table_id)
        self._computed_class_tables.add(table_id)
        self.current_scope = previous_scope

    def visit_FuncDefNode(self, node: FuncDefNode):
        function_table = node.symtab
        previous_scope = self.current_scope

        self.current_scope = function_table
        self.current_offset = 0
        self.literal_counter = 0
        self.temp_counter = 0

        node.fparams_node.accept(self)
        node.func_body_node.accept(self)
        
        self._compute_ret_val_size(node.symtab_entry.type)
        self._compute_ret_addr_size()
        function_table.size = self.current_offset

        self.current_scope = previous_scope

    def visit_ProgramBlockNode(self, node: ProgramBlockNode):
        function_table = node.symtab
        previous_scope = self.current_scope

        self.current_scope = function_table
        self.current_offset = 0
        self.literal_counter = 0
        self.temp_counter = 0

        self._compute_ret_val_size(node.symtab_entry.type)
        self._compute_ret_addr_size()
        self.visit_children(node)
        function_table.size = self.current_offset

        self.current_scope = previous_scope

    def visit_FParamNode(self, node: FParamNode):
        entry = node.symtab_entry
        entry.size = self._size_of_variable_entry(entry)
        entry.offset = self.current_offset
        self.current_offset += entry.size

    def visit_VarDeclNode(self, node: VarDeclNode):
        entry = node.symtab_entry
        entry.size = self._size_of_variable_entry(entry)
        entry.offset = self.current_offset
        self.current_offset += entry.size

    def visit_IntNumNode(self, node: IntNumNode):
        node.symtab_entry = self._make_synthetic_entry(
            name=f"__lit{self._next_literal_id()}",
            kind="literal",
            type_name=node.inferred_type,
            size=self._size_of_type(node.inferred_type, []),
            owner_class=None,
            node=node,
        )

    def visit_FloatNumNode(self, node: FloatNumNode):
        node.symtab_entry = self._make_synthetic_entry(
            name=f"__lit{self._next_literal_id()}",
            kind="literal",
            type_name=node.inferred_type,
            size=self._size_of_type(node.inferred_type, []),
            owner_class=None,
            node=node,
        )

    def visit_PlusNode(self, node: PlusNode):
        self.visit_children(node)
        self._compute_temp_for_node(node)

    visit_MinusNode = visit_PlusNode
    visit_NotNode = visit_PlusNode
    visit_AddOpNode = visit_PlusNode
    visit_MultOpNode = visit_PlusNode
    visit_RelOpNode = visit_PlusNode

    def _compute_ret_val_size(self, return_type: str | None) -> None:
        return_value_size = self._size_of_type(return_type, []) if return_type not in {None, "void"} else 0
        self._make_synthetic_entry(
            name="__ret_val",
            kind="return_value",
            type_name=return_type,
            size=return_value_size,
            owner_class=None,
        )

    def _compute_ret_addr_size(self) -> None:
        self._make_synthetic_entry(
            name="__ret_addr",
            kind="return_address",
            type_name="address",
            size=self.ADDRESS_SIZE,
            owner_class=None,
        )

    def _compute_temp_for_node(self, node) -> None:
        if self.current_scope is None or getattr(node, "inferred_type", None) is None:
            return
        node.symtab_entry = self._make_synthetic_entry(
            name=f"__tmp{self._next_temp_id()}",
            kind="temp",
            type_name=node.inferred_type,
            size=self._size_of_type(node.inferred_type, []),
            owner_class=None,
            node=node,
        )

    def _make_synthetic_entry(
        self,
        name: str,
        kind: str,
        type_name: str | None,
        size: int,
        owner_class: str | None,
        node=None,
    ) -> SymbolEntry:
        
        entry = SymbolEntry(
            name=name,
            kind=kind,
            type=type_name,
            owner_class=owner_class,
            node=node,
            size=size,
            offset=self.current_offset,
        )
        
        self.current_offset += size
        self.current_scope.entries.append(entry)
        return entry

    def _size_of_variable_entry(self, entry: SymbolEntry) -> int:
        if entry.kind == "param" and entry.array_dimensions:
            return self.ADDRESS_SIZE
        return self._size_of_type(entry.type, entry.array_dimensions)

    def _size_of_type(self, base_type: str | None, array_dimensions: list[int | None]) -> int:
        if base_type == "integer":
            size = self.INTEGER_SIZE
        elif base_type == "float":
            size = self.FLOAT_SIZE
        else:
            class_entry = self._lookup_class(base_type)
            class_table = class_entry.inner_scope_table
            class_table_id = id(class_table)
            if class_table_id not in self._computed_class_tables and class_table_id not in self._active_class_tables:
                class_entry.node.accept(self)
            size = class_table.size

        total_size = size
        for dimension in array_dimensions:
            if dimension is None:
                continue
            total_size *= dimension
        return total_size

    def _lookup_class(self, class_name: str | None) -> SymbolEntry | None:
        return self.global_table.lookup(class_name, {"class"})[0]
        base_type = self._base_type(type_name)
        if base_type in {"integer", "float", "void", None}:
            return None
        return self._lookup_class(base_type).inner_scope_table

    def _base_type(self, type_name: str | None) -> str | None:
        if type_name is None:
            return None
        return type_name.split("[", 1)[0]

    def _next_literal_id(self) -> int:
        self.literal_counter += 1
        return self.literal_counter

    def _next_temp_id(self) -> int:
        self.temp_counter += 1
        return self.temp_counter