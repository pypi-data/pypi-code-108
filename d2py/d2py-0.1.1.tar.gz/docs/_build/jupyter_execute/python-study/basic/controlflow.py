#!/usr/bin/env python
# coding: utf-8

# # 流程控制
# 
# Python 不仅仅需要可以求值的 [表达式](intro/basic-type) 与 [函数](function)，还需要一些结构用于表达循环和控制等。
# 
# Python **语句** 就是告诉你的程序应该做什么的句子。
# 
# - 程序由模块构成。
# - 模块包含语句。
# - 语句包含表达式。
# - 表达式建立并处理对象。
# 
# ## 真值测试
# 
# - 所有的对象都有一个固有的布尔值：真或假。
# - 任何非零的数字或非空的对象都是真。
# - `0`、空对象和特殊对象 `None` 被视为假。
# - 比较和相等测试是递归地应用于数据结构。
# - 比较和相等测试返回 `True` 或 `False`。
# - 布尔运算符 `and` 和 `or` 返回一个真或假的操作对象。
# - 一旦知道结果，布尔运算符就会停止评估（"短路"）。
# 
# 真值判定|结果
# :-|:-
# `X and Y`|如果 `X` 和 `Y` 都为真，则为真。
# `X or Y`|如果 `X` 或 `Y` 为真，则为真。
# `not X`|如果 `X` 是假的，则为真。
# 
# ### 比较、相等和真值
# 
# - `==` 操作符测试值的相等性。
# - `is` 表达式测试对象的一致性。
# 
# 真值判断：

# In[36]:


S1 = 'spam'
S2 = 'spam'

S1 == S2, S1 is S2


# 比较：

# In[37]:


L1 = [1, ('a', 3)] 
L2 = [1, ('a', 3)]

L1 == L2, L1 is L2, L1 < L2, L1 > L2


# In[38]:


bool('')


# ### 短路计算
# 
# - `or`: 从左到右求算操作对象，然后返回第一个为真的操作对象。
# - `and`: 从左到右求算操作对象，然后返回第一个为假的操作对象。

# In[39]:


2 or 3, 3 or 2


# In[40]:


[] or 3


# In[41]:


[] or {}


# In[42]:


2 and 3, 3 and 2


# In[43]:


[] and {}


# In[44]:


3 and []


# ### 断言
# 
# 用于测试推断：

# In[45]:


num = -1
assert num > 0, 'num 应该为正数！'


# ## `if` 条件

# In[46]:


year = 1990
if year % 4 == 0:
    if year % 400 == 0:
        print('闰年')
    elif year % 100 == 0:
        print('平年')
    else:
        print('闰年')
else:
    print('平年')


# 使用 `and` 与 `or` 的短路逻辑简化表达式：

# In[47]:


year = 1990
if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
    print('闰年')
else:
    print('平年')


# `if` 的短路（short-ciecuit）计算：`A = Y if X else Z`

# In[48]:


year = 1990
print('闰年') if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0 else print('平年')


# In[49]:


't' if 'spam' else 'f'


# ## `for` 循环
# 
# 遍历序列对象：
# 
# 
# ```python
# for target in object:                 # 将对象项目分配给目标   
#     statements                        # 循环体
# ```
# 
# - `pass` / `...`：空占位语句

# In[59]:


for i in range(5):
    ...  # 等价于 pass


# In[60]:


list(range(1, 10, 6))


# In[64]:


# 阶乘
x = 1
for i in range(1, 11):
    x *= i
print(f'10!={x}')


# Python 的 `for` 语句迭代列表或字符串等任意序列，元素的迭代顺序与在序列中出现的顺序一致。例如：

# In[61]:


# 可以是 Python 的可迭代容器
seq = [1, 2, 3, 4, 5] 
for i in seq:
    print(i)


# ### 循环的技巧
# 
# 在序列中循环时，用 {func}`enumerate` 函数可以同时取出位置索引和对应的值：

# In[65]:


for i, v in enumerate(['苹果', '相机', '飞机']):
    print(i, v)


# 同时循环两个或多个序列时，用 {func}`zip` 函数可以将其内的元素一一匹配：

# In[67]:


questions = ['名字', '缺点', '最喜爱的颜色']
answers = ['Judy', '比较懒', '天空蓝']
for q, a in zip(questions, answers):
    print(f'你的 {q} 是什么？ 答案是 {a}。')


# 逆向循环序列时，先正向定位序列，然后调用 {func}`reversed` 函数：

# In[68]:


for i in reversed(range(1, 10, 2)):
    print(i)


# 按指定顺序循环序列，可以用 {func}`sorted` 函数，在不改动原序列的基础上，重新返回一个序列：

# In[69]:


basket = ['apple', 'orange', 'apple', 'pear', 'orange', 'banana']
for i in sorted(basket, key=len):
    print(i)


