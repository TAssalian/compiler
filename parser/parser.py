from dataclasses import dataclass
from lexer.lexer import Lexer
from lexer.tokens import TokenType
from parser.table import table


token_map = {
    "openpar": "lpar",
    "closepar": "rpar",
    "opencubr": "lcurbr",
    "closecubr": "rcurbr",
    "opensqbr": "lsqbr",
    "closesqbr": "rsqbr",
    "assign": "equal",
    "noteq": "neq",
    "coloncolon": "sr",
}

ignore_tokens = {
    TokenType.BLOCKCMT,
    TokenType.INLINECMT
}

invalid_tokens = {
    TokenType.INVALIDCHAR, 
    TokenType.INVALIDNUM,
    TokenType.INVALIDCMT
}


@dataclass
class ParseResult:
    success: bool
    errors: list[str]
    derivation: list[str]


def _next_non_comment_token(lexer: Lexer):
    token = lexer.get_next_token()

    while token and token.type in ignore_tokens:
        token = lexer.get_next_token()

    return token

def _lexer_to_terminal(token):
    if token is None:
        return "$"

    if token.type in invalid_tokens:
        return None

    # Use token_map if needed, otherwise keep the original token name
    return token_map.get(token.type.value, token.type.value)

# Error message
def _describe_token(token) -> str:
    if token is None:
        return "end of file"

    return f"'{token.lexeme}' ({token.type.value})"


def _expected_lookaheads(non_terminal: str) -> str:
    """
    Return a comma-separated list of valid lookahead tokens
    for a given non-terminal (from the parse table).
    """
    expected = sorted(table[non_terminal].keys())
    return ", ".join(expected) if expected else "<none>"


# ---------------------------
# Derivation helpers
# ---------------------------

def _apply_leftmost_step(form: list[str], non_terminal: str, rhs: list[str]) -> list[str]:
    """
    Perform ONE leftmost derivation step:
    Replace the first occurrence of `non_terminal` in `form`
    with the right-hand side `rhs`.
    """
    for i, symbol in enumerate(form):
        if symbol == non_terminal:
            return form[:i] + rhs + form[i + 1 :]
    return form


def _format_form(form: list[str]) -> str:
    """
    Convert a sentential form into a printable string.
    """
    return " ".join(form) if form else "epsilon"


# ---------------------------
# Main LL(1) parser
# ---------------------------

def parse(lexer: Lexer) -> ParseResult:
    stack = ["$", "START"]
    errors: list[str] = []
    derivation = ["START"]
    form = ["START"]

    
    token = _next_non_comment_token(lexer)
    lookahead = _lexer_to_terminal(token)

    def advance():
        nonlocal token, lookahead
        token = _next_non_comment_token(lexer)
        lookahead = _lexer_to_terminal(token)

    def line_of_current() -> int:
        return token.line if token is not None else -1


    while stack and stack[-1] != "$":
        top = stack[-1]

        # Invalid token
        if lookahead is None:
            errors.append(
                f"Syntax error at line {line_of_current()}: "
                f"invalid token {_describe_token(token)}."
            )
            advance()
            continue

        # Top of stack is a terminal
        if top not in table:
            if top == lookahead:
                # Terminal matches, consume it
                stack.pop()
                advance()
            else:
                # Terminal mismatch, assume missing terminal
                errors.append(
                    f"Syntax error at line {line_of_current()}: "
                    f"expected '{top}' but found {_describe_token(token)}."
                )
                stack.pop()
        
        else:
            productions = table[top]

            # Valid production is found
            if lookahead in productions:
                rhs = productions[lookahead]
                stack.pop()
                stack.extend(reversed(rhs))

                form = _apply_leftmost_step(form, top, rhs)
                derivation.append(_format_form(form))
            # The parser has a non-terminal on top of the stack, but there is no valid rule for it.
            else: 
                errors.append(
                    f"Syntax error at line {line_of_current()}: "
                    f"unexpected {_describe_token(token)} while parsing {top}; "
                    f"expected one of: {_expected_lookaheads(top)}."
                )

                # Set of non-terminals that could go to epsilon.
                # It's ok if the non-terminal at the top of the stack goes away
                sync_set = {
                    terminal
                    for terminal, rhs in productions.items()
                    if rhs == []
                }

                # Want to find out if the problem is the top of the stack that parser is expecting, or the token it is currently seeing in the lookahead
            
                # Input looks reasonable, its possible to take its epsilon instead of expecting more input
                if lookahead in sync_set or lookahead == "$":
                    # Skip this non-terminal
                    stack.pop()
                # Current lookahead makes no sense and cannot end the current non-terminal
                else:
                    # Skip one token
                    advance()

    if errors:
        derivation.append("Incomplete derivation due to syntax errors.")

    return ParseResult(
        success=not errors,
        errors=errors,
        derivation=derivation
    )
