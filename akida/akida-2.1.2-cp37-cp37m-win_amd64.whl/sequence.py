def sequence_repr(self):
    data = "<akida.Sequence"
    data += ", name=" + self.name
    data += ", backend=" + str(self.backend).split('.')[-1]
    data += ", passes=" + repr(self.passes)
    program = self.program
    if program is not None:
        data += ", program_size=" + str(len(program))
    data += ">"
    return data


def pass_repr(self):
    data = "<akida.Pass"
    data += ", layers=" + repr(self.layers)
    data += ">"
    return data
