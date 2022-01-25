#!/usr/bin/env python
# coding: utf-8

# # 类型提示
# 
# {mod}`typing` 提供了对类型提示的运行时支持。最基本的支持包括 {data}`Any`, {data}`Union`, {data}`Callable`, {class}`TypeVar`, 和 {class}`Generic`。
# 
# 示例：

# In[10]:


def greeting(name: str) -> str:
    return 'Hello ' + name

getattr(greeting, '__annotations__', None)


# ## 类型别名
# 
# 把类型赋给别名，就可以定义类型别名。本例中，`Vector` 和 `list[float]` 相同，可互换：

# In[13]:


Vector = list[float]

def scale(scalar: float, vector: Vector) -> Vector:
    return [scalar * num for num in vector]

# 类型检查；一个浮点数的列表可以作为一个向量
new_vector = scale(2.0, [1.0, -4.2, 5.4])
new_vector


# 类型别名适用于简化复杂的类型签名。例如：

# In[21]:


from collections.abc import Sequence
from typing import NoReturn


ConnectionOptions = dict[str, str]
Address = tuple[str, int]
Server = tuple[Address, ConnectionOptions]

def broadcast_message(message: str, servers: Sequence[Server]) -> NoReturn:
    ...

# 静态类型检查器会将之前的类型签名视为与此完全等价。
def broadcast_message(
        message: str,
        servers: Sequence[tuple[tuple[str, int], dict[str, str]]]) -> NoReturn:
    ...


# ## NewType
# 
# 使用 {class}`typing.NewType` 创建简单的唯一类型，几乎没有运行时的开销。`NewType(name, tp)` 被认为是 `tp` 的子类型。在运行时，`NewType(name, tp)` 简单地返回其参数的 dummy 函数。使用方法：

# In[3]:


from typing import NewType

UserId = NewType('UserId', int)

def name_by_id(user_id: UserId) -> str: ...

UserId('user') # 类型检查失败
name_by_id(42) # 类型检查失败
name_by_id(UserId(42))  # 正确
num = UserId(5) + 1     # 类型：`int`


# 1. 静态类型检查器把新类型当作原始类型的子类，这种方式适用于捕捉逻辑错误。
# 2. `NewType` 声明把一种类型当作另一种类型的子类型。`Derived = NewType('Derived', Original)` 时，静态类型检查器把 `Derived` 当作 `Original` 的子类 ，即，`Original` 类型的值不能用在预期 `Derived` 类型的位置。这种方式适用于以最小运行时成本防止逻辑错误。
# 3. 继承 `NewType` 声明的子类型是无效的。
# 
# ## 可调对象
# 
# 预期特定签名回调函数的框架可以用 `Callable[[Arg1Type, Arg2Type], ReturnType]` 实现类型提示。

# In[5]:


from typing import Callable

def feeder(get_next_item: Callable[[], str]) -> None:
    # Body
    ...

def async_query(on_success: Callable[[int], None],
                on_error: Callable[[int, Exception], None]) -> None:
    # Body
    ...


# 无需指定调用签名，用省略号字面量替换类型提示里的参数列表： `Callable[..., ReturnType]`，就可以声明可调对象的返回类型。
# 
# 以其他可调用对象为参数的可调用对象可以使用 `ParamSpec` 来表明其参数类型是相互依赖的。此外，如果该可调用对象增加或删除了其他可调用对象的参数，可以使用 `Concatenate` 操作符。它们分别采取 `Callable[ParamSpecVariable, ReturnType]` 和 `Callable[Concatenate[Arg1Type, Arg2Type, ..., ParamSpecVariable], ReturnType]` 的形式。
# 
# ## 泛型
# 
# 容器中，对象的类型信息不能以泛型方式静态推断，因此，抽象基类扩展支持下标，用于表示容器元素的预期类型。

# ```python
# from typing import Mapping, Sequence
# 
# def notify_by_email(employees: Sequence[Employee],
#                     overrides: Mapping[str, str]) -> None: ...
# ```
# 
# {class}`typing.TypeVar` 工厂函数实现泛型参数化。
# 
# ```python
# from typing import TypeVar
# 
# T = TypeVar('T')      # Declare type variable
# 
# def first(l: Sequence[T]) -> T:   # Generic function
#     return l[0]
# ```
# 
# ## 用户定义的泛型类型
# 
# 用户定义的类可以定义为泛型类。

# In[6]:


from typing import TypeVar, Generic
from logging import Logger

T = TypeVar('T')

class LoggedVar(Generic[T]):
    def __init__(self, value: T, name: str, logger: Logger) -> None:
        self.name = name
        self.logger = logger
        self.value = value

    def set(self, new: T) -> None:
        self.log('Set ' + repr(self.value))
        self.value = new

    def get(self) -> T:
        self.log('Get ' + repr(self.value))
        return self.value

    def log(self, message: str) -> None:
        self.logger.info('%s: %s', self.name, message)


# `Generic[T]` 是定义类 `LoggedVar` 的基类，该类使用单类型参数 `T`。在该类体内，`T` 是有效的类型。

# 
