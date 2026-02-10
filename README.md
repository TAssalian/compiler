# compiler

## Overview

## Usage

### Requirements
- **Python 3.10+**

---

### Run on a single `.src` file

```bash
python3 lexdriver.py path/to/file.src
```

This generates 3 output files in the **same folder as the input file**:

- `file.outlextokens` — token list (format: `[type, lexeme, line]`)
- `file.outlextokensflaci` — token stream formatted for Flaci
- `file.outlexerrors` — lexical error log

---

### Run on a directory of `.src` files

```bash
python3 lexdriver.py path/to/folder/
```

The driver scans every `*.src` file in the directory and generates the 3 output files for each source file.

---

## Developing the lexical analyzer

### 1. Lexical Specifications

This section defines the lexical specification, expressed as regular expressions, that are used in the design of the lexical analyzer.

#### 1.1 Atomic lexical elements of the language 
```text
id       ::= letter alphanum*
integer  ::= nonzero digit* | "0"
float    ::= integer fraction ["e" [+|-] integer]


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

### 2. Design

The lexer is split into three modules: **token definitions**, the **scanner**, and the **CLI driver**.

#### `tokens.py`
Defines the data structures returned by the lexer.

- **`TokenType`**: enum of all token categories (keywords, operators, punctuation, numeric literals, invalid types).
- **`Token`**: value object containing:
  - `type` (token category)
  - `lexeme` (raw substring from the source code)
  - `line` (starting line number)

Output formatting is centralized in `Token` to keep results consistent:
- `to_outtokens()` → `[type, lexeme, line]`
- `to_flaci()` → token stream label
- `to_outerrs()` → lexical error message format

---

#### `lexer.py`
Implements lexical scanning.

The lexer reads the input character-by-character and produces tokens using deterministic rules:
- identifiers and reserved words
- integers and floats
- operators and punctuation (including multi-character tokens via lookahead)
- inline and block comments
- invalid lexemes as error tokens

Invalid inputs generate error tokens **without stopping the scan**, ensuring complete output files are produced.

---

#### `lexdriver.py`
Command-line entry point.

- Accepts either a `.src` file or a directory containing `.src` files
- Runs the lexer on each file
- Writes the required outputs per source file:
  - `*.outlextokens`
  - `*.outlextokensflaci`
  - `*.outlexerrors`

---

### 3. Tools and Implementation Notes

- **`Enum`** is used for token types to enforce consistent categories.
- **`@dataclass`** is used for token objects to store structured output cleanly and reduce boilerplate code.
- **`pathlib`** is used for convenient cross-platform file and directory handling.
- **Error recovery** is implemented by emitting invalid token categories instead of halting on the first error.
