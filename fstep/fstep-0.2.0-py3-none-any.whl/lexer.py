
class Enum1(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

Token = Enum1(['Error',
                'End',
                'Id',
                'Integer',
                'Keyword',
                'Operator',
                'Other',
                ])

class Enum2(set):
    def __getattr__(self, name):
        if (name[0].lower()+name[1:]) in self:
            return (name[0].lower()+name[1:])
        raise AttributeError

Keyword = Enum2(['if',
                'else',
                'return',
                ])

class Enum3(dict):
    def __getattr__(self, name):
        for k,v in self.items():
            if name == v:
                return k
        raise AttributeError

Operator = Enum3({'+':'Add',
                '-':'Sub',
                '*':'Mul',
                '/':'Div',
                '%':'Mod',
                '<':'Less',
                '<=':'LessEq',
                '==':'Eq',
                '!=':'NotEq',
                '&&':'LAnd',
                '||':'LOr',
                '!':'LNot',
                ':=':'Define',
                '=':'Assign',
                })

class Lexer(object):
    
    def __init__(self, f) -> None:
        self.last_char_ = ' '
        self.other_val_ = ''
        self.f = f
        self.id_val_ = ''
        self.key_val_ = ''
        self.int_val_ = ''
        self.op_val_ = ''
        self.line_no_ = 1

    def NextToken(self):
        # // skip spaces
        while not self.eof() and self.isspace(self.last_char_):
            self.NextChar()
        # // end of file
        if self.eof():
            return Token.End
        # // skip comments
        if self.last_char_ == '#':
            return self.HandleComment()
        # // id or keyword
        if self.isalpha(self.last_char_) or self.last_char_ == '_':
            return self.HandleId()
        # // number
        if self.isdigit(self.last_char_):
            return self.HandleInteger()
        # // operator
        if self.IsOperatorChar(self.last_char_):
            return self.HandleOperator()
        # // other characters
        self.other_val_ = self.last_char_
        self.NextChar()
        return Token.Other

    def isalpha(self, chr):
        return (chr <= 'Z' and chr >= 'A') or (chr <= 'z' and chr >= 'a')

    def IsOperatorChar(self, chr):
        return chr in "+-*/%<=!&|:"

    def isdigit(self, chr):
        return chr in '0123456789'

    def isspace(self, chr):
        if chr == '\n':
            self.line_no_ += 1
        return chr in ' \r\n\t'

    def eof(self):
        return self.last_char_ == ''

    def isalnum(self, chr):
        return self.isalpha(chr) or self.isdigit(chr)

    def HandleId(self):
        # // read string
        id = ''
        while True:
            id += self.last_char_
            self.NextChar()
            if not ( not self.eof() and (self.isalnum(self.last_char_) or self.last_char_ == '_')):
                break
        # // check if string is keyword
        if id not in Keyword:
            self.id_val_ = id
            return Token.Id
        else:
            self.key_val_ = id
            return Token.Keyword

    def HandleInteger(self):
        # // read string
        num = ''
        while True:
            num += self.last_char_
            self.NextChar()
            if not ( not self.eof() and (self.isdigit(self.last_char_))):
                break
        # // try to convert to integer
        self.int_val_ = int(num)
        return Token.Integer

    def HandleOperator(self):
        # // read string
        op = ''
        while True:
            op += self.last_char_
            self.NextChar()
            if self.eof() or not self.IsOperatorChar(self.last_char_):
                break
        # // check if operator is valid
        if op in Operator:
            self.op_val_ = op
            return Token.Operator
        else:
            raise Exception(f"invalid operator {op} {self.line_no_} {self.last_char_}")

    def HandleComment(self):
        # // skip the current line
        while not self.eof() and self.last_char_ != '\n' and self.last_char_ != '\r':
            self.NextChar()
        return self.NextToken()

    def HandleEOL(self):
        pass

    def NextChar(self):
        chr = self.f.read(1)
        self.last_char_ = chr

