from __future__ import annotations

import sys
from pathlib import Path

from frontend.semantics.symbols import format_diagnostics, format_symbol_table
from frontend.semantics.visitors import SemanticCheckingVisitor, SymTabCreationVisitor
from frontend.lexer.lexer import Lexer
from frontend.parser.parser import parse


def process_file(src_file: Path, output_dir: Path) -> None:
    lexer = Lexer(text=src_file.read_text(encoding="utf-8"))
    result = parse(lexer)

    out_symboltables = output_dir / f"{src_file.stem}.outsymboltables"
    out_errors = output_dir / f"{src_file.stem}.outsemanticerrors"

    if not result.success:
        errors = result.errors
        text = "\n".join(errors)
        out_symboltables.write_text("", encoding="utf-8")
        out_errors.write_text(text, encoding="utf-8")
        print(f"[AST ERROR] {src_file.name} (parser errors: {len(errors)})")
        return

    st_visitor = SymTabCreationVisitor()
    result.ast_root.accept(st_visitor)

    semantic_visitor = SemanticCheckingVisitor(global_table=st_visitor.global_table)
    result.ast_root.accept(semantic_visitor)

    symbol_text = ""
    if st_visitor.global_table is not None:
        symbol_text = format_symbol_table(st_visitor.global_table)
    error_text = format_diagnostics(st_visitor.diagnostics + semantic_visitor.diagnostics)

    out_symboltables.write_text(symbol_text, encoding="utf-8")
    out_errors.write_text(error_text, encoding="utf-8")
    print(f"[OK] Semantic phases 1-2 completed: {src_file.name}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_dir>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if input_path.is_file() and input_path.suffix == ".src":
        src_files = [input_path]
    elif input_path.is_dir():
        src_files = sorted(input_path.glob("*.src"))
    else:
        print(f"Input not found error: {input_path}")
        sys.exit(1)

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    if not src_files:
        print(f"No .src files found in: {input_path}")
        return

    for src_file in src_files:
        process_file(src_file, output_dir)


if __name__ == "__main__":
    main()
