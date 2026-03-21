from dataclasses import dataclass

from frontend.ast.nodes.base import Node
from frontend.ast.nodes.declarations.fparams_node import FParamsNode
from frontend.ast.nodes.program.funcbody_node import FuncBodyNode
from frontend.ast.nodes.references.id_node import IdNode
from frontend.ast.nodes.type.type_node import TypeNode


@dataclass
class FuncDefNode(Node):
    owner_id_node: IdNode | None = None
    id_node: IdNode | None = None
    fparams_node: FParamsNode | None = None
    return_type_node: TypeNode | None = None
    func_body_node: FuncBodyNode | None = None
