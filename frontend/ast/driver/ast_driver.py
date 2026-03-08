import sys
from pathlib import Path

from frontend.ast.driver.tree_writer import ast_to_text
from frontend.lexer.lexer import Lexer
from frontend.parser.parser import parse


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_dir>")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    if not input_dir.is_dir():
        print(f"Directory not found error: {input_dir}")
        sys.exit(1)

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    src_files = sorted(input_dir.glob("*.src"))
    if not src_files:
        print(f"No .src files found in directory: {input_dir}")
        return
    
    for src_file in src_files:
        lexer = Lexer(text=src_file.read_text(encoding="utf-8"))
        result = parse(lexer)
        out_ast = output_dir / f"{src_file.stem}.outast"
        
        if result.success and result.ast_root is not None:
            ast_root = result.ast_root
            out_ast.write_text(ast_to_text(ast_root), encoding="utf-8")
            print(f"[OK] AST built: {src_file.name}")
        else:
            errors = result.errors
            out_ast.write_text("\n".join(errors), encoding="utf-8")
            print(f"[AST ERROR] {src_file.name} (parser errors: {len(result.errors)})")


if __name__ == "__main__":
    main()
