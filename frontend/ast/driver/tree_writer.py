from frontend.ast.nodes.base import Node


def _node_label(node: Node) -> str:
    class_name = node.__class__.__name__
    label = class_name[:-4]
    return label

def ast_to_text(root: Node) -> str:
    lines: list[str] = []

    def walk(node: Node, depth: int) -> None:
        lines.append(f"{'| ' * depth}{_node_label(node)}")
        for child in node.iter_children():
            walk(child, depth + 1)

    walk(root, 0)
    return "\n".join(lines)
