# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

# Generated from CoVeriLang.g4 by ANTLR 4.7.2
from pathlib import Path
from coveriteam.interpreter import get_parsed_tree

from coveriteam.parser.CoVeriLangParser import CoVeriLangParser
from coveriteam.parser.CoVeriLangVisitor import CoVeriLangVisitor


# This class defines a complete listener for a parse tree produced by CoVeriLangParser.
class CoVeriLangToPythonConverter(CoVeriLangVisitor):
    pyp = ""
    INDENT_LEVEL = 0
    SPACE = " "
    types = {}

    def __init__(self, path):
        # TODO don't know a better way to do it.
        # I need the cvt path to resolve the file paths.
        self.__cvt_path = Path(path).parent.resolve()
        super().__init__()

    def add_indent(self):
        self.pyp += self.SPACE * self.INDENT_LEVEL

    # Visit a parse tree produced by CoVeriLangParser#program.
    def visitProgram(self, ctx: CoVeriLangParser.ProgramContext):
        self.pyp += "from coveriteam.actors.testers import *\n"
        self.pyp += "from coveriteam.actors.misc import *\n"
        self.pyp += "from coveriteam.actors.analyzers import *\n"
        self.pyp += "from coveriteam.language.artifact import *\n"
        self.pyp += "from coveriteam.language.composition import *\n"
        self.pyp += "from coveriteam.language.utilactors import *\n"
        self.pyp += (
            "from coveriteam.language.parallel_portfolio import ParallelPortfolio\n"
        )
        self.pyp += "\n"

        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#fun_decl.
    def visitFun_decl(self, ctx: CoVeriLangParser.Fun_declContext):
        self.pyp += "def " + ctx.ID().getText()
        param_str = ctx.id_list().getText() if ctx.id_list() else ""
        self.pyp += "(" + param_str + "): \n"
        self.INDENT_LEVEL = 1
        self.visitChildren(ctx)
        self.INDENT_LEVEL = 0

    # Visit a parse tree produced by CoVeriLangParser#stmt.
    def visitStmt(self, ctx: CoVeriLangParser.StmtContext):
        self.pyp += "\n"
        self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#PrintActor.
    def visitPrintActor(self, ctx: CoVeriLangParser.PrintActorContext):
        self.pyp += self.SPACE * self.INDENT_LEVEL
        self.pyp += "print("
        if ctx.actor():
            self.visit(ctx.actor())
        elif ctx.artifact():
            self.visit(ctx.artifact())
        elif ctx.ID():
            self.pyp += ctx.ID().getText()
        else:
            # This case is supposed to be a pure string.
            self.pyp += ctx.STRING().getText()
        self.pyp += ")"

    # Visit a parse tree produced by CoVeriLangParser#ExecuteActor.
    def visitExecuteActor(self, ctx: CoVeriLangParser.ExecuteActorContext):
        self.pyp += self.SPACE * self.INDENT_LEVEL
        self.visit(ctx.actor())
        # the following is done to expand the dictionary
        self.pyp += ".act_and_save_xml(**"
        if ctx.ID():
            self.pyp += ctx.ID().getText() + ")"
        else:
            self.visitArg_map(ctx)
            self.pyp += ")"
        self.pyp += "\n"

    # Visit a parse tree produced by CoVeriLangParser#return_stmt.
    def visitReturn_stmt(self, ctx: CoVeriLangParser.Return_stmtContext):
        self.pyp += self.SPACE * self.INDENT_LEVEL
        self.pyp += "return " + ctx.ID().getText() + "\n \n"

    # Visit a parse tree produced by CoVeriLangParser#SetActorName.
    def visitSetActorName(self, ctx: CoVeriLangParser.SetActorNameContext):
        self.pyp += self.SPACE * self.INDENT_LEVEL
        self.pyp += (
            "set_composite_actor_name("
            + ctx.ID().getText()
            + ","
            + ctx.STRING().getText()
            + ")"
        )

    # Visit a parse tree produced by CoVeriLangParser#arg_map.
    def visitArg_map(self, ctx: CoVeriLangParser.Arg_mapContext):
        self.pyp += "{"
        self.visitChildren(ctx)
        self.pyp += "}"

    # Visit a parse tree produced by CoVeriLangParser#map_item.
    def visitMap_item(self, ctx: CoVeriLangParser.Map_itemContext):
        # Note that this is used to describe both map and a set of strings.
        # So, we have to deal with map item as a special case.
        self.pyp += ctx.quoted_ID_with_maybe_type().getText()
        val = ": "
        if ctx.artifact():
            self.pyp += val
            ctx.artifact().accept(self)
        elif ctx.artifact_type():
            self.pyp += val
            self.pyp += " coveriteam.language.artifact."
            ctx.artifact_type().accept(self)
        # case for renaming when both are strings
        elif ctx.quoted_ID():
            self.pyp += val + ctx.quoted_ID().getText()

        self.pyp += ","

    # Visit a parse tree produced by CoVeriLangParser#spec_stmt.
    def visitSpec_stmt(self, ctx: CoVeriLangParser.Spec_stmtContext):
        self.pyp += self.SPACE * self.INDENT_LEVEL
        self.pyp += (ctx.ID().getText()) + " = "
        a = ctx.assignable()
        if a.STRING():
            self.pyp += a.STRING().getText()
        else:
            self.visitAssignable(a)

    # Visit a parse tree produced by CoVeriLangParser#Utility.
    def visitUtility(self, ctx: CoVeriLangParser.UtilityContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Parenthesis.
    def visitParenthesis(self, ctx: CoVeriLangParser.ParenthesisContext):
        self.pyp += "("
        self.visitChildren(ctx)
        self.pyp += ")"

    # Visit a parse tree produced by CoVeriLangParser#ITE.
    def visitITE(self, ctx: CoVeriLangParser.ITEContext):
        self.pyp += "ITE("
        self.visit(ctx.exp())
        self.pyp += ","
        self.visit(ctx.actor(0))
        if ctx.actor(1):
            self.pyp += ","
            self.visit(ctx.actor(1))
        self.pyp += ")"

    # Visit a parse tree produced by CoVeriLangParser#Atomic.
    def visitAtomic(self, ctx: CoVeriLangParser.AtomicContext):
        actortype = self.visitActor_type(ctx.actor_type())

        actordef = ctx.name.text

        if ctx.name.type == CoVeriLangParser.STRING:
            actordef = str((self.__cvt_path / actordef.strip('"')).resolve())
            actordef = f'"{actordef}"'

        version = ""
        if ctx.version:
            version = ", " + ctx.version.text

        self.pyp += actortype + "(" + actordef + version + ")"

    # Visit a parse tree produced by CoVeriLangParser#FunCall.
    def visitFunCall(self, ctx: CoVeriLangParser.FunCallContext):
        self.pyp += ctx.getText()

    # Visit a parse tree produced by CoVeriLangParser#Iterative.
    def visitIterative(self, ctx: CoVeriLangParser.IterativeContext):
        self.pyp += "Iterative("
        self.visit(ctx.exp())
        self.pyp += ", "
        self.visit(ctx.actor())
        self.pyp += ")"

    # Visit a parse tree produced by CoVeriLangParser#Sequence.
    def visitSequence(self, ctx: CoVeriLangParser.SequenceContext):
        self.pyp += "Sequence("
        self.visit(ctx.actor(0))
        self.pyp += ","
        self.visit(ctx.actor(1))
        self.pyp += ")"

    # Visit a parse tree produced by CoVeriLangParser#Parallel.
    def visitParallel(self, ctx: CoVeriLangParser.ParallelContext):
        self.pyp += "Parallel("
        self.visit(ctx.actor(0))
        self.pyp += ","
        self.visit(ctx.actor(1))
        self.pyp += ")"

    # Visit a parse tree produced by CoVeriLangParser#Portfolio.
    def visitParallelPortfolio(self, ctx: CoVeriLangParser.ParallelPortfolioContext):
        self.pyp += "ParallelPortfolio(["
        for child in ctx.children:
            # IsInstance needed to support compositions and atomic actors
            if isinstance(child, CoVeriLangParser.ActorAliasContext):
                self.visit(child)
                self.pyp += ","
        self.pyp = self.pyp[:-1]
        self.pyp += "]"

        if ctx.exp():
            self.pyp += ","
            self.visit(ctx.exp())

        self.pyp += ")"

    # Visit a parse tree produced by CoVeriLangParser#ActorAlias.
    def visitActorAlias(self, ctx: CoVeriLangParser.ActorAliasContext):
        self.pyp += ctx.ID().getText()

    # Visit a parse tree produced by CoVeriLangParser#Joiner.
    def visitJoiner(self, ctx: CoVeriLangParser.JoinerContext):
        self.pyp += "Joiner("
        self.visitArtifact_type(ctx.artifact_type())
        self.pyp += "," + ctx.arg_map().getText()
        self.pyp += "," + ctx.quoted_ID().getText()
        self.pyp += ")"

    # Visit a parse tree produced by CoVeriLangParser#Setter.
    def visitSetter(self, ctx: CoVeriLangParser.SetterContext):
        self.pyp += "Setter("
        self.pyp += ctx.quoted_ID().getText()
        self.pyp += "," + ctx.ID().getText()
        self.pyp += ")"

    # Visit a parse tree produced by CoVeriLangParser#Comparator.
    def visitComparator(self, ctx: CoVeriLangParser.ComparatorContext):
        self.pyp += "Comparator("
        self.visitArtifact_type(ctx.artifact_type())
        self.pyp += "," + ctx.arg_map().getText()
        self.pyp += "," + ctx.quoted_ID().getText()
        self.pyp += ")"

    # Visit a parse tree produced by CoVeriLangParser#Copy.
    def visitCopy(self, ctx: CoVeriLangParser.CopyContext):
        # At the moment assuming that Copy is taking a list in {}.
        # So converting it to a list.
        self.pyp += "CopyActor("
        self.visit(ctx.arg_map())
        self.pyp += ")"

    # Visit a parse tree produced by CoVeriLangParser#Rename.
    def visitRename(self, ctx: CoVeriLangParser.RenameContext):
        self.pyp += "CopyActor("
        self.visit(ctx.arg_map())
        self.pyp += ")"

    # Visit a parse tree produced by CoVeriLangParser#TestSpecToSpec.
    def visitTestSpecToSpec(self, ctx: CoVeriLangParser.TestSpecToSpecContext):
        self.pyp += "TestSpecToSpec()"

    # Visit a parse tree produced by CoVeriLangParser#ClassificationToActorDefinition.
    def visitClassificationToActorDefinition(
        self, ctx: CoVeriLangParser.ClassificationToActorDefinitionContext
    ):
        self.pyp += "ClassificationToActorDefinition()"

    # Visit a parse tree produced by CoVeriLangParser#SpecToTestSpec.
    def visitSpecToTestSpec(self, ctx: CoVeriLangParser.SpecToTestSpecContext):
        self.pyp += "SpecToTestSpec()"

    # Visit a parse tree produced by CoVeriLangParser#Identity.
    def visitIdentity(self, ctx: CoVeriLangParser.IdentityContext):
        if ctx.actor():
            self.pyp += "IdentityActor("
            self.visit(ctx.actor())
            self.pyp += ")"
        else:
            self.pyp += "CopyActor(set("
            self.visit(ctx.arg_map())
            self.pyp += "))"

    # Visit a parse tree produced by CoVeriLangParser#CreateArtifact.
    def visitCreateArtifact(self, ctx: CoVeriLangParser.CreateArtifactContext):
        self.visitArtifact_type(ctx.artifact_type())
        if ctx.ID():
            path = ctx.ID().getText()
        elif ctx.STRING():
            path = ctx.STRING().getText()
        else:
            path = '""'
        self.pyp += "(" + path + ")"

    # Visit a parse tree produced by CoVeriLangParser#ArtifactAlias.
    def visitArtifactAlias(self, ctx: CoVeriLangParser.ArtifactAliasContext):
        self.pyp += ctx.ID().getText()

    # Visit a parse tree produced by CoVeriLangParser#ArtifactFromMapItem.
    def visitArtifactFromMapItem(
        self, ctx: CoVeriLangParser.ArtifactFromMapItemContext
    ):
        self.pyp += ctx.ID()[0].getText() + ('["%s"]' % ctx.ID()[1].getText())

    # Visit a parse tree produced by CoVeriLangParser#artifact_type.
    def visitArtifact_type(self, ctx: CoVeriLangParser.Artifact_typeContext):
        self.pyp += ctx.getText()

    # Visit a parse tree produced by CoVeriLangParser#actor_type.
    def visitActor_type(self, ctx: CoVeriLangParser.Actor_typeContext):
        return ctx.getText()

    # Visit a parse tree produced by CoVeriLangParser#ExpAlias.
    def visitExpAlias(self, ctx: CoVeriLangParser.ExpAliasContext):
        self.pyp += ctx.getText()

    # Visit a parse tree produced by CoVeriLangParser#QuotedExpAliasForArtifacts.
    def visitQuotedExpAliasForArtifacts(
        self, ctx: CoVeriLangParser.QuotedExpAliasForArtifactsContext
    ):
        self.pyp += ctx.getText()

    # Visit a parse tree produced by CoVeriLangParser#NotLogical.
    def visitNotLogical(self, ctx: CoVeriLangParser.NotLogicalContext):
        self.pyp += ' "not " + '
        self.visit(ctx.exp())

    # Visit a parse tree produced by CoVeriLangParser#InstanceOf.
    def visitInstanceOf(self, ctx: CoVeriLangParser.InstanceOfContext):
        self.pyp += (
            '"isinstance('
            + ctx.ID().getText()
            + ", "
            + ctx.artifact_type().getText()
            + ')"'
        )

    # Visit a parse tree produced by CoVeriLangParser#ElementOf.
    def visitElementOf(self, ctx: CoVeriLangParser.ElementOfContext):
        # TODO Assumption: we are only going to use this operator for verdicts.
        # This makes use of the overload of __eq__ for Verdict.
        # Note that it does not overload the __hash__.
        self.pyp += '"' + ctx.ID().getText() + " in ["
        self.visit(ctx.verdict_list())
        self.pyp += ']"'

    # Visit a parse tree produced by CoVeriLangParser#BinaryLogical.
    def visitBinaryLogical(self, ctx: CoVeriLangParser.BinaryLogicalContext):
        self.visit(ctx.exp(0))
        self.pyp += ' + " ' + ctx.BIN_OP().getText().lower() + ' " + '
        self.visit(ctx.exp(1))

    # Visit a parse tree produced by CoVeriLangParser#Paren.
    def visitParen(self, ctx: CoVeriLangParser.ParenContext):
        self.pyp += "("
        self.visit(ctx.getExp())
        self.pyp += ")"

    # Visit a parse tree produced by CoVeriLangParser#verdict_list.
    def visitVerdict_list(self, ctx: CoVeriLangParser.Verdict_listContext):
        self.pyp += ctx.getText()


def generate_python_code(path_str):
    tree = get_parsed_tree(path_str)

    visitor = CoVeriLangToPythonConverter(path_str)
    visitor.visit(tree)
    return visitor.pyp
