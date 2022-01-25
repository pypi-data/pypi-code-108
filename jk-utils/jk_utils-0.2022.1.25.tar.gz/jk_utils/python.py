

import sys
import os
import inspect







def getMainModule():
	# based on: https://stackoverflow.com/questions/990422/how-to-get-a-reference-to-current-modules-attributes-in-python

	# search for first module in the stack
	stack_frame = inspect.currentframe()
	while stack_frame:
		#print('***', stack_frame.f_code.co_name, stack_frame.f_code.co_filename, stack_frame.f_lineno)
		if stack_frame.f_code.co_name == '<module>':
			if stack_frame.f_code.co_filename != '<stdin>':
				caller_module = inspect.getmodule(stack_frame)
			else:
				# piped or interactive import
				caller_module = sys.modules['__main__']
			if not caller_module is None:
				#... do something here ...
				#print("X")
				#for k, v in stack_frame.f_globals.items():
				#	print("-- " + k + ":", v)
				return sys.modules[stack_frame.f_globals["__name__"]]
			break
		stack_frame = stack_frame.f_back
#

def getMainModuleFilePath():
	mainModule = getMainModule()
	assert mainModule
	return os.path.realpath(mainModule.__file__)
#

def getMainModuleDirPath():
	mainModule = getMainModule()
	assert mainModule
	return os.path.dirname(os.path.realpath(mainModule.__file__))
#










