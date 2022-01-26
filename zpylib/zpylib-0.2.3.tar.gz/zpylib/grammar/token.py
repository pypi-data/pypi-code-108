names = ['NAME', 'ZNAME']

operations = ['NUMBER', 'HEX', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
              'EQUALS', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACKET', 'LBRACKET', 'RBRACE', 'DELIMITER', 'COMMENT', 'STRING']

keywords = ['FALSE', 'NONE', 'TRUE', 'AND', 'AS', 'ASSERT', 'ASYNC', 'AWAIT', 'BREAK', 'CLASS', 'CONTINUE', 'DEF', 'DEL', 'ELIF', 'ELSE', 'EXCEPT', 'FINALLY',
            'FOR', 'FROM', 'GLOBAL', 'IF', 'IMPORT', 'IN', 'IS', 'LAMBDA', 'NONLOCAL', 'NOT', 'OR', 'PASS', 'RAISE', 'RETURN', 'SELF', 'TRY', 'WHILE', 'WITH', 'YIELD']

# lexer 需要用到的 token 类型
tokens = tuple(names + operations + keywords)