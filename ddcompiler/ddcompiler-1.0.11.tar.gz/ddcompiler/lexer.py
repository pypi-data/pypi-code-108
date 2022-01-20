from .token import Token, TokenType


class DDLexer:
    END_OF_EXPRESSION = '\0'

    def __init__(self, input):
        # We could strip whitespaces from the input at the front and at the back.
        # But doing so will not correctly report exact character position at which
        # lexical or parsing error occurs if we implement that
        self.expression = input
        self.current_char = ''
        self.current_pos = -1
        self.next_char()
        self.variable_prefixes = ['user', 'conv', 'dialog', 'wf']
        # 'conv.__entities__' and 'conv.__nlu_response__' are not listed here as
        # their type is List[] and Map{} respectively and we don't want people to use
        # them in conditions
        self.system_variables = ['conv.__utterance__', 'conv.__username__', 'conv.__intent__']

    # processes the next character
    def next_char(self):
        self.current_pos += 1
        if self.current_pos < len(self.expression):
            self.current_char = self.expression[self.current_pos]
        else:
            self.current_char = DDLexer.END_OF_EXPRESSION

    # returns the lookahead character
    def peek(self):
        if self.current_pos + 1 < len(self.expression):
            return self.expression[self.current_pos + 1]
        else:
            return DDLexer.END_OF_EXPRESSION

    # error during lexical analysis, raise an error
    def abort(self, message):
        raise ValueError(f"Error during lexical analysis: {message}")

    # in expressions we support, variables have to start with ${ and end with }
    # get_token while parsing a variable already takes care of it and gives XXXX
    # from ${XXXX}
    # validate_variable_name further checks if XXXX is valid
    def validate_variable_name(self, name):
        parts = name.split('.')
        if len(parts) < 2:
            self.abort(f"Invalid variable name {name}, has to be in the form {'prefix'}.name")
        if parts[0] not in self.variable_prefixes:
            self.abort(f"Invalid variable name {name}, allowed prefixes: {self.variable_prefixes}")

        # variables indicatting dialog level state has to have 3 parts
        # dialog.dialog_id.id
        if parts[0] == 'dialog' and len(parts) < 3:
            self.abort(f"Invalid variable name {name}, has to be in the form {'dialog.x.y'}")

        if "__" in name:
            if name not in self.system_variables:
                self.abort(f"Invalid variable name {name}, allowed names with __: {self.system_variables}")

    # returns the next token
    def get_token(self):
        while self.current_char.isspace():
            self.next_char()

        token = None

        if self.current_char == '=':
            if self.peek() == '=':
                lastChar = self.current_char
                self.next_char()
                token = Token(lastChar + self.current_char, TokenType.EQ)
            else:
                self.abort(f"Expected ==, got ={self.peek()}")
        elif self.current_char == '!':
            if self.peek() == '=':
                lastChar = self.current_char
                self.next_char()
                token = Token(lastChar + self.current_char, TokenType.NOTEQ)
            else:
                self.abort(f"Expected !=, got !{self.peek()}")
        elif self.current_char == '<':
            if self.peek() == '=':
                lastChar = self.current_char
                self.next_char()
                token = Token(lastChar + self.current_char, TokenType.LTEQ)
            else:
                token = Token(self.current_char, TokenType.LT)
        elif self.current_char == '>':
            if self.peek() == '=':
                lastChar = self.current_char
                self.next_char()
                token = Token(lastChar + self.current_char, TokenType.GTEQ)
            else:
                token = Token(self.current_char, TokenType.GT)
        elif self.current_char == "\"":
            # Get characters between double quotes
            self.next_char()
            start_pos = self.current_pos
            while self.current_char != "\"":
                self.next_char()
                if self.current_char == DDLexer.END_OF_EXPRESSION:
                    self.abort(f"Incomplete string {self.expression[start_pos:self.current_pos]}")
            text = self.expression[start_pos:self.current_pos]
            token = Token(text, TokenType.STRING)
        elif self.current_char.isdigit():
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits and decimal if there is one.
            start_pos = self.current_pos
            while self.peek().isdigit():
                self.next_char()
            if self.peek() == '.':
                self.next_char()

                # must have at least one digit after decimal
                if not self.peek().isdigit():
                    self.abort("Illegal character in number")
                while self.peek().isdigit():
                    self.next_char()

            text = self.expression[start_pos:self.current_pos + 1]
            token = Token(text, TokenType.NUMBER)
        elif self.current_char == '$':
            # Get the variable name
            start_pos = self.current_pos
            self.next_char()
            if self.current_char != '{':
                self.abort("Expected { after $")

            while self.peek().isalpha() or self.peek().isnumeric() or self.peek() == '_' or self.peek() == '.':
                self.next_char()
            self.next_char()
            if self.current_char != '}':
                self.abort("Expected } after variable name")

            text = self.expression[start_pos+2:self.current_pos]
            self.validate_variable_name(text)
            token = Token(text, TokenType.VARIABLE)
        elif self.current_char.isalpha():
            start_pos = self.current_pos
            while self.peek().isalpha():
                self.next_char()
            text = self.expression[start_pos:self.current_pos + 1]
            token = Token.get_token(text)
        elif self.current_char == '(':
            token = Token('(', TokenType.LPAREN)
        elif self.current_char == ')':
            token = Token(')', TokenType.RPAREN)
        elif self.current_char == ',':
            token = Token(',', TokenType.COMMA)
        elif self.current_char == DDLexer.END_OF_EXPRESSION:
            token = Token('', TokenType.END_OF_EXPRESSION)
        else:
            self.abort(f"Invalid expression starting at {self.current_char}")

        self.next_char()
        return token
