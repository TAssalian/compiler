from dataclasses import dataclass
from enum import Enum

class TokenType(Enum):
    ID = "id"
    INTNUM = "intnum"
    FLOATNUM = "floatnum"

    EQ = "eq"             
    NOTEQ = "noteq"        
    LT = "lt"             
    GT = "gt"             
    LEQ = "leq"            
    GEQ = "geq"            
    ASSIGN = "assign"  

    PLUS = "plus"        
    MINUS = "minus"   
    MULT = "mult"    
    DIV = "div"     

    OPENPAR = "openpar" 
    CLOSEPAR = "closepar"  
    OPENCUBR = "opencubr"  
    CLOSECUBR = "closecubr" 
    OPENSQBR = "opensqbr" 
    CLOSESQBR = "closesqbr" 
    SEMI = "semi"    
    COMMA = "comma"      
    DOT = "dot"     
    COLON = "colon"      
    COLONCOLON = "coloncolon"

    IF = "if"
    THEN = "then"
    ELSE = "else"
    WHILE = "while"
    CLASS = "class"
    INTEGER = "integer"
    FLOAT = "float"
    DO = "do"
    END = "end"
    PUBLIC = "public"
    PRIVATE = "private"
    OR = "or"
    AND = "and"
    NOT = "not"
    READ = "read"
    WRITE = "write"
    RETURN = "return"
    INHERITS = "inherits"
    LOCAL = "local"
    VOID = "void"
    MAIN = "main"
    
    BLOCKCMT = "blockcmt"
    INLINECMT = "inlinecmt"
    
    # TODO: Error types
    ERROR = "error"

@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    
    def to_outtokens(self) -> str:
        return f"[{self.type.value}, {self.lexeme}, {self.line}]"

    def to_flaci(self) -> str:
        # TODO: Determine input format for Flaci tool
        return f"'{self.lexeme}' at line {self.line} in Flaci's input format"

    def to_outerrs(self) -> str:
        # TODO: Determine what error types to implement. If more than one, implement switch-case functionality to print correct, full text error.
        return f"Lexical error: Invalid [x]: '{self.lexeme}': line {self.line}."