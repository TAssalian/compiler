from frontend.ast.nodes import (
    AParamsNode,
    AddOpNode,
    ArithExprNode,
    ArraySizeNode,
    AssignOpNode,
    ClassDeclNode,
    ClassListNode,
    ExprNode,
    FParamNode,
    FParamsNode,
    FloatNumNode,
    FuncBodyNode,
    FuncDeclNode,
    FuncDefNode,
    FuncDefListNode,
    InheritsNode,
    IdNode,
    IfNode,
    IntNumNode,
    MinusNode,
    MultOpNode,
    NotNode,
    PlusNode,
    ProgramBlockNode,
    PrivateNode,
    ProgNode,
    PublicNode,
    ReadNode,
    RelExprNode,
    RelOpNode,
    ReturnNode,
    StartNode,
    StatBlockNode,
    StatementNode,
    TermNode,
    TypeNode,
    VarDeclNode,
    VariableNode,
    WhileNode,
    WriteNode,
)


semantic_stack = []
EPSILON = object()

def _pop_until_epsilon():
    nodes = []
    while semantic_stack and semantic_stack[-1] is not EPSILON:
        nodes.append(semantic_stack.pop())
    if semantic_stack and semantic_stack[-1] is EPSILON:
        semantic_stack.pop()
    nodes.reverse()
    return nodes

def _attach_children(parent, children):
    for child in children:
        parent.add_child(child)


def make_type_node(token):
    semantic_stack.append(TypeNode(token))

def make_id_node(token):
    semantic_stack.append(IdNode(token))

def make_intnum_node(token):
    semantic_stack.append(IntNumNode(token))

def make_floatnum_node(token):
    semantic_stack.append(FloatNumNode(token))

def push_epsilon(_token):
    semantic_stack.append(EPSILON)
    
def make_public_node(token):
    semantic_stack.append(PublicNode(token))
    
def make_private_node(token):
    semantic_stack.append(PrivateNode(token))

def make_minus_node(token):
    semantic_stack.append(MinusNode(token))

def make_plus_node(token):
    semantic_stack.append(PlusNode(token))

def make_not_node(token):
    semantic_stack.append(NotNode(token))

def make_addop_node(token):
    semantic_stack.append(AddOpNode(token))

def make_multop_node(token):
    semantic_stack.append(MultOpNode(token))

def make_relop_node(token):
    semantic_stack.append(RelOpNode(token))

def make_assignop_node(token):
    semantic_stack.append(AssignOpNode(token))

def make_arraysize_subtree(_token):
    dimensions = _pop_until_epsilon()
    dim_list = ArraySizeNode(token=_token, dimensions=dimensions)
    _attach_children(dim_list, dimensions)
    semantic_stack.append(dim_list)


def make_vardecl_subtree(_token):
    array_size_node = semantic_stack.pop()
    id_node = semantic_stack.pop()
    type_node = semantic_stack.pop()
    var_decl = VarDeclNode(
        token=_token,
        type_node=type_node,
        id_node=id_node,
        array_size_node=array_size_node,
    )
    var_decl.add_child(type_node)
    var_decl.add_child(id_node)
    var_decl.add_child(array_size_node)
    semantic_stack.append(var_decl)

def make_fparam_subtree(_token):
    array_size_node = semantic_stack.pop()
    id_node = semantic_stack.pop()
    type_node = semantic_stack.pop()
    fparam = FParamNode(
        token=_token,
        type_node=type_node,
        id_node=id_node,
        array_size_node=array_size_node,
    )
    fparam.add_child(type_node)
    fparam.add_child(id_node)
    fparam.add_child(array_size_node)
    semantic_stack.append(fparam)

def make_fparams_subtree(_token):
    params = _pop_until_epsilon()
    fparams = FParamsNode(token=_token, params=params)
    for param in params:
        fparams.add_child(param)
    semantic_stack.append(fparams)

def make_empty_fparams_node(token):
    semantic_stack.append(FParamsNode(token=token, params=[]))

