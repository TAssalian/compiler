from dataclasses import dataclass, field

from frontend.ast.nodes.base import Node
from frontend.ast.nodes.declarations.funcdecl_node import FuncDeclNode
from frontend.ast.nodes.declarations.vardecl_node import VarDeclNode
from frontend.ast.nodes.modifiers.private_node import PrivateNode
from frontend.ast.nodes.modifiers.public_node import PublicNode
from frontend.ast.nodes.program.inherits_node import InheritsNode
from frontend.ast.nodes.references.id_node import IdNode


@dataclass
class ClassDeclNode(Node):
    id_node: IdNode | None = None
    inherits: list[InheritsNode] = field(default_factory=list)
    members: list[VarDeclNode | FuncDeclNode] = field(default_factory=list)
    body_items: list[InheritsNode | PublicNode | PrivateNode | VarDeclNode | FuncDeclNode] = field(default_factory=list)
