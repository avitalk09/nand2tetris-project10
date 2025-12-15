"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
#import typing


from JackTokenizer import JackTokenizer



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


    def compile_class(self) -> None:
        """Compiles a complete class."""


        subroutineDec = {"function","method","constructor"}

        # Write class and { and then advance to the class content
        self.output_file.write("<class>\n")
        self.tokenizer.advance()
        self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.output_file.write("<symbol> { </symbol>\n")
        self.tokenizer.advance()


        # Class variants
        while (self.tokenizer.token_type() == "KEYWORD") and\
            (self.tokenizer.current_token == "static" or (self.tokenizer.current_token == "field")):

            self.compile_class_var_dec()


        # # all func and method in  the class
        while (self.tokenizer.token_type == "KEYWORD") and (self.tokenizer.current_token in subroutineDec):
            self.compile_subroutine()

        # the end of the class
        self.output_file.write("<symbol> } </symbol>\n")
        self.tokenizer.advance()
        self.output_file.write("</class>\n")  # TODO: check if advance is not empty


    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        """- classVarDec: ('static' | 'field') type varName (',' varName)* ';'  """

        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")    #('static' | 'field')
        self.tokenizer.advance()

        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")   # type
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


    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        """ - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody"""


        self.output_file.write("<subroutineDec>\n")
        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n") # method/func/constructor
        self.tokenizer.advance()

        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # 'void'/ type
        self.tokenizer.advance()

        self.output_file.write(f"<identifier> {self.tokenizer.identifier()}</identifier>")  # subroutineName
        self.tokenizer.advance()

        self.output_file.write("<symbol> ( </symbol>\n")  #(
        self.tokenizer.advance()

        self.compile_parameter_list()    # compile the list that is between the () in example: function int getx (x,y,z) it will be x,y,z

        self.output_file.write("<symbol> ) </symbol>\n")  # )
        self.tokenizer.advance()


        # - subroutineBody: '{' varDec* statements '}'
        self.output_file.write("<subroutineBody>\n")
        self.output_file.write("<symbol> { </symbol>\n")  # {
        self.tokenizer.advance()

        self.compile_var_dec()


        self.compile_statements()

        self.output_file.write("</subroutineBody>\n")
        self.output_file.write("<symbol> } </symbol>\n")  # }
        self.tokenizer.advance()

        self.output_file.write("</subroutineDec>\n")


    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """

        # - parameterList: ((type varName) (',' type varName)*)?

        #check if empty
        if self.tokenizer.symbol() == ")":
            self.output_file.write("<parameterList>\n"
                                   "</parameterList>\n")
            self.tokenizer.advance()

        else: # not empty
            self.output_file.write("<parameterList>\n")
            self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # type
            self.tokenizer.advance()
            self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")  # varName
            self.tokenizer.advance()

            while self.tokenizer.symbol() == ",":
                self.output_file.write(f"<symbol> , </symbol>\n")
                self.tokenizer.advance()
                self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  #  type
                self.tokenizer.advance()
                self.output_file.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
                self.tokenizer.advance()

            self.output_file.write("</parameterList>\n")
            #self.tokenizer.advance()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # varDec: 'var' type varName (',' varName)* ';'

        self.output_file.write("<varDec>\n")
        while self.tokenizer.current_token == "var":

            self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")   # write 'var'
            self.tokenizer.advance()
            self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")    # write type for example:int/char/list
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
        STATEMENTS_KEYS = {'let','if','while','do','return'}
        self.output_file.write("<statements>\n")

        while self.tokenizer.keyword() in STATEMENTS_KEYS:
            if self.tokenizer.keyword() == "let":
                self.compile_let()
            if self.tokenizer.keyword() == "while":
                self.compile_while()
            if self.tokenizer.keyword() == "do":
                self.compile_do()
            if self.tokenizer.keyword() == "return":
                self.compile_return()
            if self.tokenizer.keyword() == "if":
                self.compile_if()


        self.output_file.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        #     - doStatement: 'do' subroutineCall ';'
        # Your code goes here!
        pass

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        pass

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
        self.output_file.write("<whileStatement>\n")
        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n") # while
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
        # Your code goes here!
        self.output_file.write("<returnStatement>\n")
        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")  # return
        self.tokenizer.advance()

        while self.tokenizer.current_token != ";":
            self.compile_expression()

        self.output_file.write(f"<symbol> ; </symbol>\n")   # ;
        self.tokenizer.advance()

        self.output_file.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles an if statement, possibly with a trailing else clause."""
        #  ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
        #                    statements '}')?
        self.output_file.write("<ifStatement>\n")
        self.output_file.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n") #if
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
        # Your code goes here!
        pass

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        pass

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        pass
