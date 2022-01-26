# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0
from coveriteam.parser.CoVeriLangParser import CoVeriLangParser
from coveriteam.parser.CoVeriLangLexer import CoVeriLangLexer
from antlr4 import FileStream, CommonTokenStream


def get_parsed_tree(path):
    input_stream = FileStream(path, encoding="utf-8")

    lexer = CoVeriLangLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = CoVeriLangParser(token_stream)
    return parser.program()
