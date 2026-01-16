from dataclasses import dataclass

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

@dataclass(frozen=True)
class Lexer:
    text: str
    position: int = -1
    current_char: int | None = None
    
    def get_next_token():
        # This will be the function repeatedly called by the driver 
        # Calls the different private methods below to determine the token type and lexeme
        #
        # return: the anticipated next token
        pass
    
    
    def _create_id_or_reserved_word():
        # This is deterministically called upon seeing the first character be a letter
        # We then scan until it is no longer valid
        # Compare a hashset of the keywords for O(1) access to see if its a reserved word
        # If the capital version of the reserved word is written, also return invalid. Do this by seeing if all lowercase lexeme is in the hashset and original lexeme is not
        #
        # return: 'Token class of type id' if 'token not in hashset' else 'Token class of type reserved word'.
        pass