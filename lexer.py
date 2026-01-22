from dataclasses import dataclass
from tokens import Token, TokenType


reserved_words = {
    "if",
    "then",
    "else",
    "while",
    "class",
    "integer",
    "float",
    "do",
    "end",
    "public",
    "private",
    "or",
    "and",
    "not",
    "read",
    "write",
    "return",
    "inherits",
    "local",
    "void",
    "main"
}

nonzero_digits = {
    "1", "2", "3", "4", 
    "5", "6", "7", "8", "9"
}

single_misc = {
            "=": TokenType.ASSIGN,
            "<": TokenType.LT,
            ">": TokenType.GT,
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULT,
            "/": TokenType.DIV,
            "(": TokenType.OPENPAR,
            ")": TokenType.CLOSEPAR,
            "{": TokenType.OPENCUBR,
            "}": TokenType.CLOSECUBR,
            "[": TokenType.OPENSQBR,
            "]": TokenType.CLOSESQBR,
            ";": TokenType.SEMI,
            ",": TokenType.COMMA,
            ".": TokenType.DOT,
            ":": TokenType.COLON,
        }


@dataclass()
class Lexer:
    text: str
    pos: int = -1
    current_char: int | None = None
    line: int = 1
    
    def __post_init__(self) -> None:
        self._advance()
    
    def get_next_token(self) -> Token:
        self._skip_whitespace()

        if self.current_char is None:
            return None
        elif self.current_char.isalpha():
            return self._get_id_or_reserved_word_token()
        elif self.current_char.isdigit():
            return self._get_integer_or_float_token()
        elif self._is_comment_token():
            return self._get_comment_token()
        elif self._is_operator_or_punct():
            return self._get_operator_or_punct_token()
        else:
            lexeme = self.current_char
            self._advance()
            return Token(TokenType.INVALIDCHAR, lexeme, self.line)
    
    def _advance(self) -> None: 
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
    
    def _skip_whitespace(self) -> None:
        while self.current_char and self.current_char.isspace():
            if self.current_char == "\n":
                self.line += 1
            self._advance()
    
    def _look_ahead(self) -> str | None:
        next_pos = self.pos + 1
        return self.text[next_pos] if next_pos < len(self.text) else None
    
    
    def _get_id_or_reserved_word_token(self) -> Token:
        lexeme = self._get_id()

        if lexeme in reserved_words:
            lexeme_type = TokenType[lexeme.upper()]
        else:
            lexeme_type = TokenType.ID
        return Token(lexeme_type, lexeme, self.line)
    
    def _get_id(self) -> str:
        lexeme = ""
        while self.current_char and (self.current_char.isalnum() or self.current_char == "_"):
            lexeme += self.current_char
            self._advance()
        return lexeme
    
    
    def _get_integer_or_float_token(self) -> Token:
        lexeme = self._consume_number()

        if self._is_integer(lexeme):
            lexeme_type = TokenType.INTNUM
        elif self._is_float(lexeme):
            lexeme_type = TokenType.FLOATNUM
        else:
            lexeme_type = TokenType.INVALIDNUM
        return Token(lexeme_type, lexeme, self.line)
    
    def _consume_number(self) -> str:
        lexeme = ""
        seen_dot = False
        seen_e = False
        sign_allowed = False

        while self.current_char:
            if self.current_char.isdigit():
                lexeme += self.current_char
                self._advance()
                sign_allowed = False
            elif self.current_char == "." and not seen_dot and not seen_e:
                seen_dot = True
                lexeme += self.current_char
                self._advance()
                sign_allowed = False
            elif self.current_char == "e" and not seen_e:
                seen_e = True
                lexeme += self.current_char
                self._advance()
                sign_allowed = True
            elif self.current_char in {"+", "-"} and sign_allowed:
                lexeme += self.current_char
                self._advance()
                sign_allowed = False
            else:
                break

        return lexeme

    def _is_integer(self, lexeme: str) -> bool:
        if lexeme == "0":
            return True
        elif len(lexeme) == 1:
            return lexeme[0] in nonzero_digits
        else:
            return lexeme[0] in nonzero_digits and lexeme[1:].isdigit()

    def _is_float(self, lexeme: str) -> bool:
        if lexeme.count("e") > 1:
            return False
        base, exp = (lexeme.split("e") + [""])[:2]

        if "." not in base or base.count(".") > 1:
            return False
        integer_part, fraction_part = base.split(".")

        if not self._is_integer(integer_part):
            return False
        if not self._is_fraction(f".{fraction_part}"):
            return False

        if exp == "":
            return True
        if exp[0] in {"+", "-"}:
            return len(exp) > 1 and self._is_integer(exp[1:])
        else:
            return self._is_integer(exp)

    def _is_fraction(self, lexeme: str) -> bool:
        if lexeme == ".0":
            return True
        if not lexeme.startswith("."):
            return False
        end = lexeme[1:]
        return end.isdigit() and end[-1] in nonzero_digits

    def _is_comment_token(self) -> bool:
        char = self.current_char
        return char == "/" and self._look_ahead() in {"/", "*"}
    
    def _get_comment_token(self) -> Token:
        if self._look_ahead() not in {"/", "*"}:
            return False
        lexeme = self.current_char
        self._advance()

        if self.current_char == "/":
            lexeme += self.current_char
            self._advance()
            while self.current_char is not None and self.current_char != "\n":
                lexeme += self.current_char
                self._advance()
            return Token(TokenType.INLINECMT, lexeme, self.line)

        else:
            lexeme += self.current_char
            self._advance()
            start_line = self.line
            closed = False
            while self.current_char is not None:
                if self.current_char == "\n":
                    self.line += 1
                    lexeme += r"\n"
                else:
                    lexeme += self.current_char
                if self.current_char == "*" and self._look_ahead() == "/":
                    self._advance()
                    lexeme += self.current_char
                    self._advance()
                    closed = True
                    break
                self._advance()
            if not closed:
                return Token(TokenType.INVALIDCMT, lexeme, start_line)
            return Token(TokenType.BLOCKCMT, lexeme, start_line)

    def _is_operator_or_punct(self) -> bool:
        if self.current_char is None:
            return False
        if self.current_char in single_misc:
            return True
        return False

    def _get_operator_or_punct_token(self) -> Token:
        if self.current_char == ":" and self._look_ahead() == ":":
            self._advance()
            self._advance()
            return Token(TokenType.COLONCOLON, "::", self.line)
        if self.current_char == "=" and self._look_ahead() == "=":
            self._advance()
            self._advance()
            return Token(TokenType.EQ, "==", self.line)
        if self.current_char == "<" and self._look_ahead() == ">":
            self._advance()
            self._advance()
            return Token(TokenType.NOTEQ, "<>", self.line)
        if self.current_char == "<" and self._look_ahead() == "=":
            self._advance()
            self._advance()
            return Token(TokenType.LEQ, "<=", self.line)
        if self.current_char == ">" and self._look_ahead() == "=":
            self._advance()
            self._advance()
            return Token(TokenType.GEQ, ">=", self.line)

        char = self.current_char
        self._advance()
        return Token(single_misc[char], char, self.line)
