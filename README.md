# compiler

## Overview

## Developing the lexical analyzer

### 1. Lexical Specifications

This section defines the lexical specification, expressed as regular expressions, that are used in the design of the lexical analyzer.

#### 1.1 Atomic lexical elements of the language 
```text
id       ::= letter alphanum*
integer  ::= nonzero digit* | "0"
float    ::= integer fraction ["e" (+|-) integer]


alphanum ::= letter | digit | "_"
fraction ::= "." digit* nonzero | ".0"
letter   ::= "a".."z" | "A".."Z"
digit    ::= "0".."9"
nonzero  ::= "1".."9"
```

#### 1.2 Operators, punctuation, and reserve words
```text
Operators: ==   <>   <   >   <=   >=   +   -   *   /   =
Punctuation: (   )   {   }   [   ]   ;   ,   .   :   ::
Reserved words: if      do      read    then    end     write   else
                public  return  while   private inherits class   or
                local   integer and     void    float   not     main
```
#### 1.3 Comments
```text
blockcomment  ::= "/*" (any character, including newlines)* "*/"
inlinecomment ::= "//" (any character except newline)*
```

### 2. Finite State Automaton

### 3. Design
(Explain data structures that you've defined like a token, different techniques and algorithms, etc.)

### 4. Use of Tools
(Name tools that we used like regular expression to DFA converter)
Implement a tokenizer funciton for white space as well?
