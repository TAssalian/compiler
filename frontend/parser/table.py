table = {
    # Entry point to the program
    "START": {
        "id": ["PROG", "#make_start_subtree"],
        "class": ["PROG", "#make_start_subtree"],
        "main": ["PROG", "#make_start_subtree"]
    },
    # The program made up of, in order: class declarations, method definitions, and main body.
    "PROG": {
        "id": ["#push_epsilon", "REPT_CLASSDECLS", "REPT_FUNCDEFS", "main", "FUNCBODY", "#make_prog_subtree"],
        "class": ["#push_epsilon", "REPT_CLASSDECLS", "REPT_FUNCDEFS", "main", "FUNCBODY", "#make_prog_subtree"],
        "main": ["#push_epsilon", "REPT_CLASSDECLS", "REPT_FUNCDEFS", "main", "FUNCBODY", "#make_prog_subtree"]
    },
    
    
    # Parses zero or more class declarations
    "REPT_CLASSDECLS": {
        "id": [],
        "class": ["CLASSDECL", "REPT_CLASSDECLS"],
        "main": []
    },
    # Class declaration with attributes and methohds
    "CLASSDECL": {
        "class": ["class", "#push_epsilon", "id", "#make_id_node", "OPTCLASSDECL2", "lcurbr", "REPT_CLASS_MEMBERS", "rcurbr", "semi", "#make_classdecl_subtree"]
    },
    # Optional inheritance clause of class declaration
    "OPTCLASSDECL2": {
        "inherits": ["inherits", "id", "#make_id_node", "#make_inherits_subtree", "REPT_INHERITS_TAIL"],
        "lcurbr": []
    },
    # Parses zero or more inherited classes names separated by commas
    "REPT_INHERITS_TAIL": {
        "comma": ["comma", "id", "#make_id_node", "#make_inherits_subtree", "REPT_INHERITS_TAIL"],
        "lcurbr": []
    },
    # Zero or more member declarations inside class body
    "REPT_CLASS_MEMBERS": {
        "private": ["VISIBILITY", "MEMBERDECL", "REPT_CLASS_MEMBERS"],
        "public": ["VISIBILITY", "MEMBERDECL", "REPT_CLASS_MEMBERS"],
        "rcurbr": []
    },
    # Class member visibility modifier.
    "VISIBILITY": {
        "private": ["private", "#make_private_node"], #
        "public": ["public", "#make_public_node"] #
    },
    # Parses one class member declaration, either data member or method declaration.
    "MEMBERDECL": {
        "id": ["id", "#make_id_node", "MEMBERDECL_DISAMBIG"],
        "float": ["TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_VARDECL_DIMS", "#make_arraysize_subtree", "semi", "#make_vardecl_subtree"],
        "integer": ["TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_VARDECL_DIMS", "#make_arraysize_subtree", "semi", "#make_vardecl_subtree"]
    },
    # Disambiguates class member forms that start with an identifier between variable vs function declaration
    "MEMBERDECL_DISAMBIG": {
        "id": ["id", "#make_id_node", "#push_epsilon", "REPT_VARDECL_DIMS", "#make_arraysize_subtree", "semi", "#make_member_vardecl_subtree"],
        "lpar": ["lpar", "FPARAMS", "rpar", "colon", "RETTYPE", "semi", "#make_member_funcdecl_subtree"]
    },
    # Zero or more function definitions
    "REPT_FUNCDEFS": {
        "id": ["FUNCDEF", "REPT_FUNCDEFS"],
        "main": []
    },
    
    
    # Parses a full function definition: header, body, and semicolon
    "FUNCDEF": {
        "id": ["#push_epsilon", "FUNCHEAD", "FUNCBODY", "semi", "#make_funcdef_subtree"],
    },
    # Parses name of the function. Same as the start of MEMBERDECL
    "FUNCHEAD": {
        "id": ["id", "#make_id_node", "FUNCHEAD_TAIL"]
    },
    # Function header details like scope resolution, params, and return type. Same as the function path in MEMBERDECL_DISAMBIG
    "FUNCHEAD_TAIL": {
        "lpar": ["lpar", "FPARAMS", "rpar", "colon", "RETTYPE"],
        "sr": ["sr", "id", "#make_id_node", "lpar", "FPARAMS", "rpar", "colon", "RETTYPE"]
    },
    # Function return type
    "RETTYPE": {
        "id": ["TYPE"],
        "float": ["TYPE"],
        "integer": ["TYPE"],
        "void": ["void", "#make_void_type_node"]
    },
    # Type name token
    "TYPE": {
        "id": ["id", "#make_type_node"],
        "float": ["float", "#make_type_node"],
        "integer": ["integer", "#make_type_node"]
    },
    # Parses the full parameter list in function signature
    "FPARAMS": {
        "id": ["#push_epsilon", "TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_FPARAM_DIMS", "#make_arraysize_subtree", "#make_fparam_subtree", "REPT_FPARAMS", "#make_fparams_subtree"],
        "float": ["#push_epsilon", "TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_FPARAM_DIMS", "#make_arraysize_subtree", "#make_fparam_subtree", "REPT_FPARAMS", "#make_fparams_subtree"],
        "integer": ["#push_epsilon", "TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_FPARAM_DIMS", "#make_arraysize_subtree", "#make_fparam_subtree", "REPT_FPARAMS", "#make_fparams_subtree"],
        "rpar": ["#make_empty_fparams_node"]
    },
    # Parses zero or more array dimensions attached to a parameter in a function
    "REPT_FPARAM_DIMS": {
        "lsqbr": ["ARRAYSIZE", "REPT_FPARAM_DIMS"],
        "rpar": [],
        "comma": []
    },
    # Looks for zero or more additional function parameters
    "REPT_FPARAMS": {
        "rpar": [],
        "comma": ["FPARAMSTAIL", "REPT_FPARAMS"]
    },
    # Parses additional function parameter separated by a comma
    "FPARAMSTAIL": {
        "comma": ["comma", "TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_FPARAMTAIL_DIMS", "#make_arraysize_subtree", "#make_fparam_subtree"]
    },
    # Zero or more array dimensions on a trailing function parameter
    "REPT_FPARAMTAIL_DIMS": {
        "lsqbr": ["ARRAYSIZE", "REPT_FPARAMTAIL_DIMS"],
        "rpar": [],
        "comma": []
    },
    # Start of one array dimension
    "ARRAYSIZE": {
        "lsqbr": ["lsqbr", "ARRAYSIZE_BOUND"]
    },
    # Parses optional integer inside one array dimension
    "ARRAYSIZE_BOUND": {
        "rsqbr": ["rsqbr"],
        "intnum": ["intnum", "#make_intnum_node", "rsqbr"]
    },
    
    
    # Parses a function body with local declarations and statements
    "FUNCBODY": {
        "do": ["#push_epsilon", "OPTFUNCBODY0", "do", "REPT_FUNCBODY_STATEMENTS", "end", "#make_funcbody_subtree"],
        "local": ["#push_epsilon", "OPTFUNCBODY0", "do", "REPT_FUNCBODY_STATEMENTS", "end", "#make_funcbody_subtree"]
    },
    # Parses the optional local-declaration section
    "OPTFUNCBODY0": {
        "do": [],
        "local": ["local", "REPT_LOCAL_VARDECLS"]
    },
    # Parses zero or more local variable declarations in a function body
    "REPT_LOCAL_VARDECLS": {
        "id": ["VARDECL", "REPT_LOCAL_VARDECLS"],
        "float": ["VARDECL", "REPT_LOCAL_VARDECLS"],
        "integer": ["VARDECL", "REPT_LOCAL_VARDECLS"],
        "do": []
    },
    # Parses a complete variable declaration
    "VARDECL": {
        "id": ["TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_VARDECL_DIMS", "#make_arraysize_subtree", "semi", "#make_vardecl_subtree"], #
        "float": ["TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_VARDECL_DIMS", "#make_arraysize_subtree", "semi", "#make_vardecl_subtree"], #
        "integer": ["TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_VARDECL_DIMS", "#make_arraysize_subtree", "semi", "#make_vardecl_subtree"] #
    },
    # Parses zero or more array dimensions in a variable declaration
    "REPT_VARDECL_DIMS": {
        "lsqbr": ["ARRAYSIZE", "REPT_VARDECL_DIMS"],
        "semi": [],
    },
    # Parses zero or more statements inside a function body 'do' block
    "REPT_FUNCBODY_STATEMENTS": {
        "id": ["STATEMENT", "REPT_FUNCBODY_STATEMENTS"],
        "return": ["STATEMENT", "REPT_FUNCBODY_STATEMENTS"],
        "write": ["STATEMENT", "REPT_FUNCBODY_STATEMENTS"],
        "read": ["STATEMENT", "REPT_FUNCBODY_STATEMENTS"],
        "while": ["STATEMENT", "REPT_FUNCBODY_STATEMENTS"],
        "if": ["STATEMENT", "REPT_FUNCBODY_STATEMENTS"],
        "end": []
    },
    # Parses one executable statement
    "STATEMENT": {
        "id": ["#push_epsilon", "id", "#make_id_node", "STATEMENTID", "semi", "#make_statement_subtree"],
        "return": ["#push_epsilon", "return", "lpar", "EXPR", "rpar", "semi", "#make_return_subtree"],
        "write": ["#push_epsilon", "write", "lpar", "EXPR", "rpar", "semi", "#make_write_subtree"],
        "read": ["#push_epsilon", "read", "lpar", "VARIABLE", "rpar", "semi", "#make_read_subtree"],
        "while": ["#push_epsilon", "while", "lpar", "RELEXPR", "rpar", "STATBLOCK", "semi", "#make_while_subtree"],
        "if": ["#push_epsilon", "if", "lpar", "RELEXPR", "rpar", "then", "STATBLOCK", "else", "STATBLOCK", "semi", "#make_if_subtree"]
    },
    # Disambiguates statements that start with an id between a var assignment path or a function call path
    "STATEMENTID": {
        "lsqbr": ["REPT_VARIABLE_INDICES", "STATEMENTID_VAR_TAIL"],
        "dot": ["REPT_VARIABLE_INDICES", "STATEMENTID_VAR_TAIL"],
        "lpar": ["lpar", "APARAMS", "rpar", "STATEMENTID_CALL_TAIL"],
        "equal": ["REPT_VARIABLE_INDICES", "STATEMENTID_VAR_TAIL"]
    },
    # Parses rest of variable after a variable identifier statement
    "STATEMENTID_VAR_TAIL": {
        "dot": ["dot", "id", "#make_id_node", "STATEMENTID"],
        "equal": ["ASSIGNOP", "EXPR"]
    },
    # Assignment operator token
    "ASSIGNOP": {
        "equal": ["equal", "#make_assignop_node"]
    },
    # Parses optional member chaining after a function call identifier statement.
    "STATEMENTID_CALL_TAIL": {
        "dot": ["dot", "id", "#make_id_node", "STATEMENTID"],
        "semi": []
    },
    # Parses a single statement block including a do-end block
    "STATBLOCK": {
        "id": ["#push_epsilon", "STATEMENT", "#make_statblock_subtree"],
        "semi": [],
        "return": ["#push_epsilon", "STATEMENT", "#make_statblock_subtree"],
        "write": ["#push_epsilon", "STATEMENT", "#make_statblock_subtree"],
        "read": ["#push_epsilon", "STATEMENT", "#make_statblock_subtree"],
        "while": ["#push_epsilon", "STATEMENT", "#make_statblock_subtree"],
        "else": [],
        "if": ["#push_epsilon", "STATEMENT", "#make_statblock_subtree"],
        "do": ["#push_epsilon", "do", "REPT_STATEMENTS", "end", "#make_statblock_subtree"]
    },
    # Parses zero or more statements inside a do-end block
    "REPT_STATEMENTS": {
       "id": ["STATEMENT", "REPT_STATEMENTS"],
       "return": ["STATEMENT", "REPT_STATEMENTS"],
       "write": ["STATEMENT", "REPT_STATEMENTS"],
       "read": ["STATEMENT", "REPT_STATEMENTS"],
       "while": ["STATEMENT", "REPT_STATEMENTS"],
       "if": ["STATEMENT", "REPT_STATEMENTS"],
       "end": []
    },
    # Parses a relational expression with two arithmetic sides and a relational operator
    "RELEXPR": {
        "minus": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"],
        "plus": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"],
        "id": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"],
        "lpar": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"],
        "not": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"],
        "floatnum": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"],
        "intnum": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"]
    },
    # Matches a relational comparison operator
    "RELOP": {
        "geq": ["geq", "#make_relop_node"],
        "leq": ["leq", "#make_relop_node"],
        "gt": ["gt", "#make_relop_node"],
        "lt": ["lt", "#make_relop_node"],
        "neq": ["neq", "#make_relop_node"],
        "eq": ["eq", "#make_relop_node"]
    },
    # Parses a general expression starting from the expressions first arithmetic expression
    "EXPR": {
        "minus": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"],
        "plus": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"],
        "id": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"],
        "lpar": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"],
        "not": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"],
        "floatnum": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"],
        "intnum": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"]
    },
    # Parses the optional relational continuation of an expression
    "EXPR_REL_TAIL": {
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
    # Parses an arithmetic expression made of terms and extra arithmetic expression tails
    "ARITHEXPR": {
        "minus": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"],
        "plus": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"],
        "id": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"],
        "lpar": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"],
        "not": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"],
        "floatnum": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"],
        "intnum": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"]
    },
    # Parses extra added arithmetic expression tail of an arithmetic expression
    "ARITHEXPR_TAIL": {
        "minus": ["ADDOP", "TERM", "ARITHEXPR_TAIL"],
        "plus": ["ADDOP", "TERM", "ARITHEXPR_TAIL"],
        "or": ["ADDOP", "TERM", "ARITHEXPR_TAIL"],
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
    # Parses a term made of factors and multiplicative tails
    "TERM": {
        "minus": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"],
        "plus": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"],
        "id": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"],
        "lpar": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"],
        "not": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"],
        "floatnum": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"],
        "intnum": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"]
    },
    # Parses the extra multiplicative tail of a term
    "TERM_TAIL": {
        "minus": [],
        "plus": [],
        "and": ["MULTOP", "FACTOR", "TERM_TAIL"],
        "div": ["MULTOP", "FACTOR", "TERM_TAIL"],
        "mult": ["MULTOP", "FACTOR", "TERM_TAIL"],
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
    # Parses an expression unit like numbers, floats, ids, function calls, or parenthesized expressions
    "FACTOR": {
        "minus": ["SIGN", "FACTOR"],
        "plus": ["SIGN", "FACTOR"],
        "id": ["id", "#make_id_node", "FACTORID"],
        "lpar": ["lpar", "ARITHEXPR", "rpar"],
        "not": ["not", "#make_not_node", "FACTOR"],
        "floatnum": ["floatnum", "#make_floatnum_node"],
        "intnum": ["intnum", "#make_intnum_node"]
    },
    # Matches unary plus or unary minus sign
    "SIGN": {
        "minus": ["minus", "#make_minus_node"], #
        "plus": ["plus", "#make_plus_node"] #
    },
    # Matches math operators used between terms in arithmetic expressions
    "ADDOP": {
        "minus": ["minus", "#make_addop_node"],
        "plus": ["plus", "#make_addop_node"],
        "or": ["or", "#make_addop_node"]
    },
    # Matches multiplicative operators used between factors
    "MULTOP": {
        "and": ["and", "#make_multop_node"],
        "div": ["div", "#make_multop_node"],
        "mult": ["mult", "#make_multop_node"]
    },
    # Parses a variable reference starting from an identifier
    "VARIABLE": {
        "id": ["#push_epsilon", "id", "#make_id_node", "VARIABLE_TAIL", "#make_variable_subtree"],
    },
    # Parses the continuation/tail of a variable reference
    "VARIABLE_TAIL": {
        "lsqbr": ["REPT_VARIABLE_INDICES", "VARIABLE_CHAIN_TAIL"],
        "dot": ["REPT_VARIABLE_INDICES", "VARIABLE_CHAIN_TAIL"],
        "rpar": ["REPT_VARIABLE_INDICES", "VARIABLE_CHAIN_TAIL"],
        "lpar": ["lpar", "APARAMS", "rpar", "dot", "id", "#make_id_node", "VARIABLE_TAIL"]
    },
    # Parses variable chaining at the variable tail or closes variable reference
    "VARIABLE_CHAIN_TAIL": {
        "dot": ["dot", "id", "#make_id_node", "VARIABLE_TAIL"],
        "rpar": [],
    },
    # Parses zero or more index operations after a variable reference
    "REPT_VARIABLE_INDICES": {
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
        "lsqbr": ["INDICE", "REPT_VARIABLE_INDICES"],
        "dot": [],
        "rpar": [],
        "equal": [],
        "semi": [],
        "comma": []
    },
    # Parses one array indexing operation '[ expression ]'
    "INDICE": {
        "lsqbr": ["lsqbr", "ARITHEXPR", "rsqbr"]
    },
    # Parses list of arguments in a function call
    "APARAMS": {
        "minus": ["#push_epsilon", "EXPR", "REPT_APARAMS", "#make_aparams_subtree"],
        "plus": ["#push_epsilon", "EXPR", "REPT_APARAMS", "#make_aparams_subtree"],
        "id": ["#push_epsilon", "EXPR", "REPT_APARAMS", "#make_aparams_subtree"],
        "rpar": ["#make_empty_aparams_node"],
        "lpar": ["#push_epsilon", "EXPR", "REPT_APARAMS", "#make_aparams_subtree"],
        "not": ["#push_epsilon", "EXPR", "REPT_APARAMS", "#make_aparams_subtree"],
        "floatnum": ["#push_epsilon", "EXPR", "REPT_APARAMS", "#make_aparams_subtree"],
        "intnum": ["#push_epsilon", "EXPR", "REPT_APARAMS", "#make_aparams_subtree"]
    },
    # Parses zero or more additional arguments of a function call
    "REPT_APARAMS": {
        "rpar": [],
        "comma": ["APARAMSTAIL", "REPT_APARAMS"]
    },
    # Parses an additional function argument separated by commas
    "APARAMSTAIL": {
        "comma": ["comma", "EXPR"]
    },
    # Disambiguates identifier-based factors between variable access and function call forms
    "FACTORID": {
        "minus": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "plus": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "and": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "div": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "mult": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "or": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "geq": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "leq": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "gt": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "lt": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "neq": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "eq": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "rsqbr": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "lsqbr": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "dot": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "rpar": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "lpar": ["lpar", "APARAMS", "rpar", "FACTORID_CALL_TAIL"],
        "semi": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"],
        "comma": ["REPT_VARIABLE_INDICES", "FACTORID_VAR_TAIL"]
    },
    # Parses optional chaining that can follow a variable factor
    "FACTORID_VAR_TAIL": {
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
        "dot": ["dot", "id", "#make_id_node", "FACTORID"],
        "rpar": [],
        "semi": [],
        "comma": []
    },
    # Parses the optional chaining that can follow a function call factor
    "FACTORID_CALL_TAIL": {
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
        "dot": ["dot", "id", "#make_id_node", "FACTORID"],
        "rpar": [],
        "semi": [],
        "comma": []
    }
}
