import os


class Token:
	def __init__(self, type, line, value=None, file='stdin', pos=0, tab=0):
		self.type = type
		self.line = line
		self.value = value
		self.line_num = 0
		self.pos = pos
		self.tab = tab
		self.name = '[module]'

		if file == 'stdin':
			self.file = file
		else:
			self.file = os.path.abspath(file)

	def __repr__(self):
		return f'{self.type} {self.value} {self.line}'

class Lexer:
	def __init__(self, code, file='stdin'):
		self.code = code
		self.file = file
		self.pos = -1
		self.lin_pos = 0
		self.tab = 0
		self.tok = None
		self.next()
		self.tokenizer()

	def next(self):
		self.pos += 1

		if self.tok == '\n':
			self.lin_pos = 0
			self.tab = 0
			self.line_num += 1
		elif self.tok == '\t':
			self.tab = self.lin_pos + 4

		if self.pos < len(self.code):
			self.tok = self.code[self.pos]
			self.lin_pos += 1
		else:
			self.tok = None

	def pre(self):
		self.pos -= 1
		self.tok = self.code[self.pos]

	def syntaxError(self, log):
		print(f"  File '{os.path.abspath(self.file)}', line {self.line_num}")

		linez = self.code.split('\n')
		print(f"    {linez[self.line_num-1].strip(' ')}")

		print(' ' * (self.lin_pos + 1), '^')
		print(f'SyntaxError: ' + log)
		quit()

	def getstring(self):
		escapes = {'n':'\n', 'b':'\b', 't':'\t', 'r':'\r', '\\': '\\'}
		
		if self.tok in ['"', "'"]:
			master = self.tok
			string = ''
			self.next()
			while self.tok not in [master, '\n', None]:
				if self.tok == '\\':
					self.next()
					if self.tok == master:
						string += master
						self.next()
					else:
						if self.tok in ['n', 'b', 't', 'r', '\\']:
							string += escapes[self.tok]
							self.next()
						else:
							string += escapes['\\'] * 1

				elif self.tok == master:
					pass
				else:
					string += self.tok
					self.next()

			if self.tok == master:
				self.next()

				while self.tok == ' ':
					self.next()

				if self.tok != None:
					if self.tok != 'a' and self.tok in self.letters or self.tok in '(' + self.numbers:
						if self.tok == '(':
							self.next()
							self.syntaxError("'str' object not capable." )
						else:
							self.next()
							self.syntaxError('Invalid syntax')
					else:
						return string
				else:
					return string
			else:
				self.syntaxError('EOL while collecting string.')

	def tokenizer(self):
		if True:
			self.line_num = 1
			self.numbers = '0123456789'
			self.letters = 'abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ$'
			numbers = '0123456789'
			letters = 'abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ$'
			delimeters = ['(', ')', '{', '}', '[', ']']
			symbols = '=+-/*%'
			equality = '<>!'
			tokens = []
			escapes = {'n':'\n', 'b':'\b', 't':'\t', 'r':'\r', '\\': '\\'}

		while self.tok != None:

			if self.tok == ' ':
				space = 1
				self.next()

				while self.tok == ' ':
					space += 1
					self.next()

					if space == 4:
						break

				if space == 4:
					self.tab = self.lin_pos
				else:
					pass
					
			elif self.tok in ['"', "'"]:
				master = self.tok
				string = ''
				self.next()
				while self.tok not in [master, None, '\n']:
					if self.tok == '\\':
						self.next()
						if self.tok == master:
							string += master
							self.next()
						else:
							if self.tok in ['n', 'b', 't', 'r', '\\']:
								string += escapes[self.tok]
								self.next()
							else:
								string += escapes['\\'] * 1

					elif self.tok == master:
						pass
					else:
						string += self.tok
						self.next()


				if self.tok == master:
					self.next()

					while self.tok == ' ':
						self.next()

					if self.tok and self.tok != 'a' and self.tok in letters or self.tok in '(' + numbers:
						if self.tok == '(':
							self.next()
							self.syntaxError("'str' object not capable." )
						else:
							self.next()
							self.syntaxError('Invalid syntax')
					else:
						tokens.append(Token('STRING', self.line_num, string, self.file, self.lin_pos, self.tab))
				else:
					self.syntaxError('EOL while collecting string.')

			elif self.tok in letters:
				value = ''
				orbit = None

				while self.tok and self.tok in letters + '1234567890':
					value += self.tok
					self.next()
				
				if value in ['f', 'r', 'b']:
					if self.tok in ['"', "'"]:
						string_ = self.getstring()
						if value == 'r':
							string_ = r'%r' %string_

							if string_.startswith("'"):
								string_ = string_.strip("'")
							else:
								string_ = string_.strip('"')

							tokens.append(Token('STRING', self.line_num, string_, self.file, self.lin_pos, self.tab))
						
						elif value == 'f':
							tokens.append(Token('FORMAT', self.line_num, string_, self.file, self.lin_pos, self.tab))
						elif value == 'b':
							tokens.append(Token('STRING', self.line_num, string_.encode(), self.file, self.lin_pos, self.tab))
					else:
						tokens.append(Token('IDENTIFIER', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'let'  or value == 'var':
					tokens.append(Token('LET', self.line_num, value, self.file, self.lin_pos, self.tab))
					orbit = 'ident'
				
				elif value == 'if':
					tokens.append(Token('IF', self.line_num, value, self.file, self.lin_pos, self.tab))
				
				elif value == 'else':
					while self.tok != None and self.tok == ' ':
						self.next()

					if self.tok == 'i':
						self.next()
						if self.tok == 'f':
							self.next()
							if self.tok in letters + '0123456789':
								self.pre()
								self.pre()
								tokens.append(Token('ELSE', self.line_num, value, self.file, self.lin_pos, self.tab))
							else:
								tokens.append(Token('ELIF', self.line_num, value, self.file, self.lin_pos, self.tab))
						else:
							self.pre()
							tokens.append(Token('ELSE', self.line_num, value, self.file, self.lin_pos, self.tab))
					else:
						tokens.append(Token('ELSE', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'for':
					tokens.append(Token('FOR', self.line_num, value, self.file, self.lin_pos, self.tab))
					# orbit = 'paren'

				elif value == 'while':
					tokens.append(Token('WHILE', self.line_num, value, self.file, self.lin_pos, self.tab))
					# orbit = 'paren'

				elif value == 'function':
					tokens.append(Token('FN', self.line_num, value, self.file, self.lin_pos, self.tab))
					orbit = 'ident/paren'

				elif value == 'async':
					tokens.append(Token('ASYNC', self.line_num, value, self.file, self.lin_pos, self.tab))
					orbit = 'ident/paren'

				elif value == 'await':
					tokens.append(Token('AWAIT', self.line_num, value, self.file, self.lin_pos, self.tab))
					orbit = 'ident/paren'

				elif value == 'cls':
					tokens.append(Token('CLS', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'inherits':
					tokens.append(Token('INHERITS', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'class':
					tokens.append(Token('CLASS', self.line_num, value, self.file, self.lin_pos, self.tab))
					orbit = 'ident'

				elif value == 'this':
					tokens.append(Token('SELF', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'return':
					tokens.append(Token('RETURN', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'break':
					tokens.append(Token('BREAK', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'continue':
					tokens.append(Token('CONTINUE', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'import':
					tokens.append(Token('IMPORT', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'require':
					tokens.append(Token('USING', self.line_num, value, self.file, self.lin_pos, self.tab))
					orbit = 'ident'

				elif value == 'as':
					tokens.append(Token('AS', self.line_num, value, self.file, self.lin_pos, self.tab))
					orbit = 'ident'

				elif value == 'from':
					tokens.append(Token('FROM', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'const':
					tokens.append(Token('CONST', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'or':
					tokens.append(Token('OR', self.line_num, '|', self.file, self.lin_pos, self.tab))

				elif value == 'not':
					tokens.append(Token('NOT', self.line_num, '!', self.file, self.lin_pos, self.tab))

				elif value == 'and':
					tokens.append(Token('AND', self.line_num, '&', self.file, self.lin_pos, self.tab))

				elif value == 'in':
					tokens.append(Token('IN', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'case':
					tokens.append(Token('CASE', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'switch':
					tokens.append(Token('SWITCH', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'default':
					tokens.append(Token('DEFAULT', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'pass':
					tokens.append(Token('PASS', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'termin':
					tokens.append(Token('TERMIN', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'try':
					tokens.append(Token('TRY', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'catch':
					tokens.append(Token('CATCH', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'finally':
					tokens.append(Token('FINALLY', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == 'lambda':
					tokens.append(Token('LAMBDA', self.line_num, value, self.file, self.lin_pos, self.tab))
					orbit = 'colon'

				else:
					tokens.append(Token('IDENTIFIER', self.line_num, value, self.file, self.lin_pos, self.tab))

				if orbit:
					while self.tok != None and self.tok == ' ':
						self.next()

					if orbit == 'ident':
						if self.tok not in letters:
							self.next()
							self.syntaxError('invalid char after keyword.')
					elif orbit == 'paren':
						if self.tok != '(':
							self.next()
							self.syntaxError("EOL while declaring loop.\n... '('")
					elif orbit == 'ident/paren':
						if self.tok not in letters and self.tok != '(':
							self.next()
							self.syntaxError('invalid char function keyword.')
					elif orbit == 'colon':
						if self.tok != ':':
							self.next()
							self.syntaxError('invalid char after lambda keyword.')
			
			elif self.tok in numbers:
				num = ''
				count = 0
				skip = True

				while self.tok and self.tok in numbers + '.':
					if self.tok == '.':
						count+=1

						if count > 1:
							self.syntaxError('too many points in float data.')
						else:
							self.next()
							if self.tok in numbers:
								num += '.' + self.tok
								self.next()
							else:
								skip = False
								num += '.0'
					else:
						num += self.tok
						self.next()
				

				if self.tok != None and self.tok not in '+*-/%#:=><;)^&|!.}{],' and self.tok not in ['\n', '\t', ' '] and skip:
					capture = self.tok
					self.next()

					if capture == '(':
						self.syntaxError('int/float object not capable.')
					else:
						self.syntaxError('Invalid char while lexing number.')
				
				else:
					if not skip:
						if self.tok not in ' \n':
							self.pre()

					if '.' in num:
						tokens.append(Token('FLOAT', self.line_num, float(num), self.file, self.lin_pos, self.tab))
					else:
						tokens.append(Token('INTEGER', self.line_num, int(num), self.file, self.lin_pos, self.tab))

			elif self.tok in delimeters:
				value = self.tok
				check = True
				self.next()

				if value == '(':
					tokens.append(Token('LPAREN', self.line_num, value, self.file, self.lin_pos, self.tab))
				elif value == ')':
					tokens.append(Token('RPAREN', self.line_num, value, self.file, self.lin_pos, self.tab))
				elif value == '{':
					tokens.append(Token('LBRACE', self.line_num, value, self.file, self.lin_pos, self.tab))
				elif value == '}':
					tokens.append(Token('RBRACE', self.line_num, value, self.file, self.lin_pos, self.tab))
				elif value == '[':
					tokens.append(Token('LCURL', self.line_num, value, self.file, self.lin_pos, self.tab))
				elif value == ']':
					tokens.append(Token('RCURL', self.line_num, value, self.file, self.lin_pos, self.tab))

			elif self.tok in ',;:.':
				value = self.tok
				self.next()

				if value == ',':
					tokens.append(Token('COMMA', self.line_num, value, self.file, self.lin_pos, self.tab))
				
				elif value == '.':
					if self.tok == '.':
						self.next()
						tokens.append(Token('STARRED', self.line_num, '..', self.file, self.lin_pos, self.tab))
					elif self.tok in numbers:
						num='0.'
						while self.tok != None and self.tok in numbers:
							num += self.tok
							self.next()
						tokens.append(Token('FLOAT', self.line_num, float(num), self.file, self.lin_pos, self.tab))
					else:
						while self.tok == ' ':
							self.next()

						if self.tok not in letters:
							self.syntaxError("Invalid syntax after dot char." )
						else:
							tokens.append(Token('DOT', self.line_num, value, self.file, self.lin_pos, self.tab))

				elif value == ';':
					tokens.append(Token('SEMI-COLON', self.line_num, value, self.file, self.lin_pos, self.tab))
				elif value == ':':
					tokens.append(Token('COLON', self.line_num, value, self.file, self.lin_pos, self.tab))

			elif self.tok in symbols:
				if self.tok == '=':
					value = self.tok
					self.next()

					if self.tok ==  '=':
						value += self.tok
						tokens.append(Token('EQUALS-TO', self.line_num, value, self.file, self.lin_pos, self.tab))
						self.next()
					elif self.tok == '>':
						value += self.tok
						tokens.append(Token('ARROW', self.line_num, value, self.file, self.lin_pos, self.tab))
						self.next()
					else:
						tokens.append(Token('EQUALS', self.line_num, value, self.file, self.lin_pos, self.tab))
				else:
					master = self.tok
					self.next()

					if self.tok == '=':
						value = master + self.tok

						if master == '+':
							tokens.append(Token('PLUS-TO', self.line_num, value, self.file, self.lin_pos, self.tab))
						elif master == '-':
							tokens.append(Token('MINUS-TO', self.line_num, value, self.file, self.lin_pos, self.tab))
						elif master == '*':
							tokens.append(Token('MULT-TO', self.line_num, value, self.file, self.lin_pos, self.tab))
						else:
							tokens.append(Token('DIV-TO', self.line_num, value, self.file, self.lin_pos, self.tab))
						self.next()

					else:
						if master == '+':
							tokens.append(Token('PLUS', self.line_num, master, self.file, self.lin_pos, self.tab))
						elif master == '-':
							tokens.append(Token('MINUS', self.line_num, master, self.file, self.lin_pos, self.tab))
						elif master == '*':
							tokens.append(Token('MULT', self.line_num, master, self.file, self.lin_pos, self.tab))
						
						elif master == '/':
							if self.tok == '/':
								while self.tok not in ['\n', None]:
									self.next()
								tokens.append(Token('NEWLINE', self.line_num, 'comment', self.file, self.lin_pos, self.tab))
							elif self.tok == '*':
								self.next()
								while self.tok != None:
									if self.tok == '*':
										self.next()
										if self.tok == '/':
											self.next()
											break
										else:
											pass
									elif self.tok == '\n':
										pass
									self.next()
							else:
								tokens.append(Token('DIV', self.line_num, master, self.file, self.lin_pos, self.tab))
						
						else:
							tokens.append(Token('MOD', self.line_num, master, self.file, self.lin_pos, self.tab))

			elif self.tok == '\n':
				self.next()
				tokens.append(Token('NEWLINE', self.line_num-1, r'\n', self.file, self.lin_pos, self.tab))

			elif self.tok in equality:
				master = self.tok
				self.next()

				if self.tok == '=':
					value = master + self.tok

					if master == '<':
						tokens.append(Token('LESS-E', self.line_num, value, self.file, self.lin_pos, self.tab))
					elif master == '>':
						tokens.append(Token('GREAT-E', self.line_num, value, self.file, self.lin_pos, self.tab))
					else:
						tokens.append(Token('NOT-E', self.line_num, value, self.file, self.lin_pos, self.tab))
					self.next()
				else:
					if master == '<':
						tokens.append(Token('LESS', self.line_num, master, self.file, self.lin_pos, self.tab))
					elif master == '>':
						tokens.append(Token('GREAT', self.line_num, master, self.file, self.lin_pos, self.tab))
					else:
						tokens.append(Token('NOT', self.line_num, master, self.file, self.lin_pos, self.tab))

				while self.tok == ' ':
					self.next()

				if self.tok in ['\n', None]:
					self.syntaxError('EOL after equality symbol.')
			
			elif self.tok in '&|':
				value = self.tok
				self.next()

				if self.tok == '&':
					tokens.append(Token('AND', self.line_num, '&', self.file, self.lin_pos, self.tab))
					self.next()
				elif self.tok == '|':
					tokens.append(Token('OR', self.line_num, '|', self.file, self.lin_pos, self.tab))
					self.next()
				else:
					if value == '|':
						tokens.append(Token('OR', self.line_num, value, self.file, self.lin_pos, self.tab))
					else:
						tokens.append(Token('AND', self.line_num, value, self.file, self.lin_pos, self.tab))

				while self.tok == ' ':
					self.next()

				if self.tok in ['\n', None]:
					self.syntaxError('EOL after equality symbol.')
			
			elif self.tok == '@':
				self.next()
				tokens.append(Token('EACH', self.line_num, '@', self.file))

			elif self.tok == '#':
				while self.tok not in ['\n', None]:
					self.next()
				tokens.append(Token('NEWLINE', self.line_num, 'comment', self.file, self.lin_pos, self.tab))

			elif self.tok == '?':
				tokens.append(Token('QUESTION', self.line_num, self.tok, self.file, self.lin_pos, self.tab))
				self.next()

			elif self.tok == '`':
				self.next()

				if self.tok == '`':
					self.next()
					if self.tok == '`':
						self.next()
						string = ''
						archive = True

						while archive:
							if self.tok == '`':
								store = self.tok
								self.next()
								if self.tok == '`':
									store += self.tok
									self.next()
									if self.tok == '`':
										self.next()
										archive = False
									elif self.tok == None:
										self.syntaxError('while collecting multiline str.')
									else:
										char = ''

										if self.tok == '\\':
											char = self.tok
											self.next()

											if self.tok in ['n', 'b', 't', 'r', '\\']:
												string += store + escapes[self.tok]
												self.next()
											else:
												string += store + char
												self.prev
										else:
											string += store + self.tok
											self.next()

								elif self.tok == None:
									self.syntaxError('while collecting multiline str.')
								else:
									string += store + self.tok
									self.next()
							elif self.tok == None:
								self.syntaxError('while collecting multiline str.')
							else:
								char = ''
								if self.tok == '\\':
									char = self.tok
									self.next()

									if self.tok in ['n', 'b', 't', 'r', '\\']:
										string += escapes[self.tok]
										self.next()
									else:
										string += char
										self.prev
								else:
									string += self.tok
									self.next()

						tokens.append(Token('STRING', self.line_num, string, self.file, self.lin_pos, self.tab))
					else:
						self.syntaxError('Unparsable syntax')
				else:
					self.syntaxError('Unparsable syntax')

			else:
				if self.tok not in '~`^':
					self.next()
				else:
					self.syntaxError('Unrecognized syntax by lexer.')
			
		tokens.append(Token('NEWLINE', self.line_num-1, '\n', self.file, self.lin_pos, self.tab))
		self.tokens = tokens


