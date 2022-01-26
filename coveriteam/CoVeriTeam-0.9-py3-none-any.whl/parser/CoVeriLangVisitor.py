# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2022 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

# Generated from CoVeriLang.g4 by ANTLR 4.8
from antlr4 import *

if __name__ is not None and "." in __name__:
    from .CoVeriLangParser import CoVeriLangParser
else:
    from CoVeriLangParser import CoVeriLangParser

# This class defines a complete generic visitor for a parse tree produced by CoVeriLangParser.


class CoVeriLangVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CoVeriLangParser#program.
    def visitProgram(self, ctx: CoVeriLangParser.ProgramContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#fun_decl.
    def visitFun_decl(self, ctx: CoVeriLangParser.Fun_declContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#stmt_block.
    def visitStmt_block(self, ctx: CoVeriLangParser.Stmt_blockContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#id_list.
    def visitId_list(self, ctx: CoVeriLangParser.Id_listContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#stmt.
    def visitStmt(self, ctx: CoVeriLangParser.StmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#spec_stmt.
    def visitSpec_stmt(self, ctx: CoVeriLangParser.Spec_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#PrintActor.
    def visitPrintActor(self, ctx: CoVeriLangParser.PrintActorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#ExecuteActor.
    def visitExecuteActor(self, ctx: CoVeriLangParser.ExecuteActorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#return_stmt.
    def visitReturn_stmt(self, ctx: CoVeriLangParser.Return_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#SetActorName.
    def visitSetActorName(self, ctx: CoVeriLangParser.SetActorNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#arg_map.
    def visitArg_map(self, ctx: CoVeriLangParser.Arg_mapContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#map_item_list.
    def visitMap_item_list(self, ctx: CoVeriLangParser.Map_item_listContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#map_item.
    def visitMap_item(self, ctx: CoVeriLangParser.Map_itemContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#assignable.
    def visitAssignable(self, ctx: CoVeriLangParser.AssignableContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Atomic.
    def visitAtomic(self, ctx: CoVeriLangParser.AtomicContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#FunCall.
    def visitFunCall(self, ctx: CoVeriLangParser.FunCallContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Utility.
    def visitUtility(self, ctx: CoVeriLangParser.UtilityContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Sequence.
    def visitSequence(self, ctx: CoVeriLangParser.SequenceContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#ITE.
    def visitITE(self, ctx: CoVeriLangParser.ITEContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Iterative.
    def visitIterative(self, ctx: CoVeriLangParser.IterativeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Parallel.
    def visitParallel(self, ctx: CoVeriLangParser.ParallelContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#ParallelPortfolio.
    def visitParallelPortfolio(self, ctx: CoVeriLangParser.ParallelPortfolioContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#ActorAlias.
    def visitActorAlias(self, ctx: CoVeriLangParser.ActorAliasContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Parenthesis.
    def visitParenthesis(self, ctx: CoVeriLangParser.ParenthesisContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Joiner.
    def visitJoiner(self, ctx: CoVeriLangParser.JoinerContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Setter.
    def visitSetter(self, ctx: CoVeriLangParser.SetterContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Comparator.
    def visitComparator(self, ctx: CoVeriLangParser.ComparatorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Copy.
    def visitCopy(self, ctx: CoVeriLangParser.CopyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Rename.
    def visitRename(self, ctx: CoVeriLangParser.RenameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#TestSpecToSpec.
    def visitTestSpecToSpec(self, ctx: CoVeriLangParser.TestSpecToSpecContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#SpecToTestSpec.
    def visitSpecToTestSpec(self, ctx: CoVeriLangParser.SpecToTestSpecContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#ClassificationToActorDefinition.
    def visitClassificationToActorDefinition(
        self, ctx: CoVeriLangParser.ClassificationToActorDefinitionContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Identity.
    def visitIdentity(self, ctx: CoVeriLangParser.IdentityContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#CreateArtifact.
    def visitCreateArtifact(self, ctx: CoVeriLangParser.CreateArtifactContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#ArtifactAlias.
    def visitArtifactAlias(self, ctx: CoVeriLangParser.ArtifactAliasContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#ArtifactFromMapItem.
    def visitArtifactFromMapItem(
        self, ctx: CoVeriLangParser.ArtifactFromMapItemContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#artifact_type.
    def visitArtifact_type(self, ctx: CoVeriLangParser.Artifact_typeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#actor_type.
    def visitActor_type(self, ctx: CoVeriLangParser.Actor_typeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#ExpAlias.
    def visitExpAlias(self, ctx: CoVeriLangParser.ExpAliasContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#NotLogical.
    def visitNotLogical(self, ctx: CoVeriLangParser.NotLogicalContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#InstanceOf.
    def visitInstanceOf(self, ctx: CoVeriLangParser.InstanceOfContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#ElementOf.
    def visitElementOf(self, ctx: CoVeriLangParser.ElementOfContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#QuotedExpAliasForArtifacts.
    def visitQuotedExpAliasForArtifacts(
        self, ctx: CoVeriLangParser.QuotedExpAliasForArtifactsContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#BinaryLogical.
    def visitBinaryLogical(self, ctx: CoVeriLangParser.BinaryLogicalContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#Paren.
    def visitParen(self, ctx: CoVeriLangParser.ParenContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#verdict_list.
    def visitVerdict_list(self, ctx: CoVeriLangParser.Verdict_listContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#tc_exp.
    def visitTc_exp(self, ctx: CoVeriLangParser.Tc_expContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#quoted_ID_with_maybe_type.
    def visitQuoted_ID_with_maybe_type(
        self, ctx: CoVeriLangParser.Quoted_ID_with_maybe_typeContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CoVeriLangParser#quoted_ID.
    def visitQuoted_ID(self, ctx: CoVeriLangParser.Quoted_IDContext):
        return self.visitChildren(ctx)


del CoVeriLangParser
