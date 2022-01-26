# Python保留字
py_RESERVED = {
    'False': 'FALSE',
    'None': 'NONE',
    'True': 'TRUE',
    'and': 'AND',
    'as': 'AS',
    'assert': 'ASSERT',
    'async': 'ASYNC',
    'await': 'AWAIT',
    'break': 'BREAK',
    'class': 'CLASS',
    'continue': 'CONTINUE',
    'def': 'DEF',
    'del': 'DEL',
    'elif': 'ELIF',
    'else': 'ELSE',
    'except': 'EXCEPT',
    'finally': 'FINALLY',
    'for': 'FOR',
    'from': 'FROM',
    'global': 'GLOBAL',
    'if': 'IF',
    'import': 'IMPORT',
    'in': 'IN',
    'is': 'IS',
    'lambda': 'LAMBDA',
    'nonlocal': 'NONLOCAL',
    'not': 'NOT',
    'or': 'OR',
    'pass': 'PASS',
    'raise': 'RAISE',
    'return': 'RETURN',
    'self': 'SELF',
    'try': 'TRY',
    'while': 'WHILE',
    'with': 'WITH',
    'yield': 'YIELD',
}

# Zpy保留字
zpy_RESERVED = {
    '错': 'FALSE',
    '空': 'NONE',
    '对': 'TRUE',
    '与': 'AND',
    '作为': 'AS',
    '断言': 'ASSERT',
    '异步': 'ASYNC',
    '等待': 'AWAIT',
    '终止': 'BREAK',
    '类': 'CLASS',
    '继续': 'CONTINUE',
    '函数': 'DEF',
    '删除': 'DEL',
    '或如': 'ELIF',
    '否则': 'ELSE',
    '捕获': 'EXCEPT',
    '最后': 'FINALLY',
    '对于': 'FOR',
    '从': 'FROM',
    '全局': 'GLOBAL',
    '如果': 'IF',
    '导入': 'IMPORT',
    '在': 'IN',
    '是': 'IS',
    '匿名': 'LAMBDA',
    '非局部': 'NONLOCAL',
    '不': 'NOT',
    '或': 'OR',
    '跳过': 'PASS',
    '抛出': 'RAISE',
    '返回': 'RETURN',
    '自己': 'SELF',
    '尝试': 'TRY',
    '当': 'WHILE',
    '随着': 'WITH',
    '生成': 'YIELD',
}

# 反转字典
def invert_dict(d):
    return dict(zip(d.values(), d.keys()))

py_invert_RESERVED = invert_dict(py_RESERVED)
zpy_invert_RESERVED = invert_dict(zpy_RESERVED)

py_to_zpy = {}
zpy_to_py = {}
for item in py_invert_RESERVED:
    py_item = py_invert_RESERVED[item]
    zpy_item = zpy_invert_RESERVED[item]
    py_to_zpy[py_item] = zpy_item
    zpy_to_py[zpy_item] = py_item
