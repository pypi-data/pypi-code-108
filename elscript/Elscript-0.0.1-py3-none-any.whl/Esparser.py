import Eslexer
import os, binascii, sys
import importlib, platform
import colorama
import pathlib
import json
from Esformat import Format


sys.setrecursionlimit(12000)
sys.path.append(os.path.abspath('py_modules'))
sys.path.append(os.getcwd())

def quit():
	# if not recognized by pyinstaller
	sys.exit()

class BinOp:
	def __init__(self, left, op, right):
		self.left = left
		self.op = op
		self.right = right

	def __repr__(self):
		return f'({self.left} {self.op} {self.right})'

class Num:
	def __init__(self, token):
		self.value = token

	def __repr__(self):
		return f'{self.value}'

class tactErrors:
	def __init__(self, log, type, catch='Found error'):
		self.log = log
		self.type = type
		self.catch = catch

class tactNone:
	# none for lang
	pass

class eliotCtrl:
	def __init__(self):
		self.version = '1.0 beta'
		self.platform = sys.platform
		self.language = 'eliot'
		self.ext = 'eliot'
		self.path = ['', os.getcwd(), os.path.abspath('eliot_modules'), os.path.join(pathlib.Path.home(), '.eliot', 'modules')]

if True:
	pointers = [f'0xf7{binascii.hexlify(os.urandom(8)).decode()[:7]}e']
	global_scope = {}
	module_scope = {}

EliotSys = eliotCtrl()
RANGE = range

TOOLS = {'self': None, 'this': None}

class Eliot:
	def __init__(self):
		self.print = print
		self.dir = dir
		self.iter = iter

		self.type = type
		self.exit = sys.exit
		self.open = open

		self.str = str
		self.bytes = bytes
		self.int = int

		self.float = float
		self.complex = complex
		self.list = list

		self.dict = dict
		self.tuple = tuple
		self.set = set

		self.len = len
		self.round = round
		self.hex = hex

		self.input = input
		self.max = max
		self.min = min

		self.getattr = getattr
		self.hasattr = hasattr
		self.setattr = setattr
		self.delattr = delattr

		self.true = True
		self.false = False
		self.null = None

		self.eliot = EliotSys

	def include(self, name):
		return importlib.import_module(name)

	def range(self, x, y=None):
		if not y:
			return iter(RANGE(x))
		else:
			return iter(RANGE(x, y))

	def raw(self, data):
		return r'%r' %data

