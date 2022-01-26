# Generated from ./mint.g4 by ANTLR 4.9.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .mintParser import mintParser
else:
    from mintParser import mintParser

# This class defines a complete generic visitor for a parse tree produced by mintParser.

class mintVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by mintParser#netlist.
    def visitNetlist(self, ctx:mintParser.NetlistContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#importBlock.
    def visitImportBlock(self, ctx:mintParser.ImportBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#importStat.
    def visitImportStat(self, ctx:mintParser.ImportStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#header.
    def visitHeader(self, ctx:mintParser.HeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#ufmoduleBlock.
    def visitUfmoduleBlock(self, ctx:mintParser.UfmoduleBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#globalStats.
    def visitGlobalStats(self, ctx:mintParser.GlobalStatsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#ufmoduleStat.
    def visitUfmoduleStat(self, ctx:mintParser.UfmoduleStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#layerBlocks.
    def visitLayerBlocks(self, ctx:mintParser.LayerBlocksContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#layerBlock.
    def visitLayerBlock(self, ctx:mintParser.LayerBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#flowBlock.
    def visitFlowBlock(self, ctx:mintParser.FlowBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#controlBlock.
    def visitControlBlock(self, ctx:mintParser.ControlBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#integrationBlock.
    def visitIntegrationBlock(self, ctx:mintParser.IntegrationBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#flowStat.
    def visitFlowStat(self, ctx:mintParser.FlowStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#controlStat.
    def visitControlStat(self, ctx:mintParser.ControlStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#integrationStat.
    def visitIntegrationStat(self, ctx:mintParser.IntegrationStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#primitiveStat.
    def visitPrimitiveStat(self, ctx:mintParser.PrimitiveStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#bankDeclStat.
    def visitBankDeclStat(self, ctx:mintParser.BankDeclStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#bankGenStat.
    def visitBankGenStat(self, ctx:mintParser.BankGenStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#bankStat.
    def visitBankStat(self, ctx:mintParser.BankStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#gridGenStat.
    def visitGridGenStat(self, ctx:mintParser.GridGenStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#gridDeclStat.
    def visitGridDeclStat(self, ctx:mintParser.GridDeclStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#gridStat.
    def visitGridStat(self, ctx:mintParser.GridStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#spanStat.
    def visitSpanStat(self, ctx:mintParser.SpanStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#valveStat.
    def visitValveStat(self, ctx:mintParser.ValveStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#nodeStat.
    def visitNodeStat(self, ctx:mintParser.NodeStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#viaStat.
    def visitViaStat(self, ctx:mintParser.ViaStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#terminalStat.
    def visitTerminalStat(self, ctx:mintParser.TerminalStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#channelStat.
    def visitChannelStat(self, ctx:mintParser.ChannelStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#netStat.
    def visitNetStat(self, ctx:mintParser.NetStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#entity.
    def visitEntity(self, ctx:mintParser.EntityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#entity_element.
    def visitEntity_element(self, ctx:mintParser.Entity_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#paramsStat.
    def visitParamsStat(self, ctx:mintParser.ParamsStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#statTerminaion.
    def visitStatTerminaion(self, ctx:mintParser.StatTerminaionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#connectionParamStat.
    def visitConnectionParamStat(self, ctx:mintParser.ConnectionParamStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#paramStat.
    def visitParamStat(self, ctx:mintParser.ParamStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#constraintParams.
    def visitConstraintParams(self, ctx:mintParser.ConstraintParamsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#spacingParam.
    def visitSpacingParam(self, ctx:mintParser.SpacingParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#directionParam.
    def visitDirectionParam(self, ctx:mintParser.DirectionParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#param_element.
    def visitParam_element(self, ctx:mintParser.Param_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#intParam.
    def visitIntParam(self, ctx:mintParser.IntParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#boolParam.
    def visitBoolParam(self, ctx:mintParser.BoolParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#widthParam.
    def visitWidthParam(self, ctx:mintParser.WidthParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#verticalSpacingParam.
    def visitVerticalSpacingParam(self, ctx:mintParser.VerticalSpacingParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#horizontalSpacingParam.
    def visitHorizontalSpacingParam(self, ctx:mintParser.HorizontalSpacingParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#rotationParam.
    def visitRotationParam(self, ctx:mintParser.RotationParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#lengthParam.
    def visitLengthParam(self, ctx:mintParser.LengthParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#ufmodulename.
    def visitUfmodulename(self, ctx:mintParser.UfmodulenameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#ufterminal.
    def visitUfterminal(self, ctx:mintParser.UfterminalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#uftargets.
    def visitUftargets(self, ctx:mintParser.UftargetsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#uftarget.
    def visitUftarget(self, ctx:mintParser.UftargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#ufname.
    def visitUfname(self, ctx:mintParser.UfnameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#ufnames.
    def visitUfnames(self, ctx:mintParser.UfnamesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#value.
    def visitValue(self, ctx:mintParser.ValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#boolvalue.
    def visitBoolvalue(self, ctx:mintParser.BoolvalueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#positionConstraintStat.
    def visitPositionConstraintStat(self, ctx:mintParser.PositionConstraintStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#setCoordinate.
    def visitSetCoordinate(self, ctx:mintParser.SetCoordinateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by mintParser#orientation.
    def visitOrientation(self, ctx:mintParser.OrientationContext):
        return self.visitChildren(ctx)



del mintParser