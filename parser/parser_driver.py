import sys
from pathlib import Path

from lexer.lexer import Lexer
from parser.parser import parse 


def run_parser(input_path: Path, output_dir: Path) -> None:
    file_content = input_path.read_text(encoding="utf-8")
    lexer = Lexer(text=file_content)
    result = parse(lexer)

    out_syntax_errors = output_dir / f"{input_path.stem}.outsyntaxerrors"
    out_derivation = output_dir / f"{input_path.stem}.outderivation"
    out_syntax_errors.write_text("\n".join(result.errors), encoding="utf-8")
    out_derivation.write_text("\n".join(result.derivation), encoding="utf-8")

    if result.success:
        print(f"[OK] Parsed successfully: {input_path.name}")
    else:
        print(f"[SYNTAX ERROR] {input_path.name} ({len(result.errors)} error(s))")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:")
        print("python parserdriver.py <file.src> [more files/dirs...]")
        sys.exit(1)

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    inputs = [Path(arg) for arg in sys.argv[1:]]
    had_error = False

    for input_path in inputs:
        if not input_path.exists():
            print(f"File not found error: {input_path}")
            had_error = True
            continue

        if input_path.is_file():
            run_parser(input_path, output_dir)
            continue

        if input_path.is_dir():
            src_files = sorted(input_path.glob("*.src"))
            if not src_files:
                print(f"No .src files found in directory: {input_path}")
            for src_file in src_files:
                run_parser(src_file, output_dir)
            continue

        print(f"Not a file or directory error: {input_path}")
        had_error = True

    if had_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