class Parser:
	def __init__(self, code, scope, mode, obj=None, traces=[]):
		self.code = code
		self.scope = scope
		self.mode = mode
		self.obj = obj
		self.traces = traces
		self.for_loop = -1
		self.scoping()
		self.tokens()
		self.pos = -1
		self.next()
		self.evaluate()

	# tokenizing code with lexer
	def tokens(self):
		code_ = self.code[0]
		file_ = self.scope[2]
		self.return_ = 'None'

		self.tok = None

		if type(code_) == list:
			self.toks = code_
		else:
			self.toks = Eslexer.Lexer(code_, file_).tokens

	# increments token
	def next(self):
		self.pos += 1

		if self.pos < len(self.toks):
			self.tok = self.toks[self.pos]

		else:
			# print(self.mode[-1])
			if 'for-loop' == self.mode[-1]:
				self.for_loop += 1

				if self.for_iter:
					if self.for_single:
						try:
							item = next(self.for_value)
							self.symbol_[self.for_key[0]] = item

							self.pos = 0
							self.tok = self.toks[self.pos]
						except:
							self.terminate()
					else:
						try:
							item = next(self.for_value)

							for i in range(len(self.for_key)):
								self.symbol_[self.for_key[i]] = item[i]

							self.pos = 0
							self.tok = self.toks[self.pos]
						except:
							self.terminate()

				elif self.for_loop < len(self.for_value):
					if self.for_single:
						self.symbol_[self.for_key[0]] = self.for_value[self.for_loop]
						self.pos = 0
						self.tok = self.toks[self.pos]
					else:
						if len(self.for_value[self.for_loop]) == len(self.for_key):
							for i in range(len(self.for_key)):
								self.symbol_[self.for_key[i]] = self.for_value[self.for_loop][i]

							self.pos = 0
							self.tok = self.toks[self.pos]
						else:
							self.handleError(tactErrors('too many items to unpack by for loop', 'TypingError', f"[TypingError] too many items to unpack by for loop"))
							self.pos = len(self.toks)
							self.terminate()

				else:
					self.terminate()

			elif 'while-loop' == self.mode[-1]:
				self.pos = 0
				self.tok = self.toks[self.pos]

			else:
				# normal
				self.terminate()

	# focusing on previous token
	def prev(self):
		self.pos -= 1
		self.tok = self.toks[self.pos]

	# manages the new scope
	def scoping(self):
		self.let = []
		self.stop = None
		self.foundError = None
		self.recursive = self.scope[2]
		self.fn_args = self.code[1]
		self.symbol_ = self.scope[0]
		self.object_ = {}
		self.store('this', self.obj)

		if self.scope[1]:
			if 'for-loop' == self.mode[-1]:
				self.for_loop += 1
				self.for_key = self.fn_args[0]

				self.for_value = self.fn_args[1]
				self.for_single = True

				self.for_iter = False

				if len(self.for_key) == 1:
					if 'iterator' in str(type(self.for_value)) or 'generator' in str(type(self.for_value)):
						try:
							item = next(self.for_value)

							self.symbol_[self.for_key[0]] = item
							self.for_iter = True
						except:
							pass
					else:
						self.symbol_[self.for_key[0]] = self.for_value[self.for_loop]
				else:
					self.for_single = False

					if 'iterator' in str(type(self.for_value)) or 'generator' in str(type(self.for_value)):

						try:
							item = next(self.for_value)

							for i in range(len(self.for_key)):
								self.symbol_[self.for_key[i]] = item[i]

							self.for_iter = True
						except:
							pass
					else:
						for i in range(len(self.for_key)):
							self.symbol_[self.for_key[i]] = self.for_value[self.for_loop][i]

		else:
			new_ = f'0xf7{binascii.hexlify(os.urandom(8)).decode()[:7]}e'

			while new_ in pointers:
				new_ = f'0xf7{binascii.hexlify(os.urandom(8)).decode()[:7]}e'

			pointers.append(new_)
			self.symbol_ = self.scope[0].copy()

			if 'method' in self.mode:
				count = 0

				for i in self.fn_args[0]:
					self.symbol_[i] = self.fn_args[1][count]
					count+=1

		self.pointer = pointers[-1]
		self.glo = global_scope
		self.mod_scope = module_scope

	# makes the function AST
	def fnNode(self, name, args, toks, line, file):
		pointer = self.pointer
		tok = self.tok

		pre = self.prev
		scope = self.symbol_

		recursive = self.recursive
		traces = self.traces

		mode = self.mode
		obj = self.obj
		Cmode = self.Cmode

		class FnNode:
			def __init__(self, name, args, toks):
				self.__name__ = name
				self.toks = toks
				self.__qualname__ = f'{name}'
				self.__object__ = obj
				self.__sortArgs__(args)

				if 'class-object' in mode:
					self.repr = f"<bound method {self.__name__} at {recursive}>"
				else:
					self.repr = f"<function {self.__name__} at {pointer}>"

			def __sortArgs__(self, args):
				default_ = []
				params = []

				for i in args:
					if type(args[i]) == type(tactNone):
						params.append(i)
					else:
						params.append(i)
						default_.append(args[i])

				self.__defaults__ = tuple(default_)
				self.__params__ = tuple(params)

			def __code__(self):
				return f"file '{file}', line {line}"

			def __global__(self):
				return scope

			def __repr__(self):
				return self.repr

			def __str__(self):
				return self.repr

			def __call__(self, *args):
				if len(args + self.__defaults__) < len(self.__params__):
					unite = args + self.__defaults__
					sy = list(self.__params__).copy()
					sy.reverse()

					for i in unite:
						catch = sy.pop()

					sy.reverse()

					error = f"Method '{self.__name__}' is missing '{len(sy)}' arguments: {sy}\n  expected {len(self.__params__)  - len(self.__defaults__)} got {len(args)}."
					return tactErrors(error, 'ArgumentError', f"[ArgumentError] '{self.__name__}' missing {len(sy)} args {sy}")

				else:
					final = [self.__params__, args + self.__defaults__[:len(self.__params__)]]

					val = Parser([self.toks, final], [self.__global__(), False, recursive], Cmode('method'),
						self.__object__, traces).return_

					return val

		return FnNode(name, args, toks)

	# makes the class AST
	def clNode(self, name, toks, line, file, inherit=None, replace=None):

		handleError = self.handleError
		pointer = self.pointer
		recursive = self.recursive.split('.')

		if recursive[-1] == 'eliot':
			y = recursive.pop()

		recursive = '.'.join(recursive)

		obj_ = Parser([toks, []], [self.symbol_.copy(), False, self.recursive.split('.')[0] + f'.{name}'], self.Cmode('class-object'),
			self.obj, self.traces).object_

		class ClNode:
			def __init__(self):
				self.__name__ = name
				self.__eliotclass__ = None

			def __repr__(self):
				return f"<class {self.__name__} at {recursive}>"

			def __call__(self, *args):
				eliotrepr = f"<{recursive}.{self.__name__} object at {pointer}>"
				
				if inherit and not hasattr(inherit, '__eliotclass__'):
					
					class Object(inherit):
						def __init__(self):
							
							if '__init__' not in obj_:
								super().__init__(*args)

							self.__name__ = name
							self.__eliotrepr__ = eliotrepr
							self.__inherit__ = inherit

							for i in obj_:
								try:
									obj_[i].__object__ = self
									setattr(self, i, obj_[i])
								except:
									pass

							if '__init__' in obj_:
								val = self.__init__(*args)

								if type(val) == tactErrors:
									handleError(val)

						def __repr__(self):
							try:
								return str(self.__eliotrepr__)
							except:
								return eliotrepr

						def __call__(self, *args):
							pass
				
				else:
					class Object:
						def __init__(self):
							self.__name__ = name
							self.__eliotrepr__ = eliotrepr
							self.__inherit__ = inherit

							if inherit:
								if '__init__' not in obj_:
									herit = inherit(*args)

									for i in dir(herit):
										if i not in dir(self):
											setattr(self, i, getattr(herit, i))

							for i in obj_:
								try:
									obj_[i].__object__ = self
									setattr(self, i, obj_[i])
								except:
									pass

							if '__init__' in obj_:
								val = self.__init__(*args)

								if type(val) == tactErrors:
									handleError(val)

						def __repr__(self):
							try:
								return str(self.__eliotrepr__)
							except:
								return eliotrepr

						def __call__(self, *args):
							pass

				return Object()

		return ClNode()

	# opens files for reading
	def open_module(self, path):
		child_modules = {}

		for i in os.listdir(path):
			file = os.path.join(path, i)

			if i.endswith('.eliot') and os.path.isfile(file):
				name = i.split('.eliot')[0]
				child = open(file, 'r')

				obj = self.obj
				traces = self.traces

				code = child.read()
				child.close()

				flt = Parser([code, file], [{'Eliot': Eliot()}, False, file], ['directory-module'], self.obj, self.traces).symbol_

				class Import:
					def __init__(self):
						self.basefile = file

					def __repr__(self):
						return f"[module: '{name}' from '{os.path.abspath(file)}]"

				l = Import()

				for i in flt:
					try:
						setattr(l, i, flt[i])
					except:
						pass

				child_modules[name] = l
			
			else:
				pass

		return child_modules

	# finds all possible modules or files
	def module_(self):
		path = []

		while self.tok and self.tok.type not in ['NEWLINE', 'SEMI-COLON']:
			if self.tok.type in ['IDENTIFIER', 'STRING']:
				path.append(self.tok.value)
			elif self.tok.type == 'DOT':
				pass
			else:
				self.error('SyntaxError', f"Invalid snytax expected a path separated by dots\n... 'Eliot.print' .")

			self.next()

		found = self.extract_module(path)

		if found:
			return self.module_object(found[0], found[1])
		else:
			pass

	# makes the object for the module
	def module_object(self, new_path, attr):

		if os.path.isdir(new_path):

			flt = self.open_module(new_path)

			class eliotImport:
				def __init__(self):
					pass

				def __repr__(self):
					return f"[module: {new_path.split('/')[-1]} from '{new_path}']"

			l = eliotImport()

			for i in flt:
				setattr(l, i, flt[i])

			for i in attr:
				try:
					l = getattr(l, i)
				except Exception as e:
					self.handleError(tactErrors(e, 'AttributeError', f"[AttributeError] {e}"))
					return

			return l

		else:
			with open(new_path, 'r') as src:
				code = src.read()
				src.close()

			flt = Parser([code, new_path], [{'Eliot': Eliot()}, False, new_path], self.Cmode(['file-module'], True), self.obj, self.traces)
			self.foundError = flt.foundError

			if flt.foundError != None:
				# incase of error
				return

			else:
				flt = flt.symbol_

				class eliotImport:
					def __init__(self):
						pass

					def __repr__(self):
						path_ = '.'.join(new_path.split('/')[-1].split('.')[:-1])
						return f"[module: {path_} from '{new_path}']"

				l = eliotImport()

				for i in flt:
					try:
						setattr(l, i, flt[i])
					except:
						pass

				for i in attr:
					try:
						l = getattr(l, i)
					except Exception as e:
						self.handleError(tactErrors(e, 'AttributeError', f"[AttributeError] {e}"))
						return

				return l

	# checks path existance in list -> eliot.paths
	def check_module(self, path):
		notfound = [False, path]
		finsih = False

		old_path = path
		path = path + '.eliot'

		if os.path.exists(path):
			return [True, path]
		else:
			for i in EliotSys.path:
				__path__ = os.path.join(i, path)

				if os.path.exists(__path__):
					return [True, __path__]
				else:
					pass

		# checks paths without '.eliot'
		path = old_path

		if os.path.exists(path):
			return [True, path]
		else:
			for i in EliotSys.path:
				__path__ = os.path.join(i, path)

				if os.path.exists(__path__):
					return [True, __path__]
				else:
					pass

		return notfound

	# sends path for checking and proves it existance
	def extract_module(self, values):
		attr = []
		tusk = values.copy()

		while values:
			path_ = '/'.join(values)
			check_module = self.check_module(path_)

			if check_module[0]:
				break
			else:
				attr.append(values.pop())

		new_path = check_module[1]

		if not check_module[0]:

			error = f"module '{'/'.join(tusk)}.eliot' does not exist."
			self.handleError(tactErrors(error, 'ImportError', f"[ImportError] {error}"))

		else:
			return (new_path, attr)

	# imports eliotang module
	def importmodule(self):
		mod = []
		attr = []

		while self.tok and self.tok.type not in ['NEWLINE', 'FROM', 'SEMI-COLON']:
			if self.tok.type in ['IDENTIFIER', 'STRING', 'MULT']:
				attr.append(self.tok.value)

			elif self.tok.type == 'DOT':
				pass

			elif self.tok.type == 'COMMA':
				if len(attr):
					mod.append(attr)
					attr = []

			elif self.tok.type == 'AS':
				self.next()
				attr.append({'0f---as--------': self.tok.value})

				mod.append(attr)
				attr = []

			else:
				self.error('SyntaxError', 'Invalid char in import statement')

			self.next()

		if len(attr):
			# incase attr is not empty
			mod.append(attr)


		if not self.tok or self.tok.type != 'FROM':

			for i in mod:
				inspect = None

				if type(i[-1]) == dict:
					# to get the as keyword
					inspect = i.pop()

				certi = self.extract_module(i)

				if certi:
					objective = self.module_object(certi[0], certi[1])

					if objective:
						if inspect:
							self.symbol_[inspect['0f---as--------']] = objective
						else:
							if len(certi[1]):
								self.symbol_[certi[1][-1]] = objective
							else:
								self.symbol_[i[-1]] = objective
					else:
						pass
				else:
					pass

		else:
			self.next()
			module = self.module_()

			if module:
				for i in mod:
					saved = True
					individual = module

					for y in i:
						if type(y) == dict and '0f---as--------' in y.keys():
							saved = False
							self.symbol_[y['0f---as--------']] = individual

						else:
							if y == '*':
								for a in dir(module):

									if not str(a).startswith('__') and not str(a).endswith('__'):
										try:
											self.symbol_[a] = getattr(module, a)
										except Exception as e:
											saved = None
											self.handleError(tactErrors(e, 'AttributeError', f"[AttributeError] {e}"))
											break

								saved = False
							else:
								try:
									individual = getattr(individual, y)
								except Exception as e:
									saved = None
									self.handleError(tactErrors(e, 'AttributeError', f"[AttributeError] {e}"))
									break

					if saved:
						if len(i):
							self.symbol_[y] = individual
					else:
						pass
			else:
				pass

	# imports python module
	def importBuiltin(self):
		mod = []
		attr = []

		while self.tok and self.tok.type not in ['NEWLINE', 'SEMI-COLON']:
			if self.tok.type == 'IDENTIFIER':
				attr.append(self.tok.value)

			elif self.tok.type == 'DOT':
				pass
			elif self.tok.type == 'COMMA':
				if len(attr):
					mod.append(attr)
					attr = []

			elif self.tok.type == 'AS':
				self.next()
				attr.append({'0f---as--------': self.tok.value})

				mod.append(attr)
				attr = []

			else:
				self.error('SyntaxError', 'Invalid char in import statement')

			self.next()

		if len(attr):
			# incase attr is not empty
			mod.append(attr)

		for i in mod:
			inspect = None
			imported = False

			if type(i[-1]) == dict:
				# to get the as keyword
				inspect = i.pop()

			for x in i:
				try:
					if imported:
						l = getattr(l, x)
					else:
						imported = True
						l = importlib.import_module(x)

				except Exception as e:
					self.handleError(tactErrors(e, 'ImportError', f"[ImportError] {e}"))
					l = None
					break

			if inspect:
				self.symbol_[inspect['0f---as--------']] = l
			else:
				self.symbol_[i[-1]] = l

	# stores the variables
	def store(self, key, value, let=False):
		# saving variable to symbol table
		self.symbol_[key] = value

	# getting a variable from scope
	def get(self, key, x=True):
		if x:
			return self.symbol_[key]
		else:
			return getattr(self.obj, key)

	# returning objects errors break
	def result(self):
		# getting result
		return [self.return_, self.stop, self.foundError, self.object_]

	# collects tokens in braces or on a single line
	def collecttoks(self):
		while self.tok and self.tok.type == 'NEWLINE':
			self.next()

		code = []

		if not self.tok:
			# incase out of tokens
			return code

		elif self.tok.type == 'LBRACE':
			self.next()
			increment = 1

			while self.tok and increment != 0:
				if self.tok.type == 'LBRACE':
					increment+=1
				elif self.tok.type == 'RBRACE':
					increment-=1
					if increment == 0:
						break
				code.append(self.tok)
				self.next()

			self.next()

		else:
			while self.tok and self.tok.type not in ['NEWLINE', 'SEMI-COLON']:
				code.append(self.tok)
				self.next()

			if self.tok != None:
				code.append(self.tok)
			else:
				self.prev()
				code.append(Eslexer.Token('NEWLINE', self.tok.line, r'\n', self.tok.file, self.tok.pos, self.tok.tab))
				self.next()

			self.next()

		return code

	# collects arguments
	def collectargs(self):
		args = {}
		defaults = True

		while self.tok and self.tok.type != 'RPAREN':
			if self.tok.type == 'IDENTIFIER':
				key = self.tok.value
				self.next()

				if self.tok.type in ['COMMA', 'RPAREN', 'NEWLINE']:
					if defaults:
						args[key] = tactNone
					else:
						self.error('SyntaxError', f"Cannot assign normal param '{key}' after a default param has been set.")

				elif self.tok.type == 'COLON':
					self.next()
					value = self.eval(['NEWLINE', 'COMMA', 'RPAREN'])
					args[key] = value
					defaults = False

				elif self.tok.type in ['NEWLINE', 'COMMA']:
					self.next()

			else:
				if self.tok and self.tok.type in ['NEWLINE', 'COMMA']:
					self.next()
				else:
					self.error('SyntaxError', f"Invalid syntax, unparsable during collect params.")

		self.next()
		return args

	# collects parameters when calling
	def collectpara(self):
		paras = []
		while self.tok and self.tok.type != 'RPAREN':
			if self.tok.type in ['NEWLINE', 'COMMA']:
				self.next()

			elif self.tok.type == 'STARRED':
				self.next()
				val = self.get(self.tok.value, True)

				self.next()
				for i in val:
					paras.append(i)
			else:
				paras.append(self.eval(['NEWLINE', 'COMMA', 'RPAREN']))

		self.next()
		return tuple(paras)

	# making a set if not a dictionary
	def setdata(self, fir):
		lst = {fir}

		while self.tok.type != 'RBRACE':
			lst.add(self.eval(['COMMA', 'NEWLINE', 'RBRACE']))

			while self.tok and self.tok.type in ['COMMA', 'NEWLINE']:
				self.next()

		return lst

	# parses deifferent datatypes
	def data(self):
		if self.tok.type == 'LCURL':
			self.next()
			list_ = []

			while self.tok and self.tok.type in ['NEWLINE', 'COMMA']:
				self.next()

			while self.tok and self.tok.type != 'RCURL':
				list_.append(self.eval(['NEWLINE', 'COMMA', 'RCURL']))

				while self.tok and self.tok.type in ['NEWLINE', 'COMMA']:
					self.next()

			return list_

		elif self.tok.type == 'LPAREN':
			self.next()
			tuple_ = []

			while self.tok and self.tok.type in ['NEWLINE', 'COMMA']:
				self.next()

			while self.tok and self.tok.type != 'RPAREN':
				tuple_.append(self.eval(['NEWLINE', 'COMMA', 'RPAREN']))

				while self.tok and self.tok.type in ['NEWLINE', 'COMMA']:
					self.next()

			if len(tuple_) == 1:
				count = 1

				while self.tok and self.tok.type == 'NEWLINE':
					self.prev()
					count+=1

				self.prev()
				prev = self.tok.type

				for i in range(count):
					self.next()

				if prev != 'COMMA':
					return tuple_[0]
				else:
					return tuple(tuple_)

			else:
				# if no distributing
				return tuple(tuple_)

		elif self.tok.type == 'LBRACE':
			self.next()

			dict_ = {}
			count = 0

			while self.tok and self.tok.type in ['NEWLINE', 'COMMA']:
				self.next()

			while self.tok and self.tok.type != 'RBRACE':
				key = self.eval(['NEWLINE', 'COLON', 'COMMA', 'RBRACE'])

				if self.tok.type == 'COLON':
					self.next()
					value = self.eval(['NEWLINE', 'COLON', 'COMMA', 'RBRACE'])
					dict_[key] = value

				elif self.tok.type == 'COMMA':
					if count != 0:
						self.error('SyntaxError', "error parsing 'set' yet previous 'dict' object\n... {'a': 'A', 1, 2}.")
					else:
						self.next()
						dict_ = self.setdata(key)
						break

				while self.tok and self.tok.type in ['NEWLINE', 'COMMA']:
					self.next()

				count+=1

			return dict_

	# creating javascript object
	def objectize(self):
		self.next()

		# object class
		_object = {}

		class Object():
			def __repr__(self):
				return '[object: {...}]'

		Obj = Object()

		while self.tok and self.tok.type != 'RBRACE':

			if self.tok.type in ['NEWLINE', 'COMMA']:
				self.next()

			elif self.tok.type == 'IDENTIFIER':
				key = self.tok.value
				self.next()

				if self.tok and self.tok.type == 'COLON':
					self.next()
					value = self.eval(['NEWLINE', 'COMMA', 'RBRACE'])

					_object[key] = value
				else:
					self.error('SyntaxError', 'Invalid syntax when parsing object.')
			else:
				self.error('SyntaxError', 'Invalid syntax when parsing object.')


		for i in _object:
			try:
				setattr(Obj, i, _object[i])
			except:
				pass

		return Obj

	# makes extractor tokens
	def ctoken(self, ty, val):
		# pass
		return Eslexer.Token(ty, self.tok.line, val, self.tok.file, self.tok.pos, self.tok.tab)

	# formats an f-string
	def formats(self):
		value = self.tok.value
		new_ = ''
		l = Format(value).parse()

		for i in l:
			if type(i) == list:
				lexed = [self.ctoken('IDENTIFIER', '__DIRECT_FORMAT_VAR__'), self.ctoken('EQUALS', '=')] + Eslexer.Lexer(i[0] + '\n').tokens + [self.ctoken('NEWLINE', r'\n')]

				format_ = Parser([lexed, []], [self.symbol_, True, self.recursive], self.Cmode('format'), self.obj, self.traces).symbol_['__DIRECT_FORMAT_VAR__']

				new_ += f"{format_}"
			else:
				new_ += i

		return new_

	# syntax error
	def syError(self, log):
		print('Error (Uncaught syntax error)')
		print(f"  File '{self.tok.file}', line {self.tok.line}")

		if os.path.exists(self.tok.file):
			file = open(self.tok.file, 'r')
			data = file.read()
			file.close()

			print('       ' + data.split('\n')[self.tok.line-1].lstrip('\t').lstrip(' ') + '\n')
		else:
			print(' ')

		print(' SyntaxError', log)
		quit()

	# terminate the statement
	def terminate(self):
		self.tok = None
		self.pos = len(self.toks)

	# arguments error
	def RaiseError(self, prefix='Segmentation Fault', log=None):
		print(f'Error ({prefix})\n')
		self.prev()
		fault = [None, None]

		for i in self.traces:
			if fault[0] != i.file or fault[1] != i.line:
				try:
					print(f"  File '{i.file}', line {i.line}, ")
					fault[0] = i.file
					fault[1] = i.line

					if i.file != 'stdin':
						data = open(i.file, 'r')

						print('       ' + data.read().split('\n')[i.line-1].lstrip('\t').lstrip(' ') + '\n')
						data.close()
					else:
						pass

				except Exception as e:
					print(e)
					pass

		if self.tok.file != fault[0] or self.tok.line != fault[1]:
			print(f"  File '{self.tok.file.split('/')[-1]}', line {self.tok.line}, {self.mode[-1]}")

			if os.path.exists(self.tok.file):
				file = open(self.tok.file, 'r')
				data = file.read()

				file.close()
				print('       ' + data.split('\n')[self.tok.line-1].lstrip('\t').lstrip(' ') + '\n')
			else:
				print(' ')

		print(f'{log.type}:', log.log)

		if 'stdin' not in self.mode:
			quit()
		else:
			self.terminate()

	# general error logging
	def error(self, type_, log_=''):
		print('Uncaught Error (parser failure)')
		mod = '[ method ]'

		for i in self.traces:
			print(f"  File '{i.file.split('/')[-1]}', line {i.line}, in {mod}")
			mod = i.name

			if os.path.exists(i.file):
				file = open(i.file, 'r')
				data = file.read()
				file.close()

				content = data.split('\n')[i.line-1].lstrip('\t').lstrip(' ')
				print(f'    {content}')
			else:
				print(' ')

		if self.tok == None:
			self.prev()
		else:
			pass

		print(f"  File '{self.tok.file.split('/')[-1]}', line {self.tok.line}, in {mod}")

		if os.path.exists(self.tok.file):
			file = open(self.tok.file, 'r')
			data = file.read()
			file.close()

			content = data.split('\n')[self.tok.line-1].lstrip('\t').lstrip(' ')
			print(f'    {content}')
			print(' ' * self.tok.pos, '^')
		else:
			print(' ')

		print(f'{type_}: {log_}')

		if 'stdin' in self.mode:
			self.terminate()
		else:
			quit()

	# handling interpreter errors
	def handleError(self, error):
		if 'try-catch' in self.mode:
			self.foundError = error.catch
			self.terminate()
		else:
			if error.type == 'ArgumentError':
				self.RaiseError('Unprovided arguments', error)
			elif error.type == 'NameError':
				self.RaiseError('Naming Fault', error)
			elif error.type == 'TypingError':
				self.RaiseError('Position or Unwanted', error)
			elif error.type == 'AttributeError':
				self.RaiseError('not object attribute', error)
			elif error.type == 'ImportError':
				self.RaiseError('Check paths therary', error)
			elif error.type == 'IndexError':
				self.RaiseError('Expects int/out of range', error)
			elif error.type == 'KeyError':
				self.RaiseError('Not key of dictionary!', error)
			elif error.type == 'SyscallError':
				self.RaiseError('Sys-call', error)
			elif error.type == 'OperationError':
				self.RaiseError('different datatypes', error)
			else:
				pass

	# getting positives and negatives
	def posit(self, ty):
		self.next()
		val = self.eval(['NEWLINE', 'SEMI-COLON', 'PLUS', 'MINUS', 'DIV', 'MULT', 'COMMA', 'MOD', 'DOT', 'EQUALS-TO', 'IN', 'NOT-E', 'LESS', 'GREAT', 'LESS-E', 'GREAT-E', 'NOT', 'AND', 'OR'])

		self.prev()

		if ty == '-':
			return 0 - val
		else:
			return val

	# indexing data objects
	def Index(self, data):
		self.next()
		idx = []

		while self.tok and self.tok.type != 'RCURL':
			if self.tok.type == 'COLON':
				self.next()
				idx.append(':')
			else:
				idx.append(self.eval(['RCURL', 'COLON']))

		self.next()

		if len(idx):
			if type(data) != dict:
				if ':' in idx:
					# incase the colon starts
					if idx.index(':') == 0:
						if len(idx) > 1:
							return data[:idx[1]]
						else:
							return data

					# incase colon is in the middle or end
					elif idx.index(':') == 1:
						if len(idx) < 3:
							return data[idx[0]:]
						else:
							return data[idx[0]:idx[2]]

				else:
					if type(idx[0]) == int and idx[0] < len(data):
						if self.tok.type == 'EQUALS':
							self.next()
							data[idx[0]] = self.eval(['NEWLINE', 'SEMI-COLON'])

						elif self.tok.type in ['PLUS-TO', 'MINUS-TO', 'MULT-TO', 'DIV-TO']:
							op = self.tok.value
							self.next()

							ans = self.eval(['NEWLINE', 'SEMI-COLON'])

							if not self.foundError:
								try:
									if op == '+=':
										data[idx[0]] += ans
									elif op == '-=':
										data[idx[0]] -= ans
									elif op == '*=':
										data[idx[0]] *= ans
									else:
										data[idx[0]] /= ans
								except Exception as e:
									error = f"index-incremetion {e}"
									self.handleError(tactErrors(error, 'TypingError', error))

							else:
								pass

						else:
							return data[idx[0]]

					else:
						if type(idx[0]) == int:
							error = f"'{idx[0]}' is out of {type(data)} data range."
						else:
							error = f"'{idx[0]}' is not an 'int' datatype."

						self.handleError(tactErrors(error, 'IndexError', error))
						return

			else:
				if idx[0] in data.keys():
					if self.tok and self.tok.type == 'EQUALS':
						self.next()
						data[idx[0]] = self.eval(['NEWLINE', 'SEMI-COLON'])

					elif self.tok and self.tok.type in ['PLUS-TO', 'MINUS-TO', 'MULT-TO', 'DIV-TO']:
						op = self.tok.value
						self.next()

						ans = self.eval(['NEWLINE', 'SEMI-COLON'])

						if op == '+=':
							data[idx[0]] += ans
						elif op == '-=':
							data[idx[0]] -= ans
						elif op == '*=':
							data[idx[0]] *= ans
						else:
							data[idx[0]] /= ans

					else:
						return data[idx[0]]

				else:
					error = f"'{idx[0]}' is not a key of {type(data)} object."
					self.handleError(tactErrors(error, 'KeyError', error))

		else:
			return data

	# calling functions or callbacks
	def callFn(self, value):
		self.next()
		self.traces.append(self.tok)
		args = self.collectpara()

		if not self.foundError:
			try:
				val =  value(*args)

				if type(val) == tactErrors:
					self.handleError(val)
					x = self.traces.pop()
				else:
					x = self.traces.pop()
					return val

			except Exception as e:
				error = e
				self.handleError(tactErrors(error, 'SyscallError', error))
				x = self.traces.pop()

	# extracting attributes from object and keys from dictornaries
	def callAttr(self, value):
		self.next()
		attr = self.tok.value

		ans = None
		self.next()

		if self.tok:
			if type(value) != dict and self.tok.type in ['EQUALS', 'PLUS-TO', 'MINUS-TO', 'MULT-TO', 'DIV-TO']:
				op = self.tok.value
				self.next()

				if op == '=':
					setattr(value, attr, self.eval(['NEWLINE', 'SEMI-COLON']))
				else:
					fn = getattr(value, attr)

					if op == '+=':
						setattr(value, attr, fn + self.eval(['NEWLINE', 'SEMI-COLON']))
					elif op == '-=':
						setattr(value, attr, fn - self.eval(['NEWLINE', 'SEMI-COLON']))
					elif op == '*=':
						setattr(value, attr, fn * self.eval(['NEWLINE', 'SEMI-COLON']))
					else:
						setattr(value, attr, fn + self.eval(['NEWLINE', 'SEMI-COLON']))

				return None

			else:
				try:
					ans = getattr(value, attr)
				except Exception as e:
					if hasattr(value, '__name__'):
						seive = str(e).lstrip("'Object'")
						self.handleError(tactErrors(f"'{value.__name__}' {seive}.", 'AttributeError', f"[AttributeError] '{value.__name__}' {seive}."))
					else:
						self.handleError(tactErrors(e, 'AttributeError', f"[AttributeError] {e}"))

			return ans

	# excuting eval
	def execc(self):
		x = self.tok.value
		more = False
		ans = ()
		self.next()

		if self.tok and self.tok.type == 'LPAREN':
			self.next()

			if not self.tok.type == 'RPAREN':
				ans = self.collectpara()
				self.prev()

				if len(ans) == 1:
					ans = ans[0]
				else:
					more = True
			
			else:
				# incase no argument is provided
				more = True

			if x == 'eval':
				if more:
					error = f"'?eval' has strict syntax, expects '1' str argument."
					self.handleError(tactErrors(error, 'TypingError', f"[TypingError] {error}"))
				else:
					code = 'eliotftxtsortryqwyc1627cxqy = ' + str(ans) + '\n'
					res = Parser([code, []], [self.symbol_, True, self.recursive], self.Cmode('?eval'), self.obj, self.traces).symbol_['eliotftxtsortryqwyc1627cxqy']

					return res
			
			elif x == 'extr':
				if more:
					for x in ans:
						for i in dir(x):
							if not i.startswith('__') and not i.endswith('__'):
								self.store(i, getattr(x, i))
				else:
					for i in dir(ans):
						if not i.startswith('__') and not i.endswith('__'):
							self.store(i, getattr(ans, i))

			else:
				if more:
					error = f"'?exec' has strict syntax, expects '1' str argument."
					self.handleError(tactErrors(error, 'TypingError', f"[TypingError] {error}"))
				else:
					res = Parser([ans, []], [self.symbol_, True, self.recursive], self.Cmode('if-statement'), self.obj, self.traces).result()

					self.stop = res[1]
					self.return_ = res[0]
					self.foundError = res[2]

					if len(res[3]):
						# checking to update object
						self.object_.update(res[3])

					if res[1] in ['break', 'return-break'] or res[2]:
						# incase of break or return
						self.terminate()

					elif res[1] == 'continue':
						self.pos = len(self.toks)-1
						self.tok = self.toks[self.pos]
						self.next()

		else:
			self.error('SyntaxError', f"Expected a left parenthesis at ? functions")

	def factor(self, idn):
		if self.tok and self.tok.type in ['IDENTIFIER', 'INTEGER', 'STRING', 'SELF', 'FLOAT', 'FORMAT', 'LCURL', 'LBRACE', 'QUESTION', 'LPAREN', 'FN', 'MINUS', 'PLUS', 'LAMBDA']:
			value = None

			if self.tok.type == 'IDENTIFIER':
				if self.tok.value in self.symbol_:
					value = self.get(self.tok.value)
				else:
					error = f"name '{self.tok.value}' is not defined."
					self.handleError(tactErrors(error, 'NameError', error))

			elif self.tok.type == 'FORMAT':
				# formatted string
				value = self.formats()

			elif self.tok.type == 'SELF':
				# object
				value = self.obj

			elif self.tok.type in ['LCURL', 'LBRACE', 'LPAREN', 'QUESTION']:
				if self.tok.type == 'LBRACE':
					value = self.objectize()
				else:
					if self.tok.type == 'QUESTION':
						self.next()

						if self.tok.type == 'IDENTIFIER':
							# execute cmds in interpreter
							value = self.execc()

						else:
							value = self.data()
					else:
						value = self.data()

			elif self.tok.type == 'FN':
				fn_name = 'anonymous'
				fn_file = self.tok.file
				fn_line = self.tok.line
				self.next()

				if self.tok.type != 'LPAREN':
					self.error('SyntaxError', f"Expected a left parenthesis '('")
				else:
					self.next()

					args = self.collectargs()

					if self.tok.type != 'NEWLINE':
						toks = self.collecttoks()
					else:
						toks = self.tokens_()
						self.prev()

					node = self.fnNode(fn_name, args, toks, fn_file, fn_line)
					value = node
					self.prev()

			elif self.tok.type == 'LAMBDA':
				self.next()

				if self.tok.type in ['COLON', 'ARROW']:
					self.next()

					if self.tok.type == 'IDENTIFIER':
						call = self.get(self.tok.value)
						self.next()

						while self.tok != None and self.tok.type == 'DOT':
							call = self.callAttr(call)

						if self.tok != None and self.tok.type == 'LPAREN':
							self.next()
							params = self.collectpara()

							value = lambda:call(*params)
							self.prev()
						else:
							self.error('SyntaxError', 'missing Left parenthesis to pass fn args\n... =>fn(5, 7)')
					else:
						self.error('SyntaxError', 'expected a function name.')
				else:
					self.error("SyntaxError", "Expected an 'Arrow' or 'Colon' ...=>\n... => :")

			elif self.tok.type in ['MINUS', 'PLUS']:
				# negatives and positives
				value = self.posit(self.tok.value)

			else:
				value = self.tok.value

			self.next()

			while self.tok and self.tok.type in ['LPAREN', 'LCURL', 'DOT']:

				if self.tok.type == 'LPAREN':
					value = self.callFn(value)

				elif self.tok.type == 'DOT':
					value = self.callAttr(value)

				else:
					value = self.Index(value)

			return Num(value)
		else:
			pass

	def term(self, idn):
		node = self.factor(idn)

		while self.tok and self.tok.type in ['MULT', 'DIV', 'MOD']:
			op = self.tok.value
			self.next()
			right = self.factor(idn)
			node = BinOp(node, op, right)
		return node

	def expr(self, end, idn):
		node = self.term(idn)
		while self.tok and self.tok.type not in end and self.tok.type in ['PLUS', 'MINUS']:
			op = self.tok.value
			self.next()
			right = self.term(idn)
			node = BinOp(node, op, right)

		return node

	def Qexpr(self, end, idn):
		node = self.expr(end, idn)

		while self.tok and self.tok.type not in end and self.tok.type in ['EQUALS-TO', 'IN', 'NOT-E', 'LESS', 'GREAT', 'LESS-E', 'GREAT-E']:
			op = self.tok.value
			self.next()
			right = self.expr(end, idn)
			node = BinOp(node, op, right)

		return node

	def Nexpr(self, end, idn):
		node = self.Qexpr(end, idn)

		while self.tok and self.tok.type not in end and self.tok.type == 'NOT':
			op = self.tok.value
			self.next()
			right = self.Qexpr(end, idn)
			node = BinOp(node, '!', right)

		return node

	def Xexpr(self, end, idn):
		node = self.Nexpr(end, idn)

		while self.tok and self.tok.type not in end and self.tok.type in ['AND', 'OR']:
			op = self.tok.value
			self.next()
			right = self.Nexpr(end, idn)
			node = BinOp(node, op, right)

		return node

	def visit(self, node):
		if 'BinOp' in str(node.__class__):
			while 'BinOp' in str(node.__class__):
				left = node.left
				op = node.op
				right = node.right

				try:
					if op == '+':
						return self.visit(left) + self.visit(right)
					elif op == '-':
						return self.visit(left) - self.visit(right)
					elif op == '*':
						return self.visit(left) * self.visit(right)
					elif op == '/':
						return self.visit(left) / self.visit(right)
					elif op == '%':
						return self.visit(left) % self.visit(right)
					elif op == '==':
						return self.visit(left) == self.visit(right)
					elif op == 'in':
						return self.visit(left) in self.visit(right)
					elif op == '!=':
						return self.visit(left) != self.visit(right)
					elif op == '<':
						return self.visit(left) < self.visit(right)
					elif op == '>':
						return self.visit(left) > self.visit(right)
					elif op == '<=':
						return self.visit(left) <= self.visit(right)
					elif op == '|':
						return self.visit(left) or self.visit(right)
					elif op == '&':
						return self.visit(left) | self.visit(right)
					elif op == '!':
						return not self.visit(right)
				except Exception as e:
					self.handleError(tactErrors(e, 'OperationError', e))

		else:
			if node:
				return node.value
			else:
				# failure to parse
				self.error('SyntaxError', "Invalid syntax while evaluting object.")

	def ans(self, node):
		if hasattr(node, 'op'):
			try:
				if node.op == '+':
					return self.visit(node.left) + self.visit(node.right)
				elif node.op == '-':
					return self.visit(node.left) - self.visit(node.right)
				elif node.op == '*':
					return self.visit(node.left) * self.visit(node.right)
				elif node.op == '/':
					return self.visit(node.left) / self.visit(node.right)
				elif node.op == '%':
					return self.visit(node.left) % self.visit(node.right)
				elif node.op == '==':
					return self.visit(node.left) == self.visit(node.right)
				elif node.op == 'in':
					return self.visit(node.left) in self.visit(node.right)
				elif node.op == '!=':
					return self.visit(node.left) != self.visit(node.right)
				elif node.op == '<':
					return self.visit(node.left) < self.visit(node.right)
				elif node.op == '>':
					return self.visit(node.left) > self.visit(node.right)
				elif node.op == '<=':
					return self.visit(node.left) <= self.visit(node.right)
				elif node.op == '>=':
					return self.visit(node.left) >= self.visit(node.right)
				elif node.op == '&':
					return self.visit(node.left) and self.visit(node.right)
				elif node.op == '|':
					return self.visit(node.left) or self.visit(node.right)
				elif node.op == '!':
					return not self.visit(node.right)
			except Exception as e:
				self.handleError(tactErrors(e, 'OperationError', e))
		else:
			if node:
				return node.value
			else:
				# failure to parse
				self.error('SyntaxError', "Invalid syntax while evaluting object.")

	def eval(self, end, idn=None):
		out = self.ans(self.Xexpr(end, idn))
		return out

	def tokens_(self):
		toks = []
		self.prev()

		indent = self.tok.tab
		self.next()

		if self.mode[-1] in ['for-loop', 'while-loop']:
			while self.pos != len(self.toks) - 1:

				if self.tok.type == 'NEWLINE':
					toks.append(self.tok)
					self.next()
				else:
					if self.tok.tab > indent:
						toks.append(self.tok)
						self.next()
					else:
						break

		else:
			while self.tok:
				if self.tok.type == 'NEWLINE':
					toks.append(self.tok)
					self.next()
				else:
					if self.tok.tab > indent:
						toks.append(self.tok)
						self.next()
					else:
						break

		if not self.tok:
			self.prev()
			toks.append(Eslexer.Token('NEWLINE', self.tok.line, r'\n', self.tok.file, self.tok.pos, self.tok.line))
			self.next()

		else:
			toks.append(Eslexer.Token('NEWLINE', self.tok.line, r'\n', self.tok.file, self.tok.pos, self.tok.line))

		return toks

	def Cmode(self, mode='main', imp=False):
		if imp:
			apx = [mode]
			for i in ['try-catch', 'stdin']:
				if i in self.mode:
					apx += [i]

			return apx
		else:
			return self.mode + [mode]

	def proof_iter(self, data, fla):
		if not fla:
			return (None, None)
		else:
			if type(data) in [list, str, tuple, set]:
				return (True, data)
			else:
				null = True
				try:
					for i in data:
						break
				except:
					null = False

				if not null:
					return (False, '__not__iterable_7ebcfefrxxq__')
				else:
					if len(data) > 0:
						try:
							l = data[0]
						except:
							data = list(data)

						return (True, data)
					else:
						return (True, None)

	def console(self, value):
		fore = colorama.Fore
		style = colorama.Style

		if type(value) == str:
			print(fore.GREEN, end= '')
		elif type(value) in [int, float, complex]:
			print(fore.YELLOW, end= '')
		elif type(value) in [list, set, tuple, dict]:
			print(fore.LIGHTYELLOW_EX, end= '')
		else:
			print(fore.CYAN, end= '')

		if value not in [None, 'None']:
			if type(value) == str:
				print(r'%r' %value)
			else:
				print(value)

		print(style.RESET_ALL, end='')

	def evaluate(self):
		while self.tok:
			if self.tok.type == 'NEWLINE':
				# newline char
				self.next()

			elif self.foundError:
				# breaking if in try statement
				break

			elif self.tok.type == 'IDENTIFIER':
				var = self.tok.value
				self.next()

				if self.tok and self.tok.type == 'COMMA':
					self.next()
					var = [var]

					while self.tok and self.tok.type not in ['EQUALS', 'SEMI-COLON', 'NEWLINE']:
						if self.tok.type == 'IDENTIFIER':
							var.append(self.tok.value)
							self.next()
						elif self.tok.type == 'COMMA':
							self.next()
						else:
							self.error('SyntaxError', f"Invalid syntax while declaring variables\n... '{self.tok.value}'.")

				if self.tok == None:
					# if passing errors
					pass

				elif self.tok.type == 'EQUALS':
					self.next()
					val = self.eval(['NEWLINE', 'SEMI-COLON', 'COMMA'])

					if self.tok and self.tok.type == 'COMMA':
						val = [val]
						self.next()

						while self.tok and self.tok.type not in ['NEWLINE', 'SEMI-COLON']:
							val.append(self.eval(['NEWLINE', 'SEMI-COLON', 'COMMA']))
							if self.tok.type == 'COMMA':
								self.next()

					if self.tok:
						if type(var) == str:
							self.store(var, val)
						else:
							if type(val) not in [float, int]:
								if len(val) == len(var):
									index = 0
									for i in val:
										self.store(var[index], i)
										index+=1
								else:
									error = f"'var' length must be equal to 'value' length\n... a, b, c = (1,2,3)"
									self.handleError(tactErrors(error, 'TypingError', f"[TypingError] 'Var' length must be equal to 'Value' length\n... a, b, c = (1,2,3)."))
							else:
								error = f"Defining method supports only iterable data not '{val}'."
								self.handleError(tactErrors(error, 'TypingError', error))

				elif self.tok.type in ['PLUS-TO', 'MINUS-TO', 'MULT-TO', 'DIV-TO', 'PLUS', 'MINUS', 'MULT', 'DIV', 'MOD']:
					op = self.tok.value
					self.next()

					if type(var) == list:
						error = f"data incrementation applies to a single 'var' at a time."
						self.handleError(tactErrors(error, 'TypingError', error))
					else:
						if var in self.symbol_.keys():
							val = self.eval(['NEWLINE', 'SEMI-COLON'])

							if self.tok:
								if op == '+=':
									self.symbol_[var] += val
								elif op == '-=':
									self.symbol_[var] -= val
								elif op == '*=':
									self.symbol_[var] *= val
								elif op == '/=':
									self.symbol_[var] /= val
								else:
									ans = self.get(var)

									if op == '+':
										ans = ans + val
									elif op == '-':
										ans = ans - val
									elif op == '*':
										ans = ans * val
									elif op == '/':
										ans = ans / val
									else:
										ans = ans % val

									if 'stdin' in self.mode and self.tok.type != 'PASS':
										self.console(ans)
										self.next()
									else:
										pass
						else:
							error = f"name '{var}' is not defined."
							self.handleError(tactErrors(error, 'NameError', error))

				elif self.tok.type in ['NEWLINE', 'SEMI-COLON']:
					self.next()

					if type(var) == str:
						if var in self.symbol_.keys():
							if 'stdin' in self.mode:
								self.console(self.get(var))
							else:
								pass
						else:
							error = f"name '{var}' is not defined."
							self.handleError(tactErrors(error, 'NameError', error))
					else:
						error = f"feature applies to a single 'var' at a time."
						self.handleError(tactErrors(error, 'TypingError', error))

				elif self.tok.type in ['LPAREN', 'DOT', 'LCURL']:
					self.prev()
					output = self.eval(['NEWLINE', 'SEMI-COLON'])

					if 'stdin' in self.mode:
						self.console(output)

				else:
					# incase of wrong input
					self.error('SyntaxError', f"Unknown syntax\n... {self.tok.value}")

			elif self.tok.type == 'LET':
				self.next()
				var = self.tok.value
				self.next()

				if self.tok and self.tok.type == 'COMMA':
					self.next()
					var = [var]

					while self.tok and self.tok.type not in ['EQUALS', 'SEMI-COLON', 'NEWLINE']:
						if self.tok.type == 'IDENTIFIER':
							var.append(self.tok.value)
							self.next()
						elif self.tok.type == 'COMMA':
							self.next()
						else:
							self.error('SyntaxError', f"Invalid syntax while declaring variables\n... '{self.tok.value}'.")

				if self.tok == None:
					# incase if try
					pass

				elif self.tok.type == 'EQUALS':
					self.next()
					val = self.eval(['NEWLINE', 'SEMI-COLON', 'COMMA'])

					if self.tok and self.tok.type == 'COMMA':
						val = [val]
						self.next()
						while self.tok and self.tok.type not in ['NEWLINE', 'SEMI-COLON']:
							val.append(self.eval(['NEWLINE', 'SEMI-COLON', 'COMMA']))

							if self.tok and self.tok.type == 'COMMA':
								self.next()

					if self.tok:
						if type(var) == str:
							self.store(var, val, True)
						else:
							if type(val) not in [float, int]:
								if len(val) == len(var):
									index = 0
									for i in val:
										key = var[index]
										self.store(key, i, True)
										index+=1
								else:
									error = f"'var' length must be equal to 'value' length\n... a, b, c = (1,2,3)"
									self.handleError(tactErrors(error, 'TypingError', f"[TypingError] 'Var' length must be equal to 'Value' length\n... a, b, c = (1,2,3)."))
							else:
								error = f"Defining method supports only iterable data not '{val}'."
								self.handleError(tactErrors(error, 'TypingError', error))

				elif self.tok.type in ['NEWLINE', 'SEMI-COLON']:
					self.next()
					if type(var) == str:
						self.store(var, 'undefined', True)
					else:
						for i in var:
							self.store(i, 'undefined', True)

				else:
					# incase of invalid syntax
					self.error('SyntaxError', f"Invalid syntax during 'let' variable defining\n... {self.tok.value}")

			elif self.tok.type == 'SELF':
				self.next()

				if self.tok and self.tok.type == 'DOT':
					self.next()

					if not self.tok or self.tok.type != 'IDENTIFIER':
						# fake syntax
						self.error('SyntaxError', f"Expected an identifier next.\n... {self.tok.value}")

					else:
						var = self.tok.value
						self.next()

						if self.tok and self.tok.type == 'COMMA':
							self.next()
							var = [var]

							while self.tok and self.tok.type not in ['EQUALS', 'SEMI-COLON', 'NEWLINE']:
								if self.tok.type == 'IDENTIFIER':
									var.append(self.tok.value)
									self.next()
								elif self.tok.type == 'COMMA':
									self.next()
								else:
									self.error('SyntaxError', f"Invalid syntax while declaring object attributes\n... '{self.tok.value}'.")

						if self.tok == None:
							# incase something happened
							pass

						elif self.tok.type == 'EQUALS':
							self.next()
							val = self.eval(['NEWLINE', 'SEMI-COLON'])

							if self.tok:
								if self.tok.type == 'COMMA':
									val = [val]
									self.next()

									while self.tok and self.tok.type not in ['NEWLINE', 'SEMI-COLON']:
										val.append(self.eval(['NEWLINE', 'SEMI-COLON', 'COMMA']))

										if self.tok and self.tok.type == 'COMMA':
											self.next()

								if self.tok:
									if type(var) == str:
										setattr(self.obj, var, val)
									else:
										if type(val) not in [float, int]:
											if len(val) == len(var):
												index = 0
												for i in val:
													setattr(self.obj, var[index], i)
													index+=1
											else:
												self.error('TypingError', f"'Variable' length must be equal to 'Value' length\n... [a,b,c] = (1,2,3)")
										else:
											self.error('TypingError', f"Method does not support data of type \n... '[float, int, functions, objects]'")

						elif self.tok.type in ['PLUS-TO', 'MINUS-TO', 'MULT-TO', 'DIV-TO', 'PLUS', 'MINUS', 'MULT', 'DIV', 'MOD']:
							op = self.tok.value
							self.next()

							if type(var) == list:
								self.error('TypingError', f"Attributes incremation applies to a single attribute at atime.")
							else:
								if hasattr(self.obj, var):
									val = self.eval(['NEWLINE', 'SEMI-COLON'])
									ans = self.get(var, 0)
									exe = True

									if self.tok:
										if op == '+=':
											ans = ans + val
										elif op == '-=':
											ans = ans - val
										elif op == '*=':
											ans = ans * val
										elif op == '/=':
											ans = ans / val
										else:
											if op == '+':
												ans = ans + val
											elif op == '-':
												ans = ans - val
											elif op == '*':
												ans = ans * val
											elif op == '/':
												ans = ans / val
											else:
												ans = ans % val

											if 'stdin' in self.mode:
												self.console(ans)
												ans = None

											exe = None


										if exe:
											setattr(self.obj, var, ans)
								else:
									self.error('AttributeError', f"'{var}' isn't an attribute of this 'Object'.\n... {self.obj}")

						elif self.tok.type in ['NEWLINE', 'SEMI-COLON']:
							self.next()

							if type(var) == str:
								self.obj[var] = 'undefined'
							else:
								for i in var:
									setattr(self.obj, i, 'undefined')

						elif self.tok.type in ['LPAREN', 'DOT', 'LCURL']:
							while self.tok.type != 'SELF':
								self.prev()

							output = self.eval(['NEWLINE', 'SEMI-COLON'])

							if 'stdin' in self.mode:
								self.console(output)

						else:
							self.error('SyntaxError', f"Uknown syntax '{self.tok.value}'.")
				else:
					if 'stdin' in self.mode:
						self.console(self.get('self'))

			elif self.tok.type == 'IF':
				execute = True
				res = [None, None, None, {}]

				while self.tok:
					if self.tok.type in ['IF', 'ELIF', 'ELSE']:

						if self.tok.type in ['IF', 'ELIF']:
							master = self.tok.type
							self.next()

							condition = self.eval(['NEWLINE', 'LBRACE'])

							if self.tok:
								if self.tok.type != 'NEWLINE':
									toks = self.collecttoks()
								else:
									toks = self.tokens_()

								if master == 'IF':
									execute = True

								if condition and execute:
									execute = False

									res = Parser([toks, []], [self.symbol_, True, self.recursive], self.Cmode('if-statement'), self.obj, self.traces).result()
								else:
									pass

						else:
							self.next()

							if self.tok:
								if self.tok.type != 'NEWLINE':
									toks = self.collecttoks()
								else:
									toks = self.tokens_()

								if execute:
									res = Parser([toks, []], [self.symbol_, True, self.recursive], self.Cmode('else-statement'), self.obj, self.traces).result()
								else:
									pass

								break

					elif self.pos < len(self.toks) - 1 and self.tok.type == 'NEWLINE':
						# pass
						self.next()

					else:
						# checking if loop has ended
						break

				self.stop = res[1]
				self.return_ = res[0]
				self.foundError = res[2]

				if len(res[3]):
					# checking to update object
					self.object_.update(res[3])

				if res[1] in ['break', 'return-break'] or res[2]:
					# incase of break or return
					self.terminate()

				elif res[1] == 'continue':
					self.pos = len(self.toks)-1
					self.tok = self.toks[self.pos]
					self.next()

			elif self.tok.type == 'WLOOP':
				self.next()
				condition = self.eval(['NEWLINE'])

				if condition:
					self.next()
				else:
					self.terminate()

			elif self.tok.type == 'FOR':
				self.next()

				var = []
				ret = None

				while self.tok and self.tok.type != 'IN':
					if self.tok.type == 'IDENTIFIER':
						var.append(self.tok.value)
						self.next()
					elif self.tok.type in ['COMMA', 'NEWLINE']:
						self.next()
					else:
						self.error("SyntaxError', f'Only Identifiers or Commas expected before 'in'.")

				self.next()
				iterable = self.eval(['RBRACE', 'NEWLINE'])

				if self.tok:
					ret = None
					fla = True

					if 'iterator' in str(type(iterable)) or 'generator' in str(type(iterable)):
						# pass if its generator or iter
						fla = 'iter'

					else:
						if len(var) > 1:
							if len(var) != len(iterable[0]):
								fla = False
								error = f"'for-loop' has un-equal items to unpack."
								self.handleError(tactErrors(error, 'TypingError', f"[TypingError] {error}"))
							else:
								pass

						# proving that data is iterable
						old_iter = iterable
						proof = self.proof_iter(iterable, fla)

						fla = proof[0]
						iterable = proof[1]


					if iterable == '__not__iterable_7ebcfefrxxq__':
						error = f"'{type(old_iter)}' object is not iterable."
						self.handleError(tactErrors(error, 'TypingError', f"[TypingError] {error}"))

					else:
						pass

					if self.tok.type != 'NEWLINE':
						toks = self.collecttoks()
					else:
						toks = self.tokens_()

					if fla == 'iter':
						# incase they are generators
						ret = Parser([toks, [var, iterable]], [self.symbol_, True, self.recursive], self.Cmode('for-loop'), self.obj, self.traces).result()

					else:
						if fla and iterable not in ['not iterable', None]:
							# successfully
							ret = Parser([toks, [var, iterable]], [self.symbol_, True, self.recursive], self.Cmode('for-loop'), self.obj, self.traces).result()
						else:
							pass

					if ret:
						self.stop = ret[1]
						self.return_ = ret[0]
						self.foundError = ret[2]

						if len(ret[3]):
							# checking to update object
							self.object_.update(ret[3])

						if ret[1] == 'return-break' or ret[2]:
							self.terminate()

			elif self.tok.type == 'WHILE':
				self.next()

				condition = self.eval(['NEWLINE', 'LBRACE'])
				count = -1

				if self.tok:
					while self.tok.type != 'WHILE':
						self.prev()
						count += 1
					
					self.next()
					# count -= 1
					toks = [Eslexer.Token('WLOOP', self.tok.line, 'while', self.tok.file, self.tok.pos, self.tok.tab)]

					while count:
						toks.append(self.tok)
						self.next()
						count -= 1

					toks.append(Eslexer.Token('NEWLINE', self.tok.line, r'\n', self.tok.file, self.tok.pos, self.tok.tab))

					if self.tok.type != 'NEWLINE':
						toks += self.collecttoks()
					else:
						toks += self.tokens_()

					if condition:
						ret = Parser([toks, []], [self.symbol_, True, self.recursive], self.Cmode('while-loop'), self.obj, self.traces).result()

						self.stop = ret[1]
						self.return_ = ret[0]
						self.foundError = ret[2]

						if len(ret[3]):
							# checking to update object
							self.object_.update(ret[3])

						if ret[1] == 'return-break' or ret[2]:
							self.terminate()

					else:
						pass

			elif self.tok.type == 'SWITCH':
				self.next()
				switch = self.eval(['NEWLINE', 'LBRACE'])

				solved = True
				stop = False

				ret = [None, None, None, {}]

				if self.tok:
					while self.tok and self.tok.type != 'LBRACE':
						self.next()

					self.next()

					while self.tok:
						if self.tok.type == 'CASE':
							self.next()
							case = self.eval(['COLON'])
							self.next()

							if self.tok:
								toks = self.tokens_()
								check = toks.copy()
								check.reverse()

								if case == switch and not stop:
									solved = False
									
									for i in check:
										if i.type in ['NEWLINE', 'SEMI-COLON']:
											pass
										elif i.type == 'TERMIN':
											stop = True
											break
										else:
											break

									ret = Parser([toks, []], [self.symbol_, True, self.recursive], self.Cmode('switch-statement'), self.obj, self.traces).result()

									self.stop = ret[1]
									self.return_ = ret[0]
									self.foundError = ret[2]

									if len(ret[3]):
										# checking to update object
										self.object_.update(ret[3])

									if ret[1] in ['break', 'return-break'] or ret[2]:
										# incase of break or return
										self.terminate()

									elif ret[1] == 'continue':
										self.pos = len(self.toks)-1
										self.tok = self.toks[self.pos]
										self.next()
										break

									if self.tok and stop and self.tok.type != 'RBRACE':
										count = 1

										while count and self.tok:
											if self.tok.type == 'LBRACE':
												count += 1
											elif self.tok.type == 'RBRACE':
												count -= 1

											self.next()
										break
								
								else:
									pass

						elif self.tok.type == 'DEFAULT':
							self.next()
							self.next()

							toks = self.tokens_()
							check = toks.copy()
							check.reverse()

							if solved or not stop:
								for i in check:
									if i.type in ['NEWLINE', 'SEMI-COLON']:
										pass
									elif i.type == 'BREAK':
										stop = True
										break
									else:
										break

								ret = Parser([toks, []], [self.symbol_, True, self.recursive], self.Cmode('switch-statement'), self.obj, self.traces).result()

								self.stop = ret[1]
								self.return_ = ret[0]
								self.foundError = ret[2]

								if len(ret[3]):
									# checking to update object
									self.object_.update(ret[3])

								if ret[1] == 'return-break' and ret[2]:
									self.terminate()
								elif ret[1] == 'continue':
									self.pos = len(self.toks)-1
									self.tok = self.toks[self.pos]
									self.next()

						elif self.tok.type == 'RBRACE':
							self.next()
							break

						else:
							self.next()

			elif self.tok.type == 'TRY':
				self.next()

				if self.tok.type != 'NEWLINE':
					ty = self.collecttoks()
				else:
					ty = self.tokens_()

				while self.tok and self.tok.type == 'NEWLINE':
					self.next()

				if self.tok and self.tok.type == 'CATCH':
					self.next()

					err = self.eval(['AS'])

					if self.tok:
						if type(err) == str:
							err = [err]

						self.next()
						ident = self.tok.value
						self.next()

						if self.tok.type != 'NEWLINE':
							ct = self.collecttoks()
						else:
							ct = self.tokens_()

						while self.tok and self.tok.type == 'NEWLINE':
							self.next()

						fn = None
						key = None

						if self.tok and self.tok.type == 'FINALLY':
							self.next()

							if self.tok.type != 'NEWLINE':
								fn = self.collecttoks()
							else:
								fn = self.tokens_()

						if 'Keyboard' in err:
							try:
								res = Parser([ty, []], [self.symbol_, True, self.recursive], self.Cmode('try-catch'), self.obj, self.traces).result()
							except KeyboardInterrupt as Key:
								key = Key

						else:
							res = Parser([ty, []], [self.symbol_, True, self.recursive], self.Cmode('try-catch'), self.obj, self.traces).result()

						if not key and not res[2]:
							self.stop = res[1]
							self.return_ = res[0]

							if len(res[3]):
								# checking to update object
								self.object_.update(res[3])

							if res[1] == 'return-break':
								self.terminate()

						else:
							exe = False

							if key:
								self.symbol_[ident] = key
								exe = True

							elif 'Error' in err:
								self.symbol_[ident] = res[2]
								exe = True


							if exe:
								res = Parser([ct, []], [self.symbol_, True, self.recursive], self.Cmode(), self.obj, self.traces).result()
							else:
								error = res[2]
								self.handleError(tactErrors(error, 'SyscallError', error))

							self.stop = res[1]
							self.return_ = res[0]

							if len(res[3]):
								# checking to update object
								self.object_.update(res[3])

							if res[1] == 'return-break':
								# incase of return
								self.terminate()

							elif fn:
								res = Parser([fn, []], [self.symbol_, True, self.recursive], self.Cmode(), self.obj, self.traces).result()

								self.stop = res[1]
								self.return_ = res[0]

								if res[1] == 'return-break':
									self.terminate()

							else:
								pass

				else:
					self.error('TypingError', 'Missing required catch statement.')

			elif self.tok.type == 'RETURN':
				self.next()
				if self.tok == None or self.tok.type in ['NEWLINE', 'SEMI-COLON']:
					self.stop = 'return-break'
					break
				else:
					ret = self.eval(['COMMA', 'NEWLINE', 'SEMI-COLON'])

					if self.tok.type == 'COMMA':
						self.next()
						ret = [ret]

						while self.tok.type not in ['NEWLINE', 'SEMI-COLON']:
							if self.tok.type == 'COMMA':
								self.next()

							ret.append(self.eval(['NEWLINE', 'SEMI-COLON', 'COMMA']))

						self.return_ = tuple(ret)
					else:
						self.return_ = ret

					self.stop = 'return-break'
					break

			elif self.tok.type == 'FN':
				self.next()

				fn_name = self.tok.value
				fn_file = self.tok.file
				fn_line = self.tok.line
				trc = self.tok
				self.next()

				if self.tok.type != 'LPAREN':
					self.error('SyntaxError', f"During defining method '{fn_name}', found missing char\n... '(' -> function main()")
				else:
					self.next()

					args = self.collectargs()

					if self.tok.type != 'NEWLINE':
						toks = self.collecttoks()
					else:
						toks = self.tokens_()

					node = self.fnNode(fn_name, args, toks, fn_file, fn_line)

					if 'class-object' in self.mode:
						self.store(fn_name, node)
						self.object_[fn_name] = node
					else:
						self.store(fn_name, node)

			elif self.tok.type == 'CLASS':
				self.next()
				cl_name = self.tok.value
				cl_line = self.tok.line
				cl_file = self.tok.file

				self.next()
				inherit = None
				replace = None

				if self.tok.type == 'LPAREN':
					self.next()
					if self.tok.type == 'RPAREN':
						self.next()
					else:
						inherit = self.eval(['RPAREN'])
						self.next()

				if self.tok:
					if self.tok.type != 'NEWLINE':
						toks = self.collecttoks()
					else:
						toks = self.tokens_()

					clNode = self.clNode(cl_name, toks, cl_line, cl_file, inherit, replace)
					self.store(cl_name, clNode)

			elif self.tok.type == 'IMPORT':
				self.next()
				self.importmodule()

			elif self.tok.type == 'USING':
				self.next()
				self.importBuiltin()

			elif self.tok.type in ['BREAK', 'CONTINUE']:
				valut = self.tok.value
				self.next()

				if valut == 'break':
					self.terminate()
					self.stop = 'break'
					break
				else:
					self.pos = len(self.toks)-1
					self.tok = self.toks[self.pos]

					self.stop = 'continue'
					self.next()

			elif self.tok.type == 'EACH':
				self.next()

				if self.tok.type == 'IMPORT':
					self.next()
					self.importBuiltin()
				else:
					pass

			elif self.tok.type in ['PASS', 'TERMIN', 'STRING', 'INTEGER', 'FLOAT', 'QUESTION']:
				if 'stdin' in self.mode and self.tok.type not in ['PASS', 'TERMIN']:
					self.console(self.eval(['NEWLINE', 'SEMI-COLON']))
					self.next()
				elif self.tok.type == 'QUESTION':
					self.eval(['NEWLINE', 'SEMI-COLON'])
				else:
					self.next()

			elif self.tok.type == 'CLS':
				self.next()
				self.next()

				if self.obj != None:
					args = self.collectpara()

					cl = self.obj.__inherit__

					if hasattr(cl, '__eliotclass__'):
						cl = cl(*args)
						for i in dir(cl):
							if i not in dir(self.obj):
								setattr(self.obj, i, getattr(cl, i))
					else:
						self.obj.__inherit__.__init__(self.obj, *args)

					self.next()

				else:
					error = "'None' can not be inheritable"
					self.handleError(tactErrors(error, 'TypingError', f"[TypingError] {error}"))
			
			else:
				self.next()


