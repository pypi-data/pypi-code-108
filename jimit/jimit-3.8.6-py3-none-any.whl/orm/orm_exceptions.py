#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'James Iter'
__date__ = '2021/4/18'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2021 by James Iter.'


class ORMError(Exception):
    pass


class NotExist(ORMError):
    pass


class LimitNone(ORMError):
    pass


