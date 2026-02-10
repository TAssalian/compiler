import sys
from pathlib import Path
from lexer import Lexer
from tokens import TokenType


def run_lexer(input_path: Path, output_dir: Path) -> None:
    if not input_path.exists():
        print(f"File not found error: {input_path}")
        return

    file_content = input_path.read_text(encoding="utf-8")
    lexer = Lexer(text=file_content)

    base_name = input_path.stem

    out_tokens = output_dir / f"{base_name}.outlextokens"
    out_flaci  = output_dir / f"{base_name}.outlextokensflaci"
    out_errs   = output_dir / f"{base_name}.outlexerrors"

    with (
        open(out_tokens, "w", encoding="utf-8") as t,
        open(out_flaci, "w", encoding="utf-8") as f,
        open(out_errs, "w", encoding="utf-8") as e,
    ):
        first_flaci = True
        while True:
            token = lexer.get_next_token()
            if token is None:
                break
        
            t.write(token.to_outtokens() + "\n")
            if not first_flaci:
                f.write(" ")
            f.write(token.to_flaci())
            first_flaci = False
            if token.type in {TokenType.INVALIDCHAR, TokenType.INVALIDNUM, TokenType.INVALIDCMT}:
                e.write(token.to_outerrs() + "\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:")
        print("python lexdriver.py <file.src> [more files/dirs...]")
        print("or")
        print("python lexdriver.py <folder/> [more files/dirs...]")
        sys.exit(1)

    inputs = [Path(arg) for arg in sys.argv[1:]]
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    had_error = False
    for input_path in inputs:
        if input_path.is_file():
            run_lexer(input_path, output_dir)
            continue

        if input_path.is_dir():
            src_files = list(input_path.glob("*.src"))
            if not src_files:
                print(f"No .src files found in directory: {input_path}")
            for src_file in src_files:
                run_lexer(src_file, output_dir)
            continue

        print(f"Not a file or directory error: {input_path}")
        had_error = True

    if had_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
