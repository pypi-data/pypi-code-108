# Generated from _qpd_antlr/sql.g4 by ANTLR 4.9
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .sqlParser import sqlParser
else:
    from sqlParser import sqlParser

# This class defines a complete generic visitor for a parse tree produced by sqlParser.

class sqlVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by sqlParser#singleStatement.
    def visitSingleStatement(self, ctx:sqlParser.SingleStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#singleExpression.
    def visitSingleExpression(self, ctx:sqlParser.SingleExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#singleTableIdentifier.
    def visitSingleTableIdentifier(self, ctx:sqlParser.SingleTableIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#singleMultipartIdentifier.
    def visitSingleMultipartIdentifier(self, ctx:sqlParser.SingleMultipartIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#singleFunctionIdentifier.
    def visitSingleFunctionIdentifier(self, ctx:sqlParser.SingleFunctionIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#singleDataType.
    def visitSingleDataType(self, ctx:sqlParser.SingleDataTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#singleTableSchema.
    def visitSingleTableSchema(self, ctx:sqlParser.SingleTableSchemaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#statementDefault.
    def visitStatementDefault(self, ctx:sqlParser.StatementDefaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#dmlStatement.
    def visitDmlStatement(self, ctx:sqlParser.DmlStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#use.
    def visitUse(self, ctx:sqlParser.UseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#createNamespace.
    def visitCreateNamespace(self, ctx:sqlParser.CreateNamespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#setNamespaceProperties.
    def visitSetNamespaceProperties(self, ctx:sqlParser.SetNamespacePropertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#setNamespaceLocation.
    def visitSetNamespaceLocation(self, ctx:sqlParser.SetNamespaceLocationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#dropNamespace.
    def visitDropNamespace(self, ctx:sqlParser.DropNamespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#showNamespaces.
    def visitShowNamespaces(self, ctx:sqlParser.ShowNamespacesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#createTable.
    def visitCreateTable(self, ctx:sqlParser.CreateTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#createHiveTable.
    def visitCreateHiveTable(self, ctx:sqlParser.CreateHiveTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#createTableLike.
    def visitCreateTableLike(self, ctx:sqlParser.CreateTableLikeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#replaceTable.
    def visitReplaceTable(self, ctx:sqlParser.ReplaceTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#analyze.
    def visitAnalyze(self, ctx:sqlParser.AnalyzeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#addTableColumns.
    def visitAddTableColumns(self, ctx:sqlParser.AddTableColumnsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#renameTableColumn.
    def visitRenameTableColumn(self, ctx:sqlParser.RenameTableColumnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#dropTableColumns.
    def visitDropTableColumns(self, ctx:sqlParser.DropTableColumnsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#renameTable.
    def visitRenameTable(self, ctx:sqlParser.RenameTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#setTableProperties.
    def visitSetTableProperties(self, ctx:sqlParser.SetTablePropertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#unsetTableProperties.
    def visitUnsetTableProperties(self, ctx:sqlParser.UnsetTablePropertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#alterTableAlterColumn.
    def visitAlterTableAlterColumn(self, ctx:sqlParser.AlterTableAlterColumnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#hiveChangeColumn.
    def visitHiveChangeColumn(self, ctx:sqlParser.HiveChangeColumnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#hiveReplaceColumns.
    def visitHiveReplaceColumns(self, ctx:sqlParser.HiveReplaceColumnsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#setTableSerDe.
    def visitSetTableSerDe(self, ctx:sqlParser.SetTableSerDeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#addTablePartition.
    def visitAddTablePartition(self, ctx:sqlParser.AddTablePartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#renameTablePartition.
    def visitRenameTablePartition(self, ctx:sqlParser.RenameTablePartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#dropTablePartitions.
    def visitDropTablePartitions(self, ctx:sqlParser.DropTablePartitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#setTableLocation.
    def visitSetTableLocation(self, ctx:sqlParser.SetTableLocationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#recoverPartitions.
    def visitRecoverPartitions(self, ctx:sqlParser.RecoverPartitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#dropTable.
    def visitDropTable(self, ctx:sqlParser.DropTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#dropView.
    def visitDropView(self, ctx:sqlParser.DropViewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#createView.
    def visitCreateView(self, ctx:sqlParser.CreateViewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#createTempViewUsing.
    def visitCreateTempViewUsing(self, ctx:sqlParser.CreateTempViewUsingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#alterViewQuery.
    def visitAlterViewQuery(self, ctx:sqlParser.AlterViewQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#createFunction.
    def visitCreateFunction(self, ctx:sqlParser.CreateFunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#dropFunction.
    def visitDropFunction(self, ctx:sqlParser.DropFunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#explain.
    def visitExplain(self, ctx:sqlParser.ExplainContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#showTables.
    def visitShowTables(self, ctx:sqlParser.ShowTablesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#showTable.
    def visitShowTable(self, ctx:sqlParser.ShowTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#showTblProperties.
    def visitShowTblProperties(self, ctx:sqlParser.ShowTblPropertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#showColumns.
    def visitShowColumns(self, ctx:sqlParser.ShowColumnsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#showViews.
    def visitShowViews(self, ctx:sqlParser.ShowViewsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#showPartitions.
    def visitShowPartitions(self, ctx:sqlParser.ShowPartitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#showFunctions.
    def visitShowFunctions(self, ctx:sqlParser.ShowFunctionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#showCreateTable.
    def visitShowCreateTable(self, ctx:sqlParser.ShowCreateTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#showCurrentNamespace.
    def visitShowCurrentNamespace(self, ctx:sqlParser.ShowCurrentNamespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#describeFunction.
    def visitDescribeFunction(self, ctx:sqlParser.DescribeFunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#describeNamespace.
    def visitDescribeNamespace(self, ctx:sqlParser.DescribeNamespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#describeRelation.
    def visitDescribeRelation(self, ctx:sqlParser.DescribeRelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#describeQuery.
    def visitDescribeQuery(self, ctx:sqlParser.DescribeQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#commentNamespace.
    def visitCommentNamespace(self, ctx:sqlParser.CommentNamespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#commentTable.
    def visitCommentTable(self, ctx:sqlParser.CommentTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#refreshTable.
    def visitRefreshTable(self, ctx:sqlParser.RefreshTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#refreshResource.
    def visitRefreshResource(self, ctx:sqlParser.RefreshResourceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#cacheTable.
    def visitCacheTable(self, ctx:sqlParser.CacheTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#uncacheTable.
    def visitUncacheTable(self, ctx:sqlParser.UncacheTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#clearCache.
    def visitClearCache(self, ctx:sqlParser.ClearCacheContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#loadData.
    def visitLoadData(self, ctx:sqlParser.LoadDataContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#truncateTable.
    def visitTruncateTable(self, ctx:sqlParser.TruncateTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#repairTable.
    def visitRepairTable(self, ctx:sqlParser.RepairTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#manageResource.
    def visitManageResource(self, ctx:sqlParser.ManageResourceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#failNativeCommand.
    def visitFailNativeCommand(self, ctx:sqlParser.FailNativeCommandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#setConfiguration.
    def visitSetConfiguration(self, ctx:sqlParser.SetConfigurationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#resetConfiguration.
    def visitResetConfiguration(self, ctx:sqlParser.ResetConfigurationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#unsupportedHiveNativeCommands.
    def visitUnsupportedHiveNativeCommands(self, ctx:sqlParser.UnsupportedHiveNativeCommandsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#createTableHeader.
    def visitCreateTableHeader(self, ctx:sqlParser.CreateTableHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#replaceTableHeader.
    def visitReplaceTableHeader(self, ctx:sqlParser.ReplaceTableHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#bucketSpec.
    def visitBucketSpec(self, ctx:sqlParser.BucketSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#skewSpec.
    def visitSkewSpec(self, ctx:sqlParser.SkewSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#locationSpec.
    def visitLocationSpec(self, ctx:sqlParser.LocationSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#commentSpec.
    def visitCommentSpec(self, ctx:sqlParser.CommentSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#query.
    def visitQuery(self, ctx:sqlParser.QueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#insertOverwriteTable.
    def visitInsertOverwriteTable(self, ctx:sqlParser.InsertOverwriteTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#insertIntoTable.
    def visitInsertIntoTable(self, ctx:sqlParser.InsertIntoTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#insertOverwriteHiveDir.
    def visitInsertOverwriteHiveDir(self, ctx:sqlParser.InsertOverwriteHiveDirContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#insertOverwriteDir.
    def visitInsertOverwriteDir(self, ctx:sqlParser.InsertOverwriteDirContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#partitionSpecLocation.
    def visitPartitionSpecLocation(self, ctx:sqlParser.PartitionSpecLocationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#partitionSpec.
    def visitPartitionSpec(self, ctx:sqlParser.PartitionSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#partitionVal.
    def visitPartitionVal(self, ctx:sqlParser.PartitionValContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#namespace.
    def visitNamespace(self, ctx:sqlParser.NamespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#describeFuncName.
    def visitDescribeFuncName(self, ctx:sqlParser.DescribeFuncNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#describeColName.
    def visitDescribeColName(self, ctx:sqlParser.DescribeColNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#ctes.
    def visitCtes(self, ctx:sqlParser.CtesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#namedQuery.
    def visitNamedQuery(self, ctx:sqlParser.NamedQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#tableProvider.
    def visitTableProvider(self, ctx:sqlParser.TableProviderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#createTableClauses.
    def visitCreateTableClauses(self, ctx:sqlParser.CreateTableClausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#tablePropertyList.
    def visitTablePropertyList(self, ctx:sqlParser.TablePropertyListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#tableProperty.
    def visitTableProperty(self, ctx:sqlParser.TablePropertyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#tablePropertyKey.
    def visitTablePropertyKey(self, ctx:sqlParser.TablePropertyKeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#tablePropertyValue.
    def visitTablePropertyValue(self, ctx:sqlParser.TablePropertyValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#constantList.
    def visitConstantList(self, ctx:sqlParser.ConstantListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#nestedConstantList.
    def visitNestedConstantList(self, ctx:sqlParser.NestedConstantListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#createFileFormat.
    def visitCreateFileFormat(self, ctx:sqlParser.CreateFileFormatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#tableFileFormat.
    def visitTableFileFormat(self, ctx:sqlParser.TableFileFormatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#genericFileFormat.
    def visitGenericFileFormat(self, ctx:sqlParser.GenericFileFormatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#storageHandler.
    def visitStorageHandler(self, ctx:sqlParser.StorageHandlerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#resource.
    def visitResource(self, ctx:sqlParser.ResourceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#singleInsertQuery.
    def visitSingleInsertQuery(self, ctx:sqlParser.SingleInsertQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#multiInsertQuery.
    def visitMultiInsertQuery(self, ctx:sqlParser.MultiInsertQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#deleteFromTable.
    def visitDeleteFromTable(self, ctx:sqlParser.DeleteFromTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#updateTable.
    def visitUpdateTable(self, ctx:sqlParser.UpdateTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#mergeIntoTable.
    def visitMergeIntoTable(self, ctx:sqlParser.MergeIntoTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#queryOrganization.
    def visitQueryOrganization(self, ctx:sqlParser.QueryOrganizationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#multiInsertQueryBody.
    def visitMultiInsertQueryBody(self, ctx:sqlParser.MultiInsertQueryBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#queryTermDefault.
    def visitQueryTermDefault(self, ctx:sqlParser.QueryTermDefaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#setOperation.
    def visitSetOperation(self, ctx:sqlParser.SetOperationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#queryPrimaryDefault.
    def visitQueryPrimaryDefault(self, ctx:sqlParser.QueryPrimaryDefaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#fromStmt.
    def visitFromStmt(self, ctx:sqlParser.FromStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#table.
    def visitTable(self, ctx:sqlParser.TableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#inlineTableDefault1.
    def visitInlineTableDefault1(self, ctx:sqlParser.InlineTableDefault1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#subquery.
    def visitSubquery(self, ctx:sqlParser.SubqueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#sortItem.
    def visitSortItem(self, ctx:sqlParser.SortItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#fromStatement.
    def visitFromStatement(self, ctx:sqlParser.FromStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#fromStatementBody.
    def visitFromStatementBody(self, ctx:sqlParser.FromStatementBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#transformQuerySpecification.
    def visitTransformQuerySpecification(self, ctx:sqlParser.TransformQuerySpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#regularQuerySpecification.
    def visitRegularQuerySpecification(self, ctx:sqlParser.RegularQuerySpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#transformClause.
    def visitTransformClause(self, ctx:sqlParser.TransformClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#selectClause.
    def visitSelectClause(self, ctx:sqlParser.SelectClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#setClause.
    def visitSetClause(self, ctx:sqlParser.SetClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#matchedClause.
    def visitMatchedClause(self, ctx:sqlParser.MatchedClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#notMatchedClause.
    def visitNotMatchedClause(self, ctx:sqlParser.NotMatchedClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#matchedAction.
    def visitMatchedAction(self, ctx:sqlParser.MatchedActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#notMatchedAction.
    def visitNotMatchedAction(self, ctx:sqlParser.NotMatchedActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#assignmentList.
    def visitAssignmentList(self, ctx:sqlParser.AssignmentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#assignment.
    def visitAssignment(self, ctx:sqlParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#whereClause.
    def visitWhereClause(self, ctx:sqlParser.WhereClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#havingClause.
    def visitHavingClause(self, ctx:sqlParser.HavingClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#hint.
    def visitHint(self, ctx:sqlParser.HintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#hintStatement.
    def visitHintStatement(self, ctx:sqlParser.HintStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#fromClause.
    def visitFromClause(self, ctx:sqlParser.FromClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#aggregationClause.
    def visitAggregationClause(self, ctx:sqlParser.AggregationClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#groupingSet.
    def visitGroupingSet(self, ctx:sqlParser.GroupingSetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#pivotClause.
    def visitPivotClause(self, ctx:sqlParser.PivotClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#pivotColumn.
    def visitPivotColumn(self, ctx:sqlParser.PivotColumnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#pivotValue.
    def visitPivotValue(self, ctx:sqlParser.PivotValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#lateralView.
    def visitLateralView(self, ctx:sqlParser.LateralViewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#setQuantifier.
    def visitSetQuantifier(self, ctx:sqlParser.SetQuantifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#relation.
    def visitRelation(self, ctx:sqlParser.RelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#joinRelation.
    def visitJoinRelation(self, ctx:sqlParser.JoinRelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#joinType.
    def visitJoinType(self, ctx:sqlParser.JoinTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#joinCriteria.
    def visitJoinCriteria(self, ctx:sqlParser.JoinCriteriaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#sample.
    def visitSample(self, ctx:sqlParser.SampleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#sampleByPercentile.
    def visitSampleByPercentile(self, ctx:sqlParser.SampleByPercentileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#sampleByRows.
    def visitSampleByRows(self, ctx:sqlParser.SampleByRowsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#sampleByBucket.
    def visitSampleByBucket(self, ctx:sqlParser.SampleByBucketContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#sampleByBytes.
    def visitSampleByBytes(self, ctx:sqlParser.SampleByBytesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#identifierList.
    def visitIdentifierList(self, ctx:sqlParser.IdentifierListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#identifierSeq.
    def visitIdentifierSeq(self, ctx:sqlParser.IdentifierSeqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#orderedIdentifierList.
    def visitOrderedIdentifierList(self, ctx:sqlParser.OrderedIdentifierListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#orderedIdentifier.
    def visitOrderedIdentifier(self, ctx:sqlParser.OrderedIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#identifierCommentList.
    def visitIdentifierCommentList(self, ctx:sqlParser.IdentifierCommentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#identifierComment.
    def visitIdentifierComment(self, ctx:sqlParser.IdentifierCommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#tableName.
    def visitTableName(self, ctx:sqlParser.TableNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#aliasedQuery.
    def visitAliasedQuery(self, ctx:sqlParser.AliasedQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#aliasedRelation.
    def visitAliasedRelation(self, ctx:sqlParser.AliasedRelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#inlineTable.
    def visitInlineTable(self, ctx:sqlParser.InlineTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#functionTable.
    def visitFunctionTable(self, ctx:sqlParser.FunctionTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#tableAlias.
    def visitTableAlias(self, ctx:sqlParser.TableAliasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#rowFormatSerde.
    def visitRowFormatSerde(self, ctx:sqlParser.RowFormatSerdeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#rowFormatDelimited.
    def visitRowFormatDelimited(self, ctx:sqlParser.RowFormatDelimitedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#multipartIdentifierList.
    def visitMultipartIdentifierList(self, ctx:sqlParser.MultipartIdentifierListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#multipartIdentifier.
    def visitMultipartIdentifier(self, ctx:sqlParser.MultipartIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#tableIdentifier.
    def visitTableIdentifier(self, ctx:sqlParser.TableIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#functionIdentifier.
    def visitFunctionIdentifier(self, ctx:sqlParser.FunctionIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#namedExpression.
    def visitNamedExpression(self, ctx:sqlParser.NamedExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#namedExpressionSeq.
    def visitNamedExpressionSeq(self, ctx:sqlParser.NamedExpressionSeqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#transformList.
    def visitTransformList(self, ctx:sqlParser.TransformListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#identityTransform.
    def visitIdentityTransform(self, ctx:sqlParser.IdentityTransformContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#applyTransform.
    def visitApplyTransform(self, ctx:sqlParser.ApplyTransformContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#transformArgument.
    def visitTransformArgument(self, ctx:sqlParser.TransformArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#expression.
    def visitExpression(self, ctx:sqlParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#logicalNot.
    def visitLogicalNot(self, ctx:sqlParser.LogicalNotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#predicated.
    def visitPredicated(self, ctx:sqlParser.PredicatedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#exists.
    def visitExists(self, ctx:sqlParser.ExistsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#logicalBinary.
    def visitLogicalBinary(self, ctx:sqlParser.LogicalBinaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#predicate.
    def visitPredicate(self, ctx:sqlParser.PredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#valueExpressionDefault.
    def visitValueExpressionDefault(self, ctx:sqlParser.ValueExpressionDefaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#comparison.
    def visitComparison(self, ctx:sqlParser.ComparisonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#arithmeticBinary.
    def visitArithmeticBinary(self, ctx:sqlParser.ArithmeticBinaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#arithmeticUnary.
    def visitArithmeticUnary(self, ctx:sqlParser.ArithmeticUnaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#struct.
    def visitStruct(self, ctx:sqlParser.StructContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#dereference.
    def visitDereference(self, ctx:sqlParser.DereferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#simpleCase.
    def visitSimpleCase(self, ctx:sqlParser.SimpleCaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#columnReference.
    def visitColumnReference(self, ctx:sqlParser.ColumnReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#rowConstructor.
    def visitRowConstructor(self, ctx:sqlParser.RowConstructorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#last.
    def visitLast(self, ctx:sqlParser.LastContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#star.
    def visitStar(self, ctx:sqlParser.StarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#overlay.
    def visitOverlay(self, ctx:sqlParser.OverlayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#subscript.
    def visitSubscript(self, ctx:sqlParser.SubscriptContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#subqueryExpression.
    def visitSubqueryExpression(self, ctx:sqlParser.SubqueryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#substring.
    def visitSubstring(self, ctx:sqlParser.SubstringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#currentDatetime.
    def visitCurrentDatetime(self, ctx:sqlParser.CurrentDatetimeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#cast.
    def visitCast(self, ctx:sqlParser.CastContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#constantDefault.
    def visitConstantDefault(self, ctx:sqlParser.ConstantDefaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#lambda.
    def visitLambda(self, ctx:sqlParser.LambdaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#parenthesizedExpression.
    def visitParenthesizedExpression(self, ctx:sqlParser.ParenthesizedExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#extract.
    def visitExtract(self, ctx:sqlParser.ExtractContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#trim.
    def visitTrim(self, ctx:sqlParser.TrimContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#functionCall.
    def visitFunctionCall(self, ctx:sqlParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#searchedCase.
    def visitSearchedCase(self, ctx:sqlParser.SearchedCaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#position.
    def visitPosition(self, ctx:sqlParser.PositionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#first.
    def visitFirst(self, ctx:sqlParser.FirstContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#nullLiteral.
    def visitNullLiteral(self, ctx:sqlParser.NullLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#intervalLiteral.
    def visitIntervalLiteral(self, ctx:sqlParser.IntervalLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#typeConstructor.
    def visitTypeConstructor(self, ctx:sqlParser.TypeConstructorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#numericLiteral.
    def visitNumericLiteral(self, ctx:sqlParser.NumericLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#booleanLiteral.
    def visitBooleanLiteral(self, ctx:sqlParser.BooleanLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#stringLiteral.
    def visitStringLiteral(self, ctx:sqlParser.StringLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#comparisonOperator.
    def visitComparisonOperator(self, ctx:sqlParser.ComparisonOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#arithmeticOperator.
    def visitArithmeticOperator(self, ctx:sqlParser.ArithmeticOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#predicateOperator.
    def visitPredicateOperator(self, ctx:sqlParser.PredicateOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#booleanValue.
    def visitBooleanValue(self, ctx:sqlParser.BooleanValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#interval.
    def visitInterval(self, ctx:sqlParser.IntervalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#errorCapturingMultiUnitsInterval.
    def visitErrorCapturingMultiUnitsInterval(self, ctx:sqlParser.ErrorCapturingMultiUnitsIntervalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#multiUnitsInterval.
    def visitMultiUnitsInterval(self, ctx:sqlParser.MultiUnitsIntervalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#errorCapturingUnitToUnitInterval.
    def visitErrorCapturingUnitToUnitInterval(self, ctx:sqlParser.ErrorCapturingUnitToUnitIntervalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#unitToUnitInterval.
    def visitUnitToUnitInterval(self, ctx:sqlParser.UnitToUnitIntervalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#intervalValue.
    def visitIntervalValue(self, ctx:sqlParser.IntervalValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#intervalUnit.
    def visitIntervalUnit(self, ctx:sqlParser.IntervalUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#colPosition.
    def visitColPosition(self, ctx:sqlParser.ColPositionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#complexDataType.
    def visitComplexDataType(self, ctx:sqlParser.ComplexDataTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#primitiveDataType.
    def visitPrimitiveDataType(self, ctx:sqlParser.PrimitiveDataTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#qualifiedColTypeWithPositionList.
    def visitQualifiedColTypeWithPositionList(self, ctx:sqlParser.QualifiedColTypeWithPositionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#qualifiedColTypeWithPosition.
    def visitQualifiedColTypeWithPosition(self, ctx:sqlParser.QualifiedColTypeWithPositionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#colTypeList.
    def visitColTypeList(self, ctx:sqlParser.ColTypeListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#colType.
    def visitColType(self, ctx:sqlParser.ColTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#complexColTypeList.
    def visitComplexColTypeList(self, ctx:sqlParser.ComplexColTypeListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#complexColType.
    def visitComplexColType(self, ctx:sqlParser.ComplexColTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#whenClause.
    def visitWhenClause(self, ctx:sqlParser.WhenClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#windowClause.
    def visitWindowClause(self, ctx:sqlParser.WindowClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#namedWindow.
    def visitNamedWindow(self, ctx:sqlParser.NamedWindowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#windowRef.
    def visitWindowRef(self, ctx:sqlParser.WindowRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#windowDef.
    def visitWindowDef(self, ctx:sqlParser.WindowDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#windowFrame.
    def visitWindowFrame(self, ctx:sqlParser.WindowFrameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#frameBound.
    def visitFrameBound(self, ctx:sqlParser.FrameBoundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#qualifiedNameList.
    def visitQualifiedNameList(self, ctx:sqlParser.QualifiedNameListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#functionName.
    def visitFunctionName(self, ctx:sqlParser.FunctionNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#qualifiedName.
    def visitQualifiedName(self, ctx:sqlParser.QualifiedNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#errorCapturingIdentifier.
    def visitErrorCapturingIdentifier(self, ctx:sqlParser.ErrorCapturingIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#errorIdent.
    def visitErrorIdent(self, ctx:sqlParser.ErrorIdentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#realIdent.
    def visitRealIdent(self, ctx:sqlParser.RealIdentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#identifier.
    def visitIdentifier(self, ctx:sqlParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#unquotedIdentifier.
    def visitUnquotedIdentifier(self, ctx:sqlParser.UnquotedIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#quotedIdentifierAlternative.
    def visitQuotedIdentifierAlternative(self, ctx:sqlParser.QuotedIdentifierAlternativeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#quotedIdentifier.
    def visitQuotedIdentifier(self, ctx:sqlParser.QuotedIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#exponentLiteral.
    def visitExponentLiteral(self, ctx:sqlParser.ExponentLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#decimalLiteral.
    def visitDecimalLiteral(self, ctx:sqlParser.DecimalLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#legacyDecimalLiteral.
    def visitLegacyDecimalLiteral(self, ctx:sqlParser.LegacyDecimalLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#integerLiteral.
    def visitIntegerLiteral(self, ctx:sqlParser.IntegerLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#bigIntLiteral.
    def visitBigIntLiteral(self, ctx:sqlParser.BigIntLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#smallIntLiteral.
    def visitSmallIntLiteral(self, ctx:sqlParser.SmallIntLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#tinyIntLiteral.
    def visitTinyIntLiteral(self, ctx:sqlParser.TinyIntLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#doubleLiteral.
    def visitDoubleLiteral(self, ctx:sqlParser.DoubleLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#bigDecimalLiteral.
    def visitBigDecimalLiteral(self, ctx:sqlParser.BigDecimalLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#alterColumnAction.
    def visitAlterColumnAction(self, ctx:sqlParser.AlterColumnActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#ansiNonReserved.
    def visitAnsiNonReserved(self, ctx:sqlParser.AnsiNonReservedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#strictNonReserved.
    def visitStrictNonReserved(self, ctx:sqlParser.StrictNonReservedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sqlParser#nonReserved.
    def visitNonReserved(self, ctx:sqlParser.NonReservedContext):
        return self.visitChildren(ctx)



del sqlParser