#!/usr/bin/env python
# coding: utf-8

# # 自定义数字
# 
# 参考：{mod}`numbers`
# 
# {guilabel}`目标`：
# 
# 1. 创建“数字”这一概念
# 2. 定制数字相关运算

# In[3]:


from abc import ABC, abstractmethod


class Number(ABC):
    '''所有的数字都继承于这个类'''
    # 如果你只是想检查一个参数 x 是否是一个数字，
    # 而不关心是什么类型，可以使用 `isinstance(x, Number)`。
    __slots__ = ()
    # 具体的数字类型必须提供他们自己的哈希实现
    __hash__ = None


class Complex(Number):
    '''复数定义了在内置复数类型上工作的运算

    简而言之，这些是：
    转换为 complex、.real、.imag、+、-、*、/、**、abs()、.conjunugate、==、和 !=

    如果它被赋予异质的（heterogeneous）参数，并且没有关于它们的特殊知识，它应该返回到内置的 complex 类型。
    '''
    __slots__ = ()

    @abstractmethod
    def __complex__(self):
        """返回一个内置的 complex 实例。为 `complex(self)` 调用。"""

    def __bool__(self):
        """如果 self !=0，则为真。为 bool(self) 调用。"""
        return self != 0

    @property
    @abstractmethod
    def real(self):
        """检索这个数字的实数部分。

        这应该是 Real 的子类。
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def imag(self):
        """检索这个数字的虚数部分。

        这应该是 Real 的子类。
        """
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other):
        """self + other"""
        raise NotImplementedError

    @abstractmethod
    def __radd__(self, other):
        """other + self"""
        raise NotImplementedError

    @abstractmethod
    def __neg__(self):
        """-self"""
        raise NotImplementedError

    @abstractmethod
    def __pos__(self):
        """+self"""
        raise NotImplementedError

    def __sub__(self, other):
        """self - other"""
        return self + -other

    def __rsub__(self, other):
        """other - self"""
        return -self + other

    @abstractmethod
    def __mul__(self, other):
        """self * other"""
        raise NotImplementedError

    @abstractmethod
    def __rmul__(self, other):
        """other * self"""
        raise NotImplementedError

    @abstractmethod
    def __truediv__(self, other):
        """self / other：必要时 promote 为 float。"""
        raise NotImplementedError

    @abstractmethod
    def __rtruediv__(self, other):
        """other / self"""
        raise NotImplementedError

    @abstractmethod
    def __pow__(self, exponent):
        """self**exponent：必要时 promote 为 float 或者 complex。"""
        raise NotImplementedError

    @abstractmethod
    def __rpow__(self, base):
        """base ** self"""
        raise NotImplementedError

    @abstractmethod
    def __abs__(self):
        """返回与 0 的 `Real` 距离。为 `abs(self)` 调用。"""
        raise NotImplementedError

    @abstractmethod
    def conjugate(self):
        """(x+y*i).conjugate() 返回 (x-y*i)"""
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        """self == other"""
        raise NotImplementedError


Complex.register(complex)


class Real(Complex):
    """相对于 Complex，Real 加入了只有实数才能进行的运算。
    
    简单的说，它们是：转化至 
    float、trunc()、divmod()、 %、 <、 <=、 >、 和 >=。

    Real 还为派生运算提供了默认值。
    """

    __slots__ = ()

    @abstractmethod
    def __float__(self):
        """任何 Real 都可以被转换为原生的 float 对象。

        被 float(self) 回调
        """
        raise NotImplementedError

    @abstractmethod
    def __trunc__(self):
        """trunc(self): Truncates self to an Integral.

        Returns an Integral i such that:
          * i>0 iff self>0;
          * abs(i) <= abs(self);
          * for any Integral j satisfying the first two conditions,
            abs(i) >= abs(j) [i.e. i has "maximal" abs among those].
        i.e. "truncate towards 0".
        """
        raise NotImplementedError

    @abstractmethod
    def __floor__(self):
        """Finds the greatest Integral <= self."""
        raise NotImplementedError

    @abstractmethod
    def __ceil__(self):
        """Finds the least Integral >= self."""
        raise NotImplementedError

    @abstractmethod
    def __round__(self, ndigits=None):
        """Rounds self to ndigits decimal places, defaulting to 0.

        If ndigits is omitted or None, returns an Integral, otherwise
        returns a Real. Rounds half toward even.
        """
        raise NotImplementedError

    def __divmod__(self, other):
        """divmod(self, other): The pair (self // other, self % other).

        Sometimes this can be computed faster than the pair of
        operations.
        """
        return (self // other, self % other)

    def __rdivmod__(self, other):
        """divmod(other, self): The pair (self // other, self % other).

        Sometimes this can be computed faster than the pair of
        operations.
        """
        return (other // self, other % self)

    @abstractmethod
    def __floordiv__(self, other):
        """self // other: The floor() of self/other."""
        raise NotImplementedError

    @abstractmethod
    def __rfloordiv__(self, other):
        """other // self: The floor() of other/self."""
        raise NotImplementedError

    @abstractmethod
    def __mod__(self, other):
        """self % other"""
        raise NotImplementedError

    @abstractmethod
    def __rmod__(self, other):
        """other % self"""
        raise NotImplementedError

    @abstractmethod
    def __lt__(self, other):
        """self < other

        < on Reals defines a total ordering, except perhaps for NaN."""
        raise NotImplementedError

    @abstractmethod
    def __le__(self, other):
        """self <= other"""
        raise NotImplementedError

    # Concrete implementations of Complex abstract methods.
    def __complex__(self):
        """complex(self) == complex(float(self), 0)"""
        return complex(float(self))

    @property
    def real(self):
        """Real numbers are their real component."""
        return +self

    @property
    def imag(self):
        """Real numbers have no imaginary component."""
        return 0

    def conjugate(self):
        """Conjugate is a no-op for Reals."""
        return +self


Real.register(float)


class Rational(Real):
    """.numerator and .denominator should be in lowest terms."""

    __slots__ = ()

    @property
    @abstractmethod
    def numerator(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def denominator(self):
        raise NotImplementedError

    # Concrete implementation of Real's conversion to float.
    def __float__(self):
        """float(self) = self.numerator / self.denominator

        It's important that this conversion use the integer's "true"
        division rather than casting one side to float before dividing
        so that ratios of huge integers convert without overflowing.

        """
        return self.numerator / self.denominator


class Integral(Rational):
    """Integral adds methods that work on integral numbers.

    In short, these are conversion to int, pow with modulus, and the
    bit-string operations.
    """

    __slots__ = ()

    @abstractmethod
    def __int__(self):
        """int(self)"""
        raise NotImplementedError

    def __index__(self):
        """Called whenever an index is needed, such as in slicing"""
        return int(self)

    @abstractmethod
    def __pow__(self, exponent, modulus=None):
        """self ** exponent % modulus, but maybe faster.

        Accept the modulus argument if you want to support the
        3-argument version of pow(). Raise a TypeError if exponent < 0
        or any argument isn't Integral. Otherwise, just implement the
        2-argument version described in Complex.
        """
        raise NotImplementedError

    @abstractmethod
    def __lshift__(self, other):
        """self << other"""
        raise NotImplementedError

    @abstractmethod
    def __rlshift__(self, other):
        """other << self"""
        raise NotImplementedError

    @abstractmethod
    def __rshift__(self, other):
        """self >> other"""
        raise NotImplementedError

    @abstractmethod
    def __rrshift__(self, other):
        """other >> self"""
        raise NotImplementedError

    @abstractmethod
    def __and__(self, other):
        """self & other"""
        raise NotImplementedError

    @abstractmethod
    def __rand__(self, other):
        """other & self"""
        raise NotImplementedError

    @abstractmethod
    def __xor__(self, other):
        """self ^ other"""
        raise NotImplementedError

    @abstractmethod
    def __rxor__(self, other):
        """other ^ self"""
        raise NotImplementedError

    @abstractmethod
    def __or__(self, other):
        """self | other"""
        raise NotImplementedError

    @abstractmethod
    def __ror__(self, other):
        """other | self"""
        raise NotImplementedError

    @abstractmethod
    def __invert__(self):
        """~self"""
        raise NotImplementedError

    # Concrete implementations of Rational and Real abstract methods.
    def __float__(self):
        """float(self) == float(int(self))"""
        return float(int(self))

    @property
    def numerator(self):
        """Integers are their own numerators."""
        return +self

    @property
    def denominator(self):
        """Integers have a denominator of 1."""
        return 1


Integral.register(int)


# 
