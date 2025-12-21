"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line's end.

    - 'xxx': quotes are used for tokens that appear verbatim ('terminals').
    - xxx: regular typeface is used for names of language constructs 
           ('non-terminals').
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc.'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        TOKEN_PATTERN = re.compile(
            r'"[^"\n]*"'                # 1. String Constant: Starts with ", captures anything but " or \n, ends with "
            r'|[(){}\[\].,;+\-*/&|<>=~^#]'                # 2. Symbol: Matches any of the required symbols
            r'|\w+'               # 3. Identifiers, Keywords, Integer Constants (letters, digits, underscore)
        )
        # remove comment_starters = ["//", "/*", "/**"]
        input_text = input_stream.read()
        input_text = re.sub(r"/\*\*?.*?\*/", "", input_text, flags=re.DOTALL)
        input_text = re.sub(r"//.*", "", input_text)

        # spilt to lines
        input_lines = input_text.splitlines()
        self.current_token_index = 0
        self.current_token = None
        self.tokens = []
        # temp list of the tokens
        all_tokens = []

        for line in input_lines:
            comment_index = line.find("//")
            if comment_index != -1:
                # if its -1 the index will not be ''//''
                # cut the comment ("//")
                line = line[:comment_index]
            line = line.strip()
            if line:
                # separate lines to tokens
                tokens_on_line = TOKEN_PATTERN.findall(line)
                all_tokens.extend(tokens_on_line)
        self.tokens = all_tokens

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.current_token_index < len(self.tokens)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        if self.has_more_tokens():
            self.current_token = self.tokens[self.current_token_index]
            self.current_token_index += 1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        KEYWORD_SET = {
            'class', 'constructor', 'function', 'method', 'field',
            'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
            'false', 'null', 'this', 'let', 'do', 'if', 'else',
            'while', 'return'
        }
        SYMBOL_SET = {
            '{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
            '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#'
        }
        if self.current_token in KEYWORD_SET:
            return 'KEYWORD'
        if self.current_token in SYMBOL_SET:
            return 'SYMBOL'
        if self.current_token.isdigit():
            return 'INT_CONST'
        if self.current_token[0] == '"' and self.current_token[-1] == '"':
            return 'STRING_CONST'
        return 'IDENTIFIER'

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        if self.token_type() == 'KEYWORD':
            return self.current_token
        else:
            raise ValueError(f"Keyword method called on non-KEYWORD token: {self.current_token}")

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        if self.token_type() == 'SYMBOL':
            if self.current_token == '<':
                return '&lt;'
            elif self.current_token == '>':
                return '&gt;'
            elif self.current_token == '"':
                return '&quot;'
            elif self.current_token == "&":
                return '&amp;'
            else:
                return self.current_token
        else:
            raise ValueError(f"Symbol method called on non-Symbol token: {self.current_token}")

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc.'.
        """
        if self.token_type() == 'IDENTIFIER':
            return self.current_token
        else:
            raise ValueError(f"Identifier method called on non-IDENTIFIER token: {self.current_token}")

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        if self.token_type() == 'INT_CONST':
            return int(self.current_token)
        else:
            raise ValueError(f"Integer value method called on non-INT_CONST token: {self.current_token}")

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        if self.token_type() == 'STRING_CONST':
            string_token = self.current_token[1:-1]
            return string_token
        else:
            raise ValueError(f"String value method called on non-STRING_CONST token: {self.current_token}")
