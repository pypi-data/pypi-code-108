from parsec.text import *
from parsec.combinator import *
from parsec.atom import *
from parsec.state import BasicState

side = string('$')


@Parsec
def escape(state):
    c = state.next()
    if c == "$":
        return "$"
    elif c == "\\":
        return "\\"
    elif c == "{":
        return "{"
    elif c == "}":
        return '}'
    else:
        # 兼容非公式嵌入，对于无法识别的文本返回原文
        return f'\\{c}'


@Parsec
def escaped(state):
    c = state.next()
    if c == '\\':
        return escape(state)
    elif c == "$":
        raise ParsecError(state, "got stop char $")
    else:
        return c


@Parsec
def token_content(state):
    buffer = ""
    while True:
        c = ahead(choice(one, eof))(state)
        if c in ["{", "}", "^", "_", "$", None]:
            return buffer
        else:
            buffer += escaped(state)


@Parsec
def superscript(state):
    c = state.next()
    if c == "{":
        cnt = token_content(state)
        string("}")(state)
        return f"<sup>{cnt}</sup>"
    else:
        return f"<sup>{c}</sup>"


@Parsec
def subscript(state):
    c = state.next()
    if c == "{":
        cnt = token_content(state)
        string("}")(state)
        return f"<sub>{cnt}</sub>"
    else:
        return f"<sub>{c}</sub>"


@Parsec
def content(state):
    buffer = ""
    while True:
        try:
            tran = state.begin()
            c = state.next()
            if c == "$":
                state.commit(tran)
                return buffer
            elif c == "^":
                state.commit(tran)
                buffer += superscript(state)
            elif c == "_":
                state.commit(tran)
                buffer += subscript(state)
            else:
                state.rollback(tran)
                cnt = token_content(state)
                if cnt:
                    buffer += cnt
                else:
                    raise ParsecError(state, f"unexpect content {state.data[state.index]}")
        except ParsecEof:
            raise ParsecError(state, f"expect right $ but eof")


def processor(plain):
    st = BasicState(plain)
    buffer = ""
    while True:
        try:
            tran = st.begin()
            c = one(st)
            if c == "$":
                index = st.index
                try:
                    cnt = content(st)
                    if cnt:
                        buffer += cnt
                    else:
                        buffer += c
                except ParsecError as err:
                    st.commit(tran)
                    buffer += "$"+st.data[index:st.index]

            else:
                st.commit(tran)
                buffer += c

        except ParsecEof:
            return buffer