# 使用 {func}`set` 去除序列中的重复元素。使用 {func}`sorted` 加 {func}`set` 则按排序后的顺序，循环遍历序列中的唯一元素：

# In[70]:


basket = ['apple', 'orange', 'apple', 'pear', 'orange', 'banana']
for f in sorted(set(basket)):
    print(f)


# ### 序列和其他类型的比较
# 
# 序列对象可以与相同序列类型的其他对象比较。这种比较使用 字典式 顺序：
# 
# - 首先，比较首个元素，如果不相等，则可确定比较结果；如果相等，则比较之后的元素，以此类推，直到其中一个序列结束。
# - 如果要比较的两个元素本身是相同类型的序列，则递归地执行字典式顺序比较。
# - 如果两个序列中所有的对应元素都相等，则两个序列相等。
# - 如果一个序列是另一个的初始子序列，则较短的序列可被视为较小（较少）的序列。
# - 对于字符串来说，字典式顺序使用 Unicode 码位序号排序单个字符。
# 
# 下面列出了一些比较相同类型序列的例子：

# In[71]:


(1, 2, 3) < (1, 2, 4)


# In[72]:


[1, 2, 3] < [1, 2, 4]


# In[73]:


'ABC' < 'C' < 'Pascal' < 'Python' # 支持链式比较


# In[74]:


(1, 2, 3, 4) < (1, 2, 4)


# In[75]:


(1, 2) < (1, 2, -1)


# In[76]:


(1, 2, 3) == (1.0, 2.0, 3.0)


# In[77]:


(1, 2, ('aa', 'ab'))   < (1, 2, ('abc', 'a'), 4)


# ## `while` 循环
# 
# `while` 循环结构：
# 
# ```python
# 初值条件
# while test:  # 循环测试
#     statements  # 循环体
# ```

# In[50]:


x = 'spam'
while x: # 直至耗尽 x
    print(x, end=' ')
    x = x[1:]


# In[52]:


x = 1  # 初值条件
while x <= 100:  # 终止条件
    print(x)
    x += 27


# ### Callataz 猜想
# 
# ```{note}
# 任意取一个正整数 $n$，如果 $n$ 是一个偶数，则除以 $2$ 得到 $n/2$；
# 如果 $n$ 是一个奇数，则乘以 $3$ 加 $1$ 得到 $3n+1$，重复以上操作，我们将得到一串数字。
# 
# Collatz 猜想：任何正整数 $n$ 参照以上规则，都将回归 $1$。
# ```

# In[53]:


def collatz_guess(num):
    assert num > 0, 'num 必须为正数'
    while num != 1:
        if num % 2 == 0:
            # 保证 num 在接下来的运算为整数
            num //= 2
        else:
            num *= 3 
            num += 1
    return num

collatz_guess(75)


# ### 斐波那契数列
# 
# ```{note}
# 斐波那契数列：
# 
# $$
# \begin{cases}
# f_0 = f_1 = 1\\
# f_{n+2} = f_{n} + f_{n+1}, & n \in \mathbb{N}
# \end{cases}
# $$
# ```

# In[2]:


def fib(n): # 写出斐波那契数列，直到n
    """打印直到 n 的斐波那契数列"""
    a, b = 0, 1
    while a < n:
        print(a, end=' ')
        a, b = b, a+b
    print()

fib(2000)


# ```{note}
# 1. 第一行中的 **多重赋值**：变量 `a` 和 `b` 同时获得新值 `0` 和 `1`。
# 2. 最后一行又用了一次多重赋值，这体现在右表达式在赋值前就已经求值了。**右表达式求值顺序为从左到右。**
# ```
# 
# ## `continue`
# 
# `continue`：跳到最近所在循环的开头处（来到循环的首行）

# In[54]:


x = 10
while x:
    x -= 1
    if x % 2 != 0:
        continue  # 跳过打印
    print(x, end=' ')


# In[24]:


for num in range(2, 8):
    if num % 2 == 0:
        print(f"{num} 是偶数")
        continue
    print(f"{num} 是奇数")


# ## `else` 子句
# 
# - `break`：跳出所在的最内层循环（跳过整个循环语句）
# - `else`：只有当循环正常离开时才会执行（也就是没有碰到 `break` 语句）
# 
# 和循环 `else` 子句结合，`break` 语句通常可以忽略所需要的搜索状态标志位。

# In[14]:


def fator(y):
    '''仅仅打印 y 的首个因子'''
    x = y // 2
    while x > 1:
        if y % x == 0:
            print(y, '有因子', x)
            break
        x -= 1
    else:  # 没有碰到 break 才会执行
        print(y, '是质数！')
        


# In[26]:


fator(7), fator(88), fator(45);


# 看一个更复杂的例子：

# In[19]:


for n in range(2, 10):
    for x in range(2, n):
        if n % x == 0:
            print(n, '=', x, 'x', n//x)
            break
    else:
        # 循环失败，没有找到一个因子
        print(n, '是质数！')

