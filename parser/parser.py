from lexer.lexer import Lexer
from lexer.tokens import TokenType
from parser.table import table


def inverse_rhs_multiple_push(stack, x, a):
    rhs = table[x][a]
    for element in reversed(rhs):
        stack.append(element)
    return stack


TOKEN_MAP = {
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

IGNORE_TOKENS = {TokenType.BLOCKCMT, TokenType.INLINECMT}
INVALID_TOKENS = {TokenType.INVALIDCHAR, TokenType.INVALIDNUM, TokenType.INVALIDCMT}


def _next_non_comment_token(lexer: Lexer):
    token = lexer.get_next_token()
    while token and token.type in IGNORE_TOKENS:
        token = lexer.get_next_token()
    return token


def _to_table_terminal(token):
    if token is None:
        return "$"
    if token.type in INVALID_TOKENS:
        return None
    return TOKEN_MAP.get(token.type.value, token.type.value)


def parse(lexer: Lexer):
    stack = ["$", "START"]
    error = False

    token = _next_non_comment_token(lexer)
    a = _to_table_terminal(token)
    if a is None:
        print("[TRACE] invalid token encountered at start")
        return False
    lexeme = token.lexeme if token else ""
    print(f"[TRACE] start: stack_top={stack[-1]} lookahead={a} lexeme={lexeme}")

    while stack[-1] != "$":
        x = stack[-1]

        if x not in table:
            if x == a:
                print(f"[TRACE] match terminal: {x}")
                stack.pop()
                token = _next_non_comment_token(lexer)
                a = _to_table_terminal(token)
                if a is None:
                    error = True
                    break
                lexeme = token.lexeme if token else ""
                print(f"[TRACE] next lookahead: {a} lexeme={lexeme} stack_top={stack[-1]}")
            else:
                error = True
                break

        else:
            if a in table[x]:
                rhs = table[x][a]
                print(f"[TRACE] expand: {x} -> {rhs} on lookahead={a}")
                stack.pop()
                stack = inverse_rhs_multiple_push(stack, x, a)
            else:
                error = True
                break

    if a != "$" or error:
        return False
    return True