def make_void_type_node(token):
    semantic_stack.append(TypeNode(token))

def make_member_vardecl_subtree(_token):
    array_size_node = semantic_stack.pop()
    id_node = semantic_stack.pop()
    type_id_node = semantic_stack.pop()
    type_node = TypeNode(type_id_node.token)

    var_decl = VarDeclNode(
        token=_token,
        type_node=type_node,
        id_node=id_node,
        array_size_node=array_size_node,
    )
    var_decl.add_child(type_node)
    var_decl.add_child(id_node)
    var_decl.add_child(array_size_node)
    semantic_stack.append(var_decl)


def make_member_funcdecl_subtree(_token):
    return_type = semantic_stack.pop()
    fparams_node = semantic_stack.pop()
    id_node = semantic_stack.pop()

    func_decl = FuncDeclNode(
        token=_token,
        id_node=id_node,
        fparams_node=fparams_node,
        return_type_node=return_type,
    )
    func_decl.add_child(id_node)
    func_decl.add_child(fparams_node)
    func_decl.add_child(return_type)
    semantic_stack.append(func_decl)

def make_aparams_subtree(_token):
    args = _pop_until_epsilon()
    aparams = AParamsNode(token=_token, args=args)
    _attach_children(aparams, args)
    semantic_stack.append(aparams)

def make_empty_aparams_node(token):
    semantic_stack.append(AParamsNode(token=token, args=[]))

def make_term_subtree(_token):
    children = _pop_until_epsilon()
    node = TermNode(token=_token)
    _attach_children(node, children)
    semantic_stack.append(node)

def make_arithexpr_subtree(_token):
    children = _pop_until_epsilon()
    node = ArithExprNode(token=_token)
    _attach_children(node, children)
    semantic_stack.append(node)

def make_expr_subtree(_token):
    children = _pop_until_epsilon()
    node = ExprNode(token=_token)
    _attach_children(node, children)
    semantic_stack.append(node)

def make_relexpr_subtree(_token):
    node = RelExprNode(token=_token)
    right = semantic_stack.pop()
    relop = semantic_stack.pop()
    left = semantic_stack.pop()
    semantic_stack.pop()
    node.add_child(left)
    node.add_child(relop)
    node.add_child(right)
    semantic_stack.append(node)

def make_variable_subtree(_token):
    children = _pop_until_epsilon()
    node = VariableNode(token=_token)
    _attach_children(node, children)
    semantic_stack.append(node)

def make_statement_subtree(_token):
    children = _pop_until_epsilon()
    node = StatementNode(token=_token)
    _attach_children(node, children)
    semantic_stack.append(node)

def make_return_subtree(_token):
    node = ReturnNode(token=_token)
    expr = semantic_stack.pop()
    semantic_stack.pop()
    node.add_child(expr)
    semantic_stack.append(node)

def make_write_subtree(_token):
    node = WriteNode(token=_token)
    expr = semantic_stack.pop()
    semantic_stack.pop()
    node.add_child(expr)
    semantic_stack.append(node)

def make_read_subtree(_token):
    node = ReadNode(token=_token)
    variable = semantic_stack.pop()
    semantic_stack.pop()
    node.add_child(variable)
    semantic_stack.append(node)

def make_while_subtree(_token):
    children = _pop_until_epsilon()
    node = WhileNode(token=_token)
    _attach_children(node, children)
    semantic_stack.append(node)

def make_if_subtree(_token):
    children = _pop_until_epsilon()
    node = IfNode(token=_token)
    _attach_children(node, children)
    semantic_stack.append(node)

def make_statblock_subtree(_token):
    children = _pop_until_epsilon()
    node = StatBlockNode(token=_token)
    _attach_children(node, children)
    semantic_stack.append(node)

def make_funcbody_subtree(_token):
    children = _pop_until_epsilon()
    node = FuncBodyNode(token=_token)
    _attach_children(node, children)
    semantic_stack.append(node)