def Runtime(path):
	path_ = None
	found = True

	for i in EliotSys.path:
		__path__ = os.path.join(i, path)

		if os.path.exists(__path__):
			path = __path__
			found = True
			break
		else:
			found = False

	if found:
		if os.path.isdir(path):
			if 'main.eliot' in os.listdir(path):
				path_ = os.path.join(path, 'main.eliot')
			else:
				for i in os.listdir(path):
					if i.endswith('.eliot'):
						path_ = os.path.join(path, i)
						break
					else:
						pass

			if path_ != None:
				with open(path, 'r') as src:
					code = src.read() + '\n'
					src.close()

				try:
					Parser([code, path], [{'Eliot': Eliot()}, True, path], 'main')
				except KeyboardInterrupt as e:
					print(e)
					quit()
			else:
				print(f"not '.artl' file found in directory.")
				quit()

		else:
			with open(path, 'r') as src:
				code = src.read() + '\n'
				src.close()

			try:
				Parser([code, path], [{'Eliot': Eliot()}, True, path], ['main'])
			except KeyboardInterrupt as e:
				print(e)
				quit()
	
	else:
		print(f"file '{path}' does not exists.")

	return 0

def Console():
	code = ''
	try:
		scope = Parser([code, 'stdin'], [{'Eliot': Eliot()}, True, 'stdin'], ['stdin']).symbol_
	except KeyboardInterrupt as e:
		print('Keyboard Interruption')
	except Exception as e:
		print(e)
		scope = Parser([code, 'stdin'], [{'Eliot': Eliot()}, True, 'stdin'], ['stdin']).symbol_

	while True:
		try:
			code = input('~ ')
			if code == '.exit'.strip(' '):
				sys.exit()

			code += '\n'
		except EOFError as e:
			sys.exit()
		except KeyboardInterrupt as e:
			print('Keyboard Interruption')
			code = '\n'

		if code.lstrip(' ').lstrip('\t').startswith('.'):
			statement_code = ''

			while 1:
				try:
					code = input('   ') + '\n'
				except EOFError:
					break
					sys.exit()
				except KeyboardInterrupt as e:
					print('Keyboard Interruption')
					code = '\n'

				if not code.lstrip(' ').lstrip('\t').startswith('.'):
					statement_code += code
				else:
					break

			code = statement_code
		try:
			scope = Parser([code, 'stdin'], [scope, True, 'stdin'], ['stdin']).symbol_
		except KeyboardInterrupt as e:
			print(e)
			scope = Parser([code, 'stdin'], [scope, True, 'stdin'], ['stdin']).symbol_
		except Exception as e:
			scope = Parser([code, 'stdin'], [scope, True, 'stdin'], ['stdin']).symbol_

