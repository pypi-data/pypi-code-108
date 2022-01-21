from dudocode.utils import replace_string, replace_comment, swap, format_ifs,\
                           format_outs, format_ins, format_loops


class Transpiler(object):

    def __init__(self, name):
        self.name = name
        self.SYNTAX_SWAP = {
            'int': ['INTEGER'],
            'chr': ['CHAR'],
            'float': ['FLOAT'],
            'str': ['STRING'],
            'bool': ['BOOLEAN'],
            'and': ['AND'],
            'or': ['OR'],
            'not': ['NOT'],
            'if': ['IF'],
            'else': ['ELSE'],
            ' ': ['THEN']
        }
        self.STRICT_SWAP = {

        }
        self.OPERATOR_SWAP = {
            '==': ['='],
            '=': ['←'],
            '=': ['<-'],
            '**': ['^'],
            '!=': ['<>']
        }

    def transpile(self, source):
        proc, str_dict = replace_string(source)
        proc, com_dict = replace_comment(proc)

        proc = swap(proc, self.SYNTAX_SWAP, syntax=True)
        proc = swap(proc, self.STRICT_SWAP)
        proc = swap(proc, self.OPERATOR_SWAP)

        proc = format_ifs(proc)
        proc = format_loops(proc)
        proc = format_outs(proc)
        proc = format_ins(proc)

        for i in com_dict:
            proc = proc.replace(i, com_dict[i])
        for i in str_dict:
            proc = proc.replace(i, str_dict[i])

        return proc
