from __future__ import annotations

from frontend.ast.nodes import (
    AParamsNode,
    AddOpNode,
    AssignOpNode,
    FloatNumNode,
    IndexNode,
    IntNumNode,
    MinusNode,
    MultOpNode,
    NotNode,
    PlusNode,
    RelOpNode,
    VariableNode,
)
from frontend.semantics.visitors.visitor import Visitor

# Nodes whose memory has already been calculated earlier
_VALUE_NODES = (IntNumNode, FloatNumNode, AddOpNode, MultOpNode, RelOpNode, PlusNode, MinusNode, NotNode)


class CodeGenVisitor(Visitor):

    def __init__(self):
        self.code_stream = []
        self.data_stream = []
        self.label_counter = 0
        self.global_table = None
        self.current_scope = None

    def emit(self, line):
        self.code_stream.append(f"          {line}")

    def label(self, lbl):
        self.code_stream.append(f"{lbl:<10}")

    def new_label(self, prefix):
        lbl = f"{prefix}_{self.label_counter}"
        self.label_counter += 1
        return lbl

    def slot(self, entry):
        return f"{entry.offset}(r14)"

    def output(self):
        return "\n".join([*self.code_stream, *self.data_stream]) + "\n"

    def lookup(self, name, scope=None):
        return (scope or self.current_scope).lookup(name)[0]

    def function_label(self, entry):
        parts = [entry.name, *entry.parameter_types]
        if entry.owner_class:
            parts.insert(0, entry.owner_class)
        return "_".join(p.replace("::", "_").replace("[", "_").replace("]", "").replace(",", "_") for p in parts)

    def type_size(self, type_name):
        if not type_name or type_name == "void":
            return 0
        base = type_name.split("[", 1)[0]
        size = 4 if base == "integer" else 8 if base == "float" else self.global_table.lookup(base, {"class"})[0].inner_scope_table.size
        for chunk in type_name.split("[")[1:]:
            dim = chunk.split("]", 1)[0]
            if dim:
                size *= int(dim)
        return size

    def entry_size(self, entry):
        t = entry.type + "".join("[]" if d is None else f"[{d}]" for d in entry.array_dimensions)
        return self.type_size(t)

    def load_value(self, node, reg, addr_reg="r12"):
        if isinstance(node, _VALUE_NODES):
            self.emit(f"lw {reg},{self.slot(node.symtab_entry)}")
        else:
            self.find_address(node, addr_reg)
            self.emit(f"lw {reg},0({addr_reg})")

    def source_address(self, node, reg):
        # If its memory we've already allocated that exists cleanly, get its memory slot and return the address of it
        if isinstance(node, _VALUE_NODES):
            self.emit(f"addi {reg},r14,{node.symtab_entry.offset}")
        # If it doesn't have a temp slot so its a variable, dot-chain, or function call
        else:
            self.find_address(node, reg)

    def find_address(self, node, reg):
        # VariableNode is a wrapper where its children are IndexNode and AParamsNodes, so pass children
        if isinstance(node, VariableNode):
            self._address_chain(list(node.iter_children()), reg)
        # Node itself is an IdNode so its part of a larger Statement, we add that + its children to the list to resolve a potential dot access.
        else:
            self._address_chain([node, *node.iter_children()], reg)

    def address_entry(self, entry, reg):
        if entry.kind == "data_member":
            self.emit(f"lw r11,{self.current_scope.size}(r14)")
            self.emit(f"addi {reg},r11,{entry.offset}")
        elif entry.kind == "param" and entry.array_dimensions:
            self.emit(f"lw {reg},{self.slot(entry)}")
        else:
            self.emit(f"addi {reg},r14,{entry.offset}")

    # Goes through a dot-separated chain like 'a.b[2].c(x)' to compute the final memory address to store in 'reg'
    # 'children' is a flat list of nodes: [IdNode, IndexNode?, AParamsNode?, IdNode, IndexNode?, ...]
    # Example: 'a.b[2].c(x)' is children = [a_id, b_id, IndexNode(2), c_id, AParamsNode(x)]
    # For a simple variable like 'x', there's only one iteration: address_entry writes 'addi reg, r14, offset'
    def _address_chain(self, children, reg):
        is_first = True
        i = 0

        while i < len(children):
            # Parse one segment: grab the identifier node
            id_node = children[i]
            i += 1 

            # Collect any array index nodes following this identifier
            indices = []
            while i < len(children) and isinstance(children[i], IndexNode):
                indices.append(children[i])
                i += 1
    
            # Check if a function call follows
            call_node = None
            if i < len(children) and isinstance(children[i], AParamsNode):
                call_node = children[i]
                i += 1

            entry = id_node.symtab_entry
            
            if is_first and call_node is not None:
                self._call(entry, call_node, None)
                self.emit(f"addi {reg},r14,{self.lookup('__ret_val', entry.inner_scope_table).offset - entry.inner_scope_table.size}")

            elif is_first:
                # First identifier in the chain: resolve as data member, array param, or local var
                self.address_entry(entry, reg)
            
            elif call_node is not None:
                # Dot-chain function call like a.f(): reg already holds address of 'a'
                self._call(entry, call_node, reg)
                # Point reg to where the return value landed in our frame
                self.emit(f"addi {reg},r14,{self.lookup('__ret_val', entry.inner_scope_table).offset - entry.inner_scope_table.size}")

            else:
                # Dot-chain data access like a.b: offset into the class member
                self.emit(f"addi {reg},{reg},{entry.offset}")

            if indices:
                self._apply_indices(reg, entry, indices)

            is_first = False

    # 2.2 Pass parameters as local values to the function's code block.
    # 2.4 Call member functions that can use their object's data members.
    def _call(self, entry, call_node, receiver_reg):
        callee = entry.inner_scope_table
        for arg, param in zip(call_node.args, callee.lookup(kinds={"param"})):
            arg.accept(self)
            dst = param.offset - callee.size
            if param.array_dimensions:
                self.find_address(arg, "r1")
                self.emit(f"sw {dst}(r14),r1")
            else:
                self.source_address(arg, "r12")
                self.emit(f"addi r2,r14,{dst}")
                self._copy_block("r12", "r2", self.entry_size(param))
        if receiver_reg is not None:
            self.emit(f"sw 0(r14),{receiver_reg}")
        self.emit(f"subi r14,r14,{callee.size}")
        self.emit(f"jl r15,{self.function_label(entry)}")
        self.emit(f"addi r14,r14,{callee.size}")

    # 4.1 Arrays of basic types
    # 4.2 Arrays of objects
    # 5.2 Expression involving an array factor whose indexes are expressions
    def _apply_indices(self, reg, entry, indices):
        dims = list(entry.array_dimensions)
        remaining_type = entry.type + "".join("[]" if d is None else f"[{d}]" for d in dims[len(indices):])
        elem_size = self.type_size(remaining_type)
        for i, idx in enumerate(indices):
            expr = next(idx.iter_children())
            idx_reg = "r9" if reg != "r9" else "r11"
            stride_reg = "r10" if reg != "r10" and idx_reg != "r10" else "r11"
            addr_reg = "r8" if reg != "r8" else "r11"
            self.load_value(expr, idx_reg, addr_reg)
            stride = elem_size
            for d in dims[i + 1:]:
                if d is not None:
                    stride *= d
            self.emit(f"muli {stride_reg},{idx_reg},{stride}")
            self.emit(f"add {reg},{reg},{stride_reg}")

    def _copy_block(self, src, dst, size):
        if size <= 4:
            self.emit(f"lw r3,0({src})")
            self.emit(f"sw 0({dst}),r3")
            return
        loop, done = self.new_label("copy"), self.new_label("copy_end")
        self.emit("addi r4,r0,0")
        self.label(loop)
        self.emit(f"ceqi r5,r4,{size}")
        self.emit(f"bnz r5,{done}")
        self.emit(f"add r6,{src},r4")
        self.emit("lw r7,0(r6)")
        self.emit(f"add r8,{dst},r4")
        self.emit("sw 0(r8),r7")
        self.emit("addi r4,r4,4")
        self.emit(f"j {loop}")
        self.label(done)


    def visit_ProgNode(self, node):
        self.global_table = node.symtab
        self.current_scope = node.symtab
        class_list, func_defs, main_block = node.iter_children()
        main_label = self.new_label("main")
        self.emit("entry")
        # r14: stack frame pointer, r0: always 0, topaddr: max memory address
        self.emit("addi r14,r0,topaddr")
        self.emit(f"subi r14,r14,{main_block.symtab.size}")
        self.emit(f"j {main_label}")
        class_list.accept(self)
        func_defs.accept(self)
        self.label(main_label)
        main_block.accept(self)
        self.emit("hlt")
        # buffer space used for console output
        self.data_stream.append("buf       res 20")

    def visit_ProgramBlockNode(self, node):
        prev = self.current_scope
        self.current_scope = node.symtab
        self.visit_children(node)
        self.current_scope = prev

    # Skip because we dont care about declared vars, their memory is already allocated from prev. visitor
    def visit_VarDeclNode(self, node):
        pass

    # 2.1 Branch to a function's code block, execute it, and branch back
    # jl (ex: jl r15, f1): Holds return address of current instruction we jumped to f1 from
    # sw (ex: sw -4(r14), r15): Copies a value from register into memory
    # lw (ex: lw r15, -4(r14): Copies a value from memory into a register
    # jr (ex: jr r15): Jump back to saved return address inside r15
    def visit_FuncDefNode(self, node):
        prev = self.current_scope
        self.current_scope = node.symtab
        self.label(self.function_label(node.symtab_entry))
        self.emit(f"sw {self.slot(self.lookup('__ret_addr'))},r15")
        node.func_body_node.accept(self)
        self.emit(f"lw r15,{self.slot(self.lookup('__ret_addr'))}")
        self.emit("jr r15")
        self.current_scope = prev
            

    # 2.3 Return a value back to the calling function.
    def visit_ReturnNode(self, node):
        expr = node.first_child
        expr.accept(self)
        self.source_address(expr, "r12")
        ret_val = self.lookup("__ret_val")
        self.emit(f"addi r2,r14,{ret_val.offset}")
        self._copy_block("r12", "r2", self.type_size(expr.inferred_type))
        self.emit(f"lw r15,{self.slot(self.lookup('__ret_addr'))}")
        self.emit("jr r15")

    # 3.1 Assignment statement. (Also does func call statements)
    def visit_StatementNode(self, node):
        children = list(node.iter_children())
        assign_index = next((i for i, c in enumerate(children) if isinstance(c, AssignOpNode)), None) # Get index of AssignOpNode
        
        # Doesn't exist, so we have a function call
        if assign_index is None:
            for c in children:
                c.accept(self)
            self._address_chain(children, "r12")
            return
        left = children[:assign_index] # The left side becomes the target
        right = children[assign_index + 1] # The right side becomes the value
        for c in left:
            c.accept(self)
        right.accept(self)
        self.source_address(right, "r13") # Get where the RHS lives in memory and store it in r13
        self._address_chain(left, "r1") # Get the destination address where we want to write to and store it in r1.
        self._copy_block("r13", "r1", self.type_size(node.inferred_type)) 

    # 3.2 Conditional statement.
    def visit_IfNode(self, node):
        condition, then_block, *else_block = node.iter_children()
        else_lbl = self.new_label("if_else")
        end_lbl = self.new_label("if_end")
        condition.accept(self)
        self.load_value(condition, "r1")
        self.emit(f"bz r1,{else_lbl}")
        then_block.accept(self)
        self.emit(f"j {end_lbl}")
        self.label(else_lbl)
        if else_block:
            else_block[0].accept(self)
        self.label(end_lbl)

    # 3.3 Loop statement.
    # bz: jump to end_lbl if the value is 0, which skips the body and exits loop
    # j: Unconditional jump
    def visit_WhileNode(self, node):
        condition, body = node.iter_children()
        start_lbl = self.new_label("while_start")
        end_lbl = self.new_label("while_end")
        self.label(start_lbl) # Appends the label
        condition.accept(self) # Generate code making up the condition to get T/F value
        self.load_value(condition, "r1") 
        self.emit(f"bz r1,{end_lbl}") # Choose whether to jump to end and exit loop or not based on value in r1
        body.accept(self) # Condition is true so generate code
        self.emit(f"j {start_lbl}") # Jump back to start_lbl for next iteration
        self.label(end_lbl) # Continue with whats after this loop

    # 3.4 Input/output statements.
    # subi: "Subtract immediate": Move r14 down by the size of the current function's frame so library functions get their own space below the current frame.
    # intstr: Convert integer to string
    # putstr: Print a string to the console
    def visit_WriteNode(self, node):
        expr = node.first_child
        expr.accept(self)
        self.load_value(expr, "r1")
        self.emit(f"subi r14,r14,{self.current_scope.size}") # Example: r14 = 1000, scope size = 48, we start new frame at 952
        self.emit("sw -8(r14),r1") # Store int value in r1 at offset -8 in new r14. This is the first argument of intstr which is the num to convert
        self.emit("addi r1,r0,buf") # Store address of buf inside r1, giving
        self.emit("sw -12(r14),r1") # Store buffer address at offset -12, the second argument to instr which is where to write the string
        self.emit("jl r15,intstr") # Call intstr which reads int at -8(r14) and buffer address from -12(r14), converts to string and write it into buf, and stores string address in r13
        self.emit("sw -8(r14),r13") # Store string address into -8(r14) where putstr expects it
        self.emit("jl r15,putstr") # Call putstr, which reads the string pointer from -8(r14) and prints string to console
        self.emit("addi r1,r0,10")
        self.emit("putc r1")
        self.emit(f"addi r14,r14,{self.current_scope.size}") # Restore r14 back to where it was

    # 5.1 Computing the value of an entire complex expression.
    def visit_IntNumNode(self, node):
        self.emit(f"addi r1,r0,{node.token.lexeme}")
        self.emit(f"sw {self.slot(node.symtab_entry)},r1")

    def visit_FloatNumNode(self, node):
        self.emit("addi r1,r0,0")
        self.emit(f"sw {self.slot(node.symtab_entry)},r1")
        self.emit(f"sw {node.symtab_entry.offset + 4}(r14),r1")

    def visit_PlusNode(self, node):
        self.visit_children(node)
        self.load_value(node.first_child, "r1")
        self.emit(f"sw {self.slot(node.symtab_entry)},r1")

    def visit_MinusNode(self, node):
        self.visit_children(node)
        self.load_value(node.first_child, "r1")
        self.emit("sub r1,r0,r1")
        self.emit(f"sw {self.slot(node.symtab_entry)},r1")

    def visit_NotNode(self, node):
        self.visit_children(node)
        self.load_value(node.first_child, "r1")
        self.emit("ceq r1,r1,r0")
        self.emit(f"sw {self.slot(node.symtab_entry)},r1")

    def visit_AddOpNode(self, node):
        self._binary(node, {"+": "add", "-": "sub", "or": "or"})

    def visit_MultOpNode(self, node):
        self._binary(node, {"*": "mul", "/": "div", "and": "and"})

    def visit_RelOpNode(self, node):
        self._binary(node, {"==": "ceq", "<>": "cne", "<": "clt", "<=": "cle", ">": "cgt", ">=": "cge"})

    def _binary(self, node, ops):
        self.visit_children(node)
        left = node.first_child
        right = left.next_sibling
        self.load_value(left, "r1")
        self.load_value(right, "r2")
        self.emit(f"{ops[node.token.lexeme]} r3,r1,r2")
        self.emit(f"sw {self.slot(node.symtab_entry)},r3")
