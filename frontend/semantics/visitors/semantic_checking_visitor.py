from frontend.semantics.symbols import Diagnostic, SymbolEntry, SymbolTable
from frontend.semantics.visitors.visitor import Visitor
from frontend.ast.nodes import (
    AParamsNode,
    AddOpNode,
    AssignOpNode,
    ClassDeclNode,
    FParamNode,
    FParamsNode,
    FloatNumNode,
    FuncDeclNode,
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
    ReturnNode,
    StartNode,
    StatementNode,
    VarDeclNode,
    VariableNode,
)


class SemanticCheckingVisitor(Visitor):
    # Initialize the semantic checker with the already-built global symbol table and traversal state used while descending into classes/functions
    def __init__(self, global_table: SymbolTable | None = None) -> None:
        self.global_table = global_table # Take the global table to look at the structure of the program
        self.current_scope: SymbolTable | None = global_table
        self.current_function: SymbolEntry | None = None
        self.current_class: SymbolTable | None = None
        self.diagnostics: list[Diagnostic] = []

    def visit_ProgNode(self, node: ProgNode):
        self.global_table = node.symtab
        self.current_scope = self.global_table
        self._check_main_function()
        self._check_circular_class_dependencies() # Reject inheritance and/or member-type cycles before normal traversal
        self.visit_children(node)
        return None

    # Validate inherited class names, switch into the class scope, and then check each member declaration and definition with that class context symbol table
    def visit_ClassDeclNode(self, node: ClassDeclNode):
        # Check for undeclared inherited class
        for inherits_node in node.inherits:
            parent_name = inherits_node.id_node.token.lexeme
            if self._lookup_class(parent_name) is None:
                self._diagnostic(
                    "error",
                    "undeclared_class",
                    f"undeclared class '{parent_name}'.",
                    inherits_node,
                )

        class_table = node.symtab
        previous_scope = self.current_scope
        self.current_scope = class_table # Class member declarations are checked inside the class scope
        for member in node.members:
            member.accept(self)
        self.current_scope = previous_scope # Restore the enclosing scope after leaving the class body
        return None

    # Check the declared return type and visit parameter declarations inside the function's scope, but without a function body because this is only a declaration
    def visit_FuncDeclNode(self, node: FuncDeclNode):
        # Check if the type exists
        self._check_type_name(node.return_type_node.token.lexeme, node.return_type_node)
        
        function_table = node.symtab
        previous_scope = self.current_scope
        self.current_scope = function_table # Parameters must be validated in the function-local scope
        node.fparams_node.accept(self) # Go to the FParamsNode of this FuncDeclNode, which goes through and checks the types of each parameter in the function table for their existence
        self.current_scope = previous_scope
        return None

    # Enter a function definition, establish its local/function/class context, then validate parameters and the body before restoring the previous traversal state
    def visit_FuncDefNode(self, node: FuncDefNode):
        self._check_type_name(type_name=node.return_type_node.token.lexeme, node=node.return_type_node)
        function_table = node.symtab
        
        previous_scope = self.current_scope
        previous_function = self.current_function
        previous_class = self.current_class

        self.current_scope = function_table # To see local variables and parameters of function
        self.current_function = node.symtab_entry # Needed for return-statement type checking
        
        if function_table and function_table.parent_scope and function_table.parent_scope.kind == "class":
            self.current_class = function_table.parent_scope # Member function definitions also need their owning class context
        else:
            self.current_class = None # Free functions should not resolve data members implicitly

        node.fparams_node.accept(self)
        node.func_body_node.accept(self)

    # Restore the caller's context after finishing this function body
        self.current_scope = previous_scope
        self.current_function = previous_function
        self.current_class = previous_class
        return None

    # Program blocks represent the main/global executable block, so this method
    # swaps into its scope and function entry for the duration of the block
    def visit_ProgramBlockNode(self, node: ProgramBlockNode):
        previous_scope = self.current_scope
        previous_function = self.current_function
        previous_class = self.current_class
        self.current_scope = node.symtab
        self.current_function = node.symtab_entry
        self.current_class = None
        for child in node.iter_children():
            child.accept(self)
        self.current_scope = previous_scope
        self.current_function = previous_function
        self.current_class = previous_class
        return None

    # Visit each formal parameter so declared parameter types are validated
    def visit_FParamsNode(self, node: FParamsNode):
        for param in node.params:
            param.accept(self)
        return None

    # Validate the type named by a single formal parameter
    def visit_FParamNode(self, node: FParamNode):
        self._check_type_name(node.type_node.token.lexeme, node.type_node)
        return None

    # Report if declared variable is of a valid type (If type exists like a Class). Writes to errors if not valid
    def visit_VarDeclNode(self, node: VarDeclNode):
        self._check_type_name(node.type_node.token.lexeme, node.type_node)
        return None

    # Distinguish between expression statements and assignment statements, then resolve the left/right sides and enforce assignment compatibility
    # Expression statement: A call without '=' character
    # Assignment statement: Something with '=' character
    def visit_StatementNode(self, node: StatementNode):
        children = list(node.iter_children()) # Flatten the statement so chained ids/indexes/calls can be resolved uniformly
        assign_index = None
        for index, child in enumerate(children):
            if isinstance(child, AssignOpNode):
                assign_index = index
                break

        if assign_index is None:
            self._resolve_chain(children, node, expect_callable=True) # A statement with no assignment operator must resolve to a function/method call, else it's not a valid statement and error is reported
            return None

        left_type = self._resolve_chain(children[:assign_index], node, expect_callable=False) # Resolve the l-value chain up to the assignment operator
        right_type = children[assign_index + 1].accept(self) # Infer the assigned expression's type
        if left_type is not None and right_type is not None and not self._is_assignable(left_type, right_type):
            self._diagnostic(
                "error",
                "type_error_assignment_statement",
                f"type error in assignment statement: cannot assign '{right_type}' to '{left_type}'.",
                children[assign_index],
            )
        return None

    # Compare the returned expression type with the enclosing function's declared
    # return type and report a mismatch
    def visit_ReturnNode(self, node: ReturnNode):
        expr = node.first_child
        expr_type = expr.accept(self) if expr is not None else "void" # A missing expression is treated as returning void
        expected_type = self.current_function.type if self.current_function is not None else None # Return checking only makes sense inside a function
        if expr_type is not None and expected_type is not None and not self._is_assignable(expected_type, expr_type):
            self._diagnostic(
                "error",
                "type_error_return_statement",
                f"type error in return statement: expected '{expected_type}' but got '{expr_type}'.",
                node,
            )
        return None

    # Resolve a variable chain such as x, a[i], obj.field, or obj.method().field
    def visit_VariableNode(self, node: VariableNode):
        node.inferred_type = self._resolve_chain(list(node.iter_children()), node, expect_callable=False)
        return node.inferred_type

    # Resolve a standalone identifier node using the same chain machinery used by variables and statements so nested children are handled consistently
    def visit_IdNode(self, node: IdNode):
        node.inferred_type = self._resolve_chain([node, *node.iter_children()], node, expect_callable=False)
        return node.inferred_type

    # Integer literals always infer the built-in integer type
    def visit_IntNumNode(self, node: IntNumNode):
        node.inferred_type = "integer"
        return node.inferred_type

    # Float literals always infer the built-in float type
    def visit_FloatNumNode(self, node: FloatNumNode):
        node.inferred_type = "float"
        return node.inferred_type

    # Visit all actual arguments and store their types for overload matching during function-call resolution
    def visit_AParamsNode(self, node: AParamsNode):
        types = []
        for arg in node.args:
            types.append(arg.accept(self))
        node.argument_types = types # Persist the argument types so other phases/debugging can inspect them
        return types

    # Index nodes do not produce a type directly; they simply ensure their index
    # expressions are visited so later checks have inferred types available
    def visit_IndexNode(self, node: IndexNode):
        for child in node.iter_children():
            child.accept(self)
        return None

    # Unary minus is allowed only on numeric operands
    def visit_MinusNode(self, node: MinusNode):
        return self._visit_unary(node, allowed_types={"integer", "float"})

    # Unary plus is allowed only on numeric operands
    def visit_PlusNode(self, node: PlusNode):
        return self._visit_unary(node, allowed_types={"integer", "float"})

    # Logical not uses the language's integer-as-boolean convention
    def visit_NotNode(self, node: NotNode):
        return self._visit_unary(node, allowed_types={"integer"})

    # Addition/subtraction-style operators either act as integer logical-or or as
    # standard numeric arithmetic depending on the token lexeme
    def visit_AddOpNode(self, node: AddOpNode):
        operator = node.token.lexeme
        if operator == "or":
            return self._visit_binary(node, allowed_types={"integer"}, result_type="integer")
        return self._visit_binary(node, allowed_types={"integer", "float"})

    # Multiplication-style operators either act as integer logical-and or as
    # standard numeric arithmetic depending on the token lexeme
    def visit_MultOpNode(self, node: MultOpNode):
        operator = node.token.lexeme
        if operator == "and":
            return self._visit_binary(node, allowed_types={"integer"}, result_type="integer")
        return self._visit_binary(node, allowed_types={"integer", "float"})

    # Relational operators require numeric operands and always yield an integer
    # truth value in this language
    def visit_RelOpNode(self, node: RelOpNode):
        left = node.first_child.accept(self)
        right = node.first_child.next_sibling.accept(self)
        if left is None or right is None:
            node.inferred_type = None
            return None
        if not self._is_numeric_operand(left) or not self._is_numeric_operand(right) or left != right:
            self._diagnostic(
                "error",
                "type_error_expression",
                f"type error in expression: incompatible operands '{left}' and '{right}'.",
                node,
            )
            node.inferred_type = None
            return None
        node.inferred_type = "integer"
        return node.inferred_type

    # Shared helper for unary operators: infer the operand type, validate it
    # against the allowed set, and propagate the resulting type
    def _visit_unary(self, node, allowed_types: set[str]):
        operand = node.first_child.accept(self) if node.first_child is not None else None
        if operand is None:
            node.inferred_type = None
            return None
        if operand not in allowed_types:
            self._diagnostic(
                "error",
                "type_error_expression",
                f"type error in expression: invalid operand type '{operand}'.",
                node,
            )
            node.inferred_type = None
            return None
        node.inferred_type = operand
        return node.inferred_type

    # Shared helper for binary operators: infer both operand types, require exact
    # type agreement, and cache the result type
    def _visit_binary(self, node, allowed_types: set[str], result_type: str | None = None):
        left = node.first_child.accept(self)
        right = node.first_child.next_sibling.accept(self)
        if left is None or right is None:
            node.inferred_type = None
            return None

        if left != right or left not in allowed_types:
            self._diagnostic(
                "error",
                "type_error_expression",
                f"type error in expression: incompatible operands '{left}' and '{right}'.",
                node,
            )
            node.inferred_type = None
            return None
        node.inferred_type = result_type or left
        return node.inferred_type

    # Left to right resolver for statements
    def _resolve_chain(self, children, owner_node, expect_callable: bool) -> str | None:
        current_type = None # Holds the type of the resolved chain 
        current_entry = None # Type of previously resolved segment to check type compatibility later
        current_class_table = None  # Tracks if the result is a class type
        is_call = False # Remembers if most recent segment was a function call
        index = 0 # To go through the list of children

        # Go one index/child at a time
        while index < len(children):
            # Gets the name of the segment/child and goes to next
            id_node = children[index]
            name = id_node.token.lexeme
            index += 1

            # Collects IndexNodes in case it's an array until there are no longer any IndexNodes
            indices = []
            while index < len(children) and isinstance(children[index], IndexNode):
                indices.append(children[index]) # Collect any array indexing that immediately follows this identifier
                index += 1

            # Check if its being called as a function. If the next node is AParamsNode, it stores the params the function is being called with
            call_node = None
            if index < len(children) and isinstance(children[index], AParamsNode):
                call_node = children[index] # An argument list means this identifier is being called
                index += 1

            # Bunch of conditional statements to determine, after all of this information, what is it that we are calling?
            
            if current_type is None: # First segment in the chain
                if call_node is not None: # We have a function call, so call _resolve_initial_call which tries member functions of current class and then free functions
                    current_entry = self._resolve_initial_call(name, call_node, id_node)
                    is_call = True
                else: # If not a call, then its an id where we search if its local variable or param first, then if its a data member of the class
                    current_entry = self._resolve_identifier(name, id_node)
                    is_call = False
            
            # A previous segment was already resolved, so segment must be accessed relative to that previous resolved type
            else:
                if call_node is not None: # Doing a member function call on the previous result/object
                    current_entry = self._resolve_member_call(current_type, name, call_node, id_node) #
                    is_call = True
                else: # Member variable access
                    current_entry = self._resolve_member_variable(current_type, name, id_node)
                    is_call = False

            # If we couldn't resolve it, stop since the whole chain is invalid.
            if current_entry is None:
                setattr(owner_node, "inferred_type", None)
                return None

            id_node.symtab_entry = current_entry
            id_node.inferred_type = self._entry_type(current_entry) # Cache the composed type on the identifier itself
            current_type = self._entry_type(current_entry)
            current_class_table = self._class_table_for_type(current_type) # Needed to know whether another dot-access is legal

            if not is_call:
                current_type = self._apply_indices(current_entry, current_type, indices, id_node) # Array indexing peels away dimensions from the resolved type
                id_node.inferred_type = current_type

            if call_node is not None:
                call_node.inferred_type = current_type # Store the call result type on the argument-list node too

            if (current_class_table is None or self._dimensions(current_type)) and index < len(children):
                self._diagnostic(
                    "error",
                    "invalid_dot_operator_member_access",
                    f"invalid dot operator member access on non-class type '{current_type}'.",
                    id_node,
                )
                setattr(owner_node, "inferred_type", None)
                return None

        if current_entry is not None and self._dimensions(current_type) and not self._allows_array_reference(owner_node):
            self._diagnostic(
                "error",
                "wrong_array_dimensionality",
                f"wrong array dimensionality for '{current_entry.name}'.",
                children[0],
            )
            setattr(owner_node, "inferred_type", None)
            return None

        if expect_callable and not is_call:
            # Expression statements are only valid when they end in a call
            self._diagnostic(
                "error",
                "undeclared_undefined_free_function",
                f"undeclared or undefined free function '{children[0].token.lexeme}'.",
                children[0],
            )
            setattr(owner_node, "inferred_type", None)
            return None

        setattr(owner_node, "inferred_type", current_type) # Publish the final type on the owning AST node
        if current_entry is not None:
            owner_node.symtab_entry = current_entry
        return current_type

    # Resolve an identifier in the current local/function scope first, then in the current class scope as an implicit data-member access
    def _resolve_identifier(self, name: str, node: IdNode) -> SymbolEntry | None:
        entry = None
        if self.current_scope is not None:
            locals_found = self.current_scope.lookup(name, {"param", "local_var"}) # Parameters and locals shadow class members
            if locals_found:
                entry = locals_found[0]
        if entry is None and self.current_class is not None:
            members = self.current_class.lookup(name, {"data_member"}) # Member functions are not valid as plain variable references here
            if members:
                entry = members[0]
        if entry is None:
            self._diagnostic(
                "error",
                "undeclared_local_variable",
                f"undeclared local variable '{name}'.",
                node,
            )
        return entry

    # Resolve the first callable element in a chain, checking the class' member functions and then checking for free functions in the global scope
    def _resolve_initial_call(self, name: str, call_node: AParamsNode, node: IdNode) -> SymbolEntry | None:
        argument_types = call_node.accept(self)
        if self.current_class is not None:
            member_candidates = self.current_class.lookup(name, {"member_function"})
            if member_candidates:
                return self._select_function_candidate(
                    member_candidates,
                    argument_types,
                    node,
                    missing_code="undeclared_member_function",
                    missing_message=f"undeclared member function '{self.current_class.name}::{name}'.",
                )

        candidates = self.global_table.lookup(name, {"function"}) # Free functions are stored in the global table
        return self._select_function_candidate(
            candidates,
            argument_types,
            node,
            missing_code="undeclared_undefined_free_function",
            missing_message=f"undeclared or undefined free function '{name}'.",
        )

    # Resolve obj.field after the owner expression has already been typed
    def _resolve_member_variable(self, owner_type: str, name: str, node: IdNode) -> SymbolEntry | None:
        if self._dimensions(owner_type):
            self._diagnostic(
                "error",
                "invalid_dot_operator_member_access",
                f"invalid dot operator member access on non-class type '{owner_type}'.",
                node,
            )
            return None
        class_table = self._class_table_for_type(owner_type) # Translate the owner type name into its class symbol table
        if class_table is None:
            self._diagnostic(
                "error",
                "invalid_dot_operator_member_access",
                f"invalid dot operator member access on non-class type '{owner_type}'.",
                node,
            )
            return None
        candidates = class_table.lookup(name, {"data_member"}) # Lookup can also see inherited members because symbol tables link inheritance
        if not candidates:
            self._diagnostic(
                "error",
                "undeclared_member_variable",
                f"undeclared member variable '{class_table.name}.{name}'.",
                node,
            )
            return None
        return candidates[0]

    # Resolve obj.method(args) after the owner expression has already been typed
    def _resolve_member_call(self, owner_type: str, name: str, call_node: AParamsNode, node: IdNode) -> SymbolEntry | None:
        if self._dimensions(owner_type):
            self._diagnostic(
                "error",
                "invalid_dot_operator_member_access",
                f"invalid dot operator member access on non-class type '{owner_type}'.",
                node,
            )
            return None
        class_table = self._class_table_for_type(owner_type)
        if class_table is None:
            self._diagnostic(
                "error",
                "invalid_dot_operator_member_access",
                f"invalid dot operator member access on non-class type '{owner_type}'.",
                node,
            )
            return None
        candidates = class_table.lookup(name, {"member_function"})
        return self._select_function_candidate(
            candidates,
            call_node.accept(self), # Evaluate argument types before overload matching
            node,
            missing_code="undeclared_member_function",
            missing_message=f"undeclared member function '{class_table.name}::{name}'.",
        )

    # Choose the unique function candidate compatible with the argument list, reporting type errors when no candidate matches
    def _select_function_candidate(
        self,
        candidates: list[SymbolEntry],
        argument_types: list[str | None],
        node,
        missing_code: str,
        missing_message: str,
    ) -> SymbolEntry | None:
        if not candidates:
            self._diagnostic("error", missing_code, missing_message, node)
            return None

        expected_count = len(argument_types)
        same_arity = [candidate for candidate in candidates if len(candidate.parameter_types) == expected_count] # Arity mismatch is reported before type mismatch
        if not same_arity:
            self._diagnostic(
                "error",
                "function_call_wrong_number_of_parameters",
                f"function call with wrong number of parameters for '{candidates[0].name}'.",
                node,
            )
            return None

        concrete_argument_types = [arg for arg in argument_types if arg is not None] # If any argument failed to type-check, suppress duplicate call-type errors
        if len(concrete_argument_types) != len(argument_types):
            return None

        for candidate in same_arity:
            if self._argument_lists_match(candidate.parameter_types, concrete_argument_types):
                node.symtab_entry = candidate
                return candidate

        if any(
            self._has_array_dimension_mismatch(candidate.parameter_types, concrete_argument_types)
            for candidate in same_arity
        ):
            self._diagnostic(
                "error",
                "array_parameter_wrong_number_of_dimensions",
                f"array parameter using wrong number of dimensions for '{same_arity[0].name}'.",
                node,
            )
            return None

        self._diagnostic(
            "error",
            "function_call_wrong_type_of_parameters",
            f"function call with wrong type of parameters for '{same_arity[0].name}'.",
            node,
        )
        return None

    # Apply every array index in a chain segment, ensuring each index expression is an integer and that the number of indexes does not exceed the declared rank
    def _apply_indices(self, entry: SymbolEntry, current_type: str, indices: list[IndexNode], node) -> str | None:
        dimensions = list(entry.array_dimensions) # Work from the declared array shape stored on the symbol entry
        if len(indices) > len(dimensions):
            self._diagnostic(
                "error",
                "wrong_array_dimensionality",
                f"wrong array dimensionality for '{entry.name}'.",
                node,
            )
            return None

        for index_node in indices:
            index_type = None
            for child in index_node.iter_children():
                index_type = child.accept(self) # Index nodes usually contain a single expression child
            if index_type != "integer":
                self._diagnostic(
                    "error",
                    "non_integer_index",
                    f"array index for '{entry.name}' must be of type 'integer'.",
                    index_node,
                )
                return None

        remaining_dimensions = dimensions[len(indices):] # Each successful index removes one array dimension from the resulting type
        return self._compose_type(entry.type, remaining_dimensions)

    # Compare two parameter lists using the same exact-type compatibility rules
    # used for assignments and returns
    def _argument_lists_match(self, expected_types: list[str], actual_types: list[str]) -> bool:
        if len(expected_types) != len(actual_types):
            return False
        return all(self._is_assignable(expected, actual) for expected, actual in zip(expected_types, actual_types))

    def _has_array_dimension_mismatch(self, expected_types: list[str], actual_types: list[str]) -> bool:
        if len(expected_types) != len(actual_types):
            return False
        found_dimension_mismatch = False
        for expected, actual in zip(expected_types, actual_types):
            expected_dims = self._dimensions(expected)
            actual_dims = self._dimensions(actual)
            if not expected_dims and not actual_dims:
                if expected != actual:
                    return False
                continue
            if self._base_type(expected) != self._base_type(actual):
                return False
            if len(expected_dims) != len(actual_dims):
                found_dimension_mismatch = True
                continue
            if not self._is_assignable(expected, actual):
                return False
        return found_dimension_mismatch

    # Central type-compatibility rule used for assignments, returns, and argument passing. It supports exact matches and array-shape checks only
    def _is_assignable(self, target_type: str | None, source_type: str | None) -> bool:
        if target_type is None or source_type is None:
            return False
        if target_type == source_type:
            return True

        target_dims = self._dimensions(target_type)
        source_dims = self._dimensions(source_type)
        if target_dims or source_dims:
            if self._base_type(target_type) != self._base_type(source_type): # Array element base types must match exactly
                return False
            if len(target_dims) != len(source_dims):
                return False
            for expected_dim, actual_dim in zip(target_dims, source_dims):
                if expected_dim and actual_dim and expected_dim != actual_dim: # Unspecified dimensions behave like wildcards
                    return False
            return True

        return False

    # Return whether a type can participate in numeric operators. Arrays are wxcluded even if their base type is numeric
    def _is_numeric_operand(self, type_name: str | None) -> bool:
        return self._base_type(type_name) in {"integer", "float"} and not self._dimensions(type_name)

    # Validate that a referenced type name is either built in or a previously declared class visible from the global symbol table
    def _check_type_name(self, type_name: str, node) -> None:
        if type_name in {"integer", "float", "void"}:
            return
        if self._lookup_class(type_name) is None:
            self._diagnostic("error", "undeclared_class", f"undeclared class '{type_name}'.", node)

    # The grammar should produce exactly one program block that becomes the sole main function entry. Check the global table anyway so malformed ASTs or future grammar changes do not silently violate the semantic contract
    def _check_main_function(self) -> None:
        if self.global_table is None:
            return
        main_entries = self.global_table.lookup("main", {"function"})
        if len(main_entries) != 1:
            node = self.global_table.entries[0].node if self.global_table.entries else None
            if node is not None:
                self._diagnostic(
                    "error",
                    "invalid_main_function_count",
                    f"program must contain exactly one main function, found {len(main_entries)}.",
                    node,
                )

    # Lookup a class entry by name in the global symbol table
    def _lookup_class(self, class_name: str) -> SymbolEntry | None:
        if self.global_table is None:
            return None
        classes = self.global_table.lookup(class_name, {"class"})
        if not classes:
            return None
        return classes[0]

    # Convert a type name into the symbol table for that class so member access can search its fields and methods
    def _class_table_for_type(self, type_name: str) -> SymbolTable | None:
        class_entry = self._lookup_class(self._base_type(type_name))
        if class_entry is None:
            return None
        return class_entry.inner_scope_table

    # Rebuild the full source-language type string from a symbol-table entry
    def _entry_type(self, entry: SymbolEntry) -> str:
        return self._compose_type(entry.type, entry.array_dimensions)

    # Compose a type like `integer[][]` or `MyClass[10]` from its base type plus stored array dimensions
    def _compose_type(self, base_type: str | None, dimensions: list[int | None]) -> str | None:
        if base_type is None:
            return None
        suffix = []
        for dimension in dimensions:
            if dimension is None:
                suffix.append("[]")
            else:
                suffix.append(f"[{dimension}]")
        return f"{base_type}{''.join(suffix)}"

    # Strip any array suffix from a type string and return just the base type
    def _base_type(self, type_name: str | None) -> str | None:
        if type_name is None:
            return None
        return type_name.split("[", 1)[0]

    # Parse the bracketed dimensions from a type string so array compatibility and indexing can reason about rank and declared sizes
    def _dimensions(self, type_name: str | None) -> list[str]:
        if type_name is None:
            return []
        dimensions = []
        index = type_name.find("[")
        while index != -1:
            end = type_name.find("]", index)
            dimensions.append(type_name[index + 1:end]) # Empty string means an unspecified dimension like []
            index = type_name.find("[", end)
        return dimensions

    # Array values may only remain array-typed when they are being passed as actual arguments; otherwise references must index all declared dimensions
    def _allows_array_reference(self, owner_node) -> bool:
        return isinstance(getattr(owner_node, "parent", None), AParamsNode)

    # Build a dependency graph between classes based on inheritance and class-typed data members, then run DFS to detect cycles and report each class involved
    def _check_circular_class_dependencies(self) -> None:
        graph: dict[str, set[str]] = {}
        # For each class entry, get its dependencies
        for class_entry in self.global_table.lookup(kinds={"class"}):
            dependencies = set()
            class_node = class_entry.node
            
            # Getting dependencies through inherited classes
            for inherits_node in class_node.inherits:
                dependencies.add(inherits_node.id_node.token.lexeme) # Inheriting from a class creates a dependency edge
            
            # Get the members of this same class to check for dependencies on class-typed data members
            class_table = class_entry.inner_scope_table
            for member in class_table.lookup(kinds={"data_member"}):
                member_type = member.type
                if member_type not in {"integer", "float", "void"} and member_type != class_entry.name:
                    dependencies.add(member_type) # Class-typed fields also create dependencies
                elif member_type == class_entry.name:
                    dependencies.add(member_type) # A class containing itself directly is also treated as circular
            graph[class_entry.name] = dependencies

        # Graph is now created
        
        visiting: set[str] = set() # Classes currently on the active DFS recursion path
        explored: set[str] = set() # Classes whose dependency graphs have already been checked
        reported: set[str] = set() # Prevent duplicate diagnostics when multiple DFS paths hit the same cycle
        stack: list[str] = [] # Tracks the current DFS path so the exact cycle can be extracted

        def dfs(class_name: str) -> None:
            visiting.add(class_name) # Mark this class as currently processing before exploring its dependencies
            stack.append(class_name)
            for dependency in graph[class_name]:
                if dependency not in graph:
                    continue # Ignore dependencies that are not known classes like inheriting a class that doesn't exist, that specific check is reported elsewhere like in visit_ClassDeclNode
                
                if dependency in visiting: # Reaching a class currently in our recursion means there's a cycle
                    cycle = stack[stack.index(dependency):] # Slice the current recursion stack down to the cycle
                    for cycle_name in cycle:
                        if cycle_name in reported:
                            continue
                        class_entry = self._lookup_class(cycle_name)
                        self._diagnostic(
                            "error",
                            "circular_class_dependency",
                            f"circular class dependency involving '{cycle_name}'.",
                            class_entry.node,
                        )
                        reported.add(cycle_name)
                    continue
                
                elif dependency not in explored: # The class has not been seen in the current recursion and also has not been explored, so we must explore this one for circular dependencies
                    dfs(dependency)
                
            stack.pop() # Remove this class once all dependencies have been explored
            visiting.remove(class_name)
            explored.add(class_name)

        # Loop through the classes in the graph
        for class_name in graph:
            if class_name not in explored: # If this class wasn't explored yet, start a DFS from it because we might have multiply disconnected graphs
                dfs(class_name)

    # Record a semantic diagnostic at the source line owned by the provided AST node
    def _diagnostic(self, severity: str, code: str, message: str, node) -> None:
        self.diagnostics.append(Diagnostic(severity=severity, code=code, message=message, line=node.token.line))
