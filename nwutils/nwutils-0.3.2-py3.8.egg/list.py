from typing import List, T

# @brief Flattens a list of lists
# @return The flattened list
def flattenList(x: List[List[T]]) -> List[T]:
	if x == []:
		return []
	res = []
	for item in x:
		if isinstance(item, list):
			res.extend(flattenList(item))
		else:
			res.append(item)
	return res