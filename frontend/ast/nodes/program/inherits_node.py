from dataclasses import dataclass

from frontend.ast.nodes.base import Node
from frontend.ast.nodes.references.id_node import IdNode


@dataclass
class InheritsNode(Node):
    id_node: IdNode | None = None
