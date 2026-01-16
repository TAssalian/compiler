from dataclasses import dataclass
from tokens import Token, TokenType


reserved_words = set(
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
)

@dataclass()
class Lexer:
    text: str
    pos: int = -1
    current_char: int | None = None
    
    def __post_init__(self):
        self._advance()
    
    def get_next_token(self):
        self._skip_whitespace()
        lexeme = self.current_char
        
        if self.current_char.isalpha():
            self._advance()
            return self._get_id_or_reserved_word_token(lexeme)
        else:
            print("Not yet implemented")
    
    def _advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None    
    
    def _skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self._advance()
    
    def _get_id_or_reserved_word_token(self, lexeme):
        while self.current_char.isalnum() or self.current_char == "_":
            lexeme += self.current_char
            self._advance()
        
        if not self.current_char.isspace():
            lexeme = self._exhaust_invalid_id(lexeme)
            lexeme_type = "invalidid" # TODO: Remove hardcore after determining what error types to include
        else:
            lexeme_type = self._get_id_or_reserved_word_type(lexeme)
        
        return Token(lexeme_type, lexeme, -1) # TODO: Remove this hardcoded value for actual line numbern
        
    def _get_id_or_reserved_word_type(self, lexeme):
        if lexeme in reserved_words:
            return TokenType[lexeme.upper()]
        elif lexeme.lower() in reserved_words and lexeme not in reserved_words:
            return "invalidreservedword" # TODO: Remove hardcore after determining what error types to include
        else:
            return TokenType.ID
    
    def _exhaust_invalid_id(self, lexeme):
        lexeme += self.current_char
        self._advance()
        while not self.current_char.isspace():
            lexeme += self.current_char
            self._advance()
        return lexeme
    