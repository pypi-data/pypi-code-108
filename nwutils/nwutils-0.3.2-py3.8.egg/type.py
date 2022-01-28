from typing import Union, TypeVar, List, Sequence # type: ignore

# @brief Returns true if whatType is subclass of baseType. The parameters can be instantiated objects or types. In the
#  first case, the parameters are converted to their type and then the check is done.
def isBaseOf(whatType, baseType):
	if not isinstance(whatType, type):
		whatType = type(whatType)
	if not isinstance(baseType, type):
		baseType = type(baseType)
	return baseType in type(object).mro(whatType)

# Given a Type and a dictionary of {Type : Item}, returns the first Item that matches any ancestor of Type (assumed in
#  order of importance!)
# Example: B (extends) A (extends) Base (extends) Object
# pickTypeFromMRO(B, {Base: "msg1", A: "msg2", Object: "msg3"}) will return msg2 because that's how mro() works.
def pickTypeFromMRO(Type, switchType):
	Type = Type if isinstance(Type, type) else type(Type)
	typeMRO = Type.mro()
	for Type in typeMRO:
		if Type in switchType:
			return switchType[Type]
	assert False, "%s not in %s" % (typeMRO, switchType)

# @brief Returns true if the item is of that particular type. Can be used for complex types (Number, Dict etc.) as
#  well, by checking __args__, which works on Unions.
# @param[in] item The item whose type is checked
# @param[in] Type The type 
def isType(item, Type) -> bool:
	itemType = item if isinstance(item, type) else type(item)
	if hasattr(Type, "__args__"): # type: ignore
		return itemType in Type.__args__ # type: ignore
	else:
		return itemType is Type # type: ignore
