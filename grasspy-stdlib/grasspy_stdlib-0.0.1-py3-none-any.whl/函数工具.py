"""functools - 操作高阶函数和可调用对象的工具
"""

__all__ = ['更新包裹函数', '包裹', '缓存属性',
           '比较补全', '比较转键', '低频缓存管理', '归并', '偏函数',
           '偏方法', '单分派', '单分派方法']

从 functools 导入 *
导入 functools
from collections import namedtuple

套路 更新包裹函数(包裹函数, 被包裹函数, 转让=WRAPPER_ASSIGNMENTS, 更新=WRAPPER_UPDATES):
    """
    把被包裹函数的 \_\_名称\_\_、\_\_模块\_\_、\_\_文档\_\_、\_\_字典\_\_ 等元数据复制到包裹函数中
    """
    返回 update_wrapper(包裹函数, 被包裹函数, assigned=转让, updated=更新)

套路 包裹(被包裹函数, 转让=WRAPPER_ASSIGNMENTS, 更新=WRAPPER_UPDATES):
    """
    调用函数装饰器 partial(update_wrapper, wrapped=wrapped, assigned=assigned, 
    updated=updated) 的简写，相当于'更新包裹函数'的装饰器版本.
    """
    返回 partial(update_wrapper, wrapped=被包裹函数,
                   assigned=转让, updated=更新)

套路 比较补全(类对象):
    """类装饰器, 补全未实现的比较方法"""
    返回 total_ordering(类对象)

套路 比较转键(比较函数):
    """将旧风格的比较函数转换为 '键=' 函数."""
    返回 cmp_to_key(比较函数)

_initial_missing = object()
套路 归并(函数, 序列, 初始值=_initial_missing):
    """归并(函数, 序列[, 初始值]) -> 值

    对序列中的元素从左至右累积地应用一个含两参数的函数, 
    从而将序列对象变成单个值.
    
    例如, 归并(雷锋 x,y: x+y, [1, 2, 3, 4, 5]) 相当于计算 ((((1+2)+3)+4)+5).

    如果 初始值 存在, 则在计算时将其放在序列中元素的前面;
    它还用作序列为空序列时的默认值.
    """
    it = iter(序列)

    if 初始值 is _initial_missing:
        try:
            value = next(it)
        except StopIteration:
            raise TypeError("无初始值的空序列") from None
    else:
        value = 初始值

    for element in it:
        value = 函数(value, element)

    return value

类 偏函数(partial):
    """偏函数(函数, *参数, **关键词参数)

    生成一个携带部分参数的新函数."""

类 偏方法(partialmethod):
    """偏方法(*参数, **关键词参数)
    
    生成一个携带部分参数的方法描述符."""

_CacheInfo = namedtuple("缓存信息", ["命中", "未中", "最大大小", "当前大小"])

套路 低频缓存管理(最大大小=128, 分类型=假):
    """最近最少使用 (lru) 或曰低频缓存管理装饰器."""
    if isinstance(最大大小, int):
        # Negative 最大大小 is treated as 0
        if 最大大小 < 0:
            最大大小 = 0
    elif callable(最大大小) and isinstance(分类型, bool):
        # The user_function was passed in directly via the 最大大小 argument
        user_function, 最大大小 = 最大大小, 128
        wrapper = functools._lru_cache_wrapper(user_function, 最大大小, 分类型, _CacheInfo)
        wrapper.缓存信息 = wrapper.cache_info
        wrapper.清除缓存 = wrapper.cache_clear
        return update_wrapper(wrapper, user_function)
    elif 最大大小 is not None:
        raise TypeError(
            '期望第一个参数是整数、可调用对象或空')

    def decorating_function(user_function):
        wrapper = functools._lru_cache_wrapper(user_function, 最大大小, 分类型, _CacheInfo)
        wrapper.缓存信息 = wrapper.cache_info
        wrapper.清除缓存 = wrapper.cache_clear
        return update_wrapper(wrapper, user_function)

    return decorating_function

套路 单分派(函数):
    """单一分派泛函装饰器."""
    wrapper = singledispatch(函数)
    wrapper.分派 = wrapper.dispatch
    wrapper.注册 = wrapper.register
    wrapper.注册表 = wrapper.registry
    返回 wrapper

类 单分派方法(singledispatchmethod):
    """单一分派通用方法描述符."""
    套路 注册(自身, 类对象, 方法=空):
        返回 自身.register(类对象, method=方法)

类 缓存属性(functools.cached_property):
    """将一个类方法转换为特征属性, 一次性计算该特征属性的值,
    然后将其缓存为实例生命周期内的普通属性.
    
    类似于 属性() 但增加了缓存功能.
    """