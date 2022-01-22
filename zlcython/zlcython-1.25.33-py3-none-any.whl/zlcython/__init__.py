trandic={
    "遍历": "for",
    "在": "in",
    "定义": "def",
    "类": "class",
    "继承": "extends",
    "如果": "if",
    "返回": "return",
    "退出循环": "break",
    "跳过": "continue",
    "触发异常": "raise",
    "导入": "import",
    "从": "from",
    "到": "to",
    "结束": "end",
    "当": "as",
    "等于": "==",
    "不等于": "!=",
    "大于": ">",
    "小于": "<",
    "大于等于": ">=",
    "小于等于": "<=",
    "与": "and",
    "或": "or",
    "非": "not",
    "和": "and",
    "缩进": "   ",
    "所有": "*",
    "如果循环": "while",
}
replace_trandic={
    "”": '"',
    "“": '"',
    "‘": "'",
    "’": "'",
    "（": "(",
    "）": ")",
    "，": ",",
    "：": ":",
    "；": ";",
    "【": "[",
    "】": "]",
    "。": ".",
    "输出": "print",
    "输入": "input",
    "转整数": "int",
    "转浮点数": "float",
    "转字符串": "str",
    "转布尔": "bool",
    "转列表": "list",
    "转元组": "tuple",
    "转字典": "dict",
    "转集合": "set",
    "转比特": "bytes",
    "转字节": "bytearray",
    "真": "True",
    "假": "False",
    "无": "None",
    "范围": "range",
    "请求网页": "get__.urlopen",
    "获取网页内容": "read()",
    "占位符": "pass",
}
import sys
def tran_code_f(codefile,encodefile):
    decodecode=''
    useurllib_request=False
    with open(codefile,encoding="utf-8") as f:
        code=f.readlines()
    for line in code:
        while True:
            if line.startswith("    "):
                decodecode+="    "
                line=line[4:]
            else:
                break
        lines=line.split()
        if len(lines)==0:
            continue
        for i in range(len(lines)):
            if "请求网页" in lines[i]:
                useurllib_request=True
            if lines[i] in trandic:
                lines[i]=trandic[lines[i]]
                continue
        replace_line=(' '.join(lines)+'\n')
        for key,value in replace_trandic.items():
            replace_line=replace_line.replace(key,value)
        decodecode+=replace_line
    with open(encodefile,mode="w",encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("#!python3"+"\n"*3)
        if useurllib_request:
            f.write("import urllib.request as get__"+"\n")
        f.write(decodecode)
        f.write("\n"*2)