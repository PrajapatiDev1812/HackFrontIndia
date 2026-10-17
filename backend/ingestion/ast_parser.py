# pyrefly: ignore[missing-import]
import tree_sitter_python as tspython
# pyrefly: ignore[missing-import]
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def parse_python_diff(file_path: str, content: str) -> list[str]:
    try:
        tree = parser.parse(bytes(content, "utf8"))
        symbols = []
        def traverse(node):
            if node.type in ['function_definition', 'class_definition']:
                for child in node.children:
                    if child.type == 'identifier':
                        symbols.append(child.text.decode('utf8'))
            for child in node.children:
                traverse(child)
        traverse(tree.root_node)
        return list(set(symbols))
    except Exception:
        return []