def make_funcdef_subtree(_token):
    children = _pop_until_epsilon()
    func_body = children.pop()
    return_type = children.pop()
    fparams_node = children.pop()

    node = FuncDefNode(token=_token)
    for child in children:
        node.add_child(child)
    node.add_child(fparams_node)
    node.add_child(return_type)
    node.add_child(func_body)
    semantic_stack.append(node)

def make_classdecl_subtree(_token):
    children = _pop_until_epsilon()
    node = ClassDeclNode(token=_token)
    _attach_children(node, children)
    semantic_stack.append(node)

def make_inherits_subtree(_token):
    id_node = semantic_stack.pop()
    node = InheritsNode(token=_token, id_node=id_node)
    node.add_child(id_node)
    semantic_stack.append(node)

def make_prog_subtree(_token):
    children = _pop_until_epsilon()
    node = ProgNode(token=_token)
    class_list = ClassListNode(token=_token)
    funcdef_list = FuncDefListNode(token=_token)
    program_block = ProgramBlockNode(token=_token)
    main_body = children.pop()

    for child in children:
        if isinstance(child, ClassDeclNode):
            class_list.add_child(child)
        else:
            funcdef_list.add_child(child)

    for child in main_body.iter_children():
        program_block.add_child(child)

    node.add_child(class_list)
    node.add_child(funcdef_list)
    node.add_child(program_block)
    semantic_stack.append(node)

def make_start_subtree(_token):
    child = semantic_stack.pop()
    node = StartNode(token=_token)
    node.add_child(child)
    semantic_stack.append(node)

semantic_actions = {
    "#make_type_node": make_type_node,
    "#make_id_node": make_id_node,
    "#make_intnum_node": make_intnum_node,
    "#make_floatnum_node": make_floatnum_node,
    "#push_epsilon": push_epsilon,
    "#make_arraysize_subtree": make_arraysize_subtree,
    "#make_vardecl_subtree": make_vardecl_subtree,
    "#make_fparam_subtree": make_fparam_subtree,
    "#make_fparams_subtree": make_fparams_subtree,
    "#make_empty_fparams_node": make_empty_fparams_node,
    "#make_void_type_node": make_void_type_node,
    "#make_public_node": make_public_node,
    "#make_private_node": make_private_node,
    "#make_minus_node": make_minus_node,
    "#make_plus_node": make_plus_node,
    "#make_not_node": make_not_node,
    "#make_addop_node": make_addop_node,
    "#make_multop_node": make_multop_node,
    "#make_relop_node": make_relop_node,
    "#make_assignop_node": make_assignop_node,
    "#make_member_vardecl_subtree": make_member_vardecl_subtree,
    "#make_member_funcdecl_subtree": make_member_funcdecl_subtree,
    "#make_aparams_subtree": make_aparams_subtree,
    "#make_empty_aparams_node": make_empty_aparams_node,
    "#make_term_subtree": make_term_subtree,
    "#make_arithexpr_subtree": make_arithexpr_subtree,
    "#make_expr_subtree": make_expr_subtree,
    "#make_relexpr_subtree": make_relexpr_subtree,
    "#make_variable_subtree": make_variable_subtree,
    "#make_statement_subtree": make_statement_subtree,
    "#make_return_subtree": make_return_subtree,
    "#make_write_subtree": make_write_subtree,
    "#make_read_subtree": make_read_subtree,
    "#make_while_subtree": make_while_subtree,
    "#make_if_subtree": make_if_subtree,
    "#make_statblock_subtree": make_statblock_subtree,
    "#make_funcbody_subtree": make_funcbody_subtree,
    "#make_funcdef_subtree": make_funcdef_subtree,
    "#make_classdecl_subtree": make_classdecl_subtree,
    "#make_inherits_subtree": make_inherits_subtree,
    "#make_prog_subtree": make_prog_subtree,
    "#make_start_subtree": make_start_subtree
}
