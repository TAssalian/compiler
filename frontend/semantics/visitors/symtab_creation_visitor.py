from __future__ import annotations

from frontend.semantics.symbols import Diagnostic, SymbolEntry, SymbolTable
from frontend.semantics.visitors.visitor import Visitor
from frontend.ast.nodes import ClassDeclNode, FParamNode, FParamsNode, FuncDeclNode, FuncDefNode, ProgNode, ProgramBlockNode, StartNode, VarDeclNode


class SymTabCreationVisitor(Visitor):
    def __init__(self) -> None:
        self.global_table: SymbolTable | None = None # Used to track all top-level declarations + what subscopes have access to
        self.current_scope: SymbolTable | None = None # Says where to insert new SymbolEntrys, what names are visible when checking for duplicates and the types of var declarations
        self.class_entries_by_name: dict[str, SymbolEntry] = {} # Maps class name to its SymbolEntry to find each parent class entry and its inner table for inheritance checks
        self.member_functions: dict[tuple[str, str, tuple[str, ...]], dict[str, SymbolEntry | list[FuncDefNode] | None]] = {} # Because this grammar separates func. declarations from func. definitions, we want to add the definition to a previously declared function instead of creating a second function entry and table.
        self.diagnostics: list[Diagnostic] = [] # Gather semantic warnings and errors

    def generic_visit(self, node):
        for child in node.iter_children():
            child.accept(self)
        return node.symtab

    def visit_StartNode(self, node: StartNode):
        program = node.first_child
        program.accept(self)
        node.symtab = program.symtab
        return node.symtab

    def visit_ProgNode(self, node: ProgNode):
        self.global_table = SymbolTable("global", "global")
        node.symtab = self.global_table
        self._visit_in_scope(child_nodes=node.iter_children(), scope=self.global_table) # Enter the global scope by passing it and then going through the children node with that scope activated. Here we enter the global scope to add entries to the global table

        self._link_inheritance() # Append inherited symbol tables to the class' table's list of inherited tables. This is for type checking phase.
        self._match_member_functions() 
        return self.global_table
    
    def visit_ClassDeclNode(self, node: ClassDeclNode):        
        class_name = node.id_node.token.lexeme
        
        existing = self.current_scope.lookup(class_name, {"class"})
        if existing:
            self._diagnostic("error", "multiply_declared_class", f"multiply declared class '{class_name}'.", node)
            node.symtab_entry = existing[0]
            node.symtab = existing[0].inner_scope_table
            return existing[0].inner_scope_table

        class_table = SymbolTable(class_name, "class", parent_scope=self.current_scope)        
        node.symtab = class_table 
        
        entry = SymbolEntry(
            name=class_name,
            kind="class",
            type=class_name,
            inner_scope_table=class_table,
            node=node,
        )
        self.current_scope.entries.append(entry) 
        self.class_entries_by_name[class_name] = entry
        node.symtab_entry = entry
        
        self._visit_in_scope(node.members, class_table) # Visit the scope of this class table to see its members
        return class_table
    
    def visit_FuncDeclNode(self, node: FuncDeclNode):
        entry = self._make_entry(node, "member_function", owner_class=self.current_scope.name)
        duplicate = None
        existing_functions = self.current_scope.lookup(entry.name, {"member_function"})
        for existing in existing_functions:
            if existing.parameter_types == entry.parameter_types:
                duplicate = existing
                break
        if duplicate:
            self._diagnostic(
                "error",
                "multiply_declared_member_function",
                f"multiply declared member function '{self.current_scope.name}::{entry.name}'.",
                node,
            )
            node.symtab_entry = duplicate
            node.symtab = duplicate.inner_scope_table
            return duplicate.inner_scope_table

        if self.current_scope.lookup(entry.name, {"member_function"}):
            self._diagnostic(
                "warning",
                "overloaded_member_function",
                f"overloaded member function '{self.current_scope.name}::{entry.name}'.",
                node,
            )

        function_table = SymbolTable(f"{self.current_scope.name}::{entry.name}", "function", parent_scope=self.current_scope)
        node.symtab = function_table
        entry.inner_scope_table = function_table
        
        self.current_scope.entries.append(entry)
        node.symtab_entry = entry
        previous_scope = self.current_scope
        self.current_scope = function_table
        node.fparams_node.accept(self)
        self.current_scope = previous_scope

        # Track this declaration by its full method signature so it can be matched later with a corresponding member-function definition
        key = (entry.owner_class, entry.name, tuple(entry.parameter_types))
        self.member_functions[key] = {"declaration": entry, "definitions": []}
        return function_table

    def visit_FuncDefNode(self, node: FuncDefNode):
        # If the function belongs to a class -> ClassName::Method(...), add this definition to it in the record
        if node.owner_id_node is not None:
            owner_name = node.owner_id_node.token.lexeme
            parameter_types = []
            for param in node.fparams_node.params:
                parameter_types.append(self._format_type(param.type_node.token.lexeme, param.array_size_node))
            key = (owner_name, node.id_node.token.lexeme, tuple(parameter_types))
            record = self.member_functions.setdefault(key, {"declaration": None, "definitions": []})
            record["definitions"].append(node)
            return None

        # This is a free function that we found
        entry = self._make_entry(node, "function")
        duplicate = None
        existing_functions = self.global_table.lookup(entry.name, {"function"})
        
        for existing in existing_functions:
            if existing.parameter_types == entry.parameter_types:
                duplicate = existing
                break
        if duplicate:
            self._diagnostic("error", "multiply_declared_function", f"multiply declared free function '{entry.name}'.", node)
            node.symtab_entry = duplicate
            node.symtab = duplicate.inner_scope_table
            return duplicate.inner_scope_table

        if self.global_table.lookup(entry.name, {"function"}):
            self._diagnostic("warning", "overloaded_function", f"overloaded free function '{entry.name}'.", node)

        function_table = SymbolTable(entry.name, "function", parent_scope=self.global_table)
        node.symtab = function_table
        entry.inner_scope_table = function_table
        
        self.global_table.entries.append(entry)
        node.symtab_entry = entry
        self._visit_function_definition(node, function_table)
        return function_table

    def visit_FParamNode(self, node: FParamNode):
        entry = self._make_entry(node, "param")
        duplicate = None
        existing_variables = self.current_scope.lookup(entry.name, {"param", "local_var"})
        for existing in existing_variables:
            duplicate = existing
            break
        if duplicate:
            self._diagnostic("error", "multiply_declared_variable", f"multiply declared local variable '{entry.name}'.", node)
            node.symtab_entry = duplicate
            return duplicate

        self.current_scope.entries.append(entry)
        node.symtab_entry = entry
        return entry

    def visit_VarDeclNode(self, node: VarDeclNode):
        # Decide if it's a class variable or a local variable
        kind = "local_var"
        if self.current_scope.kind == "class":
            kind = "data_member"
        
        entry = self._make_entry(node, kind)

        if kind == "data_member":
            duplicate = None
            existing_members = self.current_scope.lookup(entry.name, {"data_member"})
            for existing in existing_members:
                duplicate = existing
                break
            if duplicate:
                self._diagnostic("error", "multiply_declared_data_member", f"multiply declared data member '{entry.name}'.", node)
                node.symtab_entry = duplicate
                return duplicate
        else:
            duplicate = None
            existing_variables = self.current_scope.lookup(entry.name, {"param", "local_var"})
            for existing in existing_variables:
                duplicate = existing
                break
            if duplicate:
                self._diagnostic("error", "multiply_declared_variable", f"multiply declared local variable '{entry.name}'.", node)
                node.symtab_entry = duplicate
                return duplicate
            owner_class = None
            if self.current_scope.parent_scope and self.current_scope.parent_scope.kind == "class":
                owner_class = self.class_entries_by_name.get(self.current_scope.parent_scope.name)
            if owner_class and owner_class.inner_scope_table.lookup(entry.name, {"data_member"}):
                self._diagnostic(
                    "warning",
                    "local_shadows_data_member",
                    f"local variable '{entry.name}' in member function shadows data member of class '{owner_class.name}'.",
                    node,
                )

        self.current_scope.entries.append(entry)
        node.symtab_entry = entry
        return entry

    def visit_ProgramBlockNode(self, node: ProgramBlockNode):
        function_table = SymbolTable("main", "function", parent_scope=self.global_table)
        entry = SymbolEntry(
            name="main",
            kind="function",
            type="void",
            parameter_types=[],
            inner_scope_table=function_table,
            node=node,
        )
        self.global_table.entries.append(entry)
        node.symtab_entry = entry
        node.symtab = function_table
        self._visit_in_scope(node.iter_children(), function_table)
        return function_table

    def _visit_function_definition(self, node: FuncDefNode, function_table: SymbolTable) -> None:
        node.symtab = function_table
        child_nodes = [node.func_body_node]
        if not function_table.lookup(kinds={"param"}):
            child_nodes.insert(0, node.fparams_node)
        self._visit_in_scope(child_nodes, function_table)

    # Store a class table's inheritance class table for quick checks related to inheritance
    def _link_inheritance(self) -> None:
        # Loop through all class SymbolEntry objects of the SymTabCreationVisitor
        for class_entry in self.class_entries_by_name.values():
            
            # Get the class node belonging to the SymbolEntry + SymbolTable stored at this entry containing members and function declarations of the class
            class_node = class_entry.node
            class_table = class_entry.inner_scope_table
            
            # Loop through all the classes this current node inherits from
            for inherits_node in class_node.inherits:
                inherits_node_name = inherits_node.id_node.token.lexeme
                parents_symbol_entry = self.class_entries_by_name.get(inherits_node_name)
                # Append the parent's symbol table to the current class' list of inherited symbol tables because it has access to the same members and we want it to in a quick way
                if parents_symbol_entry and parents_symbol_entry.inner_scope_table:
                    class_table.inherited_class_tables.append(parents_symbol_entry.inner_scope_table)
            
            # Throw warnings if members in the child class shadow inherited members.
            for entry in class_table.entries:
                inherited_data_members = []
                inherited_member_functions = []
                for inherited_table in class_table.inherited_class_tables:
                    inherited_data_members.extend(
                        inherited_table.lookup(entry.name, {"data_member"}, visited={id(class_table)})
                    )
                    inherited_member_functions.extend(
                        inherited_table.lookup(entry.name, {"member_function"}, visited={id(class_table)})
                    )

                if entry.kind == "data_member" and inherited_data_members:
                    self._diagnostic(
                        "warning",
                        "shadowed_inherited_data_member",
                        f"class '{class_table.name}' shadows inherited data member '{entry.name}'.",
                        entry.node,
                    )
                elif entry.kind == "member_function" and inherited_member_functions:
                    same_signature = any(
                        inherited.parameter_types == entry.parameter_types
                        for inherited in inherited_member_functions
                    )
                    if same_signature:
                        self._diagnostic(
                            "warning",
                            "overridden_member_function",
                            f"overridden member function '{class_table.name}::{entry.name}'.",
                            entry.node,
                        )
                    else:
                        self._diagnostic(
                            "warning",
                            "shadowed_inherited_member_function",
                            f"class '{class_table.name}' shadows inherited member function '{entry.name}'.",
                            entry.node,
                        )

    # Only called when creating global table
    # connects a class method's header to the actual body by finding matching declaration/definition pairs
    def _match_member_functions(self) -> None:
        for key, record in self.member_functions.items():
            declaration = record["declaration"] # Get symbol entry for declared method
            definitions = record["definitions"] # Get list of FuncDefNodes or an empty list if not defined

            # If function declared + defined, match them
            if declaration and definitions:
                definition = definitions[0]
                definition.symtab_entry = declaration
                definition.symtab = declaration.inner_scope_table
                self._visit_function_definition(definition, declaration.inner_scope_table)

            for extra_definition in definitions[1:]:
                self._diagnostic(
                    "error",
                    "multiply_defined_member_function",
                    f"multiply declared member function '{key[0]}::{key[1]}'.",
                    extra_definition,
                )

            if declaration and not definitions:
                self._diagnostic(
                    "error",
                    "missing_member_definition",
                    f"undefined member function declaration '{declaration.owner_class}::{declaration.name}'.",
                    declaration.node,
                )

            if definitions and not declaration:
                for definition in definitions:
                    self._diagnostic(
                        "error",
                        "undeclared_member_definition",
                        f"undeclared member function definition '{key[0]}::{key[1]}'.",
                        definition,
                    )

    # Make a function declaration, definition, function parameter or variable declaration SymbolEntry to put into a SymbolTable
    def _make_entry(self, node: FuncDeclNode | FuncDefNode | FParamNode | VarDeclNode, kind: str, owner_class: str | None = None) -> SymbolEntry:
        type_node = getattr(node, "return_type_node", None) or getattr(node, "type_node", None)
        parameter_types = [] # Store string representation of parameter
        
        if isinstance(node, (FuncDeclNode, FuncDefNode)) and node.fparams_node is not None:
            for param in node.fparams_node.params:
                parameter_types.append(self._format_type(param.type_node.token.lexeme, param.array_size_node))
        
        array_dimensions = []
        if isinstance(node, (FParamNode, VarDeclNode)) and node.array_size_node is not None:
            array_dimensions = self._dimensions(node.array_size_node)
            
        return SymbolEntry(
            name=node.id_node.token.lexeme,
            kind=kind,
            type=type_node.token.lexeme,
            parameter_types=parameter_types,
            array_dimensions=array_dimensions,
            owner_class=owner_class,
            node=node,
        )

    def _dimensions(self, array_size_node) -> list[int | None]:
        dimensions = []
        for dimension in array_size_node.dimensions:
            if dimension is None:
                dimensions.append(None)
            else:
                dimensions.append(int(dimension.token.lexeme))
        return dimensions

    def _format_type(self, base_type: str, array_size_node) -> str:
        dims = self._dimensions(array_size_node)
        suffix = []
        for dim in dims:
            if dim is None:
                suffix.append("[]")
            else:
                suffix.append(f"[{dim}]")
        suffix = "".join(suffix)
        return f"{base_type}{suffix}"

    # Switches the visitor into a different scope, looks at the children to add to the new scope, then restore the previous state
    def _visit_in_scope(self, child_nodes, scope: SymbolTable) -> None:
        previous_scope = self.current_scope        
        self.current_scope = scope
        
        for node in child_nodes:
            node.accept(self)
            
        self.current_scope = previous_scope

    def _diagnostic(self, severity: str, code: str, message: str, node) -> None:
        self.diagnostics.append(Diagnostic(severity=severity, code=code, message=message, line=node.token.line))
