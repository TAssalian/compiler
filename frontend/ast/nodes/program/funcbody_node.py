from dataclasses import dataclass, field

from frontend.ast.nodes.base import Node
from frontend.ast.nodes.declarations.vardecl_node import VarDeclNode


@dataclass
class FuncBodyNode(Node):
    local_vars: list[VarDeclNode] = field(default_factory=list)
