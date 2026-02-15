table = {
    "ADDOP": {
        "minus": ["minus"],
        "plus": ["plus"],
        "or": ["or"]
    },
    "APARAMS": {
        "minus": ["EXPR", "REPTAPARAMS1"],
        "plus": ["EXPR", "REPTAPARAMS1"],
        "id": ["EXPR", "REPTAPARAMS1"],
        "rpar": [],
        "lpar": ["EXPR", "REPTAPARAMS1"],
        "not": ["EXPR", "REPTAPARAMS1"],
        "floatnum": ["EXPR", "REPTAPARAMS1"],
        "intnum": ["EXPR", "REPTAPARAMS1"]
    },
    "APARAMSTAIL": {
        "comma": ["comma", "EXPR"]
    },
    "ARITHEXPR": {
        "minus": ["TERM", "RIGHTRECARITHEXPR"],
        "plus": ["TERM", "RIGHTRECARITHEXPR"],
        "id": ["TERM", "RIGHTRECARITHEXPR"],
        "lpar": ["TERM", "RIGHTRECARITHEXPR"],
        "not": ["TERM", "RIGHTRECARITHEXPR"],
        "floatnum": ["TERM", "RIGHTRECARITHEXPR"],
        "intnum": ["TERM", "RIGHTRECARITHEXPR"]
    },
    "ARRAYSIZE": {
        "lsqbr": ["lsqbr", "ARRAYSIZE1"]
    },
    "ARRAYSIZE1": {
        "rsqbr": ["rsqbr"],
        "intnum": ["intnum", "rsqbr"]
    },
    "ASSIGNOP": {
        "equal": ["equal"]
    },
    "CLASSDECL": {
        "class": ["class", "id", "OPTCLASSDECL2", "lcurbr", "REPTCLASSDECL4", "rcurbr", "semi"]
    },
    "EXPR": {
        "minus": ["ARITHEXPR", "EXPR1"],
        "plus": ["ARITHEXPR", "EXPR1"],
        "id": ["ARITHEXPR", "EXPR1"],
        "lpar": ["ARITHEXPR", "EXPR1"],
        "not": ["ARITHEXPR", "EXPR1"],
        "floatnum": ["ARITHEXPR", "EXPR1"],
        "intnum": ["ARITHEXPR", "EXPR1"]
    },
    "EXPR1": {
        "geq": ["RELOP", "ARITHEXPR"],
        "leq": ["RELOP", "ARITHEXPR"],
        "gt": ["RELOP", "ARITHEXPR"],
        "lt": ["RELOP", "ARITHEXPR"],
        "neq": ["RELOP", "ARITHEXPR"],
        "eq": ["RELOP", "ARITHEXPR"],
        "rpar": [],
        "semi": [],
        "comma": []
    },
    "FACTOR": {
        "minus": ["SIGN", "FACTOR"],
        "plus": ["SIGN", "FACTOR"],
        "id": ["id", "FACTORID"],
        "lpar": ["lpar", "ARITHEXPR", "rpar"],
        "not": ["not", "FACTOR"],
        "floatnum": ["floatnum"],
        "intnum": ["intnum"]
    },
    "FACTORID": {
        "minus": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "plus": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "and": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "div": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "mult": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "or": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "geq": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "leq": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "gt": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "lt": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "neq": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "eq": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "rsqbr": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "lsqbr": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "dot": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "rpar": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "lpar": ["lpar", "APARAMS", "rpar", "FACTORID_AFTERCALL"],
        "semi": ["REPTVARIABLE2", "FACTORID_AFTERVAR"],
        "comma": ["REPTVARIABLE2", "FACTORID_AFTERVAR"]
    },
    "FACTORID_AFTERCALL": {
        "minus": [],
        "plus": [],
        "and": [],
        "div": [],
        "mult": [],
        "or": [],
        "geq": [],
        "leq": [],
        "gt": [],
        "lt": [],
        "neq": [],
        "eq": [],
        "rsqbr": [],
        "dot": ["dot", "id", "FACTORID"],
        "rpar": [],
        "semi": [],
        "comma": []
    },
    "FACTORID_AFTERVAR": {
        "minus": [],
        "plus": [],
        "and": [],
        "div": [],
        "mult": [],
        "or": [],
        "geq": [],
        "leq": [],
        "gt": [],
        "lt": [],
        "neq": [],
        "eq": [],
        "rsqbr": [],
        "dot": ["dot", "id", "FACTORID"],
        "rpar": [],
        "semi": [],
        "comma": []
    },
    "FPARAMS": {
        "id": ["TYPE", "id", "REPTFPARAMS2", "REPTFPARAMS3"],
        "float": ["TYPE", "id", "REPTFPARAMS2", "REPTFPARAMS3"],
        "integer": ["TYPE", "id", "REPTFPARAMS2", "REPTFPARAMS3"],
        "rpar": []
    },
    "FPARAMSTAIL": {
        "comma": ["comma", "TYPE", "id", "REPTFPARAMSTAIL3"]
    },
    "FUNCBODY": {
        "do": ["OPTFUNCBODY0", "do", "REPTFUNCBODY2", "end"],
        "local": ["OPTFUNCBODY0", "do", "REPTFUNCBODY2", "end"]
    },
    "FUNCDEF": {
        "id": ["FUNCHEAD", "FUNCBODY", "semi"],
    },
    "FUNCHEAD": {
        "id": ["id", "FUNCHEAD1"]
    },
    "FUNCHEAD1": {
        "lpar": ["lpar", "FPARAMS", "rpar", "colon", "RETTYPE"],
        "sr": ["sr", "id", "lpar", "FPARAMS", "rpar", "colon", "RETTYPE"]
    },
    "INDICE": {
        "lsqbr": ["lsqbr", "ARITHEXPR", "rsqbr"]
    },
    "MEMBERDECL": {
        "id": ["id", "MEMBERDECL1"],
        "float": ["float", "id", "REPTVARDECL2", "semi"],
        "integer": ["integer", "id", "REPTVARDECL2", "semi"]
    },
    "MEMBERDECL1": {
        "id": ["id", "REPTVARDECL2", "semi"],
        "lpar": ["lpar", "FPARAMS", "rpar", "colon", "RETTYPE", "semi"]
    },
    "MULTOP": {
        "and": ["and"],
        "div": ["div"],
        "mult": ["mult"]
    },
    "OPTCLASSDECL2": {
        "inherits": ["inherits", "id", "REPTOPTCLASSDECL22"],
        "lcurbr": []
    },
    "OPTFUNCBODY0": {
        "do": [],
        "local": ["local", "REPTOPTFUNCBODY01"]
    },
    "PROG": {
        "id": ["REPTPROG0", "REPTPROG1", "main", "FUNCBODY"],
        "class": ["REPTPROG0", "REPTPROG1", "main", "FUNCBODY"],
        "main": ["REPTPROG0", "REPTPROG1", "main", "FUNCBODY"]
    },
    "RELEXPR": {
        "minus": ["ARITHEXPR", "RELOP", "ARITHEXPR"],
        "plus": ["ARITHEXPR", "RELOP", "ARITHEXPR"],
        "id": ["ARITHEXPR", "RELOP", "ARITHEXPR"],
        "lpar": ["ARITHEXPR", "RELOP", "ARITHEXPR"],
        "not": ["ARITHEXPR", "RELOP", "ARITHEXPR"],
        "floatnum": ["ARITHEXPR", "RELOP", "ARITHEXPR"],
        "intnum": ["ARITHEXPR", "RELOP", "ARITHEXPR"]
    },
    "RELOP": {
        "geq": ["geq"],
        "leq": ["leq"],
        "gt": ["gt"],
        "lt": ["lt"],
        "neq": ["neq"],
        "eq": ["eq"]
    },
    "REPTAPARAMS1": {
        "rpar": [],
        "comma": ["APARAMSTAIL", "REPTAPARAMS1"]
    },
    "REPTCLASSDECL4": {
        "private": ["VISIBILITY", "MEMBERDECL", "REPTCLASSDECL4"],
        "public": ["VISIBILITY", "MEMBERDECL", "REPTCLASSDECL4"],
        "rcurbr": []
    },
    "REPTFPARAMS2": {
        "lsqbr": ["ARRAYSIZE", "REPTFPARAMS2"],
        "rpar": [],
        "comma": []
    },
    "REPTFPARAMS3": {
        "rpar": [],
        "comma": ["FPARAMSTAIL", "REPTFPARAMS3"]
    },
    "REPTFPARAMSTAIL3": {
        "lsqbr": ["ARRAYSIZE", "REPTFPARAMSTAIL3"],
        "rpar": [],
        "comma": []
    },
    "REPTFUNCBODY2": {
        "id": ["STATEMENT", "REPTFUNCBODY2"],
        "return": ["STATEMENT", "REPTFUNCBODY2"],
        "write": ["STATEMENT", "REPTFUNCBODY2"],
        "read": ["STATEMENT", "REPTFUNCBODY2"],
        "while": ["STATEMENT", "REPTFUNCBODY2"],
        "if": ["STATEMENT", "REPTFUNCBODY2"],
        "end": []
        
    },
    "REPTOPTCLASSDECL22": {
        "comma": ["comma", "id", "REPTOPTCLASSDECL22"],
        "lcurbr": []
    },
    "REPTOPTFUNCBODY01": {
        "id": ["VARDECL", "REPTOPTFUNCBODY01"],
        "float": ["VARDECL", "REPTOPTFUNCBODY01"],
        "integer": ["VARDECL", "REPTOPTFUNCBODY01"],
        "do": []
    },
    "REPTPROG0": {
        "id": [],
        "class": ["CLASSDECL", "REPTPROG0"],
        "main": []
    },
    "REPTPROG1": {
        "id": ["FUNCDEF", "REPTPROG1"],
        "main": []
    },
    "REPTSTATBLOCK1": {
       "id": ["STATEMENT", "REPTSTATBLOCK1"],
       "return": ["STATEMENT", "REPTSTATBLOCK1"],
       "write": ["STATEMENT", "REPTSTATBLOCK1"],
       "read": ["STATEMENT", "REPTSTATBLOCK1"],
       "while": ["STATEMENT", "REPTSTATBLOCK1"],
       "if": ["STATEMENT", "REPTSTATBLOCK1"],
       "end": []
    },
    "RETTYPE": {
        "id": ["TYPE"],
        "float": ["TYPE"],
        "integer": ["TYPE"],
        "void": ["void"]
    },
    "REPTVARDECL2": {
        "lsqbr": ["ARRAYSIZE", "REPTVARDECL2"],
        "semi": [],
    },
    "REPTVARIABLE2": {
        "minus": [],
        "plus": [],
        "and": [],
        "div": [],
        "mult": [],
        "or": [],
        "geq": [],
        "leq": [],
        "gt": [],
        "lt": [],
        "neq": [],
        "eq": [],
        "rsqbr": [],
        "lsqbr": ["INDICE", "REPTVARIABLE2"],
        "dot": [],
        "rpar": [],
        "equal": [],
        "semi": [],
        "comma": []
    },
    "RIGHTRECARITHEXPR": {
        "minus": ["ADDOP", "TERM", "RIGHTRECARITHEXPR"],
        "plus": ["ADDOP", "TERM", "RIGHTRECARITHEXPR"],
        "or": ["ADDOP", "TERM", "RIGHTRECARITHEXPR"],
        "geq": [],
        "leq": [],
        "gt": [],
        "lt": [],
        "neq": [],
        "eq": [],
        "rsqbr": [],
        "rpar": [],
        "semi": [],
        "comma": []
    },
    "RIGHTRECTERM": {
        "minus": [],
        "plus": [],
        "and": ["MULTOP", "FACTOR", "RIGHTRECTERM"],
        "div": ["MULTOP", "FACTOR", "RIGHTRECTERM"],
        "mult": ["MULTOP", "FACTOR", "RIGHTRECTERM"],
        "or": [],
        "geq": [],
        "leq": [],
        "gt": [],
        "lt": [],
        "neq": [],
        "eq": [],
        "rsqbr": [],
        "rpar": [],
        "semi": [],
        "comma": []
    },
    "SIGN": {
        "minus": ["minus"],
        "plus": ["plus"]
    },
    "START": {
        "id": ["PROG"],
        "class": ["PROG"],
        "main": ["PROG"]
    },
    "STATBLOCK": {
        "id": ["STATEMENT"],
        "semi": [],
        "return": ["STATEMENT"],
        "write": ["STATEMENT"],
        "read": ["STATEMENT"],
        "while": ["STATEMENT"],
        "else": [],
        "if": ["STATEMENT"],
        "do": ["do", "REPTSTATBLOCK1", "end"]
    },
    "STATEMENT": {
        "id": ["id", "STATEMENTID", "semi"],
        "return": ["return", "lpar", "EXPR", "rpar", "semi"],
        "write": ["write", "lpar", "EXPR", "rpar", "semi"],
        "read": ["read", "lpar", "VARIABLE", "rpar", "semi"],
        "while": ["while", "lpar", "RELEXPR", "rpar", "STATBLOCK", "semi"],
        "if": ["if", "lpar", "RELEXPR", "rpar", "then", "STATBLOCK", "else", "STATBLOCK", "semi"]
    },
    "STATEMENTID": {
        "lsqbr": ["REPTVARIABLE2", "STATEMENTID_AFTERVAR"],
        "dot": ["REPTVARIABLE2", "STATEMENTID_AFTERVAR"],
        "lpar": ["lpar", "APARAMS", "rpar", "STATEMENTID_AFTERCALL"],
        "equal": ["REPTVARIABLE2", "STATEMENTID_AFTERVAR"]
    },
    "STATEMENTID_AFTERCALL": {
        "dot": ["dot", "id", "STATEMENTID"],
        "semi": []
    },
    "STATEMENTID_AFTERVAR": {
        "dot": ["dot", "id", "STATEMENTID"],
        "equal": ["ASSIGNOP", "EXPR"]
    },
    "TERM": {
        "minus": ["FACTOR", "RIGHTRECTERM"],
        "plus": ["FACTOR", "RIGHTRECTERM"],
        "id": ["FACTOR", "RIGHTRECTERM"],
        "lpar": ["FACTOR", "RIGHTRECTERM"],
        "not": ["FACTOR", "RIGHTRECTERM"],
        "floatnum": ["FACTOR", "RIGHTRECTERM"],
        "intnum": ["FACTOR", "RIGHTRECTERM"]
    },
    "TYPE": {
        "id": ["id"],
        "float": ["float"],
        "integer": ["integer"]
    },
    "VARDECL": {
        "id": ["TYPE", "id", "REPTVARDECL2", "semi"],
        "float": ["TYPE", "id", "REPTVARDECL2", "semi"],
        "integer": ["TYPE", "id", "REPTVARDECL2", "semi"]
    },
    "VARIABLE": {
        "id": ["id", "VARIABLE1"],
    },
    "VARIABLE1": {
        "lsqbr": ["REPTVARIABLE2", "VARIABLE2"],
        "dot": ["REPTVARIABLE2", "VARIABLE2"],
        "rpar": ["REPTVARIABLE2", "VARIABLE2"],
        "lpar": ["lpar", "APPARAMS", "rpar", "dot", "id", "VARIABLE1"]
    },
    "VARIABLE2": {
        "dot": ["dot", "id", "VARIABLE1"],
        "rpar": [],
    },
    "VISIBILITY": {
        "private": ["private"],
        "public": ["public"]
    }   
}

terminals = {
    ",",
    "+",
    "-",
    "or",
    "[",
    "intNum",
    "]",
    "=",
    "class",
    "id",
    "{",
    "}",
    ";",
    "(",
    ")",
    "floatNum",
    "not",
    "do",
    "end",
    ":",
    "void",
    ".",
    "*",
    "/",
    "and",
    "inherits",
    "local",
    "sr",
    "main",
    "eq",
    "geq",
    "gt",
    "leq",
    "lt",
    "neq",
    "if",
    "then",
    "else",
    "read",
    "return",
    "while",
    "write",
    "float",
    "integer",
    "private",
    "public"
}


def count_non_null_entries(table: dict) -> int:
    return sum(
        1
        for nonterminal, row in table.items()
        for terminal, production in row.items()
    )
    
count = count_non_null_entries(table)
print("Non-null LL(1) table entries:", count)