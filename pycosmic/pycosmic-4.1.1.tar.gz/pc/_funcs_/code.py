import inspect 


__all__ = ["get_params","codeof","get_doc"]

def get_params(val):
	return inspect.signature(val)


def codeof(name):
	return inspect.getsource(name)


def get_doc(name):
	return inspect.getdoc(name)











	

