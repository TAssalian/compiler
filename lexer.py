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
        lexeme = self.current_char
        
        if self.current_char is None:
            return
        elif self.current_char.isalpha():
            self._advance()
            return self._get_id_or_reserved_word_token(lexeme)
        elif self.current_char.isdigit():
            self._advance()
            return self._get_integer_or_float_token(lexeme)
        else:
            print("Not yet implemented")
    
    def _advance(self) -> None: 
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        if self.current_char == "\n":
            self.line += 1
    
    def _skip_whitespace(self) -> None:
        while self.current_char and self.current_char.isspace():
            self._advance()
    
    def _exhaust_token(self, lexeme: str) -> str:
        while self.current_char and not self.current_char.isspace():
            lexeme += self.current_char
            self._advance()
        return lexeme
    
    def _get_id_or_reserved_word_token(self, lexeme: str) -> Token:
        lexeme = self._exhaust_token(lexeme)

        if self._is_id(lexeme):
            if lexeme in reserved_words:
                lexeme_type = TokenType[lexeme.upper()]
            elif lexeme.lower() in reserved_words and lexeme not in reserved_words:
                lexeme_type = TokenType.ERROR
            else:
                lexeme_type = TokenType.ID
        else:
            lexeme_type = TokenType.ERROR
        return Token(lexeme_type, lexeme, self.line)
    
    def _is_id(self, lexeme: str) -> bool:
        return all(char.isalnum() or char == "_" for char in lexeme[1:])

    
    def _get_integer_or_float_token(self, lexeme: str) -> Token:
        lexeme = self._exhaust_token(lexeme)

        if self._is_integer(lexeme):
            lexeme_type = TokenType.INTEGER
        elif self._is_float(lexeme):
            lexeme_type = TokenType.FLOAT
        else:
            lexeme_type = TokenType.ERROR
        return Token(lexeme_type, lexeme, self.line)

    def _is_integer(self, lexeme: str) -> bool:
        if lexeme == "0":
            return True
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
        if len(exp) < 2 or exp[0] not in {"+", "-"}:
            return False
        return self._is_integer(exp[1:])

    def _is_fraction(self, lexeme: str) -> bool:
        if lexeme == ".0":
            return True
        if not lexeme.startswith("."):
            return False
        tail = lexeme[1:]
        return tail.isdigit() and tail[-1] in nonzero_digits