import sys
from pathlib import Path

from lexer.lexer import Lexer
from parser.parser import parse 


def run_parser(input_path: Path) -> None:
    if not input_path.exists():
        print(f"File not found error: {input_path}")
        return

    file_content = input_path.read_text(encoding="utf-8")

    lexer = Lexer(text=file_content)

    success = parse(lexer)

    if success:
        print(f"[OK] Parsed successfully: {input_path.name}")
    else:
        print(f"[SYNTAX ERROR] {input_path.name}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:")
        print("python parserdriver.py <file.src> [more files/dirs...]")
        sys.exit(1)

    inputs = [Path(arg) for arg in sys.argv[1:]]
    had_error = False

    for input_path in inputs:
        if input_path.is_file():
            run_parser(input_path)
            continue

        if input_path.is_dir():
            src_files = list(input_path.glob("*.src"))
            if not src_files:
                print(f"No .src files found in directory: {input_path}")
            for src_file in src_files:
                run_parser(src_file)
            continue

        print(f"Not a file or directory error: {input_path}")
        had_error = True

    if had_error:
        sys.exit(1)


if __name__ == "__main__":
    main()