def Interpreter():
	argv = sys.argv

	if len(argv) > 1:
		if argv[1] == '--build':
			if len(argv) > 2:
				project = argv[2]
			else:
				project = 'app'

			if not os.path.exists(project):
				os.makedirs(project)

			if not os.path.exists(os.path.join(project, 'main.eliot')):
				fl = open(os.path.join(project, 'main.eliot'), 'w')
				fl.write("Eliot.print('hello world!')\n")
				fl.close()

			if not os.path.exists(os.path.join(project, 'imports.py')):
				fx = open(os.path.join(project, 'imports.py'), 'w')
				fx.close()

			for i in ['py_modules', 'eliot_modules']:
				if not os.path.exists(os.path.join(project, i)):
					os.makedirs(os.path.join(project, i))

			print('  Successfully made project')
			print(colorama.Fore.GREEN, end='')
			print(f"        {os.path.abspath(project)}")
			print(colorama.Style.RESET_ALL)

			print('  (Project files include)')
			data = os.listdir(project)
			data.sort()
			print(colorama.Fore.GREEN, end='')

			for i in data:
				print(f'        {i}')

			print(colorama.Style.RESET_ALL)

		else:
			# sends given path to eliot runtime
			Runtime(argv[1])
	
	else:
		# run in console
		print(f'Eliot 1.0 Beta {platform.python_compiler()}..')
		print(f'{platform.version()}\n..')
		Console()
