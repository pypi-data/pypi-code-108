import sys

from parsec import one, eof
from parsec.combinator import *
from parsec.text import *
from .market_math import processor

"""
使用 markdown 编写的问题应该总是一个固定格式，即

# 问题标题

问题描述

## 模板

```java
package app;
public class App {
    public static void main(String[] args){
        $code
    }
}
```

如果第一个二级标题为 template，则生成一个可选的 template 字段，template 章节中的代码段会作为代码模板，用于被生成的 notebook 

## aop

AOP（面向切面）章节定义 notebook 生成时插入的 cell ，如果定义了这个二级标题，其下复合定义的章节会插在必要的位置。

### before

这里的章节会写入到答案代码之前。

### after

这里的章节会写入到答案代码之后

## 答案

这里写正确答案。此处的代码会写入到 notebook 中，如过定义了模板章节，会将其合并后生成 notebook。

```java
```

## 选项

### A 选项标题会被忽略

可选的描述

```
//  代码
```

### B

可选的描述

```
//  代码
```

### C

可选的描述

```
//  代码
```

### D

可选的描述

```
//  代码
```

需要注意的是，选项的标题并不会出现在最终的题目中，仅作为编辑过程中的标注。而第一个选项就是答案。其顺序在最终展现时由服务代码进行混淆。

"""


class Paragraph:
    def __init__(self, source="", language=""):
        self.source = source
        self.language = language

    def isEmpty(self):
        return self.source == "" and self.language == ""

    def to_map(self):
        return {"content": self.source, "language": self.language}


class Option:
    def __init__(self, paras=None):
        self.paras = paras if paras else []

    def to_map(self):
        return [p.to_map() for p in self.paras]


class Exercise:
    def __init__(self, title, answer, description, options):
        self.title = title
        self.answer = answer
        self.description = description
        self.options = options


@Parsec
def spaces(state):
    return skip1(space)(state)


def maybe_spaces(state):
    return skip(space)(state)


def inline(state):
    char = one(state)
    if char == '\n':
        raise ParsecError(state, "unexpected newline")
    else:
        return char


@Parsec
def title(state):
    """
    解析问题标题
    """
    parser = string("#").then(spaces).then(many1(inline)).over(string('\n'))
    data = parser(state)
    return "".join(data)


@Parsec
def chapter_title(state):
    """
    解析章标题
    @param state:
    @return:
    """
    parser = string("##").then(spaces).then(many1(inline)).over(string('\n'))
    data = parser(state)
    return "".join(data)


@Parsec
def section_title(state):
    """
    解析节标题
    @param state:
    @return:
    """
    parser = string("###").then(spaces).then(many1(inline)).over(string('\n'))
    data = parser(state)
    return "".join(data)


@Parsec
def paragraph(state):
    """
    解析文字段落
    """
    buffer = ""
    line = many(inline).over(choice(attempt(string("\n")), eof))
    stop = choices(attempt(string("\n")), attempt(string("### ")), string("## "))
    while True:
        maybe_spaces(state)
        result = "".join(line(state))
        data = result
        if data:
            buffer += '\n' + result
        else:
            break
        tran = state.begin()
        try:
            stop(state)
        except ParsecError:
            continue
        finally:
            state.rollback(tran)
        return Paragraph(processor(buffer).strip(), "markdown")

    return Paragraph(processor(buffer), "markdown")


@Parsec
def code(state):
    side = choice(attempt(string("````")), string("```"))
    left = many(attempt(inline)).over(string("\n"))

    side_token = side(state)
    language = ''.join(left(state))

    right = attempt(string("\n"+side_token).over(choice(attempt(string("\n")), eof)))
    buffer = ""
    while True:
        try:
            right(state)
            return Paragraph(buffer, language)
        except ParsecError:
            buffer += one(state)


@Parsec
def desc(state):
    """解析问题或选项描述
    问题描述由若干段落或代码组成，内部结构遵循 markdown 语法
    """
    buffer = []
    parser = choice(attempt(code), paragraph)
    stop = choices(attempt(string("## ")), attempt(string("### ")), eof)
    while True:
        tran = state.begin()
        try:
            stop(state)
            return buffer
        except ParsecError:
            pass
        finally:
            state.rollback(tran)

        buffer.append(parser(state))
        maybe_spaces(state)


def option(state):
    "解析选项"
    parser = attempt(string("###").then(spaces).then(many1(attempt(inline))).over(string('\n')))
    parser(state)
    maybe_spaces(state)
    return Option(desc(state))


def template(state):
    "解析模板，返回对应的模板代码对象，如果解析失败，返回 None 并恢复 state"
    tran = state.begin()
    try:
        title = chapter_title(state)
        if title == "template":
            state.commit(tran)
            maybe_spaces(state)
            return code(state)
        else:
            raise ParsecError(state, "template not found")
    except ParsecError:
        state.rollback(tran)
        return None


@Parsec
def aop_parser(state):
    """
    解析AOP，返回对应的AOP字典，如果解析失败，返回 None 并恢复 state
    @param state:
    @return:
    """
    result = {}
    stop = attempt(chapter_title)
    tt = state.begin()
    try:
        title = chapter_title(state)
        if title == "aop":
            state.commit(tt)
            maybe_spaces(state)
            while True:
                tran = state.begin()
                try:
                    stop(state)
                    state.rollback(tran)
                    if len(result) == 0:
                        return None
                    else:
                        return result
                except ParsecError:
                    state.rollback(tran)
                    maybe_spaces(state)
                    st = section_title(state)
                    maybe_spaces(state)
                    if st == "before":
                        result["before"] = desc(state)
                    elif st == "after":
                        result["after"] = desc(state)
                    else:
                        raise ParsecError(state, f"invalid section {st} in aop chapter")

        else:
            raise ParsecError(state, "aop not found")
    except ParsecError as err:
        state.rollback(tt)
        return None


@Parsec
def parse(state):
    t = title(state)
    maybe_spaces(state)
    try:
        description = desc(state)
    except ParsecError as err:
        raise err
    tmpl = template(state)
    maybe_spaces(state)
    aop = aop_parser(state)
    ct = chapter_title(state)
    if ct == "答案":
        maybe_spaces(state)
        answer = desc(state)
    else:
        raise ParsecError(state, "chapter [答案] is required")
    ct = chapter_title(state)
    if ct == "选项":
        maybe_spaces(state)
        options = []
        while True:
            try:
                opt = option(state)
                options.append(opt)
                maybe_spaces(state)
            except ParsecError as err:
                result = Exercise(t, answer, description, options)
                if tmpl is None:
                    tmpl = template(state)
                if aop is None:
                    aop = aop_parser(state)
                if tmpl is not None:
                    result.template = tmpl
                if aop is not None:
                    result.aop = aop
                return result
    else:
        raise ParsecError(state, "chapter [选项] not found")
