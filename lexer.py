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

@dataclass()
class Lexer:
    text: str
    pos: int = -1
    current_char: int | None = None
    
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
        else:
            print("Not yet implemented")
    
    def _advance(self) -> None: 
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None    
    
    def _skip_whitespace(self) -> None:
        while self.current_char is not None and self.current_char.isspace():
            self._advance()
            
    def _get_id_or_reserved_word_token(self, lexeme: str) -> Token:
        while self.current_char is not None and self.current_char.isalnum() or self.current_char == "_":
            lexeme += self.current_char
            self._advance()
        
        if self.current_char is not None and not self.current_char.isspace():
            lexeme = self._exhaust_invalid_id(lexeme)
        
        lexeme_type = self._get_id_or_reserved_word_tokentype(lexeme)
        return Token(lexeme_type, lexeme, -1) # TODO: Remove this hardcoded value for actual line number
        
    def _get_id_or_reserved_word_tokentype(self, lexeme: str) -> TokenType:
        if not all(char.isalnum() or char == "_" for char in lexeme):
            return TokenType.ERROR # TODO: Remove hardcode after determining what error types to include
        
        if lexeme in reserved_words:
            return TokenType[lexeme.upper()]
        
        elif lexeme.lower() in reserved_words and lexeme not in reserved_words:
            return TokenType.ERROR # TODO: Remove hardcode after determining what error types to include
        
        return TokenType.ID
    
    def _exhaust_invalid_id(self, lexeme: str) -> str:
        while self.current_char is not None and not self.current_char.isspace():
            lexeme += self.current_char
            self._advance()
        return lexeme
    