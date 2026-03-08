from dataclasses import dataclass
from frontend.lexer.lexer import Lexer
from frontend.lexer.tokens import Token, TokenType
from frontend.parser.table import table
from frontend.ast.nodes.program.start_node import StartNode


from frontend.ast.semantic_actions import semantic_actions, semantic_stack


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
    ast_root: StartNode | None = None


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

    return token_map.get(token.type.value, token.type.value)

def _describe_token(token) -> str:
    if token is None:
        return "end of file"

    return f"'{token.lexeme}' ({token.type.value})"


def _expected_lookaheads(non_terminal: str) -> str:
    expected = sorted(table[non_terminal].keys())
    return ", ".join(expected) if expected else "<none>"


def _apply_leftmost_step(form: list[str], non_terminal: str, rhs: list[str]) -> list[str]:
    for i, symbol in enumerate(form):
        if symbol == non_terminal:
            return form[:i] + rhs + form[i + 1 :]
    return form


def _format_form(form: list[str]) -> str:
    return " ".join(form) if form else "epsilon"


def parse(lexer: Lexer) -> ParseResult:
    semantic_stack.clear()
    stack = ["$", "START"]
    errors: list[str] = []
    derivation = ["START"]
    form = ["START"]
    
    token = _next_non_comment_token(lexer)
    lookahead = _lexer_to_terminal(token)
    last_matched_token: Token | None = None

    def advance():
        nonlocal token, lookahead
        token = _next_non_comment_token(lexer)
        lookahead = _lexer_to_terminal(token)

    def line_of_current() -> int:
        return token.line if token is not None else -1


    while stack and stack[-1] != "$":
        top = stack[-1]

        if lookahead is None:
            errors.append(
                f"Syntax error at line {line_of_current()}: "
                f"invalid token {_describe_token(token)}."
            )
            advance()
            continue

        if top not in table and not top.startswith("#"):
            if top == lookahead:
                stack.pop()
                last_matched_token = token
                advance()
            else:
                errors.append(
                    f"Syntax error at line {line_of_current()}: "
                    f"expected '{top}' but found {_describe_token(token)}."
                )
                stack.pop()
        
        elif top in table:
            productions = table[top]

            if lookahead in productions:
                rhs = productions[lookahead]
                stack.pop()
                stack.extend(reversed(rhs))

                form = _apply_leftmost_step(form, top, rhs)
                derivation.append(_format_form(form))
            else: 
                errors.append(
                    f"Syntax error at line {line_of_current()}: "
                    f"unexpected {_describe_token(token)} while parsing {top}; "
                    f"expected one of: {_expected_lookaheads(top)}."
                )

                sync_set = {
                    terminal
                    for terminal, rhs in productions.items()
                }
            
                if lookahead in sync_set or lookahead == "$":
                    stack.pop()
                else:
                    while lookahead not in sync_set and lookahead != "$":
                        advance()
                    stack.pop()
        else:
            stack.pop()
            create_node_func = semantic_actions[top]
            if create_node_func is None:
                errors.append(
                    f"Semantic error at line {line_of_current()}: "
                    f"unknown semantic action '{top}'."
                )
                continue
            create_node_func(last_matched_token)
        
    if errors:
        derivation.append("Incomplete derivation due to syntax errors.")

    ast_root = semantic_stack[-1] if semantic_stack else None
    if ast_root is not None and not isinstance(ast_root, StartNode):
        errors.append("Semantic error: parse completed without a StartNode root.")
        ast_root = None

    return ParseResult(
        success=not errors,
        errors=errors,
        derivation=derivation,
        ast_root=ast_root,
    )
