class STAT(object):
    NORMAL = 0
    COMMENT = 1
    ALPHABET = 2
    NUMBER = 3
    QUTATION = 4
    COLON = 5


class EscapeLiteralSQL(object):
    def __init__(self, sql=''):
        self.substitute = '#'
        self.substitute_num = '#'
        self.substitute_str_mode = False
        self.pos = 0
        self.chars = list(sql)
        self.length = len(self.chars)
        self.parsedSql = ''
        self.param = ''
        self.status = -1
        self.sqlType = 0
    
    def setSubstitute(self, chr):
        self.substitute = chr
        
        if self.substitute_str_mode:
            self.substitute_num = '"' + chr + '"'
        else:
            self.substitute_num = self.substitute
        
        return self
    
    def setSubstituteStringMode(self, b):
        if self.substitute_str_mode == b:
            return self
        
        self.substitute_str_mode = b
        if self.substitute_str_mode:
            self.substitute_num = '"' + self.substitute + '"'
        else:
            self.substitute_num = self.substitute
        return self
    
    def process(self):
        self.status = STAT.NORMAL
        
        for c in self.chars:
            if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                self._number()
            elif c == ':':
                self._colon()
            elif c == '.':
                self._dot()
            elif c == '-':
                self._minus()
            elif c == '/':
                self._slash()
            elif c == '*':
                self._astar()
            elif c in ['\'', '\"']:
                self._quotation()
            else:
                self._others()
                
            self.pos += 1
        
        return self
    
    def _others(self):
        status = self.status
        
        if status == STAT.COMMENT:
            self.parsedSql += self.chars[self.pos]
        elif status == STAT.ALPHABET:
            self.parsedSql += self.chars[self.pos]
            if not self.isProgLetter(self.chars[self.pos]):
                self.status = STAT.NORMAL
        elif status == STAT.NUMBER:
            self.parsedSql += self.chars[self.pos]
            self.status = STAT.NORMAL
        elif status == STAT.QUTATION:
            self.param += self.chars[self.pos]
        else:
            if self.isProgLetter(self.chars[self.pos]):
                self.status = STAT.ALPHABET
                if not self.sqlType:
                    self.define_crud()
            else:
                self.status = STAT.NORMAL
            self.parsedSql += self.chars[self.pos]
    
    def isProgLetter(self, ch):
        return isLetter(ch) or ch == '_'
    
    def define_crud(self):
        self.sqlType = self.chars[self.pos].upper()
        
        if self.sqlType not in ['S', 'D', 'U', 'I']:
            self.sqlType = '*'
    
    def _colon(self):
        status = self.status
        
        if status == STAT.COMMENT:
            self.parsedSql += self.chars[self.pos]
        elif status == STAT.QUTATION:
            self.param += self.chars[self.pos]
        else:
            self.parsedSql += self.chars[self.pos]
            self.status = STAT.COLON
    
    def _quotation(self):
        status = self.status
        
        if status == STAT.NORMAL:
            if len(self.param) > 0:
                self.param += ','
            self.param += self.chars[self.pos]
            self.status = STAT.QUTATION
        elif status == STAT.COMMENT:
            self.parsedSql += self.chars[self.pos]
        elif status == STAT.ALPHABET:
            self.parsedSql += self.chars[self.pos]
            self.status = STAT.QUTATION
        elif status == STAT.NUMBER:
            self.parsedSql += self.chars[self.pos]
            self.status = STAT.QUTATION
        elif status == STAT.QUTATION:
            self.param += '"'
            self.parsedSql = self.parsedSql + '\'' + self.substitute + '\''
            self.status = STAT.NORMAL
    
    def _astar(self):
        status = self.status
        
        if status == STAT.COMMENT:
            self.parsedSql += self.chars[self.pos]
            if self.getNext(self.pos) == '/':
                self.parsedSql += '/'
                self.pos += 1
                self.status = STAT.NORMAL
        elif status == STAT.QUTATION:
            self.param += self.chars[self.pos]
        else:
            self.parsedSql += self.chars[self.pos]
            self.status = STAT.NORMAL
    
    def _slash(self):
        
        status = self.status
        
        if status == STAT.COMMENT:
            self.parsedSql += self.chars[self.pos]
        elif status == STAT.QUTATION:
            self.param += self.chars[self.pos]
        else:
            if self.getNext(self.pos) == '*':
                self.pos += 1
                self.parsedSql += '/*'
                self.status = STAT.COMMENT
    
    def _minus(self):
        
        status = self.status
        
        if status == STAT.COMMENT:
            self.parsedSql += self.chars[self.pos]
        elif status == STAT.QUTATION:
            self.param += self.chars[self.pos]
        else:
            if self.getNext(self.pos) == '-':
                self.parsedSql += self.chars[self.pos]
                while self.chars[self.pos] != '\n':
                    self.pos += 1
                    if self.pos < self.length:
                        self.parsedSql += self.chars[self.pos]
                    else:
                        break
            else:
                self.parsedSql += self.chars[self.pos]
            self.status = STAT.NORMAL
    
    def _dot(self):
        
        status = self.status
        
        if status == STAT.NORMAL:
            self.parsedSql += self.chars[self.pos]
        elif status == STAT.COMMENT:
            self.parsedSql += self.chars[self.pos]
        elif status == STAT.ALPHABET:
            self.parsedSql += self.chars[self.pos]
            self.status = STAT.NORMAL
        elif status == STAT.NUMBER:
            self.param += self.chars[self.pos]
        elif status == STAT.QUTATION:
            self.param += self.chars[self.pos]
    
    def _number(self):
        
        status = self.status
        
        if status == STAT.NORMAL:
            if len(self.param):
                self.param += ','
            self.param += self.chars[self.pos]
            self.parsedSql += self.substitute_num
            self.status = STAT.NUMBER
        elif status in [STAT.COMMENT, STAT.COLON, STAT.ALPHABET]:
            self.parsedSql += self.chars[self.pos]
        elif status in [STAT.NUMBER, STAT.QUTATION]:
            self.param += self.chars[self.pos]
    
    def getNext(self, x):
        return self.chars[x + 1] if x < self.length else 0
    
    def getParsedSql(self):
        return self.parsedSql
    
    def getParameter(self):
        return self.param


ASCII_a = 97
ASCII_z = 122
ASCII_A = 65
ASCII_Z = 90


def isLetter(ch):
    str = ord(ch[0])
    return ((str >= ASCII_a) and (str <= ASCII_z)) or (
        (str >= ASCII_A) and (str <= ASCII_Z))
