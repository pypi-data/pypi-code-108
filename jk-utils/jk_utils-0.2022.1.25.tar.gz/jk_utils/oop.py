


def singleton(clazz):
	assert clazz
	assert type(clazz) == type

	clazz.instance = clazz()
	clazz.INSTANCE = clazz.instance

	return clazz
#






