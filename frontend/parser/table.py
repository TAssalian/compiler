table = {
    # used when parsing the start symbol of the program
    "START": {
        "id": ["PROG", "#make_start_subtree"],
        "class": ["PROG", "#make_start_subtree"],
        "main": ["PROG", "#make_start_subtree"]
    },
    # used when parsing the full program: class declarations, function definitions, and main body
    "PROG": {
        "id": ["#push_epsilon", "REPT_CLASSDECLS", "REPT_FUNCDEFS", "main", "FUNCBODY", "#make_prog_subtree"],
        "class": ["#push_epsilon", "REPT_CLASSDECLS", "REPT_FUNCDEFS", "main", "FUNCBODY", "#make_prog_subtree"],
        "main": ["#push_epsilon", "REPT_CLASSDECLS", "REPT_FUNCDEFS", "main", "FUNCBODY", "#make_prog_subtree"]
    },
    
    
    #
    # Class part of the program
    #
    # used when parsing zero or more class declarations
    "REPT_CLASSDECLS": {
        "id": [],
        "class": ["CLASSDECL", "REPT_CLASSDECLS"],
        "main": []
    },
    # used when parsing one class declaration with members
    "CLASSDECL": {
        "class": ["class", "#push_epsilon", "id", "#make_id_node", "OPTCLASSDECL2", "lcurbr", "REPT_CLASS_MEMBERS", "rcurbr", "semi", "#make_classdecl_subtree"]
    },
    # used when parsing an optional inherits clause in a class declaration
    "OPTCLASSDECL2": {
        "inherits": ["inherits", "id", "#make_id_node", "#make_inherits_subtree", "REPT_INHERITS_TAIL"],
        "lcurbr": []
    },
    # used when parsing additional inherited class names after inherits
    "REPT_INHERITS_TAIL": {
        "comma": ["comma", "id", "#make_id_node", "#make_inherits_subtree", "REPT_INHERITS_TAIL"],
        "lcurbr": []
    },
    # used when parsing zero or more class member declarations
    "REPT_CLASS_MEMBERS": {
        "private": ["VISIBILITY", "MEMBERDECL", "REPT_CLASS_MEMBERS"],
        "public": ["VISIBILITY", "MEMBERDECL", "REPT_CLASS_MEMBERS"],
        "rcurbr": []
    },
    # used when parsing a class member visibility modifier
    "VISIBILITY": {
        "private": ["private", "#make_private_node"],
        "public": ["public", "#make_public_node"]
    },
    # used when parsing a class member declaration
    "MEMBERDECL": {
        "id": ["id", "#make_id_node", "MEMBERDECL_DISAMBIG"],
        "float": ["TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_VARDECL_DIMS", "#make_arraysize_subtree", "semi", "#make_vardecl_subtree"],
        "integer": ["TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_VARDECL_DIMS", "#make_arraysize_subtree", "semi", "#make_vardecl_subtree"]
    },
    # used when deciding whether an id-starting member is a variable or function declaration
    "MEMBERDECL_DISAMBIG": {
        "id": ["id", "#make_id_node", "#push_epsilon", "REPT_VARDECL_DIMS", "#make_arraysize_subtree", "semi", "#make_member_vardecl_subtree"],
        "lpar": ["lpar", "FPARAMS", "rpar", "colon", "RETTYPE", "semi", "#make_member_funcdecl_subtree"]
    },
    
    
    #
    # Function definition part of the program
    #
    # used when parsing zero or more function definitions
    "REPT_FUNCDEFS": {
        "id": ["FUNCDEF", "REPT_FUNCDEFS"],
        "main": []
    },
    # used when parsing a full function definition
    "FUNCDEF": {
        "id": ["#push_epsilon", "FUNCHEAD", "FUNCBODY", "semi", "#make_funcdef_subtree"],
    },
    # used when parsing the start of a function header
    "FUNCHEAD": {
        "id": ["id", "#make_id_node", "FUNCHEAD_TAIL"]
    },
    # used when parsing the rest of a function header
    "FUNCHEAD_TAIL": {
        "lpar": ["lpar", "FPARAMS", "rpar", "colon", "RETTYPE"],
        "sr": ["sr", "id", "#make_id_node", "lpar", "FPARAMS", "rpar", "colon", "RETTYPE"]
    },
    # used when parsing a function return type
    "RETTYPE": {
        "id": ["TYPE"],
        "float": ["TYPE"],
        "integer": ["TYPE"],
        "void": ["void", "#make_void_type_node"]
    },
    # used when parsing a type token
    "TYPE": {
        "id": ["id", "#make_type_node"],
        "float": ["float", "#make_type_node"],
        "integer": ["integer", "#make_type_node"]
    },
    # used when parsing a function parameter list in the function header
    "FPARAMS": {
        "id": ["#push_epsilon", "TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_FPARAM_DIMS", "#make_arraysize_subtree", "#make_fparam_subtree", "REPT_FPARAMS", "#make_fparams_subtree"],
        "float": ["#push_epsilon", "TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_FPARAM_DIMS", "#make_arraysize_subtree", "#make_fparam_subtree", "REPT_FPARAMS", "#make_fparams_subtree"],
        "integer": ["#push_epsilon", "TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_FPARAM_DIMS", "#make_arraysize_subtree", "#make_fparam_subtree", "REPT_FPARAMS", "#make_fparams_subtree"],
        "rpar": ["#make_empty_fparams_node"]
    },
    # used when parsing zero or more array dimensions on a parameter
    "REPT_FPARAM_DIMS": {
        "lsqbr": ["ARRAYSIZE", "REPT_FPARAM_DIMS"],
        "rpar": [],
        "comma": []
    },
    # used when we want to parse additional function parameters after the first one in the function header
    "REPT_FPARAMS": {
        "rpar": [],
        "comma": ["FPARAMSTAIL", "REPT_FPARAMS"]
    },
    # used when parsing a single additional function parameter that's in the function header
    "FPARAMSTAIL": {
        "comma": ["comma", "TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_FPARAMTAIL_DIMS", "#make_arraysize_subtree", "#make_fparam_subtree"]
    },
    # used when parsing array dimensions on a trailing function parameter
    "REPT_FPARAMTAIL_DIMS": {
        "lsqbr": ["ARRAYSIZE", "REPT_FPARAMTAIL_DIMS"],
        "rpar": [],
        "comma": []
    },
    # used when parsing one array dimension
    "ARRAYSIZE": {
        "lsqbr": ["lsqbr", "ARRAYSIZE_BOUND"]
    },
    # used when parsing the optional bound inside one array dimension
    "ARRAYSIZE_BOUND": {
        "rsqbr": ["#make_empty_dimension_marker", "rsqbr"],
        "intnum": ["intnum", "#make_intnum_node", "rsqbr"]
    },
    
    #
    # Main program
    #
    # used when parsing a function body
    "FUNCBODY": {
        "do": ["#push_epsilon", "OPTFUNCBODY0", "do", "REPT_FUNCBODY_STATEMENTS", "end", "#make_funcbody_subtree"],
        "local": ["#push_epsilon", "OPTFUNCBODY0", "do", "REPT_FUNCBODY_STATEMENTS", "end", "#make_funcbody_subtree"]
    },
    # used when parsing the optional local declaration section in a function body
    "OPTFUNCBODY0": {
        "do": [],
        "local": ["local", "REPT_LOCAL_VARDECLS"]
    },
    # used when parsing zero or more local variable declarations
    "REPT_LOCAL_VARDECLS": {
        "id": ["VARDECL", "REPT_LOCAL_VARDECLS"],
        "float": ["VARDECL", "REPT_LOCAL_VARDECLS"],
        "integer": ["VARDECL", "REPT_LOCAL_VARDECLS"],
        "do": []
    },
    # used when parsing one variable declaration
    "VARDECL": {
        "id": ["TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_VARDECL_DIMS", "#make_arraysize_subtree", "semi", "#make_vardecl_subtree"],
        "float": ["TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_VARDECL_DIMS", "#make_arraysize_subtree", "semi", "#make_vardecl_subtree"],
        "integer": ["TYPE", "id", "#make_id_node", "#push_epsilon", "REPT_VARDECL_DIMS", "#make_arraysize_subtree", "semi", "#make_vardecl_subtree"]
    },
    # used when parsing zero or more array dimensions in a variable declaration
    "REPT_VARDECL_DIMS": {
        "lsqbr": ["ARRAYSIZE", "REPT_VARDECL_DIMS"],
        "semi": [],
    },
    # used when parsing zero or more statements in a function body do-end block
    "REPT_FUNCBODY_STATEMENTS": {
        "id": ["STATEMENT", "REPT_FUNCBODY_STATEMENTS"],
        "return": ["STATEMENT", "REPT_FUNCBODY_STATEMENTS"],
        "write": ["STATEMENT", "REPT_FUNCBODY_STATEMENTS"],
        "read": ["STATEMENT", "REPT_FUNCBODY_STATEMENTS"],
        "while": ["STATEMENT", "REPT_FUNCBODY_STATEMENTS"],
        "if": ["STATEMENT", "REPT_FUNCBODY_STATEMENTS"],
        "end": []
    },
    # used when parsing one statement
    "STATEMENT": {
        "id": ["#push_epsilon", "id", "#make_id_node", "STATEMENTID", "semi", "#make_statement_subtree"],
        "return": ["#push_epsilon", "return", "lpar", "EXPR", "rpar", "semi", "#make_return_subtree"],
        "write": ["#push_epsilon", "write", "lpar", "EXPR", "rpar", "semi", "#make_write_subtree"],
        "read": ["#push_epsilon", "read", "lpar", "VARIABLE", "rpar", "semi", "#make_read_subtree"],
        "while": ["#push_epsilon", "while", "lpar", "RELEXPR", "rpar", "STATBLOCK", "semi", "#make_while_subtree"],
        "if": ["#push_epsilon", "if", "lpar", "RELEXPR", "rpar", "then", "STATBLOCK", "else", "STATBLOCK", "semi", "#make_if_subtree"]
    },
    # used when deciding whether an id-starting statement is assignment/variable access or function call
    "STATEMENTID": {
        "lsqbr": ["REPT_VARIABLE_INDICES", "STATEMENTID_VAR_TAIL"],
        "dot": ["REPT_VARIABLE_INDICES", "STATEMENTID_VAR_TAIL"],
        "lpar": ["lpar", "APARAMS", "rpar", "STATEMENTID_CALL_TAIL"],
        "equal": ["REPT_VARIABLE_INDICES", "STATEMENTID_VAR_TAIL"]
    },
    # used when parsing the variable tail in an id-starting statement
    "STATEMENTID_VAR_TAIL": {
        "dot": ["dot", "id", "#make_id_node", "STATEMENTID"],
        "equal": ["ASSIGNOP", "EXPR"]
    },
    # used when parsing an assignment operator
    "ASSIGNOP": {
        "equal": ["equal", "#make_assignop_node"]
    },
    # used when parsing optional chaining after a function call in a statement
    "STATEMENTID_CALL_TAIL": {
        "dot": ["dot", "id", "#make_id_node", "STATEMENTID"],
        "semi": []
    },
    # used when parsing a statement block
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
    # used when parsing zero or more statements in a do-end block
    "REPT_STATEMENTS": {
       "id": ["STATEMENT", "REPT_STATEMENTS"],
       "return": ["STATEMENT", "REPT_STATEMENTS"],
       "write": ["STATEMENT", "REPT_STATEMENTS"],
       "read": ["STATEMENT", "REPT_STATEMENTS"],
       "while": ["STATEMENT", "REPT_STATEMENTS"],
       "if": ["STATEMENT", "REPT_STATEMENTS"],
       "end": []
    },
    # used when parsing a relational expression
    "RELEXPR": {
        "minus": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"],
        "plus": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"],
        "id": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"],
        "lpar": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"],
        "not": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"],
        "floatnum": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"],
        "intnum": ["#push_epsilon", "ARITHEXPR", "RELOP", "ARITHEXPR", "#make_relexpr_subtree"]
    },
    # used when parsing a relational operator
    "RELOP": {
        "geq": ["geq", "#make_relop_node"],
        "leq": ["leq", "#make_relop_node"],
        "gt": ["gt", "#make_relop_node"],
        "lt": ["lt", "#make_relop_node"],
        "neq": ["neq", "#make_relop_node"],
        "eq": ["eq", "#make_relop_node"]
    },
    # used when parsing an expression
    "EXPR": {
        "minus": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"],
        "plus": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"],
        "id": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"],
        "lpar": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"],
        "not": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"],
        "floatnum": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"],
        "intnum": ["#push_epsilon", "ARITHEXPR", "EXPR_REL_TAIL", "#make_expr_subtree"]
    },
    # used when parsing the optional relational tail of an expression
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
    # used when parsing an arithmetic expression
    "ARITHEXPR": {
        "minus": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"],
        "plus": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"],
        "id": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"],
        "lpar": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"],
        "not": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"],
        "floatnum": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"],
        "intnum": ["#push_epsilon", "TERM", "ARITHEXPR_TAIL", "#make_arithexpr_subtree"]
    },
    # used when parsing the tail of an arithmetic expression
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
    # used when parsing a term. a term is factors joined by *, /, and
    "TERM": {
        "minus": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"],
        "plus": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"],
        "id": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"],
        "lpar": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"],
        "not": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"],
        "floatnum": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"],
        "intnum": ["#push_epsilon", "FACTOR", "TERM_TAIL", "#make_term_subtree"]
    },
    # used when parsing the multiplicative tail of a term
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
    # used when parsing a factor. a factor is a single unit like 2, x, -x
    "FACTOR": {
        "minus": ["SIGN", "FACTOR"],
        "plus": ["SIGN", "FACTOR"],
        "id": ["id", "#make_id_node", "FACTORID"],
        "lpar": ["lpar", "ARITHEXPR", "rpar"],
        "not": ["not", "#make_not_node", "FACTOR"],
        "floatnum": ["floatnum", "#make_floatnum_node"],
        "intnum": ["intnum", "#make_intnum_node"]
    },
    # used when parsing a unary sign
    "SIGN": {
        "minus": ["minus", "#make_minus_node"],
        "plus": ["plus", "#make_plus_node"]
    },
    # used when parsing an additive operator
    "ADDOP": {
        "minus": ["minus", "#make_addop_node"],
        "plus": ["plus", "#make_addop_node"],
        "or": ["or", "#make_addop_node"]
    },
    # used when parsing a multiplicative operator
    "MULTOP": {
        "and": ["and", "#make_multop_node"],
        "div": ["div", "#make_multop_node"],
        "mult": ["mult", "#make_multop_node"]
    },
    # used when parsing a variable reference
    "VARIABLE": {
        "id": ["#push_epsilon", "id", "#make_id_node", "VARIABLE_TAIL", "#make_variable_subtree"],
    },
    # used when parsing the tail of a variable reference
    "VARIABLE_TAIL": {
        "lsqbr": ["REPT_VARIABLE_INDICES", "VARIABLE_CHAIN_TAIL"],
        "dot": ["REPT_VARIABLE_INDICES", "VARIABLE_CHAIN_TAIL"],
        "rpar": ["REPT_VARIABLE_INDICES", "VARIABLE_CHAIN_TAIL"],
        "lpar": ["lpar", "APARAMS", "rpar", "dot", "id", "#make_id_node", "VARIABLE_TAIL"]
    },
    # used when parsing variable chaining or ending a variable reference
    "VARIABLE_CHAIN_TAIL": {
        "dot": ["dot", "id", "#make_id_node", "VARIABLE_TAIL"],
        "rpar": [],
    },
    # used when parsing zero or more index operations on a variable
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
    # used when parsing one array index operation
    "INDICE": {
        "lsqbr": ["lsqbr", "#push_epsilon", "ARITHEXPR", "rsqbr", "#make_index_subtree"]
    },
    # used when parsing actual parameters in a function call
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
    # used when parsing additional actual parameters in a function call
    "REPT_APARAMS": {
        "rpar": [],
        "comma": ["APARAMSTAIL", "REPT_APARAMS"]
    },
    # used when parsing one trailing actual parameter in a function call after a comma
    "APARAMSTAIL": {
        "comma": ["comma", "EXPR"]
    },
    # used when deciding what comes after id in FACTOR, is it a variable or a function call
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
    # used when parsing optional chaining after a variable factor
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
    # used when parsing optional chaining after a function call factor
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
