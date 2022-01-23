import inspect


def test_general_fun():
    pass


async def test_asunc_fun():
    await test_async_fun_2()


async def test_async_fun_2():
    pass


print("++++++++++ General function checking ++++++++++")
__isasyncgen = inspect.isasyncgen(test_general_fun)
print("isasyncgen: ", __isasyncgen)
__isawaitable = inspect.isawaitable(test_general_fun)
print("isawaitable: ", __isawaitable)
__iscoroutine = inspect.iscoroutine(test_general_fun)
print("iscoroutine: ", __iscoroutine)
__iscoroutinefunction = inspect.iscoroutinefunction(test_general_fun)
print("iscoroutinefunction", __iscoroutinefunction)
__isasyncgenfunction = inspect.isasyncgenfunction(test_general_fun)
print("isasyncgenfunction: ", __isasyncgenfunction)


print("++++++++++ Async function checking ++++++++++")
__isasyncgen = inspect.isasyncgen(test_asunc_fun)
print("isasyncgen: ", __isasyncgen)
__isawaitable = inspect.isawaitable(test_asunc_fun)
print("isawaitable: ", __isawaitable)
__iscoroutine = inspect.iscoroutine(test_asunc_fun)
print("iscoroutine: ", __iscoroutine)
__iscoroutinefunction = inspect.iscoroutinefunction(test_asunc_fun)
print("iscoroutinefunction", __iscoroutinefunction)
__isasyncgenfunction = inspect.isasyncgenfunction(test_asunc_fun)
print("isasyncgenfunction: ", __isasyncgenfunction)


"""

++++++++++ General function checking ++++++++++
isasyncgen:  False
isawaitable:  False
iscoroutine:  False
iscoroutinefunction False
isasyncgenfunction:  False
++++++++++ Async function checking ++++++++++
isasyncgen:  False
isawaitable:  False
iscoroutine:  False
iscoroutinefunction True
isasyncgenfunction:  False

"""
