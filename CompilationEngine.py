"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from JackTokenizer import JackTokenizer

OPERATIONS = {'+', '-', '/', '&', '|', '<', '>', '=', '*'}
UNARY_OPERATIONS = {'-', '~', '#', '^'}
KEYWORD_CONSTANTS = {'true', 'false', 'null', 'this'}

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.tokenizer = input_stream
        self.output_file = output_stream
        self.space_counter = 0

    def compile_class(self) -> None:
        """Compiles a complete class."""

        subroutine_dec = {"function", "method", "constructor"}

        self.output_file.write("<class>\n")  # beginning of file

        # Write class and { and then advance to the class content
        self.output_file.write("<keyword> class </keyword>\n")
        self.tokenizer.advance()
        self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        self.output_file.write("<symbol> { </symbol>\n")
        self.tokenizer.advance()

        # Class variants
        while ((self.tokenizer.token_type() == "KEYWORD") and
               (self.tokenizer.current_token == "static" or (self.tokenizer.current_token == "field"))):
            self.compile_class_var_dec()

        # all func and method in  the class
        while (self.tokenizer.token_type() == "KEYWORD") and (self.tokenizer.current_token in subroutine_dec):
            self.compile_subroutine()

        # the end of the class
        self.output_file.write("<symbol> } </symbol>\n")
        self.tokenizer.advance()  # TODO: check if advance is not empty

        self.output_file.write("</class>\n")  # end of file

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        """- classVarDec: ('static' | 'field') type varName (',' varName)* ';'  """

        self.output_file.write("<classVarDec>\n")

        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")    # ('static' | 'field')
        self.tokenizer.advance()

        if self.tokenizer.token_type() == "KEYWORD":
            self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # type
            self.tokenizer.advance()
        else:
            self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")  # type (object kind)
            self.tokenizer.advance()

        self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")   # # varName
        self.tokenizer.advance()

        while self.tokenizer.current_token == ",":
            self.output_file.write(f"<symbol> , </symbol>\n")
            self.tokenizer.advance()
            self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()

        self.output_file.write(f"<symbol> ; </symbol>\n")
        self.tokenizer.advance()
        self.output_file.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        """ - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody"""

        self.output_file.write("<subroutineDec>\n")
        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # method/func/constructor
        self.tokenizer.advance()

        if self.tokenizer.token_type() == "KEYWORD":
            self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # type
            self.tokenizer.advance()
        else:
            self.output_file.write(
                f"<identifier> {self.tokenizer.identifier()} </identifier>\n")  # type (object kind)
            self.tokenizer.advance()

        self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")  # subroutineName
        self.tokenizer.advance()

        self.output_file.write("<symbol> ( </symbol>\n")  # (
        self.tokenizer.advance()

        self.compile_parameter_list()  # compile the list that is between the () in example: function int getx (x,y,z) it will be x,y,z

        self.output_file.write("<symbol> ) </symbol>\n")  # )
        self.tokenizer.advance()

        # - subroutineBody: '{' varDec* statements '}'
        self.output_file.write("<subroutineBody>\n")
        self.output_file.write("<symbol> { </symbol>\n")  # {
        self.tokenizer.advance()

        self.compile_var_dec()

        self.compile_statements()


        self.output_file.write("<symbol> } </symbol>\n")  # }
        self.output_file.write("</subroutineBody>\n")
        self.tokenizer.advance()

        self.output_file.write("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """

        # - parameterList: ((type varName) (',' type varName)*)?
        # check if empty
        if self.tokenizer.token_type() == "SYMBOL":
            if self.tokenizer.symbol() == ")":
                self.output_file.write("<parameterList>\n"
                                       "</parameterList>\n")
                return
        else:  # not empty
            self.output_file.write("<parameterList>\n")
            self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # type
            self.tokenizer.advance()
            self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")  # varName
            self.tokenizer.advance()

            while self.tokenizer.symbol() == ",":
                self.output_file.write(f"<symbol> , </symbol>\n")
                self.tokenizer.advance()
                self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # type
                self.tokenizer.advance()
                self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
                self.tokenizer.advance()

            self.output_file.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # varDec: 'var' type varName (',' varName)* ';'
        while self.tokenizer.current_token == "var":
            self.output_file.write("<varDec>\n")

            self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")   # write 'var'
            self.tokenizer.advance()

            if self.tokenizer.token_type() == "KEYWORD":
                self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # type
                self.tokenizer.advance()
            else:
                self.output_file.write(
                    f"<identifier> {self.tokenizer.identifier()} </identifier>\n")  # type (object kind)
                self.tokenizer.advance()

            self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")  # write the varName
            self.tokenizer.advance()
            # write all the parameters
            while self.tokenizer.symbol() == ",":
                self.output_file.write(f"<symbol> , </symbol>\n")
                self.tokenizer.advance()
                self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
                self.tokenizer.advance()

            self.output_file.write(f"<symbol> ; </symbol>\n")
            self.tokenizer.advance()
            self.output_file.write("</varDec>\n")


    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        # - statement: letStatement | ifStatement | whileStatement | doStatement |
        #                  returnStatement
        STATEMENTS_KEYS = {'let', 'if', 'while', 'do', 'return'}

        self.output_file.write("<statements>\n")

        while self.tokenizer.token_type() == "KEYWORD":
            if self.tokenizer.keyword() in STATEMENTS_KEYS:
                if self.tokenizer.keyword() == "let":
                    self.compile_let()
                elif self.tokenizer.keyword() == "while":
                    self.compile_while()
                elif self.tokenizer.keyword() == "do":
                    self.compile_do()
                elif self.tokenizer.keyword() == "return":
                    self.compile_return()
                elif self.tokenizer.keyword() == "if":
                    self.compile_if()

        self.output_file.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # - doStatement: 'do' subroutineCall ';'

        self.output_file.write("<doStatement>\n")

        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # do
        self.tokenizer.advance()

        # subroutineCall
        self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        # if we have '.' we add another identifier before :(expressionList)
        if self.tokenizer.current_token == '.':
            self.output_file.write("<symbol> . </symbol>\n")
            self.tokenizer.advance()
            self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()

        self.output_file.write("<symbol> ( </symbol>\n")
        self.tokenizer.advance()
        self.compile_expression_list()
        self.output_file.write("<symbol> ) </symbol>\n")
        self.tokenizer.advance()

        self.output_file.write(f"<symbol> ; </symbol>\n")   # ;
        self.tokenizer.advance()

        self.output_file.write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""

        self.output_file.write("<letStatement>\n")

        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # let
        self.tokenizer.advance()

        self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")  # varName
        self.tokenizer.advance()

        if self.tokenizer.current_token == "[":  # option for [expression]
            self.output_file.write("<symbol> [ </symbol>\n")
            self.tokenizer.advance()
            self.compile_expression()
            self.output_file.write("<symbol> ] </symbol>\n")
            self.tokenizer.advance()

        self.output_file.write("<symbol> = </symbol>\n")  # =
        self.tokenizer.advance()

        self.compile_expression()  # expression

        self.output_file.write(f"<symbol> ; </symbol>\n")   # ;
        self.tokenizer.advance()

        self.output_file.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
        self.output_file.write("<whileStatement>\n")

        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # while
        self.tokenizer.advance()
        self.output_file.write("<symbol> ( </symbol>\n")
        self.tokenizer.advance()
        self.compile_expression()
        self.output_file.write("<symbol> ) </symbol>\n")
        self.tokenizer.advance()
        self.output_file.write("<symbol> { </symbol>\n")
        self.tokenizer.advance()
        self.compile_statements()
        self.output_file.write("<symbol> } </symbol>\n")
        self.tokenizer.advance()

        self.output_file.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output_file.write("<returnStatement>\n")
        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # return
        self.tokenizer.advance()

        if self.tokenizer.current_token != ";":  # check for expression
            self.compile_expression()

        self.output_file.write("<symbol> ; </symbol>\n")  # ;
        self.tokenizer.advance()

        self.output_file.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles an if statement, possibly with a trailing else clause."""
        #  ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
        #                    statements '}')?
        self.output_file.write("<ifStatement>\n")

        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # if
        self.tokenizer.advance()

        self.output_file.write("<symbol> ( </symbol>\n")
        self.tokenizer.advance()
        self.compile_expression()
        self.output_file.write("<symbol> ) </symbol>\n")
        self.tokenizer.advance()

        self.output_file.write("<symbol> { </symbol>\n")
        self.tokenizer.advance()
        self.compile_statements()
        self.output_file.write("<symbol> } </symbol>\n")
        self.tokenizer.advance()

        while self.tokenizer.current_token == "else":

            self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # else
            self.tokenizer.advance()

            self.output_file.write("<symbol> { </symbol>\n")
            self.tokenizer.advance()
            self.compile_statements()
            self.output_file.write("<symbol> } </symbol>\n")
            self.tokenizer.advance()

        self.output_file.write("</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # term (op term)?
        self.output_file.write("<expression>\n")
        self.compile_term()

        if self.tokenizer.current_token in OPERATIONS:
            self.output_file.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
            self.compile_term()

        self.output_file.write("</expression>\n")

    def compile_term(self) -> None:
        """ Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # first check if it's a simple number or string or const keyword
        # then check for the two other recognisable options : (expression) , unaryOp term
        self.output_file.write("<term>\n")
        if self.tokenizer.token_type() == "INT_CONST":
            self.output_file.write(f"<integerConstant> {self.tokenizer.int_val()} </integerConstant>\n")
            self.tokenizer.advance()

        elif self.tokenizer.token_type() == "STRING_CONST":
            self.output_file.write(f"<stringConstant> {self.tokenizer.string_val()} </stringConstant>\n")
            self.tokenizer.advance()

        elif self.tokenizer.current_token in KEYWORD_CONSTANTS:
            self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
            self.tokenizer.advance()

        elif self.tokenizer.current_token == '(':
            self.output_file.write("<symbol> ( </symbol>\n")
            self.tokenizer.advance()
            self.compile_expression()
            self.output_file.write("<symbol> ) </symbol>\n")
            self.tokenizer.advance()

        elif self.tokenizer.current_token in UNARY_OPERATIONS:
            # #(y+3) is an option, so we either get' unaryOp term' or 'unaryOp (expression)'
            self.output_file.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
            if self.tokenizer.current_token == '(':
                self.output_file.write("<term>\n")
                self.output_file.write("<symbol> ( </symbol>\n")
                self.tokenizer.advance()
                self.compile_expression()
                self.output_file.write("<symbol> ) </symbol>\n")
                self.tokenizer.advance()
                self.output_file.write("</term>\n")
            else:
                self.compile_term()

        elif self.tokenizer.token_type() == "IDENTIFIER":
            # keep the current token and advance to check what the next one is
            prev_token = self.tokenizer.current_token
            self.tokenizer.advance()

            if self.tokenizer.current_token == '[':
                self.output_file.write(f"<identifier> {prev_token} </identifier>\n")
                self.output_file.write("<symbol> [ </symbol>\n")
                self.tokenizer.advance()
                self.compile_expression()
                self.output_file.write("<symbol> ] </symbol>\n")
                self.tokenizer.advance()

            elif self.tokenizer.current_token == '(':
                self.output_file.write(f"<identifier> {prev_token} </identifier>\n")
                self.output_file.write("<symbol> ( </symbol>\n")
                self.tokenizer.advance()
                self.compile_expression_list()
                self.output_file.write("<symbol> ) </symbol>\n")
                self.tokenizer.advance()

            elif self.tokenizer.current_token == '.':
                self.output_file.write(f"<identifier> {prev_token} </identifier>\n")
                self.output_file.write("<symbol> . </symbol>\n")
                self.tokenizer.advance()
                self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
                self.tokenizer.advance()
                self.output_file.write("<symbol> ( </symbol>\n")
                self.tokenizer.advance()
                self.compile_expression_list()
                self.output_file.write("<symbol> ) </symbol>\n")
                self.tokenizer.advance()

            else:
                self.output_file.write(f"<identifier> {prev_token} </identifier>\n")
        self.output_file.write("</term>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # if it's empty do nothing
        self.output_file.write("<expressionList>\n")

        if self.tokenizer.current_token == ')':
            self.output_file.write("</expressionList>\n")   #############

            return

        # compile the first expression
        self.compile_expression()


        # while we have commas, compile the expression that comes after
        while self.tokenizer.current_token == ",":
            self.output_file.write("<symbol> , </symbol>\n")
            self.tokenizer.advance()
            self.compile_expression()

        self.output_file.write("</expressionList>\n")
