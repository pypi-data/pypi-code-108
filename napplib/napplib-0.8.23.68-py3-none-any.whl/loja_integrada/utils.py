from functools import wraps


def return_response(accept_status: int = 200):
	def _decorate(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			response = func(*args, **kwargs)
			status = response.status_code
			url = str(response.url).split("?")[0]
			method =  response.request.method
			if status != accept_status:
				print(f"({status})[{method}]{url} - Request failed: {response.content}")
				return None
			print(f"({status})[{method}]{url} - Request success!!")
			return response
		return wrapper
	return _decorate