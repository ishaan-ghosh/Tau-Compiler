import tau.asts as asts
from tau import tokens, error
from tau.tokens import Span, Coord, Token, punctuation, keywords
import string

class Parser:
    def __init__(self, scanner):
        self.scanner = scanner

    def error(self, msg: str):
        raise Exception(msg + " at " + str(self.scanner.peek()))

    def match(self, kind: str):
        if self.current() == kind:
            return self.scanner.consume()
        else:
            self.error(f"expected {kind}")

    def current(self):
        return self.scanner.peek().kind

    def parse(self):
        v = self._program()
        self.match("EOF")
        return v
    # program -> { func_decl }
    def _program(self):
        _program_ = []
        while self.current() in {'func'}:
            _tmp__program__4509372496 = self._func_decl()
            _program_.append(_tmp__program__4509372496)
        return _program_
    # func_decl -> "func" ID "(" [ param_decl { "," param_decl } ] ")" ":" type compound_stmt
    def _func_decl(self):
        # def __init__(
        #     self,
        #     id: Id,
        #     params: list[ParamDecl],
        #     ret_type_ast: TypeAST,
        #     body: CompoundStmt,
        #     span: Span,
        # ):
        self.match('func')
        funcIdTok = self.match('ID')
        funcID = asts.Id(funcIdTok) 
        self.match('(')
        funcParamDeclList = []
        if self.current() in {'ID'}:
            paramDeclIdTok, paramDeclTypeTok = self._param_decl()
            coord1 = paramDeclIdTok.span.start
            coord2 = paramDeclTypeTok.span.end
            paramDeclSpan = Span(coord1, coord2)
            while self.current() in {','}:
                self.match(',')
                paramDeclIdTok, paramDeclTypeTok = self._param_decl()
        self.match(')')
        self.match(':')
        self._type()
        self._compound_stmt()
        _func_decl_ = None # default?
        return _func_decl_
    # param_decl -> ID ":" type
    def _param_decl(self):
        paramDeclIdTok = self.match('ID')
        self.match(':')
        paramDeclTypeTok = self._type()
        # _param_decl_ = None # default?
        return paramDeclIdTok, paramDeclTypeTok
    # type -> "void" | primitive_type | "[" "]" primitive_type
    def _type(self):
        if self.current() in {'void'}:
            _type_ = self.match('void')
        elif self.current() in {'bool', 'int'}:
            _type_ = self._primitive_type()
        elif self.current() in {'['}:
            self.match('[')
            self.match(']')
            self._primitive_type()
            _type_ = None # default?
        else:
            self.error('syntax error')
            assert False
        return _type_
    # primitive_type -> "int" | "bool"
    def _primitive_type(self):
        if self.current() in {'int'}:
            _primitive_type_ = self.match('int')
        elif self.current() in {'bool'}:
            _primitive_type_ = self.match('bool')
        else:
            self.error('syntax error')
            assert False
        return _primitive_type_
    # array_decl -> "[" [ expression ] "]" primitive_type
    def _array_decl(self):
        self.match('[')
        if self.current() in {'(', '-', 'false', 'not', 'true', 'ID', 'INT'}:
            self._expression()
        self.match(']')
        self._primitive_type()
        _array_decl_ = None # default?
        return _array_decl_
    # array_index -> "[" expression "]"
    def _array_index(self):
        self.match('[')
        self._expression()
        self.match(']')
        _array_index_ = None # default?
        return _array_index_
    # compound_stmt -> "{" { var_decl } { stmt } [ return_stmt ] "}"
    def _compound_stmt(self):
        self.match('{')
        while self.current() in {'var'}:
            self._var_decl()
        while self.current() in {'(', '-', 'call', 'false', 'if', 'not', 'print', 'true', 'while', '{', 'ID', 'INT'}:
            self._stmt()
        if self.current() in {'return'}:
            self._return_stmt()
        self.match('}')
        _compound_stmt_ = None # default?
        return _compound_stmt_
    # var_decl -> "var" ID ":" ([ expression ] primitive_type | array_decl)
    def _var_decl(self):
        self.match('var')
        self.match('ID')
        self.match(':')
        if self.current() in {'(', '-', 'bool', 'false', 'int', 'not', 'true', 'ID', 'INT'}:
            if self.current() in {'(', '-', 'false', 'not', 'true', 'ID', 'INT'}:
                self._expression()
            self._primitive_type()
        elif self.current() in {'['}:
            self._array_decl()
        else:
            self.error('syntax error')
            assert False
        _var_decl_ = None # default?
        return _var_decl_
    # stmt -> compound_stmt | if_stmt | while_stmt | assign_stmt | call_stmt | print_stmt
    def _stmt(self):
        if self.current() in {'{'}:
            _stmt_ = self._compound_stmt()
        elif self.current() in {'if'}:
            _stmt_ = self._if_stmt()
        elif self.current() in {'while'}:
            _stmt_ = self._while_stmt()
        elif self.current() in {'(', '-', 'false', 'not', 'true', 'ID', 'INT'}:
            _stmt_ = self._assign_stmt()
        elif self.current() in {'call'}:
            _stmt_ = self._call_stmt()
        elif self.current() in {'print'}:
            _stmt_ = self._print_stmt()
        else:
            self.error('syntax error')
            assert False
        return _stmt_
    # if_stmt -> "if" expression compound_stmt [ "else" stmt ]
    def _if_stmt(self):
        self.match('if')
        self._expression()
        self._compound_stmt()
        if self.current() in {'else'}:
            self.match('else')
            self._stmt()
        _if_stmt_ = None # default?
        return _if_stmt_
    # while_stmt -> "while" expression compound_stmt
    def _while_stmt(self):
        self.match('while')
        self._expression()
        self._compound_stmt()
        _while_stmt_ = None # default?
        return _while_stmt_
    # assign_stmt -> expression "=" expression
    def _assign_stmt(self):
        self._expression()
        self.match('=')
        self._expression()
        _assign_stmt_ = None # default?
        return _assign_stmt_
    # return_stmt -> "return" [ expression ]
    def _return_stmt(self):
        self.match('return')
        if self.current() in {'(', '-', 'false', 'not', 'true', 'ID', 'INT'}:
            self._expression()
        _return_stmt_ = None # default?
        return _return_stmt_
    # call_stmt -> "call" ID func_expr
    def _call_stmt(self):
        self.match('call')
        self.match('ID')
        self._func_expr()
        _call_stmt_ = None # default?
        return _call_stmt_
    # func_expr -> argument_list
    def _func_expr(self):
        _func_expr_ = self._argument_list()
        return _func_expr_
    # print_stmt -> "print" expression
    def _print_stmt(self):
        self.match('print')
        self._expression()
        _print_stmt_ = None # default?
        return _print_stmt_
    # argument_list -> "(" [ expression { "," expression } ] ")"
    def _argument_list(self):
        self.match('(')
        if self.current() in {'(', '-', 'false', 'not', 'true', 'ID', 'INT'}:
            self._expression()
            while self.current() in {','}:
                self.match(',')
                self._expression()
        self.match(')')
        _argument_list_ = None # default?
        return _argument_list_
    # expression -> or_expr { "or" or_expr }
    def _expression(self):
        self._or_expr()
        while self.current() in {'or'}:
            self.match('or')
            self._or_expr()
        _expression_ = None # default?
        return _expression_
    # or_expr -> and_expr { "and" and_expr }
    def _or_expr(self):
        self._and_expr()
        while self.current() in {'and'}:
            self.match('and')
            self._and_expr()
        _or_expr_ = None # default?
        return _or_expr_
    # and_expr -> relational_expr { ("==" | "!=" | "<" | "<=" | ">" | ">=") relational_expr }
    def _and_expr(self):
        self._relational_expr()
        while self.current() in {'!=', '<', '<=', '==', '>', '>='}:
            if self.current() in {'=='}:
                self.match('==')
            elif self.current() in {'!='}:
                self.match('!=')
            elif self.current() in {'<'}:
                self.match('<')
            elif self.current() in {'<='}:
                self.match('<=')
            elif self.current() in {'>'}:
                self.match('>')
            elif self.current() in {'>='}:
                self.match('>=')
            else:
                self.error('syntax error')
                assert False
            self._relational_expr()
        _and_expr_ = None # default?
        return _and_expr_
    # relational_expr -> additive_expr { ("+" | "-") additive_expr }
    def _relational_expr(self):
        self._additive_expr()
        # AMBIGUOUS lookahead(s): {'"-"'}
        while self.current() in {'+', '-'}:
            if self.current() in {'+'}:
                self.match('+')
            elif self.current() in {'-'}:
                self.match('-')
            else:
                self.error('syntax error')
                assert False
            self._additive_expr()
        _relational_expr_ = None # default?
        return _relational_expr_
    # additive_expr -> multiplicative_expr { ("*" | "/") multiplicative_expr }
    def _additive_expr(self):
        self._multiplicative_expr()
        while self.current() in {'*', '/'}:
            if self.current() in {'*'}:
                self.match('*')
            elif self.current() in {'/'}:
                self.match('/')
            else:
                self.error('syntax error')
                assert False
            self._multiplicative_expr()
        _additive_expr_ = None # default?
        return _additive_expr_
    # multiplicative_expr -> { ("-" | "not") } primary_expr
    def _multiplicative_expr(self):
        while self.current() in {'-', 'not'}:
            if self.current() in {'-'}:
                self.match('-')
            elif self.current() in {'not'}:
                self.match('not')
            else:
                self.error('syntax error')
                assert False
        self._primary_expr()
        _multiplicative_expr_ = None # default?
        return _multiplicative_expr_
    # primary_expr -> INT | bool_literal | "(" expression ")" | ID [ func_expr | array_index ]
    def _primary_expr(self):
        if self.current() in {'INT'}:
            _primary_expr_ = self.match('INT')
        elif self.current() in {'false', 'true'}:
            _primary_expr_ = self._bool_literal()
        elif self.current() in {'('}:
            self.match('(')
            self._expression()
            self.match(')')
            _primary_expr_ = None # default?
        elif self.current() in {'ID'}:
            self.match('ID')
            # AMBIGUOUS lookahead(s): {'"("'}
            if self.current() in {'(', '['}:
                if self.current() in {'('}:
                    self._func_expr()
                elif self.current() in {'['}:
                    self._array_index()
                else:
                    self.error('syntax error')
                    assert False
            _primary_expr_ = None # default?
        else:
            self.error('syntax error')
            assert False
        return _primary_expr_
    # bool_literal -> "true" | "false"
    def _bool_literal(self):
        if self.current() in {'true'}:
            _bool_literal_ = self.match('true')
        elif self.current() in {'false'}:
            _bool_literal_ = self.match('false')
        else:
            self.error('syntax error')
            assert False
        return _bool_literal_
