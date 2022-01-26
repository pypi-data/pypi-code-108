from typing import List
from backports.cached_property import cached_property
from .asts import AST

class TerminalSymbol(AST):
    pass


class CXXAST(AST):
    pass


class CAST(CXXAST, AST):
    pass


class CNewline(CAST, TerminalSymbol, AST):
    pass


class CXXLogicalNot(AST):
    pass


class CLogicalNot(CAST, CXXLogicalNot, TerminalSymbol, AST):
    pass


class CXXNotEqual(AST):
    pass


class CNotEqual(CAST, CXXNotEqual, TerminalSymbol, AST):
    pass


class CDoubleQuote(CAST, TerminalSymbol, AST):
    pass


class CMacroDefine(CAST, TerminalSymbol, AST):
    pass


class CMacroElif(CAST, TerminalSymbol, AST):
    pass


class CMacroElse(CAST, TerminalSymbol, AST):
    pass


class CMacroEndIf(CAST, TerminalSymbol, AST):
    pass


class CMacroIf(CAST, TerminalSymbol, AST):
    pass


class CMacroIfDefined(CAST, TerminalSymbol, AST):
    pass


class CMacroIfNotDefined(CAST, TerminalSymbol, AST):
    pass


class CMacroInclude(CAST, TerminalSymbol, AST):
    pass


class CXXModulo(AST):
    pass


class CModulo(CAST, CXXModulo, TerminalSymbol, AST):
    pass


class CModuleAssign(CAST, TerminalSymbol, AST):
    pass


class CXXBitwiseAnd(AST):
    pass


class CBitwiseAnd(CAST, CXXBitwiseAnd, TerminalSymbol, AST):
    pass


class CXXLogicalAnd(AST):
    pass


class CLogicalAnd(CAST, CXXLogicalAnd, TerminalSymbol, AST):
    pass


class CBitwiseAndAssign(CAST, TerminalSymbol, AST):
    pass


class CSingleQuote(CAST, TerminalSymbol, AST):
    pass


class COpenParenthesis(CAST, TerminalSymbol, AST):
    pass


class CCloseParenthesis(CAST, TerminalSymbol, AST):
    pass


class CXXMultiply(AST):
    pass


class CMultiply(CAST, CXXMultiply, TerminalSymbol, AST):
    pass


class CMultiplyAssign(CAST, TerminalSymbol, AST):
    pass


class CXXAdd(AST):
    pass


class CAdd(CAST, CXXAdd, TerminalSymbol, AST):
    pass


class CXXIncrement(AST):
    pass


class CIncrement(CAST, CXXIncrement, TerminalSymbol, AST):
    pass


class CAddAssign(CAST, TerminalSymbol, AST):
    pass


class CComma(CAST, TerminalSymbol, AST):
    pass


class CXXSubtract(AST):
    pass


class CSubtract(CAST, CXXSubtract, TerminalSymbol, AST):
    pass


class CXXDecrement(AST):
    pass


class CDecrement(CAST, CXXDecrement, TerminalSymbol, AST):
    pass


class CAttributeSubtract(CAST, TerminalSymbol, AST):
    pass


class CBased(CAST, TerminalSymbol, AST):
    pass


class CCdecl(CAST, TerminalSymbol, AST):
    pass


class CClrcall(CAST, TerminalSymbol, AST):
    pass


class CDeclspec(CAST, TerminalSymbol, AST):
    pass


class CFastcall(CAST, TerminalSymbol, AST):
    pass


class CStdcall(CAST, TerminalSymbol, AST):
    pass


class CThiscall(CAST, TerminalSymbol, AST):
    pass


class CUnderscoreUnaligned(CAST, TerminalSymbol, AST):
    pass


class CVectorcall(CAST, TerminalSymbol, AST):
    pass


class CSubtractAssign(CAST, TerminalSymbol, AST):
    pass


class CArrow(CAST, TerminalSymbol, AST):
    pass


class CAbstractDeclarator(CAST, AST):
    pass


class CAtomic(CAST, TerminalSymbol, AST):
    pass


class CDeclarator(CAST, AST):
    pass


class ExpressionAST(AST):
    pass


class CExpression(CAST, ExpressionAST, AST):
    pass


class CFieldDeclarator(CAST, AST):
    pass


class StatementAST(AST):
    pass


class CStatement(CAST, StatementAST, AST):
    pass


class CTypeDeclarator(CAST, AST):
    pass


class CTypeSpecifier(CAST, AST):
    pass


class CUnaligned(CAST, TerminalSymbol, AST):
    pass


class CDot(CAST, TerminalSymbol, AST):
    pass


class CEllipsis(CAST, TerminalSymbol, AST):
    pass


class CXXDivide(AST):
    pass


class CDivide(CAST, CXXDivide, TerminalSymbol, AST):
    pass


class CDivideAssign(CAST, TerminalSymbol, AST):
    pass


class CColon(CAST, TerminalSymbol, AST):
    pass


class CScopeResolution(CAST, TerminalSymbol, AST):
    pass


class CSemicolon(CAST, TerminalSymbol, AST):
    pass


class CXXLessThan(AST):
    pass


class CLessThan(CAST, CXXLessThan, TerminalSymbol, AST):
    pass


class CXXBitshiftLeft(AST):
    pass


class CBitshiftLeft(CAST, CXXBitshiftLeft, TerminalSymbol, AST):
    pass


class CBitshiftLeftAssign(CAST, TerminalSymbol, AST):
    pass


class CXXLessThanOrEqual(AST):
    pass


class CLessThanOrEqual(CAST, CXXLessThanOrEqual, TerminalSymbol, AST):
    pass


class CAssign(CAST, TerminalSymbol, AST):
    pass


class CXXEqual(AST):
    pass


class CEqual(CAST, CXXEqual, TerminalSymbol, AST):
    pass


class CXXGreaterThan(AST):
    pass


class CGreaterThan(CAST, CXXGreaterThan, TerminalSymbol, AST):
    pass


class CXXGreaterThanOrEqual(AST):
    pass


class CGreaterThanOrEqual(CAST, CXXGreaterThanOrEqual, TerminalSymbol, AST):
    pass


class CXXBitshiftRight(AST):
    pass


class CBitshiftRight(CAST, CXXBitshiftRight, TerminalSymbol, AST):
    pass


class CBitshiftRightAssign(CAST, TerminalSymbol, AST):
    pass


class CQuestion(CAST, TerminalSymbol, AST):
    pass


class CXXAbstractArrayDeclarator(AST):
    pass


class CAbstractArrayDeclarator(CAbstractDeclarator, CXXAbstractArrayDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def size(self) -> AST:
            return self.child_slot("SIZE")


class CXXAbstractFunctionDeclarator(AST):
    pass


class CAbstractFunctionDeclarator(CAbstractDeclarator, CXXAbstractFunctionDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CAbstractParenthesizedDeclarator(CAbstractDeclarator, AST):
    pass


class CXXAbstractPointerDeclarator(AST):
    pass


class CAbstractPointerDeclarator(CAbstractDeclarator, CXXAbstractPointerDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")


class CXXArgumentList(AST):
    pass


class CArgumentList(CAST, CXXArgumentList, AST):
    pass


class CArgumentList0(CArgumentList, AST):
    pass


class CArgumentList1(CArgumentList, AST):
    pass


class CXXArrayDeclarator(AST):
    pass


class CArrayDeclarator(CTypeDeclarator, CFieldDeclarator, CDeclarator, CXXArrayDeclarator, AST):
    pass


class CArrayDeclarator0(CArrayDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def size(self) -> AST:
            return self.child_slot("SIZE")


class CArrayDeclarator1(CArrayDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def size(self) -> AST:
            return self.child_slot("SIZE")


class DeclarationAST(AST):
    pass


class VariableDeclarationAST(DeclarationAST, AST):
    pass


class VariableInitializationAST(VariableDeclarationAST, AST):
    pass


class AssignmentAST(AST):
    pass


class CXXAssignmentExpression(AST):
    pass


class CAssignmentExpression(CExpression, CXXAssignmentExpression, AssignmentAST, VariableInitializationAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class CAttribute(CAST, AST):
    pass


class CAttribute0(CAttribute, AST):
        @cached_property
        def prefix(self) -> AST:
            return self.child_slot("PREFIX")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CAttribute1(CAttribute, AST):
        @cached_property
        def prefix(self) -> AST:
            return self.child_slot("PREFIX")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CAttribute2(CAttribute, AST):
        @cached_property
        def prefix(self) -> AST:
            return self.child_slot("PREFIX")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CAttribute3(CAttribute, AST):
        @cached_property
        def prefix(self) -> AST:
            return self.child_slot("PREFIX")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CAttributeDeclaration(CAST, AST):
    pass


class CAttributeSpecifier(CAST, AST):
    pass


class CAttributedDeclarator(CTypeDeclarator, CFieldDeclarator, CDeclarator, AST):
    pass


class CAttributedDeclarator0(CAttributedDeclarator, AST):
    pass


class CAttributedDeclarator1(CAttributedDeclarator, AST):
    pass


class CAttributedStatement(CAST, AST):
    pass


class CAttributedStatement0(CAttributedStatement, AST):
    pass


class CAttributedStatement1(CAttributedStatement, AST):
    pass


class CAuto(CAST, TerminalSymbol, AST):
    pass


class BinaryAST(ExpressionAST, AST):
    pass


class CXXBinaryExpression(AST):
    pass


class CBinaryExpression(CExpression, CXXBinaryExpression, BinaryAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class CBitfieldClause(CAST, AST):
    pass


class CBreak(CAST, TerminalSymbol, AST):
    pass


class CXXBreakStatement(AST):
    pass


class CBreakStatement(CStatement, CXXBreakStatement, AST):
    pass


class CallAST(ExpressionAST, AST):
    pass


class CXXCallExpression(AST):
    pass


class CCallExpression(CExpression, CXXCallExpression, CallAST, AST):
    pass


class CCallExpression0(CCallExpression, AST):
        @cached_property
        def function(self) -> AST:
            return self.child_slot("FUNCTION")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class CCallExpression1(CCallExpression, AST):
        @cached_property
        def function(self) -> AST:
            return self.child_slot("FUNCTION")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class CCase(CAST, TerminalSymbol, AST):
    pass


class ControlFlowAST(AST):
    pass


class CXXCaseStatement(AST):
    pass


class CCaseStatement(CStatement, CXXCaseStatement, ControlFlowAST, AST):
    pass


class CCaseStatement0(CCaseStatement, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def statements(self) -> List[AST]:
            return self.child_slot("STATEMENTS")


class CCaseStatement1(CCaseStatement, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def statements(self) -> List[AST]:
            return self.child_slot("STATEMENTS")


class CXXCastExpression(AST):
    pass


class CCastExpression(CExpression, CXXCastExpression, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CXXCharLiteral(AST):
    pass


class CCharLiteral(CExpression, CXXCharLiteral, AST):
    pass


class CCommaExpression(CAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class CommentAST(AST):
    pass


class CXXComment(AST):
    pass


class CComment(CAST, CXXComment, CommentAST, AST):
    pass


class CCompoundLiteralExpression(CExpression, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CompoundAST(AST):
    pass


class CXXCompoundStatement(AST):
    pass


class CCompoundStatement(CStatement, CXXCompoundStatement, CompoundAST, AST):
    pass


class CConcatenatedString(CExpression, AST):
    pass


class CConditionalExpression(CExpression, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CConst(CAST, TerminalSymbol, AST):
    pass


class CContinue(CAST, TerminalSymbol, AST):
    pass


class CXXContinueStatement(AST):
    pass


class CContinueStatement(CStatement, CXXContinueStatement, AST):
    pass


class CXXDeclaration(AST):
    pass


class CDeclaration(CAST, CXXDeclaration, StatementAST, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CDeclarationList(CAST, AST):
    pass


class CDefault(CAST, TerminalSymbol, AST):
    pass


class CDefined(CAST, TerminalSymbol, AST):
    pass


class CDo(CAST, TerminalSymbol, AST):
    pass


class LoopAST(ControlFlowAST, AST):
    pass


class CXXDoStatement(AST):
    pass


class CDoStatement(CStatement, CXXDoStatement, LoopAST, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")


class CElse(CAST, TerminalSymbol, AST):
    pass


class CEnum(CAST, TerminalSymbol, AST):
    pass


class DefinitionAST(AST):
    pass


class TypeDeclarationAST(DeclarationAST, AST):
    pass


class CXXEnumSpecifier(AST):
    pass


class CEnumSpecifier(CTypeSpecifier, CXXEnumSpecifier, TypeDeclarationAST, DefinitionAST, AST):
    pass


class CEnumSpecifier0(CEnumSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CEnumSpecifier1(CEnumSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CXXEnumerator(AST):
    pass


class CEnumerator(CAST, CXXEnumerator, AST):
    pass


class CEnumerator0(CEnumerator, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CEnumerator1(CEnumerator, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CXXEnumeratorList(AST):
    pass


class CEnumeratorList(CAST, CXXEnumeratorList, AST):
    pass


class CEnumeratorList0(CEnumeratorList, AST):
    pass


class CEnumeratorList1(CEnumeratorList, AST):
    pass


class CEnumeratorList2(CEnumeratorList, AST):
    pass


class CEnumeratorList3(CEnumeratorList, AST):
    pass


class ParseErrorAST(AST):
    pass


class CXXError(AST):
    pass


class CError(CAST, CXXError, ParseErrorAST, AST):
    pass


class CEscapeSequence(CAST, AST):
    pass


class ExpressionStatementAST(AST):
    pass


class CXXExpressionStatement(AST):
    pass


class CExpressionStatement(CStatement, CXXExpressionStatement, ExpressionStatementAST, AST):
    pass


class CExpressionStatement0(CExpressionStatement, AST):
    pass


class CExpressionStatement1(CExpressionStatement, AST):
    pass


class CExtern(CAST, TerminalSymbol, AST):
    pass


class LiteralAST(AST):
    pass


class BooleanAST(LiteralAST, AST):
    pass


class BooleanFalseAST(BooleanAST, AST):
    pass


class CFalse(CExpression, BooleanFalseAST, AST):
    pass


class CXXFieldDeclaration(AST):
    pass


class CFieldDeclaration(CAST, CXXFieldDeclaration, DeclarationAST, DefinitionAST, AST):
    pass


class CFieldDeclaration0(CFieldDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CFieldDeclaration1(CFieldDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CFieldDeclaration2(CFieldDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CFieldDeclaration3(CFieldDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CFieldDeclarationList(CAST, AST):
    pass


class CFieldDesignator(CAST, AST):
    pass


class FieldAST(AST):
    pass


class CXXFieldExpression(AST):
    pass


class CFieldExpression(CExpression, CXXFieldExpression, FieldAST, AST):
        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def field(self) -> AST:
            return self.child_slot("FIELD")


class IdentifierAST(AST):
    pass


class CXXFieldIdentifier(AST):
    pass


class CFieldIdentifier(CFieldDeclarator, CXXFieldIdentifier, IdentifierAST, AST):
    pass


class CFor(CAST, TerminalSymbol, AST):
    pass


class CXXForStatement(AST):
    pass


class CForStatement(CStatement, CXXForStatement, LoopAST, AST):
    pass


class CForStatement0(CForStatement, AST):
        @cached_property
        def initializer(self) -> AST:
            return self.child_slot("INITIALIZER")

        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def update(self) -> AST:
            return self.child_slot("UPDATE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CForStatement1(CForStatement, AST):
        @cached_property
        def initializer(self) -> AST:
            return self.child_slot("INITIALIZER")

        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def update(self) -> AST:
            return self.child_slot("UPDATE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CXXFunctionDeclarator(AST):
    pass


class CFunctionDeclarator(CTypeDeclarator, CFieldDeclarator, CDeclarator, CXXFunctionDeclarator, AST):
    pass


class CFunctionDeclarator0(CFunctionDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CFunctionDeclarator1(CFunctionDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class FunctionAST(AST):
    pass


class FunctionDeclarationAST(FunctionAST, DeclarationAST, AST):
    pass


class CXXFunctionDefinition(AST):
    pass


class CFunctionDefinition(CAST, CXXFunctionDefinition, FunctionDeclarationAST, StatementAST, AST):
    pass


class CFunctionDefinition0(CFunctionDefinition, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CFunctionDefinition1(CFunctionDefinition, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CGoto(CAST, TerminalSymbol, AST):
    pass


class GotoAST(StatementAST, AST):
    pass


class CGotoStatement(CStatement, GotoAST, AST):
        @cached_property
        def label(self) -> AST:
            return self.child_slot("LABEL")


class CXXIdentifier(AST):
    pass


class CIdentifier(CDeclarator, CExpression, CXXIdentifier, IdentifierAST, AST):
    pass


class CIf(CAST, TerminalSymbol, AST):
    pass


class ConditionalAST(AST):
    pass


class IfAST(ControlFlowAST, ConditionalAST, AST):
    pass


class CXXIfStatement(AST):
    pass


class CIfStatement(CStatement, CXXIfStatement, IfAST, AST):
    pass


class CIfStatement0(CIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CIfStatement1(CIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CXXInitDeclarator(AST):
    pass


class CInitDeclarator(CAST, CXXInitDeclarator, VariableInitializationAST, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CInitializerList(CAST, AST):
    pass


class CInitializerList0(CInitializerList, AST):
    pass


class CInitializerList1(CInitializerList, AST):
    pass


class CInitializerList2(CInitializerList, AST):
    pass


class CInitializerList3(CInitializerList, AST):
    pass


class CXXInitializerPair(AST):
    pass


class CInitializerPair(CAST, CXXInitializerPair, AST):
        @cached_property
        def designator(self) -> List[AST]:
            return self.child_slot("DESIGNATOR")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CInline(CAST, TerminalSymbol, AST):
    pass


class TextFragment(AST):
    pass


class InnerWhitespace(TextFragment, AST):
    pass


class CInnerWhitespace(CAST, InnerWhitespace, AST):
    pass


class CWcharDoubleQuote(CAST, TerminalSymbol, AST):
    pass


class CWcharSingleQuote(CAST, TerminalSymbol, AST):
    pass


class CLabeledStatement(CStatement, AST):
        @cached_property
        def label(self) -> AST:
            return self.child_slot("LABEL")

        @cached_property
        def statement(self) -> AST:
            return self.child_slot("STATEMENT")


class CLinkageSpecification(CAST, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CLong(CAST, TerminalSymbol, AST):
    pass


class CMacroTypeSpecifier(CTypeSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class CMsBasedModifier(CAST, AST):
    pass


class CMsCallModifier(CAST, AST):
    pass


class CMsDeclspecModifier(CAST, AST):
    pass


class CMsPointerModifier(CAST, AST):
    pass


class CMsRestrictModifier(CAST, AST):
    pass


class CMsSignedPtrModifier(CAST, AST):
    pass


class CMsUnalignedPtrModifier(CAST, AST):
    pass


class CMsUnsignedPtrModifier(CAST, AST):
    pass


class CNull(CExpression, AST):
    pass


class NumberAST(LiteralAST, AST):
    pass


class CXXNumberLiteral(AST):
    pass


class CNumberLiteral(CExpression, CXXNumberLiteral, NumberAST, AST):
    pass


class ParameterAST(VariableDeclarationAST, AST):
    pass


class CXXParameterDeclaration(AST):
    pass


class CParameterDeclaration(CAST, CXXParameterDeclaration, ParameterAST, AST):
    pass


class CParameterDeclaration0(CParameterDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CParameterDeclaration1(CParameterDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CParameterList(CAST, AST):
    pass


class CParameterList0(CParameterList, AST):
    pass


class CParameterList1(CParameterList, AST):
    pass


class CXXParenthesizedDeclarator(AST):
    pass


class CParenthesizedDeclarator(CTypeDeclarator, CFieldDeclarator, CDeclarator, CXXParenthesizedDeclarator, AST):
    pass


class CParenthesizedDeclarator0(CParenthesizedDeclarator, AST):
    pass


class CParenthesizedDeclarator1(CParenthesizedDeclarator, AST):
    pass


class ParenthesizedExpressionAST(AST):
    pass


class CXXParenthesizedExpression(AST):
    pass


class CParenthesizedExpression(CExpression, CXXParenthesizedExpression, ParenthesizedExpressionAST, AST):
    pass


class CParenthesizedExpression0(CParenthesizedExpression, AST):
    pass


class CParenthesizedExpression1(CParenthesizedExpression, AST):
    pass


class CXXPointerDeclarator(AST):
    pass


class CPointerDeclarator(CTypeDeclarator, CFieldDeclarator, CDeclarator, CXXPointerDeclarator, AST):
    pass


class CPointerDeclarator0(CPointerDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")


class CPointerDeclarator1(CPointerDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")


class CXXPointerExpression(AST):
    pass


class CPointerExpression(CExpression, CXXPointerExpression, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class CXXPreprocArg(AST):
    pass


class CPreprocArg(CAST, CXXPreprocArg, AST):
    pass


class CPreprocCall(CAST, AST):
        @cached_property
        def directive(self) -> AST:
            return self.child_slot("DIRECTIVE")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class CXXPreprocDef(AST):
    pass


class CPreprocDef(CAST, CXXPreprocDef, DefinitionAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPreprocDefined(CAST, AST):
    pass


class CPreprocDefined0(CPreprocDefined, AST):
    pass


class CPreprocDefined1(CPreprocDefined, AST):
    pass


class CPreprocDirective(CAST, AST):
    pass


class CXXPreprocElif(AST):
    pass


class CPreprocElif(CAST, CXXPreprocElif, AST):
    pass


class CPreprocElif0(CPreprocElif, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CPreprocElif1(CPreprocElif, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CXXPreprocElse(AST):
    pass


class CPreprocElse(CAST, CXXPreprocElse, AST):
    pass


class CPreprocElse0(CPreprocElse, AST):
    pass


class CPreprocElse1(CPreprocElse, AST):
    pass


class CXXPreprocFunctionDef(AST):
    pass


class CPreprocFunctionDef(CAST, CXXPreprocFunctionDef, DefinitionAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPreprocIf(CAST, AST):
    pass


class CPreprocIf0(CPreprocIf, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CPreprocIf1(CPreprocIf, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CPreprocIfdef(CAST, AST):
    pass


class CPreprocIfdef0(CPreprocIfdef, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")

        @cached_property
        def operator(self) -> List[AST]:
            return self.child_slot("OPERATOR")


class CPreprocIfdef1(CPreprocIfdef, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")

        @cached_property
        def operator(self) -> List[AST]:
            return self.child_slot("OPERATOR")


class CXXPreprocInclude(AST):
    pass


class CPreprocInclude(CAST, CXXPreprocInclude, AST):
        @cached_property
        def path(self) -> AST:
            return self.child_slot("PATH")


class CXXPreprocParams(AST):
    pass


class CPreprocParams(CAST, CXXPreprocParams, AST):
    pass


class CXXPrimitiveType(AST):
    pass


class CPrimitiveType(CTypeSpecifier, CXXPrimitiveType, AST):
    pass


class CRegister(CAST, TerminalSymbol, AST):
    pass


class CRestrict(CAST, TerminalSymbol, AST):
    pass


class CReturn(CAST, TerminalSymbol, AST):
    pass


class ReturnAST(StatementAST, AST):
    pass


class CXXReturnStatement(AST):
    pass


class CReturnStatement(CStatement, CXXReturnStatement, ReturnAST, AST):
    pass


class CReturnStatement0(CReturnStatement, AST):
    pass


class CReturnStatement1(CReturnStatement, AST):
    pass


class CShort(CAST, TerminalSymbol, AST):
    pass


class CXXSigned(AST):
    pass


class CSigned(CAST, CXXSigned, TerminalSymbol, AST):
    pass


class CXXSizedTypeSpecifier(AST):
    pass


class CSizedTypeSpecifier(CTypeSpecifier, CXXSizedTypeSpecifier, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def modifiers(self) -> List[AST]:
            return self.child_slot("MODIFIERS")


class CSizeof(CAST, TerminalSymbol, AST):
    pass


class CXXSizeofExpression(AST):
    pass


class CSizeofExpression(CExpression, CXXSizeofExpression, AST):
    pass


class CSizeofExpression0(CSizeofExpression, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CSizeofExpression1(CSizeofExpression, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class SourceTextFragment(AST):
    pass


class CSourceTextFragment(CAST, SourceTextFragment, AST):
    pass


class CStatementIdentifier(CAST, AST):
    pass


class CStatic(CAST, TerminalSymbol, AST):
    pass


class CXXStorageClassSpecifier(AST):
    pass


class CStorageClassSpecifier(CAST, CXXStorageClassSpecifier, AST):
    pass


class StringAST(LiteralAST, AST):
    pass


class CXXStringLiteral(AST):
    pass


class CStringLiteral(CExpression, CXXStringLiteral, StringAST, AST):
    pass


class CStruct(CAST, TerminalSymbol, AST):
    pass


class CXXStructSpecifier(AST):
    pass


class CStructSpecifier(CTypeSpecifier, CXXStructSpecifier, TypeDeclarationAST, DefinitionAST, AST):
    pass


class CStructSpecifier0(CStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CStructSpecifier1(CStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CStructSpecifier2(CStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CStructSpecifier3(CStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CStructSpecifier4(CStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CStructSpecifier5(CStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CSubscriptDesignator(CAST, AST):
    pass


class SubscriptAST(AST):
    pass


class CXXSubscriptExpression(AST):
    pass


class CSubscriptExpression(CExpression, CXXSubscriptExpression, SubscriptAST, AST):
        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")

        @cached_property
        def index(self) -> AST:
            return self.child_slot("INDEX")


class CSwitch(CAST, TerminalSymbol, AST):
    pass


class CXXSwitchStatement(AST):
    pass


class CSwitchStatement(CStatement, CXXSwitchStatement, ControlFlowAST, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CSystemLibString(CAST, AST):
    pass


class RootAST(AST):
    pass


class CTranslationUnit(CAST, RootAST, AST):
    pass


class BooleanTrueAST(BooleanAST, AST):
    pass


class CTrue(CExpression, BooleanTrueAST, AST):
    pass


class CXXTypeDefinition(AST):
    pass


class CXXTypeIdentifier(AST):
    pass


class CTypeDefinition(CAST, CXXTypeIdentifier, CXXTypeDefinition, TypeDeclarationAST, DefinitionAST, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")


class CXXTypeDescriptor(AST):
    pass


class CTypeDescriptor(CAST, CXXTypeDescriptor, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_type_qualifiers(self) -> List[AST]:
            return self.child_slot("PRE-TYPE-QUALIFIERS")

        @cached_property
        def post_type_qualifiers(self) -> List[AST]:
            return self.child_slot("POST-TYPE-QUALIFIERS")


class CTypeIdentifier(CTypeDeclarator, CTypeSpecifier, AST):
    pass


class CXXTypeQualifier(AST):
    pass


class CTypeQualifier(CAST, CXXTypeQualifier, AST):
    pass


class CTypedef(CAST, TerminalSymbol, AST):
    pass


class CUnicodeDoubleQuote(CAST, TerminalSymbol, AST):
    pass


class CUnsignedTerminalDoubleQuote(CAST, TerminalSymbol, AST):
    pass


class CUnicodeSingleQuote(CAST, TerminalSymbol, AST):
    pass


class CUnsignedTerminalSingleQuote(CAST, TerminalSymbol, AST):
    pass


class CUnsigned8bitTerminalDoubleQuote(CAST, TerminalSymbol, AST):
    pass


class CUnsigned8bitTerminalSingleQuote(CAST, TerminalSymbol, AST):
    pass


class UnaryAST(ExpressionAST, AST):
    pass


class CXXUnaryExpression(AST):
    pass


class CUnaryExpression(CExpression, CXXUnaryExpression, UnaryAST, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class CUnion(CAST, TerminalSymbol, AST):
    pass


class CXXUnionSpecifier(AST):
    pass


class CUnionSpecifier(CTypeSpecifier, CXXUnionSpecifier, TypeDeclarationAST, DefinitionAST, AST):
    pass


class CUnionSpecifier0(CUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CUnionSpecifier1(CUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CUnionSpecifier2(CUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CUnionSpecifier3(CUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CUnsigned(CAST, TerminalSymbol, AST):
    pass


class CXXUpdateExpression(AST):
    pass


class CUpdateExpression(CExpression, CXXUpdateExpression, AssignmentAST, AST):
    pass


class CUpdateExpressionPostfix(CUpdateExpression, AST):
        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class CUpdateExpressionPrefix(CUpdateExpression, AST):
        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class CVariadicDeclaration(CParameterDeclaration, CIdentifier, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CVariadicParameter(CAST, AST):
    pass


class CVolatile(CAST, TerminalSymbol, AST):
    pass


class CWhile(CAST, TerminalSymbol, AST):
    pass


class WhileAST(ControlFlowAST, ConditionalAST, AST):
    pass


class CXXWhileStatement(AST):
    pass


class CWhileStatement(CStatement, CXXWhileStatement, LoopAST, WhileAST, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class COpenBracket(CAST, TerminalSymbol, AST):
    pass


class COpenAttribute(CAST, TerminalSymbol, AST):
    pass


class CCloseBracket(CAST, TerminalSymbol, AST):
    pass


class CCloseAttribute(CAST, TerminalSymbol, AST):
    pass


class CXXBitwiseXor(AST):
    pass


class CBitwiseXor(CAST, CXXBitwiseXor, TerminalSymbol, AST):
    pass


class CBitwiseXorAssign(CAST, TerminalSymbol, AST):
    pass


class COpenBrace(CAST, TerminalSymbol, AST):
    pass


class CXXBitwiseOr(AST):
    pass


class CBitwiseOr(CAST, CXXBitwiseOr, TerminalSymbol, AST):
    pass


class CBitwiseOrAssign(CAST, TerminalSymbol, AST):
    pass


class CXXLogicalOr(AST):
    pass


class CLogicalOr(CAST, CXXLogicalOr, TerminalSymbol, AST):
    pass


class CCloseBrace(CAST, TerminalSymbol, AST):
    pass


class CXXBitwiseNot(AST):
    pass


class CBitwiseNot(CAST, CXXBitwiseNot, TerminalSymbol, AST):
    pass


class CPPAST(CXXAST, AST):
    pass


class CPPNewline(CPPAST, TerminalSymbol, AST):
    pass


class CPPLogicalNot(CPPAST, CXXLogicalNot, TerminalSymbol, AST):
    pass


class CPPNotEqual(CPPAST, CXXNotEqual, TerminalSymbol, AST):
    pass


class CPPDoubleQuote(CPPAST, TerminalSymbol, AST):
    pass


class CPPEmptyString(CPPAST, TerminalSymbol, AST):
    pass


class CPPMacroDefine(CPPAST, TerminalSymbol, AST):
    pass


class CPPMacroElif(CPPAST, TerminalSymbol, AST):
    pass


class CPPMacroElse(CPPAST, TerminalSymbol, AST):
    pass


class CPPMacroEndIf(CPPAST, TerminalSymbol, AST):
    pass


class CPPMacroIf(CPPAST, TerminalSymbol, AST):
    pass


class CPPMacroIfDefined(CPPAST, TerminalSymbol, AST):
    pass


class CPPMacroIfNotDefined(CPPAST, TerminalSymbol, AST):
    pass


class CPPMacroInclude(CPPAST, TerminalSymbol, AST):
    pass


class CPPModulo(CPPAST, CXXModulo, TerminalSymbol, AST):
    pass


class CPPModuleAssign(CPPAST, TerminalSymbol, AST):
    pass


class CPPBitwiseAnd(CPPAST, CXXBitwiseAnd, TerminalSymbol, AST):
    pass


class CPPLogicalAnd(CPPAST, CXXLogicalAnd, TerminalSymbol, AST):
    pass


class CPPBitwiseAndAssign(CPPAST, TerminalSymbol, AST):
    pass


class CPPSingleQuote(CPPAST, TerminalSymbol, AST):
    pass


class CPPOpenParenthesis(CPPAST, TerminalSymbol, AST):
    pass


class CPPCallOperator(CPPAST, TerminalSymbol, AST):
    pass


class CPPCloseParenthesis(CPPAST, TerminalSymbol, AST):
    pass


class CPPMultiply(CPPAST, CXXMultiply, TerminalSymbol, AST):
    pass


class CPPMultiplyAssign(CPPAST, TerminalSymbol, AST):
    pass


class CPPAdd(CPPAST, CXXAdd, TerminalSymbol, AST):
    pass


class CPPIncrement(CPPAST, CXXIncrement, TerminalSymbol, AST):
    pass


class CPPAddAssign(CPPAST, TerminalSymbol, AST):
    pass


class CPPComma(CPPAST, TerminalSymbol, AST):
    pass


class CPPSubtract(CPPAST, CXXSubtract, TerminalSymbol, AST):
    pass


class CPPDecrement(CPPAST, CXXDecrement, TerminalSymbol, AST):
    pass


class CPPAttributeSubtract(CPPAST, TerminalSymbol, AST):
    pass


class CPPBased(CPPAST, TerminalSymbol, AST):
    pass


class CPPCdecl(CPPAST, TerminalSymbol, AST):
    pass


class CPPClrcall(CPPAST, TerminalSymbol, AST):
    pass


class CPPDeclspec(CPPAST, TerminalSymbol, AST):
    pass


class CPPFastcall(CPPAST, TerminalSymbol, AST):
    pass


class CPPStdcall(CPPAST, TerminalSymbol, AST):
    pass


class CPPThiscall(CPPAST, TerminalSymbol, AST):
    pass


class CPPUnderscoreUnaligned(CPPAST, TerminalSymbol, AST):
    pass


class CPPVectorcall(CPPAST, TerminalSymbol, AST):
    pass


class CPPSubtractAssign(CPPAST, TerminalSymbol, AST):
    pass


class CPPArrow(CPPAST, TerminalSymbol, AST):
    pass


class CPPPointerToMemberArrow(CPPAST, TerminalSymbol, AST):
    pass


class CPPAbstractDeclarator(CPPAST, AST):
    pass


class CPPAtomic(CPPAST, TerminalSymbol, AST):
    pass


class CPPDeclarator(CPPAST, AST):
    pass


class CPPExpression(CPPAST, AST):
    pass


class CPPFieldDeclarator(CPPAST, AST):
    pass


class CPPStatement(CPPAST, StatementAST, AST):
    pass


class CPPTypeDeclarator(CPPAST, AST):
    pass


class CPPTypeSpecifier(CPPAST, AST):
    pass


class CPPUnaligned(CPPAST, TerminalSymbol, AST):
    pass


class CPPDot(CPPAST, TerminalSymbol, AST):
    pass


class CPPEllipsis(CPPAST, TerminalSymbol, AST):
    pass


class CPPDivide(CPPAST, CXXDivide, TerminalSymbol, AST):
    pass


class CPPDivideAssign(CPPAST, TerminalSymbol, AST):
    pass


class CPPColon(CPPAST, TerminalSymbol, AST):
    pass


class CPPScopeResolution(CPPAST, TerminalSymbol, AST):
    pass


class CPPSemicolon(CPPAST, TerminalSymbol, AST):
    pass


class CPPLessThan(CPPAST, CXXLessThan, TerminalSymbol, AST):
    pass


class CPPBitshiftLeft(CPPAST, CXXBitshiftLeft, TerminalSymbol, AST):
    pass


class CPPBitshiftLeftAssign(CPPAST, TerminalSymbol, AST):
    pass


class CPPLessThanOrEqual(CPPAST, CXXLessThanOrEqual, TerminalSymbol, AST):
    pass


class CPPSpaceship(CPPAST, TerminalSymbol, AST):
    pass


class CPPAssign(CPPAST, TerminalSymbol, AST):
    pass


class CPPEqual(CPPAST, CXXEqual, TerminalSymbol, AST):
    pass


class CPPGreaterThan(CPPAST, CXXGreaterThan, TerminalSymbol, AST):
    pass


class CPPGreaterThanOrEqual(CPPAST, CXXGreaterThanOrEqual, TerminalSymbol, AST):
    pass


class CPPBitshiftRight(CPPAST, CXXBitshiftRight, TerminalSymbol, AST):
    pass


class CPPBitshiftRightAssign(CPPAST, TerminalSymbol, AST):
    pass


class CPPQuestion(CPPAST, TerminalSymbol, AST):
    pass


class CPPAbstractArrayDeclarator(CPPAbstractDeclarator, CXXAbstractArrayDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def size(self) -> AST:
            return self.child_slot("SIZE")


class CPPAbstractFunctionDeclarator(CPPAbstractDeclarator, CXXAbstractFunctionDeclarator, AST):
    pass


class CPPAbstractFunctionDeclarator0(CPPAbstractFunctionDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPAbstractFunctionDeclarator1(CPPAbstractFunctionDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPAbstractFunctionDeclarator2(CPPAbstractFunctionDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPAbstractFunctionDeclarator3(CPPAbstractFunctionDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPAbstractParenthesizedDeclarator(CPPAbstractDeclarator, AST):
    pass


class CPPAbstractPointerDeclarator(CPPAbstractDeclarator, CXXAbstractPointerDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")


class CPPAbstractReferenceDeclarator(CPPAbstractDeclarator, AST):
    pass


class CPPAbstractReferenceDeclarator0(CPPAbstractReferenceDeclarator, AST):
    pass


class CPPAbstractReferenceDeclarator1(CPPAbstractReferenceDeclarator, AST):
    pass


class CPPAccessSpecifier(CPPAST, AST):
        @cached_property
        def keyword(self) -> AST:
            return self.child_slot("KEYWORD")


class CPPAliasDeclaration(CPPAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class CPPArgumentList(CPPAST, CXXArgumentList, AST):
    pass


class CPPArgumentList0(CPPArgumentList, AST):
    pass


class CPPArgumentList1(CPPArgumentList, AST):
    pass


class CPPArrayDeclarator(CPPTypeDeclarator, CPPFieldDeclarator, CPPDeclarator, CXXArrayDeclarator, AST):
    pass


class CPPArrayDeclarator0(CPPArrayDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def size(self) -> AST:
            return self.child_slot("SIZE")


class CPPArrayDeclarator1(CPPArrayDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def size(self) -> AST:
            return self.child_slot("SIZE")


class CPPAssignmentExpression(CPPExpression, CXXAssignmentExpression, AssignmentAST, VariableInitializationAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class CPPAttribute(CPPAST, AST):
    pass


class CPPAttribute0(CPPAttribute, AST):
        @cached_property
        def prefix(self) -> AST:
            return self.child_slot("PREFIX")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPAttribute1(CPPAttribute, AST):
        @cached_property
        def prefix(self) -> AST:
            return self.child_slot("PREFIX")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPAttribute2(CPPAttribute, AST):
        @cached_property
        def prefix(self) -> AST:
            return self.child_slot("PREFIX")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPAttribute3(CPPAttribute, AST):
        @cached_property
        def prefix(self) -> AST:
            return self.child_slot("PREFIX")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPAttributeDeclaration(CPPAST, AST):
    pass


class CPPAttributeSpecifier(CPPAST, AST):
    pass


class CPPAttributedDeclarator(CPPTypeDeclarator, CPPFieldDeclarator, CPPDeclarator, AST):
    pass


class CPPAttributedDeclarator0(CPPAttributedDeclarator, AST):
    pass


class CPPAttributedDeclarator1(CPPAttributedDeclarator, AST):
    pass


class CPPAttributedStatement(CPPAST, AST):
    pass


class CPPAttributedStatement0(CPPAttributedStatement, AST):
    pass


class CPPAttributedStatement1(CPPAttributedStatement, AST):
    pass


class CPPAuto(CPPAST, AST):
    pass


class CPPBaseClassClause(CPPAST, AST):
    pass


class CPPBaseClassClause0(CPPBaseClassClause, AST):
    pass


class CPPBaseClassClause1(CPPBaseClassClause, AST):
    pass


class CPPBaseClassClause2(CPPBaseClassClause, AST):
    pass


class CPPBaseClassClause3(CPPBaseClassClause, AST):
    pass


class CPPBaseClassClause4(CPPBaseClassClause, AST):
    pass


class CPPBaseClassClause5(CPPBaseClassClause, AST):
    pass


class CPPBinaryExpression(CPPExpression, CXXBinaryExpression, BinaryAST, AST):
    pass


class CPPBinaryExpression0(CPPBinaryExpression, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class CPPBinaryExpression1(CPPBinaryExpression, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class CPPBitfieldClause(CPPAST, AST):
    pass


class CPPBreak(CPPAST, TerminalSymbol, AST):
    pass


class CPPBreakStatement(CPPStatement, CXXBreakStatement, AST):
    pass


class CPPCallExpression(CPPExpression, CXXCallExpression, CallAST, AST):
    pass


class CPPCallExpression0(CPPCallExpression, AST):
        @cached_property
        def function(self) -> AST:
            return self.child_slot("FUNCTION")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class CPPCallExpression1(CPPCallExpression, AST):
        @cached_property
        def function(self) -> AST:
            return self.child_slot("FUNCTION")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class CPPCase(CPPAST, TerminalSymbol, AST):
    pass


class CPPCaseStatement(CPPStatement, CXXCaseStatement, AST):
    pass


class CPPCaseStatement0(CPPCaseStatement, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def statements(self) -> List[AST]:
            return self.child_slot("STATEMENTS")


class CPPCaseStatement1(CPPCaseStatement, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def statements(self) -> List[AST]:
            return self.child_slot("STATEMENTS")


class CPPCastExpression(CPPExpression, CXXCastExpression, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPCatch(CPPAST, TerminalSymbol, AST):
    pass


class CatchAST(StatementAST, AST):
    pass


class CPPCatchClause(CPPAST, CatchAST, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CharAST(LiteralAST, AST):
    pass


class CPPCharLiteral(CPPExpression, CXXCharLiteral, CharAST, AST):
    pass


class CPPClass(CPPAST, TerminalSymbol, AST):
    pass


class CPPClassSpecifier(CPPTypeSpecifier, AST):
    pass


class CPPClassSpecifier0(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier1(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier10(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier11(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier12(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier13(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier14(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier15(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier16(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier17(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier18(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier19(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier2(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier20(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier21(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier22(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier23(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier24(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier25(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier26(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier27(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier28(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier29(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier3(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier30(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier31(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier32(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier33(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier34(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier35(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier4(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier5(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier6(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier7(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier8(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPClassSpecifier9(CPPClassSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPCoAwait(CPPAST, TerminalSymbol, AST):
    pass


class CPPCoAwaitExpression(CPPExpression, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class CPPCoReturn(CPPAST, TerminalSymbol, AST):
    pass


class CPPCoReturnStatement(CPPStatement, AST):
    pass


class CPPCoReturnStatement0(CPPCoReturnStatement, AST):
    pass


class CPPCoReturnStatement1(CPPCoReturnStatement, AST):
    pass


class CPPCoYield(CPPAST, TerminalSymbol, AST):
    pass


class CPPCoYieldStatement(CPPStatement, AST):
    pass


class CPPCommaExpression(CPPAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class CPPComment(CPPAST, CXXComment, CommentAST, AST):
    pass


class CPPCompoundLiteralExpression(CPPExpression, AST):
    pass


class CPPCompoundLiteralExpression0(CPPCompoundLiteralExpression, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPCompoundLiteralExpression1(CPPCompoundLiteralExpression, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPCompoundRequirement(CPPAST, AST):
    pass


class CPPCompoundRequirement0(CPPCompoundRequirement, AST):
    pass


class CPPCompoundRequirement1(CPPCompoundRequirement, AST):
    pass


class CPPCompoundRequirement2(CPPCompoundRequirement, AST):
    pass


class CPPCompoundRequirement3(CPPCompoundRequirement, AST):
    pass


class CPPCompoundStatement(CPPStatement, CXXCompoundStatement, CompoundAST, AST):
    pass


class CPPConcatenatedString(CPPExpression, AST):
    pass


class CPPConcept(CPPAST, TerminalSymbol, AST):
    pass


class CPPConceptDefinition(CPPAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CXXConditionClause(AST):
    pass


class CPPConditionClause(CPPAST, CXXConditionClause, AST):
    pass


class CPPConditionClause0(CPPConditionClause, AST):
        @cached_property
        def initializer(self) -> AST:
            return self.child_slot("INITIALIZER")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPConditionClause1(CPPConditionClause, AST):
        @cached_property
        def initializer(self) -> AST:
            return self.child_slot("INITIALIZER")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPConditionalExpression(CPPExpression, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CPPConst(CPPAST, TerminalSymbol, AST):
    pass


class CPPConsteval(CPPAST, TerminalSymbol, AST):
    pass


class CPPConstexpr(CPPAST, TerminalSymbol, AST):
    pass


class CPPConstinit(CPPAST, TerminalSymbol, AST):
    pass


class CPPContinue(CPPAST, TerminalSymbol, AST):
    pass


class CPPContinueStatement(CPPStatement, CXXContinueStatement, AST):
    pass


class CPPDeclaration(CPPAST, CXXDeclaration, VariableDeclarationAST, StatementAST, AST):
    pass


class CPPDeclaration0(CPPDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPDeclaration1(CPPDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPDeclarationList(CPPAST, AST):
    pass


class CPPDecltype(CPPTypeSpecifier, AST):
    pass


class CPPDecltypeTerminal(CPPTypeSpecifier, TerminalSymbol, AST):
    pass


class CPPDefault(CPPAST, TerminalSymbol, AST):
    pass


class CPPDefaultMethodClause(CPPAST, AST):
    pass


class CPPDefined(CPPAST, TerminalSymbol, AST):
    pass


class CPPDelete(CPPAST, TerminalSymbol, AST):
    pass


class CPPDeleteExpression(CPPExpression, AST):
    pass


class CPPDeleteExpression0(CPPDeleteExpression, AST):
    pass


class CPPDeleteExpression1(CPPDeleteExpression, AST):
    pass


class CPPDeleteMethodClause(CPPAST, AST):
    pass


class CPPDependentName(CPPAST, AST):
    pass


class CPPDependentName0(CPPDependentName, AST):
    pass


class CPPDependentName1(CPPDependentName, AST):
    pass


class CPPDependentType(CPPTypeSpecifier, AST):
    pass


class CPPDestructorName(CPPDeclarator, AST):
    pass


class CPPDo(CPPAST, TerminalSymbol, AST):
    pass


class CPPDoStatement(CPPStatement, CXXDoStatement, LoopAST, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")


class CPPElse(CPPAST, TerminalSymbol, AST):
    pass


class CPPEnum(CPPAST, TerminalSymbol, AST):
    pass


class CPPEnumSpecifier(CPPTypeSpecifier, CXXEnumSpecifier, TypeDeclarationAST, DefinitionAST, AST):
    pass


class CPPEnumSpecifier0(CPPEnumSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def base(self) -> AST:
            return self.child_slot("BASE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPEnumSpecifier1(CPPEnumSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def base(self) -> AST:
            return self.child_slot("BASE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPEnumSpecifier2(CPPEnumSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def base(self) -> AST:
            return self.child_slot("BASE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPEnumSpecifier3(CPPEnumSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def base(self) -> AST:
            return self.child_slot("BASE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPEnumSpecifier4(CPPEnumSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def base(self) -> AST:
            return self.child_slot("BASE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPEnumSpecifier5(CPPEnumSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def base(self) -> AST:
            return self.child_slot("BASE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPEnumSpecifier6(CPPEnumSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def base(self) -> AST:
            return self.child_slot("BASE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPEnumSpecifier7(CPPEnumSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def base(self) -> AST:
            return self.child_slot("BASE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPEnumSpecifier8(CPPEnumSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def base(self) -> AST:
            return self.child_slot("BASE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPEnumSpecifier9(CPPEnumSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def base(self) -> AST:
            return self.child_slot("BASE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPEnumerator(CPPAST, CXXEnumerator, AST):
    pass


class CPPEnumerator0(CPPEnumerator, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPEnumerator1(CPPEnumerator, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPEnumeratorList(CPPAST, CXXEnumeratorList, AST):
    pass


class CPPEnumeratorList0(CPPEnumeratorList, AST):
    pass


class CPPEnumeratorList1(CPPEnumeratorList, AST):
    pass


class CPPEnumeratorList2(CPPEnumeratorList, AST):
    pass


class CPPEnumeratorList3(CPPEnumeratorList, AST):
    pass


class CPPError(CPPAST, CXXError, ParseErrorAST, AST):
    pass


class CPPEscapeSequence(CPPAST, AST):
    pass


class CPPExplicit(CPPAST, TerminalSymbol, AST):
    pass


class CPPExplicitFunctionSpecifier(CPPAST, AST):
    pass


class CPPExplicitFunctionSpecifier0(CPPExplicitFunctionSpecifier, AST):
    pass


class CPPExplicitFunctionSpecifier1(CPPExplicitFunctionSpecifier, AST):
    pass


class CPPExpressionStatement(CPPStatement, CXXExpressionStatement, ExpressionStatementAST, AST):
    pass


class CPPExpressionStatement0(CPPExpressionStatement, AST):
    pass


class CPPExpressionStatement1(CPPExpressionStatement, AST):
    pass


class CPPExtern(CPPAST, TerminalSymbol, AST):
    pass


class CPPFalse(CPPExpression, BooleanFalseAST, AST):
    pass


class CPPFieldDeclaration(CPPAST, CXXFieldDeclaration, DeclarationAST, DefinitionAST, AST):
    pass


class CPPFieldDeclaration0(CPPFieldDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def default_value(self) -> AST:
            return self.child_slot("DEFAULT-VALUE")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPFieldDeclaration1(CPPFieldDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def default_value(self) -> AST:
            return self.child_slot("DEFAULT-VALUE")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPFieldDeclaration2(CPPFieldDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def default_value(self) -> AST:
            return self.child_slot("DEFAULT-VALUE")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPFieldDeclaration3(CPPFieldDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def default_value(self) -> AST:
            return self.child_slot("DEFAULT-VALUE")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPFieldDeclaration4(CPPFieldDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def default_value(self) -> AST:
            return self.child_slot("DEFAULT-VALUE")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPFieldDeclaration5(CPPFieldDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def default_value(self) -> AST:
            return self.child_slot("DEFAULT-VALUE")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPFieldDeclaration6(CPPFieldDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def default_value(self) -> AST:
            return self.child_slot("DEFAULT-VALUE")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPFieldDeclaration7(CPPFieldDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")

        @cached_property
        def default_value(self) -> AST:
            return self.child_slot("DEFAULT-VALUE")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPFieldDeclarationList(CPPAST, AST):
    pass


class CPPFieldDesignator(CPPAST, AST):
    pass


class CPPFieldExpression(CPPExpression, CXXFieldExpression, FieldAST, AST):
        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def field(self) -> AST:
            return self.child_slot("FIELD")


class CPPFieldIdentifier(CPPFieldDeclarator, CXXFieldIdentifier, IdentifierAST, AST):
    pass


class CPPFieldInitializer(CPPAST, AST):
    pass


class CPPFieldInitializer0(CPPFieldInitializer, AST):
    pass


class CPPFieldInitializer1(CPPFieldInitializer, AST):
    pass


class CPPFieldInitializer2(CPPFieldInitializer, AST):
    pass


class CPPFieldInitializerList(CPPAST, AST):
    pass


class CPPFinal(CPPAST, TerminalSymbol, AST):
    pass


class CPPFor(CPPAST, TerminalSymbol, AST):
    pass


class CPPForRangeLoop(CPPStatement, LoopAST, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPForStatement(CPPStatement, CXXForStatement, LoopAST, AST):
    pass


class CPPForStatement0(CPPForStatement, AST):
        @cached_property
        def initializer(self) -> AST:
            return self.child_slot("INITIALIZER")

        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def update(self) -> AST:
            return self.child_slot("UPDATE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPForStatement1(CPPForStatement, AST):
        @cached_property
        def initializer(self) -> AST:
            return self.child_slot("INITIALIZER")

        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def update(self) -> AST:
            return self.child_slot("UPDATE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPFriend(CPPAST, TerminalSymbol, AST):
    pass


class CPPFriendDeclaration(CPPAST, AST):
    pass


class CPPFriendDeclaration0(CPPFriendDeclaration, AST):
    pass


class CPPFriendDeclaration1(CPPFriendDeclaration, AST):
    pass


class CPPFriendDeclaration2(CPPFriendDeclaration, AST):
    pass


class CPPFriendDeclaration3(CPPFriendDeclaration, AST):
    pass


class CPPFriendDeclaration4(CPPFriendDeclaration, AST):
    pass


class CPPFriendDeclaration5(CPPFriendDeclaration, AST):
    pass


class CPPFriendDeclaration6(CPPFriendDeclaration, AST):
    pass


class CPPFunctionDeclarator(CPPTypeDeclarator, CPPFieldDeclarator, CPPDeclarator, CXXFunctionDeclarator, AST):
    pass


class CPPFunctionDeclarator0(CPPFunctionDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPFunctionDeclarator1(CPPFunctionDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPFunctionDefinition(CPPAST, CXXFunctionDefinition, FunctionDeclarationAST, StatementAST, AST):
    pass


class CPPFunctionDefinition0(CPPFunctionDefinition, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPFunctionDefinition1(CPPFunctionDefinition, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPGoto(CPPAST, TerminalSymbol, AST):
    pass


class CPPGotoStatement(CPPStatement, GotoAST, AST):
        @cached_property
        def label(self) -> AST:
            return self.child_slot("LABEL")


class CPPIdentifier(CPPDeclarator, CPPExpression, CXXIdentifier, IdentifierAST, AST):
    pass


class CPPIf(CPPAST, TerminalSymbol, AST):
    pass


class CPPIfStatement(CPPStatement, CXXIfStatement, AST):
    pass


class CPPIfStatement0(CPPIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CPPIfStatement1(CPPIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CPPIfStatement2(CPPIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CPPIfStatement3(CPPIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CPPInitDeclarator(CPPAST, CXXInitDeclarator, VariableInitializationAST, AST):
    pass


class CPPInitDeclarator0(CPPInitDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPInitDeclarator1(CPPInitDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPInitializerList(CPPAST, AST):
    pass


class CPPInitializerList0(CPPInitializerList, AST):
    pass


class CPPInitializerList1(CPPInitializerList, AST):
    pass


class CPPInitializerList2(CPPInitializerList, AST):
    pass


class CPPInitializerList3(CPPInitializerList, AST):
    pass


class CPPInitializerPair(CPPAST, CXXInitializerPair, AST):
        @cached_property
        def designator(self) -> List[AST]:
            return self.child_slot("DESIGNATOR")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPInline(CPPAST, TerminalSymbol, AST):
    pass


class CPPInnerWhitespace(CPPAST, InnerWhitespace, AST):
    pass


class CPPWcharDoubleQuote(CPPAST, TerminalSymbol, AST):
    pass


class CPPWcharSingleQuote(CPPAST, TerminalSymbol, AST):
    pass


class CPPLabeledStatement(CPPStatement, AST):
        @cached_property
        def label(self) -> AST:
            return self.child_slot("LABEL")

        @cached_property
        def statement(self) -> AST:
            return self.child_slot("STATEMENT")


class CPPLambdaCaptureSpecifier(CPPAST, AST):
    pass


class CPPLambdaCaptureSpecifier0(CPPLambdaCaptureSpecifier, AST):
    pass


class CPPLambdaCaptureSpecifier1(CPPLambdaCaptureSpecifier, AST):
    pass


class CPPLambdaCaptureSpecifier2(CPPLambdaCaptureSpecifier, AST):
    pass


class CPPLambdaCaptureSpecifier3(CPPLambdaCaptureSpecifier, AST):
    pass


class CPPLambdaDefaultCapture(CPPAST, AST):
    pass


class CPPLambdaExpression(CPPExpression, AST):
    pass


class CPPLambdaExpression0(CPPLambdaExpression, AST):
        @cached_property
        def captures(self) -> AST:
            return self.child_slot("CAPTURES")

        @cached_property
        def template_parameters(self) -> AST:
            return self.child_slot("TEMPLATE-PARAMETERS")

        @cached_property
        def constraint(self) -> AST:
            return self.child_slot("CONSTRAINT")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPLambdaExpression1(CPPLambdaExpression, AST):
        @cached_property
        def captures(self) -> AST:
            return self.child_slot("CAPTURES")

        @cached_property
        def template_parameters(self) -> AST:
            return self.child_slot("TEMPLATE-PARAMETERS")

        @cached_property
        def constraint(self) -> AST:
            return self.child_slot("CONSTRAINT")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPLambdaExpression2(CPPLambdaExpression, AST):
        @cached_property
        def captures(self) -> AST:
            return self.child_slot("CAPTURES")

        @cached_property
        def template_parameters(self) -> AST:
            return self.child_slot("TEMPLATE-PARAMETERS")

        @cached_property
        def constraint(self) -> AST:
            return self.child_slot("CONSTRAINT")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPLambdaExpression3(CPPLambdaExpression, AST):
        @cached_property
        def captures(self) -> AST:
            return self.child_slot("CAPTURES")

        @cached_property
        def template_parameters(self) -> AST:
            return self.child_slot("TEMPLATE-PARAMETERS")

        @cached_property
        def constraint(self) -> AST:
            return self.child_slot("CONSTRAINT")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPLambdaExpression4(CPPLambdaExpression, AST):
        @cached_property
        def captures(self) -> AST:
            return self.child_slot("CAPTURES")

        @cached_property
        def template_parameters(self) -> AST:
            return self.child_slot("TEMPLATE-PARAMETERS")

        @cached_property
        def constraint(self) -> AST:
            return self.child_slot("CONSTRAINT")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPLambdaExpression5(CPPLambdaExpression, AST):
        @cached_property
        def captures(self) -> AST:
            return self.child_slot("CAPTURES")

        @cached_property
        def template_parameters(self) -> AST:
            return self.child_slot("TEMPLATE-PARAMETERS")

        @cached_property
        def constraint(self) -> AST:
            return self.child_slot("CONSTRAINT")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPLinkageSpecification(CPPAST, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPLiteralSuffix(CPPAST, AST):
    pass


class CPPLong(CPPAST, TerminalSymbol, AST):
    pass


class CPPMsBasedModifier(CPPAST, AST):
    pass


class CPPMsCallModifier(CPPAST, AST):
    pass


class CPPMsDeclspecModifier(CPPAST, AST):
    pass


class CPPMsPointerModifier(CPPAST, AST):
    pass


class CPPMsRestrictModifier(CPPAST, AST):
    pass


class CPPMsSignedPtrModifier(CPPAST, AST):
    pass


class CPPMsUnalignedPtrModifier(CPPAST, AST):
    pass


class CPPMsUnsignedPtrModifier(CPPAST, AST):
    pass


class CPPMutable(CPPAST, TerminalSymbol, AST):
    pass


class CPPNamespace(CPPAST, TerminalSymbol, AST):
    pass


class CPPNamespaceAliasDefinition(CPPAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPNamespaceDefinition(CPPAST, DefinitionAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPNamespaceDefinitionName(CPPAST, AST):
    pass


class CPPNamespaceDefinitionName0(CPPNamespaceDefinitionName, AST):
    pass


class CPPNamespaceDefinitionName1(CPPNamespaceDefinitionName, AST):
    pass


class CPPNamespaceIdentifier(CPPAST, IdentifierAST, AST):
    pass


class CPPNew(CPPAST, TerminalSymbol, AST):
    pass


class CPPNewDeclarator(CPPAST, AST):
    pass


class CPPNewDeclarator0(CPPNewDeclarator, AST):
        @cached_property
        def length(self) -> AST:
            return self.child_slot("LENGTH")


class CPPNewDeclarator1(CPPNewDeclarator, AST):
        @cached_property
        def length(self) -> AST:
            return self.child_slot("LENGTH")


class CPPNewExpression(CPPExpression, AST):
        @cached_property
        def placement(self) -> AST:
            return self.child_slot("PLACEMENT")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class CPPNoexcept(CPPAST, AST):
    pass


class CPPNoexcept0(CPPNoexcept, AST):
    pass


class CPPNoexcept1(CPPNoexcept, AST):
    pass


class CPPNoexcept2(CPPNoexcept, AST):
    pass


class CPPNoexceptTerminal(CPPAST, TerminalSymbol, AST):
    pass


class CPPNull(CPPExpression, AST):
    pass


class CPPNullptr(CPPExpression, AST):
    pass


class CPPNumberLiteral(CPPExpression, CXXNumberLiteral, NumberAST, AST):
    pass


class CPPOperator(CPPAST, TerminalSymbol, AST):
    pass


class CPPOperatorCast(CPPAST, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPOperatorName(CPPFieldDeclarator, CPPDeclarator, AST):
    pass


class CPPOperatorName0(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName1(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName10(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName11(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName12(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName13(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName14(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName15(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName16(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName17(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName18(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName19(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName2(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName20(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName21(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName22(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName23(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName24(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName25(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName26(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName27(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName28(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName29(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName3(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName30(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName31(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName32(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName33(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName34(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName35(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName36(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName37(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName38(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName39(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName4(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName40(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName41(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName42(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName43(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName5(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName6(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName7(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName8(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOperatorName9(CPPOperatorName, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPOptionalParameterDeclaration(CPPAST, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def default_value(self) -> AST:
            return self.child_slot("DEFAULT-VALUE")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPOptionalTypeParameterDeclaration(CPPAST, AST):
    pass


class CPPOptionalTypeParameterDeclaration0(CPPOptionalTypeParameterDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def default_type(self) -> AST:
            return self.child_slot("DEFAULT-TYPE")


class CPPOptionalTypeParameterDeclaration1(CPPOptionalTypeParameterDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def default_type(self) -> AST:
            return self.child_slot("DEFAULT-TYPE")


class CPPOverride(CPPAST, TerminalSymbol, AST):
    pass


class CPPParameterDeclaration(CPPAST, CXXParameterDeclaration, ParameterAST, VariableDeclarationAST, AST):
    pass


class CPPParameterDeclaration0(CPPParameterDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPParameterDeclaration1(CPPParameterDeclaration, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPParameterList(CPPAST, AST):
    pass


class CPPParameterList0(CPPParameterList, AST):
    pass


class CPPParameterList1(CPPParameterList, AST):
    pass


class CPPParameterList2(CPPParameterList, AST):
    pass


class CPPParameterPackExpansion(CPPExpression, AST):
    pass


class CPPParameterPackExpansion0(CPPParameterPackExpansion, AST):
        @cached_property
        def pattern(self) -> AST:
            return self.child_slot("PATTERN")


class CPPParameterPackExpansion1(CPPParameterPackExpansion, AST):
        @cached_property
        def pattern(self) -> AST:
            return self.child_slot("PATTERN")


class CPPParenthesizedDeclarator(CPPTypeDeclarator, CPPFieldDeclarator, CPPDeclarator, CXXParenthesizedDeclarator, AST):
    pass


class CPPParenthesizedDeclarator0(CPPParenthesizedDeclarator, AST):
    pass


class CPPParenthesizedDeclarator1(CPPParenthesizedDeclarator, AST):
    pass


class CPPParenthesizedExpression(CPPExpression, CXXParenthesizedExpression, ParenthesizedExpressionAST, AST):
    pass


class CPPParenthesizedExpression0(CPPParenthesizedExpression, AST):
    pass


class CPPParenthesizedExpression1(CPPParenthesizedExpression, AST):
    pass


class CPPPlaceholderTypeSpecifier(CPPTypeSpecifier, AST):
    pass


class CPPPlaceholderTypeSpecifier0(CPPPlaceholderTypeSpecifier, AST):
        @cached_property
        def constraint(self) -> AST:
            return self.child_slot("CONSTRAINT")


class CPPPlaceholderTypeSpecifier1(CPPPlaceholderTypeSpecifier, AST):
        @cached_property
        def constraint(self) -> AST:
            return self.child_slot("CONSTRAINT")


class CPPPointerDeclarator(CPPTypeDeclarator, CPPFieldDeclarator, CPPDeclarator, CXXPointerDeclarator, AST):
    pass


class CPPPointerDeclarator0(CPPPointerDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")


class CPPPointerDeclarator1(CPPPointerDeclarator, AST):
        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")


class CPPPointerExpression(CPPExpression, CXXPointerExpression, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class CPPPreprocArg(CPPAST, CXXPreprocArg, AST):
    pass


class CPPPreprocCall(CPPAST, AST):
        @cached_property
        def directive(self) -> AST:
            return self.child_slot("DIRECTIVE")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class CPPPreprocDef(CPPAST, CXXPreprocDef, DefinitionAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPPreprocDefined(CPPAST, AST):
    pass


class CPPPreprocDefined0(CPPPreprocDefined, AST):
    pass


class CPPPreprocDefined1(CPPPreprocDefined, AST):
    pass


class CPPPreprocDirective(CPPAST, AST):
    pass


class CPPPreprocElif(CPPAST, CXXPreprocElif, AST):
    pass


class CPPPreprocElif0(CPPPreprocElif, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CPPPreprocElif1(CPPPreprocElif, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CPPPreprocElse(CPPAST, CXXPreprocElse, AST):
    pass


class CPPPreprocElse0(CPPPreprocElse, AST):
    pass


class CPPPreprocElse1(CPPPreprocElse, AST):
    pass


class CPPPreprocFunctionDef(CPPAST, CXXPreprocFunctionDef, DefinitionAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPPreprocIf(CPPAST, AST):
    pass


class CPPPreprocIf0(CPPPreprocIf, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CPPPreprocIf1(CPPPreprocIf, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class CPPPreprocIfdef(CPPAST, AST):
    pass


class CPPPreprocIfdef0(CPPPreprocIfdef, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")

        @cached_property
        def operator(self) -> List[AST]:
            return self.child_slot("OPERATOR")


class CPPPreprocIfdef1(CPPPreprocIfdef, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")

        @cached_property
        def operator(self) -> List[AST]:
            return self.child_slot("OPERATOR")


class CPPPreprocInclude(CPPAST, CXXPreprocInclude, AST):
        @cached_property
        def path(self) -> AST:
            return self.child_slot("PATH")


class CPPPreprocParams(CPPAST, CXXPreprocParams, AST):
    pass


class CPPPrimitiveType(CPPTypeSpecifier, CXXPrimitiveType, IdentifierAST, AST):
    pass


class CPPPrivate(CPPAST, TerminalSymbol, AST):
    pass


class CPPProtected(CPPAST, TerminalSymbol, AST):
    pass


class CPPPublic(CPPAST, TerminalSymbol, AST):
    pass


class CPPQualifiedIdentifier(CPPDeclarator, CPPTypeSpecifier, CPPExpression, IdentifierAST, AST):
    pass


class CPPQualifiedIdentifier0(CPPQualifiedIdentifier, AST):
        @cached_property
        def scope(self) -> AST:
            return self.child_slot("SCOPE")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPQualifiedIdentifier1(CPPQualifiedIdentifier, AST):
        @cached_property
        def scope(self) -> AST:
            return self.child_slot("SCOPE")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class CPPRawStringLiteral(CPPExpression, StringAST, AST):
    pass


class CPPRefQualifier(CPPAST, AST):
    pass


class CPPReferenceDeclarator(CPPFieldDeclarator, CPPDeclarator, AST):
    pass


class CPPReferenceDeclarator0(CPPReferenceDeclarator, AST):
        @cached_property
        def valueness(self) -> AST:
            return self.child_slot("VALUENESS")


class CPPReferenceDeclarator1(CPPReferenceDeclarator, AST):
        @cached_property
        def valueness(self) -> AST:
            return self.child_slot("VALUENESS")


class CPPRegister(CPPAST, TerminalSymbol, AST):
    pass


class CPPRequirementSeq(CPPAST, AST):
    pass


class CPPRequires(CPPAST, TerminalSymbol, AST):
    pass


class CPPRequiresClause(CPPExpression, AST):
        @cached_property
        def constraint(self) -> AST:
            return self.child_slot("CONSTRAINT")


class CPPRequiresExpression(CPPExpression, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def requirements(self) -> AST:
            return self.child_slot("REQUIREMENTS")


class CPPRestrict(CPPAST, TerminalSymbol, AST):
    pass


class CPPReturn(CPPAST, TerminalSymbol, AST):
    pass


class CPPReturnStatement(CPPStatement, CXXReturnStatement, ReturnAST, AST):
    pass


class CPPReturnStatement0(CPPReturnStatement, AST):
    pass


class CPPReturnStatement1(CPPReturnStatement, AST):
    pass


class CPPReturnStatement2(CPPReturnStatement, AST):
    pass


class CPPShort(CPPAST, TerminalSymbol, AST):
    pass


class CPPSigned(CPPAST, CXXSigned, TerminalSymbol, AST):
    pass


class CPPSimpleRequirement(CPPAST, AST):
    pass


class CPPSizedTypeSpecifier(CPPTypeSpecifier, CXXSizedTypeSpecifier, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def modifiers(self) -> List[AST]:
            return self.child_slot("MODIFIERS")


class CPPSizeof(CPPAST, TerminalSymbol, AST):
    pass


class CPPSizeofExpression(CPPExpression, CXXSizeofExpression, AST):
    pass


class CPPSizeofExpression0(CPPSizeofExpression, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPSizeofExpression1(CPPSizeofExpression, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class CPPSourceTextFragment(CPPAST, SourceTextFragment, AST):
    pass


class CPPStatementIdentifier(CPPAST, AST):
    pass


class CPPStatic(CPPAST, TerminalSymbol, AST):
    pass


class CPPStaticAssert(CPPAST, TerminalSymbol, AST):
    pass


class CPPStaticAssertDeclaration(CPPAST, AST):
    pass


class CPPStaticAssertDeclaration0(CPPStaticAssertDeclaration, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def message(self) -> AST:
            return self.child_slot("MESSAGE")


class CPPStaticAssertDeclaration1(CPPStaticAssertDeclaration, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def message(self) -> AST:
            return self.child_slot("MESSAGE")


class CPPStorageClassSpecifier(CPPAST, CXXStorageClassSpecifier, AST):
    pass


class CPPStringLiteral(CPPExpression, CXXStringLiteral, StringAST, AST):
    pass


class CPPStruct(CPPAST, TerminalSymbol, AST):
    pass


class CPPStructSpecifier(CPPTypeSpecifier, CXXStructSpecifier, TypeDeclarationAST, DefinitionAST, AST):
    pass


class CPPStructSpecifier0(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier1(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier10(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier11(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier12(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier13(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier14(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier15(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier16(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier17(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier18(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier19(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier2(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier20(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier21(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier22(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier23(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier24(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier25(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier26(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier27(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier28(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier29(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier3(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier30(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier31(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier32(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier33(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier34(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier35(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier4(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier5(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier6(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier7(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier8(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructSpecifier9(CPPStructSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPStructuredBindingDeclarator(CPPDeclarator, AST):
    pass


class CPPSubscriptDesignator(CPPAST, AST):
    pass


class CPPSubscriptExpression(CPPExpression, CXXSubscriptExpression, SubscriptAST, AST):
        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")

        @cached_property
        def index(self) -> AST:
            return self.child_slot("INDEX")


class CPPSwitch(CPPAST, TerminalSymbol, AST):
    pass


class CPPSwitchStatement(CPPStatement, CXXSwitchStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPSystemLibString(CPPAST, AST):
    pass


class CPPTemplate(CPPAST, TerminalSymbol, AST):
    pass


class CPPTemplateArgumentList(CPPAST, AST):
    pass


class CPPTemplateArgumentList0(CPPTemplateArgumentList, AST):
    pass


class CPPTemplateArgumentList1(CPPTemplateArgumentList, AST):
    pass


class CPPTemplateArgumentList2(CPPTemplateArgumentList, AST):
    pass


class CPPTemplateDeclaration(CPPAST, AST):
    pass


class CPPTemplateDeclaration0(CPPTemplateDeclaration, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPTemplateDeclaration1(CPPTemplateDeclaration, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPTemplateDeclaration2(CPPTemplateDeclaration, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPTemplateDeclaration3(CPPTemplateDeclaration, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPTemplateDeclaration4(CPPTemplateDeclaration, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPTemplateDeclaration5(CPPTemplateDeclaration, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPTemplateDeclaration6(CPPTemplateDeclaration, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPTemplateDeclaration7(CPPTemplateDeclaration, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPTemplateFunction(CPPDeclarator, CPPExpression, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class CPPTemplateInstantiation(CPPAST, AST):
    pass


class CPPTemplateInstantiation0(CPPTemplateInstantiation, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPTemplateInstantiation1(CPPTemplateInstantiation, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPTemplateMethod(CPPFieldDeclarator, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class CPPTemplateParameterList(CPPAST, AST):
    pass


class CPPTemplateParameterList0(CPPTemplateParameterList, AST):
    pass


class CPPTemplateParameterList1(CPPTemplateParameterList, AST):
    pass


class CPPTemplateTemplateParameterDeclaration(CPPAST, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")


class CPPTemplateType(CPPTypeSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class CPPThis(CPPExpression, AST):
    pass


class CPPThreadLocal(CPPAST, TerminalSymbol, AST):
    pass


class CPPThrow(CPPAST, TerminalSymbol, AST):
    pass


class CPPThrowSpecifier(CPPAST, AST):
    pass


class CPPThrowSpecifier0(CPPThrowSpecifier, AST):
    pass


class CPPThrowSpecifier1(CPPThrowSpecifier, AST):
    pass


class CPPThrowStatement(CPPStatement, AST):
    pass


class CPPThrowStatement0(CPPThrowStatement, AST):
    pass


class CPPThrowStatement1(CPPThrowStatement, AST):
    pass


class CPPTrailingReturnType(CPPAST, AST):
    pass


class CPPTrailingReturnType0(CPPTrailingReturnType, AST):
    pass


class CPPTrailingReturnType1(CPPTrailingReturnType, AST):
    pass


class CPPTrailingReturnType2(CPPTrailingReturnType, AST):
    pass


class CPPTrailingReturnType3(CPPTrailingReturnType, AST):
    pass


class CPPTranslationUnit(CPPAST, RootAST, AST):
    pass


class CPPTrue(CPPExpression, BooleanTrueAST, AST):
    pass


class CPPTry(CPPAST, TerminalSymbol, AST):
    pass


class CPPTryStatement(CPPStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPTypeDefinition(CPPAST, CXXTypeDefinition, TypeDeclarationAST, DefinitionAST, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> List[AST]:
            return self.child_slot("DECLARATOR")


class CPPTypeDescriptor(CPPAST, CXXTypeDescriptor, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_type_qualifiers(self) -> List[AST]:
            return self.child_slot("PRE-TYPE-QUALIFIERS")

        @cached_property
        def post_type_qualifiers(self) -> List[AST]:
            return self.child_slot("POST-TYPE-QUALIFIERS")


class TypeIdentifierAST(IdentifierAST, AST):
    pass


class CPPTypeIdentifier(CPPTypeDeclarator, CPPTypeSpecifier, CXXTypeIdentifier, TypeIdentifierAST, IdentifierAST, AST):
    pass


class CPPTypeParameterDeclaration(CPPAST, AST):
    pass


class CPPTypeParameterDeclaration0(CPPTypeParameterDeclaration, AST):
        @cached_property
        def keyword(self) -> AST:
            return self.child_slot("KEYWORD")


class CPPTypeParameterDeclaration1(CPPTypeParameterDeclaration, AST):
        @cached_property
        def keyword(self) -> AST:
            return self.child_slot("KEYWORD")


class CPPTypeQualifier(CPPAST, CXXTypeQualifier, AST):
    pass


class CPPTypeRequirement(CPPAST, AST):
    pass


class CPPTypeRequirement0(CPPTypeRequirement, AST):
    pass


class CPPTypeRequirement1(CPPTypeRequirement, AST):
    pass


class CPPTypeRequirement2(CPPTypeRequirement, AST):
    pass


class CPPTypedef(CPPAST, TerminalSymbol, AST):
    pass


class CPPTypename(CPPAST, TerminalSymbol, AST):
    pass


class CPPUnicodeDoubleQuote(CPPAST, TerminalSymbol, AST):
    pass


class CPPUnsignedTerminalDoubleQuote(CPPAST, TerminalSymbol, AST):
    pass


class CPPUnicodeSingleQuote(CPPAST, TerminalSymbol, AST):
    pass


class CPPUnsignedTerminalSingleQuote(CPPAST, TerminalSymbol, AST):
    pass


class CPPUnsigned8bitTerminalDoubleQuote(CPPAST, TerminalSymbol, AST):
    pass


class CPPUnsigned8bitTerminalSingleQuote(CPPAST, TerminalSymbol, AST):
    pass


class CPPUnaryExpression(CPPExpression, CXXUnaryExpression, UnaryAST, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class CPPUnion(CPPAST, TerminalSymbol, AST):
    pass


class CPPUnionSpecifier(CPPTypeSpecifier, CXXUnionSpecifier, TypeDeclarationAST, DefinitionAST, AST):
    pass


class CPPUnionSpecifier0(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier1(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier10(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier11(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier12(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier13(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier14(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier15(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier16(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier17(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier18(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier19(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier2(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier20(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier21(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier22(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier23(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier24(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier25(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier26(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier27(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier28(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier29(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier3(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier30(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier31(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier32(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier33(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier34(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier35(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier4(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier5(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier6(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier7(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier8(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnionSpecifier9(CPPUnionSpecifier, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPUnsigned(CPPAST, TerminalSymbol, AST):
    pass


class CPPUpdateExpression(CPPExpression, CXXUpdateExpression, AssignmentAST, AST):
    pass


class CPPUpdateExpression0(CPPUpdateExpression, AST):
        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class CPPUpdateExpression1(CPPUpdateExpression, AST):
        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class CPPUserDefinedLiteral(CPPExpression, AST):
    pass


class CPPUsing(CPPAST, TerminalSymbol, AST):
    pass


class CPPUsingDeclaration(CPPAST, AST):
    pass


class CPPUsingDeclaration0(CPPUsingDeclaration, AST):
    pass


class CPPUsingDeclaration1(CPPUsingDeclaration, AST):
    pass


class CPPVariadicDeclaration(CPPParameterDeclaration, CPPIdentifier, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPVariadicDeclarator(CPPAST, AST):
    pass


class CPPVariadicDeclarator0(CPPVariadicDeclarator, AST):
    pass


class CPPVariadicDeclarator1(CPPVariadicDeclarator, AST):
    pass


class CPPVariadicParameterDeclaration(CPPAST, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def declarator(self) -> AST:
            return self.child_slot("DECLARATOR")

        @cached_property
        def pre_specifiers(self) -> List[AST]:
            return self.child_slot("PRE-SPECIFIERS")

        @cached_property
        def post_specifiers(self) -> List[AST]:
            return self.child_slot("POST-SPECIFIERS")


class CPPVariadicTypeParameterDeclaration(CPPAST, AST):
    pass


class CPPVariadicTypeParameterDeclaration0(CPPVariadicTypeParameterDeclaration, AST):
    pass


class CPPVariadicTypeParameterDeclaration1(CPPVariadicTypeParameterDeclaration, AST):
    pass


class CPPVirtual(CPPAST, TerminalSymbol, AST):
    pass


class CPPVirtualFunctionSpecifier(CPPAST, AST):
    pass


class CPPVirtualSpecifier(CPPAST, AST):
    pass


class CPPVolatile(CPPAST, TerminalSymbol, AST):
    pass


class CPPWhile(CPPAST, TerminalSymbol, AST):
    pass


class CPPWhileStatement(CPPStatement, CXXWhileStatement, LoopAST, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class CPPOpenBracket(CPPAST, TerminalSymbol, AST):
    pass


class CPPOpenAttribute(CPPAST, TerminalSymbol, AST):
    pass


class CPPEmptyCaptureClause(CPPAST, TerminalSymbol, AST):
    pass


class CPPCloseBracket(CPPAST, TerminalSymbol, AST):
    pass


class CPPCloseAttribute(CPPAST, TerminalSymbol, AST):
    pass


class CPPBitwiseXor(CPPAST, CXXBitwiseXor, TerminalSymbol, AST):
    pass


class CPPBitwiseXorAssign(CPPAST, TerminalSymbol, AST):
    pass


class CPPOpenBrace(CPPAST, TerminalSymbol, AST):
    pass


class CPPBitwiseOr(CPPAST, CXXBitwiseOr, TerminalSymbol, AST):
    pass


class CPPBitwiseOrAssign(CPPAST, TerminalSymbol, AST):
    pass


class CPPLogicalOr(CPPAST, CXXLogicalOr, TerminalSymbol, AST):
    pass


class CPPCloseBrace(CPPAST, TerminalSymbol, AST):
    pass


class CPPBitwiseNot(CPPAST, CXXBitwiseNot, TerminalSymbol, AST):
    pass


class InnerParent(AST):
    pass


class ECMAAST(AST):
    pass


class JavascriptAST(ECMAAST, AST):
    pass


class JavascriptLogicalNot(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptNotEqual(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptStrictlyNotEqual(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptDoubleQuote(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptOpenTemplateLiteral(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptModulo(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptModuleAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptBitwiseAnd(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptLogicalAnd(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptLogicalAndAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptBitwiseAndAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptSingleQuote(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptOpenParenthesis(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptCloseParenthesis(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptMultiply(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptPow(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptPowAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptMultiplyAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptAdd(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptIncrement(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptAddAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptComma(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptSubtract(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptDecrement(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptSubtractAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptAutomaticSemicolon(JavascriptAST, AST):
    pass


class JavascriptTemplateChars(JavascriptAST, AST):
    pass


class JavascriptTernaryQmark(JavascriptAST, AST):
    pass


class JavascriptDot(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptEllipsis(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptDivide(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptDivideAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptColon(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptSemicolon(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptLessThan(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptBitshiftLeft(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptBitshiftLeftAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptLessThanOrEqual(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptEqual(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptStrictlyEqual(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptArrow(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptGreaterThan(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptGreaterThanOrEqual(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptBitshiftRight(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptBitshiftRightAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptUnsignedBitshiftRight(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptUnsignedBitshiftRightAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptQuestion(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptChaining(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptNullishCoalescing(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptNullishCoalescingAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptMatrixMultiply(JavascriptAST, TerminalSymbol, AST):
    pass


class ArgumentsAST(AST):
    pass


class ECMAArguments(AST):
    pass


class JavascriptArguments(JavascriptAST, ECMAArguments, ArgumentsAST, AST):
    pass


class JavascriptArguments0(JavascriptArguments, AST):
    pass


class JavascriptArguments1(JavascriptArguments, AST):
    pass


class JavascriptArguments2(JavascriptArguments, AST):
    pass


class JavascriptExpression(JavascriptAST, AST):
    pass


class JavascriptPrimaryExpression(JavascriptExpression, AST):
    pass


class JavascriptArray(JavascriptPrimaryExpression, AST):
    pass


class JavascriptArray0(JavascriptArray, AST):
    pass


class JavascriptArray1(JavascriptArray, AST):
    pass


class JavascriptArray2(JavascriptArray, AST):
    pass


class JavascriptPattern(JavascriptAST, AST):
    pass


class JavascriptArrayPattern(JavascriptPattern, AST):
    pass


class JavascriptArrayPattern0(JavascriptArrayPattern, AST):
    pass


class JavascriptArrayPattern1(JavascriptArrayPattern, AST):
    pass


class JavascriptArrayPattern2(JavascriptArrayPattern, AST):
    pass


class LambdaAST(FunctionAST, AST):
    pass


class JavascriptArrowFunction(JavascriptPrimaryExpression, LambdaAST, AST):
    pass


class JavascriptArrowFunction0(JavascriptArrowFunction, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptArrowFunction1(JavascriptArrowFunction, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptAs(JavascriptAST, TerminalSymbol, AST):
    pass


class ECMAAssignmentExpression(AST):
    pass


class JavascriptAssignmentExpression(JavascriptExpression, AssignmentAST, ECMAAssignmentExpression, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class ECMAAssignmentPattern(AST):
    pass


class JavascriptAssignmentPattern(JavascriptAST, AssignmentAST, ECMAAssignmentPattern, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class JavascriptAsync(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptAugmentedAssignmentExpression(JavascriptExpression, AssignmentAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class JavascriptAwait(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptAwaitExpression(JavascriptExpression, AST):
    pass


class JavascriptBinaryExpression(JavascriptExpression, BinaryAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class JavascriptBreak(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptStatement(JavascriptAST, StatementAST, AST):
    pass


class JavascriptBreakStatement(JavascriptStatement, AST):
        @cached_property
        def label(self) -> AST:
            return self.child_slot("LABEL")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class ECMACallExpression(AST):
    pass


class JavascriptCallExpression(JavascriptPrimaryExpression, ECMACallExpression, CallAST, AST):
    pass


class JavascriptCallExpression0(JavascriptCallExpression, AST):
        @cached_property
        def function(self) -> AST:
            return self.child_slot("FUNCTION")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class JavascriptCallExpression1(JavascriptCallExpression, AST):
        @cached_property
        def function(self) -> AST:
            return self.child_slot("FUNCTION")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class JavascriptCase(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptCatch(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptCatchClause(JavascriptAST, CatchAST, AST):
    pass


class JavascriptCatchClause0(JavascriptCatchClause, AST):
        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptCatchClause1(JavascriptCatchClause, AST):
        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptClass(JavascriptPrimaryExpression, AST):
    pass


class JavascriptClass0(JavascriptClass, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptClass1(JavascriptClass, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptClassBody(JavascriptAST, AST):
        @cached_property
        def member(self) -> List[AST]:
            return self.child_slot("MEMBER")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class ClassAST(TypeDeclarationAST, AST):
    pass


class JavascriptDeclaration(JavascriptStatement, AST):
    pass


class JavascriptClassDeclaration(JavascriptDeclaration, ClassAST, AST):
    pass


class JavascriptClassDeclaration0(JavascriptClassDeclaration, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptClassDeclaration1(JavascriptClassDeclaration, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptClassHeritage(JavascriptAST, AST):
    pass


class JavascriptClassTerminal(JavascriptPrimaryExpression, TerminalSymbol, AST):
    pass


class ECMAComment(CommentAST, AST):
    pass


class JavascriptComment(JavascriptAST, ECMAComment, CommentAST, AST):
    pass


class JavascriptComputedPropertyName(JavascriptAST, AST):
    pass


class JavascriptConst(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptContinue(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptContinueStatement(JavascriptStatement, AST):
        @cached_property
        def label(self) -> AST:
            return self.child_slot("LABEL")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class JavascriptDebugger(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptDebuggerStatement(JavascriptStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class JavascriptDecorator(JavascriptAST, AST):
    pass


class JavascriptDecorator0(JavascriptDecorator, AST):
    pass


class JavascriptDecorator1(JavascriptDecorator, AST):
    pass


class JavascriptDecorator2(JavascriptDecorator, AST):
    pass


class JavascriptDefault(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptDelete(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptDo(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptDoStatement(JavascriptStatement, LoopAST, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class JavascriptElse(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptElseClause(JavascriptAST, AST):
    pass


class JavascriptEmptyStatement(JavascriptStatement, AST):
    pass


class ECMAError(AST):
    pass


class JavascriptError(JavascriptAST, ECMAError, ParseErrorAST, AST):
    pass


class JavascriptEscapeSequence(JavascriptAST, AST):
    pass


class JavascriptExport(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptExportClause(JavascriptAST, AST):
    pass


class JavascriptExportClause0(JavascriptExportClause, AST):
    pass


class JavascriptExportClause1(JavascriptExportClause, AST):
    pass


class JavascriptExportClause2(JavascriptExportClause, AST):
    pass


class JavascriptExportClause3(JavascriptExportClause, AST):
    pass


class JavascriptExportSpecifier(JavascriptAST, AST):
    pass


class JavascriptExportSpecifier0(JavascriptExportSpecifier, AST):
    pass


class JavascriptExportSpecifier1(JavascriptExportSpecifier, AST):
    pass


class JavascriptExportStatement(JavascriptStatement, AST):
    pass


class JavascriptExportStatement0(JavascriptExportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declaration(self) -> AST:
            return self.child_slot("DECLARATION")

        @cached_property
        def default(self) -> AST:
            return self.child_slot("DEFAULT")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class JavascriptExportStatement1(JavascriptExportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declaration(self) -> AST:
            return self.child_slot("DECLARATION")

        @cached_property
        def default(self) -> AST:
            return self.child_slot("DEFAULT")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class JavascriptExpressionStatement(JavascriptStatement, ExpressionStatementAST, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class JavascriptExtends(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptFalse(JavascriptPrimaryExpression, BooleanFalseAST, AST):
    pass


class JavascriptFieldDefinition(JavascriptAST, AST):
    pass


class JavascriptFieldDefinition0(JavascriptFieldDefinition, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def property(self) -> AST:
            return self.child_slot("PROPERTY")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class JavascriptFieldDefinition1(JavascriptFieldDefinition, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def property(self) -> AST:
            return self.child_slot("PROPERTY")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class JavascriptFinally(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptFinallyClause(JavascriptAST, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptFor(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptForInStatement(JavascriptStatement, AST):
    pass


class JavascriptForInStatement0(JavascriptForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptForInStatement1(JavascriptForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptForInStatement2(JavascriptForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptForInStatement3(JavascriptForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptForInStatement4(JavascriptForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptForInStatement5(JavascriptForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptForInStatement6(JavascriptForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptForInStatement7(JavascriptForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptForStatement(JavascriptStatement, LoopAST, AST):
        @cached_property
        def initializer(self) -> AST:
            return self.child_slot("INITIALIZER")

        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def increment(self) -> AST:
            return self.child_slot("INCREMENT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class ParametersAST(AST):
    pass


class JavascriptFormalParameters(JavascriptAST, ParametersAST, AST):
    pass


class JavascriptFormalParameters0(JavascriptFormalParameters, AST):
    pass


class JavascriptFormalParameters1(JavascriptFormalParameters, AST):
    pass


class JavascriptFrom(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptFunction(JavascriptPrimaryExpression, LambdaAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptFunctionDeclaration(JavascriptDeclaration, FunctionDeclarationAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def javascript_async(self) -> AST:
            return self.child_slot("JAVASCRIPT-ASYNC")


class JavascriptFunctionTerminal(JavascriptPrimaryExpression, LambdaAST, TerminalSymbol, AST):
    pass


class JavascriptGeneratorFunction(JavascriptPrimaryExpression, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptGeneratorFunctionDeclaration(JavascriptDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptGet(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptHashBangLine(JavascriptAST, AST):
    pass


class JavascriptIdentifier(JavascriptPattern, JavascriptPrimaryExpression, IdentifierAST, AST):
    pass


class JavascriptIf(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptIfStatement(JavascriptStatement, IfAST, AST):
    pass


class JavascriptIfStatement0(JavascriptIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class JavascriptIfStatement1(JavascriptIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class JavascriptImport(JavascriptPrimaryExpression, AST):
    pass


class JavascriptImportClause(JavascriptAST, AST):
    pass


class JavascriptImportClause0(JavascriptImportClause, AST):
    pass


class JavascriptImportClause1(JavascriptImportClause, AST):
    pass


class JavascriptImportClause2(JavascriptImportClause, AST):
    pass


class JavascriptImportSpecifier(JavascriptAST, AST):
    pass


class JavascriptImportSpecifier0(JavascriptImportSpecifier, AST):
    pass


class JavascriptImportSpecifier1(JavascriptImportSpecifier, AST):
    pass


class JavascriptImportStatement(JavascriptStatement, AST):
    pass


class JavascriptImportStatement0(JavascriptImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class JavascriptImportStatement1(JavascriptImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class JavascriptImportTerminal(JavascriptPrimaryExpression, TerminalSymbol, AST):
    pass


class JavascriptIn(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptInnerWhitespace(JavascriptAST, InnerWhitespace, AST):
    pass


class JavascriptInstanceof(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptJsxAttribute(JavascriptAST, AST):
    pass


class JavascriptJsxAttribute0(JavascriptJsxAttribute, AST):
    pass


class JavascriptJsxAttribute1(JavascriptJsxAttribute, AST):
    pass


class JavascriptJsxAttribute2(JavascriptJsxAttribute, AST):
    pass


class JavascriptJsxAttribute3(JavascriptJsxAttribute, AST):
    pass


class JavascriptJsxAttribute4(JavascriptJsxAttribute, AST):
    pass


class JavascriptJsxAttribute5(JavascriptJsxAttribute, AST):
    pass


class JavascriptJsxClosingElement(JavascriptAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class JavascriptJsxElement(JavascriptExpression, AST):
        @cached_property
        def open_tag(self) -> AST:
            return self.child_slot("OPEN-TAG")

        @cached_property
        def close_tag(self) -> AST:
            return self.child_slot("CLOSE-TAG")


class JavascriptJsxExpression(JavascriptAST, AST):
    pass


class JavascriptJsxExpression0(JavascriptJsxExpression, AST):
    pass


class JavascriptJsxExpression1(JavascriptJsxExpression, AST):
    pass


class JavascriptJsxFragment(JavascriptExpression, AST):
    pass


class JavascriptJsxNamespaceName(JavascriptAST, AST):
    pass


class JavascriptJsxOpeningElement(JavascriptAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def attribute(self) -> List[AST]:
            return self.child_slot("ATTRIBUTE")


class JavascriptJsxSelfClosingElement(JavascriptExpression, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def attribute(self) -> List[AST]:
            return self.child_slot("ATTRIBUTE")


class JavascriptJsxText(JavascriptAST, AST):
    pass


class JavascriptLabeledStatement(JavascriptStatement, AST):
        @cached_property
        def label(self) -> AST:
            return self.child_slot("LABEL")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptLet(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptLexicalDeclaration(JavascriptDeclaration, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class ECMAMemberExpression(AST):
    pass


class JavascriptMemberExpression(JavascriptPattern, JavascriptPrimaryExpression, ECMAMemberExpression, FieldAST, AST):
    pass


class JavascriptMemberExpression0(JavascriptMemberExpression, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def property(self) -> AST:
            return self.child_slot("PROPERTY")


class JavascriptMemberExpression1(JavascriptMemberExpression, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def property(self) -> AST:
            return self.child_slot("PROPERTY")


class JavascriptMetaProperty(JavascriptPrimaryExpression, AST):
    pass


class JavascriptMethodDefinition(JavascriptAST, AST):
    pass


class JavascriptMethodDefinition0(JavascriptMethodDefinition, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptMethodDefinition1(JavascriptMethodDefinition, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptMethodDefinition2(JavascriptMethodDefinition, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptMethodDefinition3(JavascriptMethodDefinition, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptNamedImports(JavascriptAST, AST):
    pass


class JavascriptNamedImports0(JavascriptNamedImports, AST):
    pass


class JavascriptNamedImports1(JavascriptNamedImports, AST):
    pass


class JavascriptNamedImports2(JavascriptNamedImports, AST):
    pass


class JavascriptNamedImports3(JavascriptNamedImports, AST):
    pass


class JavascriptNamespaceExport(JavascriptAST, AST):
    pass


class JavascriptNamespaceImport(JavascriptAST, AST):
    pass


class JavascriptNamespaceImport0(JavascriptNamespaceImport, AST):
    pass


class JavascriptNamespaceImport1(JavascriptNamespaceImport, AST):
    pass


class JavascriptNestedIdentifier(JavascriptAST, AST):
    pass


class JavascriptNew(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptNewExpression(JavascriptExpression, AST):
        @cached_property
        def constructor(self) -> AST:
            return self.child_slot("CONSTRUCTOR")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class JavascriptNull(JavascriptPrimaryExpression, AST):
    pass


class FloatAST(NumberAST, AST):
    pass


class JavascriptNumber(JavascriptPrimaryExpression, FloatAST, AST):
    pass


class JavascriptObject(JavascriptPrimaryExpression, AST):
    pass


class JavascriptObject0(JavascriptObject, AST):
    pass


class JavascriptObject1(JavascriptObject, AST):
    pass


class JavascriptObject2(JavascriptObject, AST):
    pass


class JavascriptObject3(JavascriptObject, AST):
    pass


class JavascriptObjectAssignmentPattern(JavascriptAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class JavascriptObjectPattern(JavascriptPattern, AST):
    pass


class JavascriptObjectPattern0(JavascriptObjectPattern, AST):
    pass


class JavascriptObjectPattern1(JavascriptObjectPattern, AST):
    pass


class JavascriptObjectPattern2(JavascriptObjectPattern, AST):
    pass


class JavascriptObjectPattern3(JavascriptObjectPattern, AST):
    pass


class JavascriptOf(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptPair(JavascriptAST, AST):
        @cached_property
        def key(self) -> AST:
            return self.child_slot("KEY")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class JavascriptPairPattern(JavascriptAST, AST):
        @cached_property
        def key(self) -> AST:
            return self.child_slot("KEY")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class JavascriptParenthesizedExpression(JavascriptPrimaryExpression, ParenthesizedExpressionAST, AST):
    pass


class JavascriptPrivatePropertyIdentifier(JavascriptAST, AST):
    pass


class JavascriptProgram(JavascriptAST, RootAST, AST):
    pass


class JavascriptProgram0(JavascriptProgram, AST):
    pass


class JavascriptProgram1(JavascriptProgram, AST):
    pass


class JavascriptPropertyIdentifier(JavascriptAST, IdentifierAST, AST):
    pass


class JavascriptRegex(JavascriptPrimaryExpression, AST):
        @cached_property
        def pattern(self) -> AST:
            return self.child_slot("PATTERN")

        @cached_property
        def flags(self) -> AST:
            return self.child_slot("FLAGS")


class JavascriptRegexFlags(JavascriptAST, AST):
    pass


class JavascriptRegexPattern(JavascriptAST, AST):
    pass


class ECMARestPattern(AST):
    pass


class JavascriptRestPattern(JavascriptPattern, ECMARestPattern, AST):
    pass


class JavascriptRestPattern0(JavascriptRestPattern, AST):
    pass


class JavascriptRestPattern1(JavascriptRestPattern, AST):
    pass


class JavascriptRestPattern2(JavascriptRestPattern, AST):
    pass


class JavascriptReturn(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptReturnStatement(JavascriptStatement, ReturnAST, AST):
    pass


class JavascriptReturnStatement0(JavascriptReturnStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class JavascriptReturnStatement1(JavascriptReturnStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class JavascriptSequenceExpression(JavascriptAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class JavascriptSet(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptShorthandPropertyIdentifier(JavascriptAST, IdentifierAST, AST):
    pass


class JavascriptShorthandPropertyIdentifierPattern(JavascriptAST, IdentifierAST, AST):
    pass


class JavascriptSourceTextFragment(JavascriptAST, SourceTextFragment, AST):
    pass


class JavascriptSpreadElement(JavascriptAST, AST):
    pass


class JavascriptStatementBlock(JavascriptStatement, CompoundAST, AST):
    pass


class JavascriptStatementIdentifier(JavascriptAST, AST):
    pass


class JavascriptStatic(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptString(JavascriptPrimaryExpression, StringAST, AST):
    pass


class JavascriptString0(JavascriptString, AST):
    pass


class JavascriptString1(JavascriptString, AST):
    pass


class JavascriptStringFragment(JavascriptAST, AST):
    pass


class JavascriptSubscriptExpression(JavascriptPattern, JavascriptPrimaryExpression, SubscriptAST, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def index(self) -> AST:
            return self.child_slot("INDEX")


class JavascriptSuper(JavascriptPrimaryExpression, AST):
    pass


class JavascriptSwitch(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptSwitchBody(JavascriptAST, AST):
    pass


class JavascriptSwitchCase(JavascriptAST, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def body(self) -> List[AST]:
            return self.child_slot("BODY")


class JavascriptSwitchDefault(JavascriptAST, AST):
        @cached_property
        def body(self) -> List[AST]:
            return self.child_slot("BODY")


class JavascriptSwitchStatement(JavascriptStatement, ControlFlowAST, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptTarget(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptTemplateString(JavascriptPrimaryExpression, AST):
    pass


class JavascriptTemplateSubstitution(JavascriptAST, AST):
    pass


class JavascriptTernaryExpression(JavascriptExpression, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class JavascriptThis(JavascriptPrimaryExpression, AST):
    pass


class JavascriptThrow(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptThrowStatement(JavascriptStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class JavascriptTrue(JavascriptPrimaryExpression, BooleanTrueAST, AST):
    pass


class JavascriptTry(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptTryStatement(JavascriptStatement, ControlFlowAST, AST):
    pass


class JavascriptTryStatement0(JavascriptTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def handler(self) -> AST:
            return self.child_slot("HANDLER")

        @cached_property
        def finalizer(self) -> AST:
            return self.child_slot("FINALIZER")


class JavascriptTryStatement1(JavascriptTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def handler(self) -> AST:
            return self.child_slot("HANDLER")

        @cached_property
        def finalizer(self) -> AST:
            return self.child_slot("FINALIZER")


class JavascriptTryStatement2(JavascriptTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def handler(self) -> AST:
            return self.child_slot("HANDLER")

        @cached_property
        def finalizer(self) -> AST:
            return self.child_slot("FINALIZER")


class JavascriptTryStatement3(JavascriptTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def handler(self) -> AST:
            return self.child_slot("HANDLER")

        @cached_property
        def finalizer(self) -> AST:
            return self.child_slot("FINALIZER")


class JavascriptTypeof(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptUnaryExpression(JavascriptExpression, UnaryAST, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class JavascriptUndefined(JavascriptPattern, JavascriptPrimaryExpression, AST):
    pass


class JavascriptUpdateExpression(JavascriptExpression, AssignmentAST, AST):
    pass


class JavascriptUpdateExpression0(JavascriptUpdateExpression, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class JavascriptUpdateExpression1(JavascriptUpdateExpression, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class JavascriptVar(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptVariableDeclaration(JavascriptDeclaration, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class ECMAVariableDeclarator(AST):
    pass


class JavascriptVariableDeclarator(JavascriptAST, ECMAVariableDeclarator, AST):
    pass


class JavascriptVariableDeclarator0(JavascriptVariableDeclarator, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class JavascriptVariableDeclarator1(JavascriptVariableDeclarator, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class JavascriptVoid(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptWhile(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptWhileStatement(JavascriptStatement, LoopAST, WhileAST, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptWith(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptWithStatement(JavascriptStatement, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class JavascriptYield(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptYieldExpression(JavascriptExpression, AST):
    pass


class JavascriptYieldExpression0(JavascriptYieldExpression, AST):
    pass


class JavascriptYieldExpression1(JavascriptYieldExpression, AST):
    pass


class JavascriptYieldExpression2(JavascriptYieldExpression, AST):
    pass


class JavascriptOpenBracket(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptCloseBracket(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptBitwiseXor(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptBitwiseXorAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptBackQuote(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptOpenBrace(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptBitwiseOr(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptBitwiseOrAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptLogicalOr(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptLogicalOrAssign(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptCloseBrace(JavascriptAST, TerminalSymbol, AST):
    pass


class JavascriptBitwiseNot(JavascriptAST, TerminalSymbol, AST):
    pass


class PythonAST(AST):
    pass


class PythonNotEqual(PythonAST, TerminalSymbol, AST):
    pass


class PythonDoubleQuote(PythonAST, TerminalSymbol, AST):
    pass


class PythonModulo(PythonAST, TerminalSymbol, AST):
    pass


class PythonModuleAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonBitwiseAnd(PythonAST, TerminalSymbol, AST):
    pass


class PythonBitwiseAndAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonOpenParenthesis(PythonAST, TerminalSymbol, AST):
    pass


class PythonCloseParenthesis(PythonAST, TerminalSymbol, AST):
    pass


class PythonMultiply(PythonAST, TerminalSymbol, AST):
    pass


class PythonPow(PythonAST, TerminalSymbol, AST):
    pass


class PythonPowAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonMultiplyAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonAdd(PythonAST, TerminalSymbol, AST):
    pass


class PythonAddAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonComma(PythonAST, TerminalSymbol, AST):
    pass


class PythonSubtract(PythonAST, TerminalSymbol, AST):
    pass


class PythonFutureSubtract(PythonAST, TerminalSymbol, AST):
    pass


class PythonSubtractAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonArrow(PythonAST, TerminalSymbol, AST):
    pass


class PythonCompoundStatement(PythonAST, StatementAST, AST):
    pass


class PythonDedent(PythonAST, AST):
    pass


class PythonIndent(PythonAST, AST):
    pass


class PythonNewline(PythonAST, AST):
    pass


class PythonSimpleStatement(PythonAST, StatementAST, AST):
    pass


class PythonStringContent(PythonAST, AST):
    pass


class PythonStringEnd(PythonAST, AST):
    pass


class PythonStringStart(PythonAST, AST):
    pass


class PythonDot(PythonAST, TerminalSymbol, AST):
    pass


class PythonDivide(PythonAST, TerminalSymbol, AST):
    pass


class PythonFloorDivide(PythonAST, TerminalSymbol, AST):
    pass


class PythonFloorDivideAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonDivideAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonColon(PythonAST, TerminalSymbol, AST):
    pass


class PythonWalrus(PythonAST, TerminalSymbol, AST):
    pass


class PythonSemicolon(PythonAST, TerminalSymbol, AST):
    pass


class PythonLessThan(PythonAST, TerminalSymbol, AST):
    pass


class PythonBitshiftLeft(PythonAST, TerminalSymbol, AST):
    pass


class PythonBitshiftLeftAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonLessThanOrEqual(PythonAST, TerminalSymbol, AST):
    pass


class PythonNotEqualFlufl(PythonAST, TerminalSymbol, AST):
    pass


class PythonAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonEqual(PythonAST, TerminalSymbol, AST):
    pass


class PythonGreaterThan(PythonAST, TerminalSymbol, AST):
    pass


class PythonGreaterThanOrEqual(PythonAST, TerminalSymbol, AST):
    pass


class PythonBitshiftRight(PythonAST, TerminalSymbol, AST):
    pass


class PythonBitshiftRightAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonMatrixMultiply(PythonAST, TerminalSymbol, AST):
    pass


class PythonMatrixMultiplyAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonAliasedImport(PythonAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def alias(self) -> AST:
            return self.child_slot("ALIAS")


class PythonAnd(PythonAST, TerminalSymbol, AST):
    pass


class PythonArgumentList(PythonAST, ArgumentsAST, AST):
    pass


class PythonArgumentList0(PythonArgumentList, AST):
    pass


class PythonArgumentList1(PythonArgumentList, AST):
    pass


class PythonArgumentList2(PythonArgumentList, AST):
    pass


class PythonArgumentList3(PythonArgumentList, AST):
    pass


class PythonArgumentList4(PythonArgumentList, AST):
    pass


class PythonAs(PythonAST, TerminalSymbol, AST):
    pass


class PythonAssert(PythonAST, TerminalSymbol, AST):
    pass


class PythonAssertStatement(PythonSimpleStatement, AST):
    pass


class PythonAssignment(PythonAST, AssignmentAST, VariableDeclarationAST, AST):
    pass


class PythonAssignment0(PythonAssignment, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class PythonAssignment1(PythonAssignment, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class PythonAssignment2(PythonAssignment, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class PythonAsync(PythonAST, TerminalSymbol, AST):
    pass


class PythonExpression(PythonAST, ExpressionAST, AST):
    pass


class PythonPrimaryExpression(PythonExpression, AST):
    pass


class PythonPattern(PythonAST, AST):
    pass


class PythonAttribute(PythonPattern, PythonPrimaryExpression, FieldAST, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def attribute(self) -> AST:
            return self.child_slot("ATTRIBUTE")


class PythonAugmentedAssignment(PythonAST, AssignmentAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class PythonAwait(PythonExpression, AST):
    pass


class PythonAwaitTerminal(PythonExpression, TerminalSymbol, AST):
    pass


class PythonBinaryOperator(PythonPrimaryExpression, BinaryAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class PythonBlock(PythonAST, CompoundAST, AST):
    pass


class PythonBooleanOperator(PythonExpression, BinaryAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class PythonBreak(PythonAST, TerminalSymbol, AST):
    pass


class PythonBreakStatement(PythonSimpleStatement, AST):
    pass


class PythonCall(PythonPrimaryExpression, CallAST, AST):
        @cached_property
        def function(self) -> AST:
            return self.child_slot("FUNCTION")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class PythonChevron(PythonAST, AST):
    pass


class PythonClass(PythonAST, TerminalSymbol, AST):
    pass


class PythonClassDefinition(PythonCompoundStatement, ClassAST, AST):
    pass


class PythonClassDefinition0(PythonClassDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def superclasses(self) -> AST:
            return self.child_slot("SUPERCLASSES")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonClassDefinition1(PythonClassDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def superclasses(self) -> AST:
            return self.child_slot("SUPERCLASSES")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonComment(PythonAST, CommentAST, AST):
    pass


class PythonComparisonOperator(PythonExpression, AST):
    pass


class PythonComparisonOperator0(PythonComparisonOperator, AST):
        @cached_property
        def operators(self) -> List[AST]:
            return self.child_slot("OPERATORS")


class PythonComparisonOperator1(PythonComparisonOperator, AST):
        @cached_property
        def operators(self) -> List[AST]:
            return self.child_slot("OPERATORS")


class PythonComparisonOperator10(PythonComparisonOperator, AST):
        @cached_property
        def operators(self) -> List[AST]:
            return self.child_slot("OPERATORS")


class PythonComparisonOperator2(PythonComparisonOperator, AST):
        @cached_property
        def operators(self) -> List[AST]:
            return self.child_slot("OPERATORS")


class PythonComparisonOperator3(PythonComparisonOperator, AST):
        @cached_property
        def operators(self) -> List[AST]:
            return self.child_slot("OPERATORS")


class PythonComparisonOperator4(PythonComparisonOperator, AST):
        @cached_property
        def operators(self) -> List[AST]:
            return self.child_slot("OPERATORS")


class PythonComparisonOperator5(PythonComparisonOperator, AST):
        @cached_property
        def operators(self) -> List[AST]:
            return self.child_slot("OPERATORS")


class PythonComparisonOperator6(PythonComparisonOperator, AST):
        @cached_property
        def operators(self) -> List[AST]:
            return self.child_slot("OPERATORS")


class PythonComparisonOperator7(PythonComparisonOperator, AST):
        @cached_property
        def operators(self) -> List[AST]:
            return self.child_slot("OPERATORS")


class PythonComparisonOperator8(PythonComparisonOperator, AST):
        @cached_property
        def operators(self) -> List[AST]:
            return self.child_slot("OPERATORS")


class PythonComparisonOperator9(PythonComparisonOperator, AST):
        @cached_property
        def operators(self) -> List[AST]:
            return self.child_slot("OPERATORS")


class PythonConcatenatedString(PythonPrimaryExpression, AST):
    pass


class PythonConditionalExpression(PythonExpression, ControlFlowAST, AST):
    pass


class PythonContinue(PythonAST, TerminalSymbol, AST):
    pass


class PythonContinueStatement(PythonSimpleStatement, AST):
    pass


class PythonDecoratedDefinition(PythonCompoundStatement, AST):
        @cached_property
        def definition(self) -> AST:
            return self.child_slot("DEFINITION")


class PythonDecorator(PythonAST, AST):
    pass


class PythonDef(PythonAST, TerminalSymbol, AST):
    pass


class PythonParameter(PythonAST, AST):
    pass


class PythonDefaultParameter(PythonParameter, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class PythonDel(PythonAST, TerminalSymbol, AST):
    pass


class PythonDeleteStatement(PythonSimpleStatement, AST):
    pass


class PythonDictionary(PythonPrimaryExpression, AST):
    pass


class PythonDictionary0(PythonDictionary, AST):
    pass


class PythonDictionary1(PythonDictionary, AST):
    pass


class PythonDictionary2(PythonDictionary, AST):
    pass


class PythonDictionary3(PythonDictionary, AST):
    pass


class PythonDictionaryComprehension(PythonPrimaryExpression, ControlFlowAST, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonDictionarySplat(PythonAST, AST):
    pass


class PythonDictionarySplatPattern(PythonParameter, AST):
    pass


class PythonDictionarySplatPattern0(PythonDictionarySplatPattern, AST):
    pass


class PythonDictionarySplatPattern1(PythonDictionarySplatPattern, AST):
    pass


class PythonDottedName(PythonAST, AST):
    pass


class PythonElif(PythonAST, TerminalSymbol, AST):
    pass


class PythonElifClause(PythonAST, AST):
    pass


class PythonElifClause0(PythonElifClause, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")


class PythonElifClause1(PythonElifClause, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")


class PythonEllipsis(PythonPrimaryExpression, AST):
    pass


class PythonElse(PythonAST, TerminalSymbol, AST):
    pass


class PythonElseClause(PythonAST, AST):
    pass


class PythonElseClause0(PythonElseClause, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonElseClause1(PythonElseClause, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonEmptyArgumentList(PythonArgumentList, AST):
    pass


class PythonParameters(PythonAST, ParametersAST, AST):
    pass


class PythonEmptyParameters(PythonParameters, AST):
    pass


class PythonTuple(PythonPrimaryExpression, AST):
    pass


class PythonEmptyTuple(PythonTuple, AST):
    pass


class PythonError(PythonAST, ParseErrorAST, AST):
    pass


class PythonEscapeSequence(PythonAST, AST):
    pass


class PythonExcept(PythonAST, TerminalSymbol, AST):
    pass


class PythonExceptClause(PythonAST, CatchAST, AST):
    pass


class PythonExceptClause0(PythonExceptClause, AST):
    pass


class PythonExceptClause1(PythonExceptClause, AST):
    pass


class PythonExceptClause2(PythonExceptClause, AST):
    pass


class PythonExceptClause3(PythonExceptClause, AST):
    pass


class PythonExceptClause4(PythonExceptClause, AST):
    pass


class PythonExceptClause5(PythonExceptClause, AST):
    pass


class PythonExec(PythonAST, TerminalSymbol, AST):
    pass


class PythonExecStatement(PythonSimpleStatement, AST):
    pass


class PythonExecStatement0(PythonExecStatement, AST):
        @cached_property
        def code(self) -> AST:
            return self.child_slot("CODE")


class PythonExecStatement1(PythonExecStatement, AST):
        @cached_property
        def code(self) -> AST:
            return self.child_slot("CODE")


class PythonExpressionList(PythonAST, AST):
    pass


class PythonExpressionList0(PythonExpressionList, AST):
    pass


class PythonExpressionList1(PythonExpressionList, AST):
    pass


class PythonExpressionStatement(PythonSimpleStatement, ExpressionStatementAST, AST):
    pass


class PythonExpressionStatement0(PythonExpressionStatement, AST):
    pass


class PythonExpressionStatement1(PythonExpressionStatement, AST):
    pass


class PythonFalse(PythonPrimaryExpression, BooleanFalseAST, AST):
    pass


class PythonFinally(PythonAST, TerminalSymbol, AST):
    pass


class PythonFinallyClause(PythonAST, AST):
    pass


class PythonFinallyClause0(PythonFinallyClause, AST):
    pass


class PythonFinallyClause1(PythonFinallyClause, AST):
    pass


class PythonFloat(PythonPrimaryExpression, FloatAST, AST):
    pass


class PythonFor(PythonAST, TerminalSymbol, AST):
    pass


class PythonForInClause(PythonAST, LoopAST, AST):
    pass


class PythonForInClause0(PythonForInClause, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> List[AST]:
            return self.child_slot("RIGHT")


class PythonForInClause1(PythonForInClause, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> List[AST]:
            return self.child_slot("RIGHT")


class PythonForStatement(PythonCompoundStatement, LoopAST, AST):
    pass


class PythonForStatement0(PythonForStatement, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")

        @cached_property
        def python_async(self) -> AST:
            return self.child_slot("PYTHON-ASYNC")


class PythonForStatement1(PythonForStatement, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")

        @cached_property
        def python_async(self) -> AST:
            return self.child_slot("PYTHON-ASYNC")


class PythonFormatExpression(PythonAST, AST):
    pass


class PythonFormatSpecifier(PythonAST, AST):
    pass


class PythonFrom(PythonAST, TerminalSymbol, AST):
    pass


class PythonFunctionDefinition(PythonCompoundStatement, FunctionDeclarationAST, AST):
    pass


class PythonFunctionDefinition0(PythonFunctionDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def python_async(self) -> AST:
            return self.child_slot("PYTHON-ASYNC")


class PythonFunctionDefinition1(PythonFunctionDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def python_async(self) -> AST:
            return self.child_slot("PYTHON-ASYNC")


class PythonFunctionDefinition2(PythonFunctionDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def python_async(self) -> AST:
            return self.child_slot("PYTHON-ASYNC")


class PythonFunctionDefinition3(PythonFunctionDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def python_async(self) -> AST:
            return self.child_slot("PYTHON-ASYNC")


class PythonFutureImportStatement(PythonSimpleStatement, AST):
    pass


class PythonFutureImportStatement0(PythonFutureImportStatement, AST):
        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")


class PythonFutureImportStatement1(PythonFutureImportStatement, AST):
        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")


class PythonGeneratorExpression(PythonPrimaryExpression, ControlFlowAST, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonGlobal(PythonAST, TerminalSymbol, AST):
    pass


class PythonGlobalStatement(PythonSimpleStatement, AST):
    pass


class PythonIdentifier(PythonParameter, PythonPattern, PythonPrimaryExpression, IdentifierAST, AST):
    pass


class PythonIf(PythonAST, TerminalSymbol, AST):
    pass


class PythonIfClause(PythonAST, AST):
    pass


class PythonIfStatement(PythonCompoundStatement, IfAST, AST):
    pass


class PythonIfStatement0(PythonIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> List[AST]:
            return self.child_slot("ALTERNATIVE")


class PythonIfStatement1(PythonIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> List[AST]:
            return self.child_slot("ALTERNATIVE")


class PythonIfStatement2(PythonIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> List[AST]:
            return self.child_slot("ALTERNATIVE")


class PythonIfStatement3(PythonIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> List[AST]:
            return self.child_slot("ALTERNATIVE")


class PythonImport(PythonAST, TerminalSymbol, AST):
    pass


class PythonImportFromStatement(PythonSimpleStatement, AST):
    pass


class PythonImportFromStatement0(PythonImportFromStatement, AST):
        @cached_property
        def module_name(self) -> AST:
            return self.child_slot("MODULE-NAME")

        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")


class PythonImportFromStatement1(PythonImportFromStatement, AST):
        @cached_property
        def module_name(self) -> AST:
            return self.child_slot("MODULE-NAME")

        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")


class PythonImportFromStatement2(PythonImportFromStatement, AST):
        @cached_property
        def module_name(self) -> AST:
            return self.child_slot("MODULE-NAME")

        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")


class PythonImportPrefix(PythonAST, AST):
    pass


class PythonImportStatement(PythonSimpleStatement, AST):
        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")


class PythonIn(PythonAST, TerminalSymbol, AST):
    pass


class PythonInnerWhitespace(PythonAST, InnerWhitespace, AST):
    pass


class IntegerAST(NumberAST, AST):
    pass


class PythonInteger(PythonPrimaryExpression, IntegerAST, AST):
    pass


class PythonInterpolation(PythonAST, AST):
    pass


class PythonInterpolation0(PythonInterpolation, AST):
    pass


class PythonInterpolation1(PythonInterpolation, AST):
    pass


class PythonInterpolation2(PythonInterpolation, AST):
    pass


class PythonInterpolation3(PythonInterpolation, AST):
    pass


class PythonIs(PythonAST, TerminalSymbol, AST):
    pass


class PythonKeywordArgument(PythonAST, VariableDeclarationAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class PythonKeywordOnlySeparator(PythonParameter, AST):
    pass


class PythonLambda(PythonExpression, LambdaAST, AST):
        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonLambdaParameters(PythonAST, ParametersAST, AST):
    pass


class PythonLambdaTerminal(PythonExpression, LambdaAST, TerminalSymbol, AST):
    pass


class PythonList(PythonPrimaryExpression, AST):
    pass


class PythonList0(PythonList, AST):
    pass


class PythonList1(PythonList, AST):
    pass


class PythonListComprehension(PythonPrimaryExpression, ControlFlowAST, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonListPattern(PythonPattern, AST):
    pass


class PythonListPattern0(PythonListPattern, AST):
    pass


class PythonListPattern1(PythonListPattern, AST):
    pass


class PythonListSplat(PythonAST, AST):
    pass


class PythonListSplatPattern(PythonParameter, PythonPattern, AST):
    pass


class PythonListSplatPattern0(PythonListSplatPattern, AST):
    pass


class PythonListSplatPattern1(PythonListSplatPattern, AST):
    pass


class PythonModule(PythonAST, RootAST, AST):
    pass


class PythonNamedExpression(PythonExpression, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class PythonNone(PythonPrimaryExpression, AST):
    pass


class PythonNonlocal(PythonAST, TerminalSymbol, AST):
    pass


class PythonNonlocalStatement(PythonSimpleStatement, AST):
    pass


class PythonNot(PythonAST, TerminalSymbol, AST):
    pass


class PythonNotOperator(PythonExpression, UnaryAST, AST):
        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class PythonOr(PythonAST, TerminalSymbol, AST):
    pass


class PythonPair(PythonAST, AST):
        @cached_property
        def key(self) -> AST:
            return self.child_slot("KEY")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class PythonParameters0(PythonParameters, AST):
    pass


class PythonParenthesizedExpression(PythonPrimaryExpression, ParenthesizedExpressionAST, AST):
    pass


class PythonParenthesizedExpression0(PythonParenthesizedExpression, AST):
    pass


class PythonParenthesizedExpression1(PythonParenthesizedExpression, AST):
    pass


class PythonParenthesizedListSplat(PythonAST, AST):
    pass


class PythonParenthesizedListSplat0(PythonParenthesizedListSplat, AST):
    pass


class PythonParenthesizedListSplat1(PythonParenthesizedListSplat, AST):
    pass


class PythonPass(PythonAST, TerminalSymbol, AST):
    pass


class PythonPassStatement(PythonSimpleStatement, AST):
    pass


class PythonPatternList(PythonAST, AST):
    pass


class PythonPatternList0(PythonPatternList, AST):
    pass


class PythonPatternList1(PythonPatternList, AST):
    pass


class PythonPositionalOnlySeparator(PythonParameter, AST):
    pass


class PythonPrint(PythonAST, TerminalSymbol, AST):
    pass


class PythonPrintStatement(PythonSimpleStatement, AST):
    pass


class PythonPrintStatement0(PythonPrintStatement, AST):
        @cached_property
        def argument(self) -> List[AST]:
            return self.child_slot("ARGUMENT")


class PythonPrintStatement1(PythonPrintStatement, AST):
        @cached_property
        def argument(self) -> List[AST]:
            return self.child_slot("ARGUMENT")


class PythonRaise(PythonAST, TerminalSymbol, AST):
    pass


class PythonRaiseStatement(PythonSimpleStatement, AST):
    pass


class PythonRaiseStatement0(PythonRaiseStatement, AST):
        @cached_property
        def cause(self) -> AST:
            return self.child_slot("CAUSE")


class PythonRaiseStatement1(PythonRaiseStatement, AST):
        @cached_property
        def cause(self) -> AST:
            return self.child_slot("CAUSE")


class PythonRaiseStatement2(PythonRaiseStatement, AST):
        @cached_property
        def cause(self) -> AST:
            return self.child_slot("CAUSE")


class PythonRaiseStatement3(PythonRaiseStatement, AST):
        @cached_property
        def cause(self) -> AST:
            return self.child_slot("CAUSE")


class PythonRelativeImport(PythonAST, AST):
    pass


class PythonRelativeImport0(PythonRelativeImport, AST):
    pass


class PythonRelativeImport1(PythonRelativeImport, AST):
    pass


class PythonReturn(PythonAST, TerminalSymbol, AST):
    pass


class PythonReturnStatement(PythonSimpleStatement, ReturnAST, AST):
    pass


class PythonReturnStatement0(PythonReturnStatement, AST):
    pass


class PythonReturnStatement1(PythonReturnStatement, AST):
    pass


class PythonSet(PythonPrimaryExpression, AST):
    pass


class PythonSetComprehension(PythonPrimaryExpression, ControlFlowAST, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonSlice(PythonAST, AST):
    pass


class PythonSlice0(PythonSlice, AST):
    pass


class PythonSlice1(PythonSlice, AST):
    pass


class PythonSlice10(PythonSlice, AST):
    pass


class PythonSlice11(PythonSlice, AST):
    pass


class PythonSlice2(PythonSlice, AST):
    pass


class PythonSlice3(PythonSlice, AST):
    pass


class PythonSlice4(PythonSlice, AST):
    pass


class PythonSlice5(PythonSlice, AST):
    pass


class PythonSlice6(PythonSlice, AST):
    pass


class PythonSlice7(PythonSlice, AST):
    pass


class PythonSlice8(PythonSlice, AST):
    pass


class PythonSlice9(PythonSlice, AST):
    pass


class PythonSourceTextFragment(PythonAST, SourceTextFragment, AST):
    pass


class PythonString(PythonPrimaryExpression, StringAST, AST):
    pass


class PythonSubscript(PythonPattern, PythonPrimaryExpression, SubscriptAST, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def subscript(self) -> List[AST]:
            return self.child_slot("SUBSCRIPT")


class PythonTrue(PythonPrimaryExpression, BooleanTrueAST, AST):
    pass


class PythonTry(PythonAST, TerminalSymbol, AST):
    pass


class PythonTryStatement(PythonCompoundStatement, ControlFlowAST, AST):
    pass


class PythonTryStatement0(PythonTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonTryStatement1(PythonTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonTryStatement2(PythonTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonTryStatement3(PythonTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonTryStatement4(PythonTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonTryStatement5(PythonTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonTryStatement6(PythonTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonTryStatement7(PythonTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonTryStatement8(PythonTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonTryStatement9(PythonTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class PythonTuple0(PythonTuple, AST):
    pass


class PythonTuplePattern(PythonParameter, PythonPattern, AST):
    pass


class PythonTuplePattern0(PythonTuplePattern, AST):
    pass


class PythonTuplePattern1(PythonTuplePattern, AST):
    pass


class PythonType(PythonAST, AST):
    pass


class PythonTypeConversion(PythonAST, AST):
    pass


class PythonTypedDefaultParameter(PythonParameter, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class PythonTypedParameter(PythonParameter, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class PythonUnaryOperator(PythonPrimaryExpression, UnaryAST, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class PythonWhile(PythonAST, TerminalSymbol, AST):
    pass


class PythonWhileStatement(PythonCompoundStatement, LoopAST, WhileAST, AST):
    pass


class PythonWhileStatement0(PythonWhileStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class PythonWhileStatement1(PythonWhileStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class PythonWhileStatement2(PythonWhileStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class PythonWhileStatement3(PythonWhileStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class PythonWildcardImport(PythonAST, AST):
    pass


class PythonWith(PythonAST, TerminalSymbol, AST):
    pass


class PythonWithClause(PythonAST, AST):
    pass


class PythonWithClause0(PythonWithClause, AST):
    pass


class PythonWithClause1(PythonWithClause, AST):
    pass


class PythonWithItem(PythonAST, AST):
    pass


class PythonWithItem0(PythonWithItem, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def alias(self) -> AST:
            return self.child_slot("ALIAS")


class PythonWithItem1(PythonWithItem, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def alias(self) -> AST:
            return self.child_slot("ALIAS")


class PythonWithStatement(PythonCompoundStatement, AST):
    pass


class PythonWithStatement0(PythonWithStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def python_async(self) -> AST:
            return self.child_slot("PYTHON-ASYNC")


class PythonWithStatement1(PythonWithStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def python_async(self) -> AST:
            return self.child_slot("PYTHON-ASYNC")


class PythonYield(PythonAST, AST):
    pass


class PythonYield0(PythonYield, AST):
    pass


class PythonYield1(PythonYield, AST):
    pass


class PythonYield2(PythonYield, AST):
    pass


class PythonYieldTerminal(PythonAST, TerminalSymbol, AST):
    pass


class PythonOpenBracket(PythonAST, TerminalSymbol, AST):
    pass


class PythonCloseBracket(PythonAST, TerminalSymbol, AST):
    pass


class PythonBitwiseXor(PythonAST, TerminalSymbol, AST):
    pass


class PythonBitwiseXorAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonOpenBrace(PythonAST, TerminalSymbol, AST):
    pass


class PythonDoubleOpenBrace(PythonAST, TerminalSymbol, AST):
    pass


class PythonBitwiseOr(PythonAST, TerminalSymbol, AST):
    pass


class PythonBitwiseOrAssign(PythonAST, TerminalSymbol, AST):
    pass


class PythonCloseBrace(PythonAST, TerminalSymbol, AST):
    pass


class PythonDoubleCloseBrace(PythonAST, TerminalSymbol, AST):
    pass


class PythonBitwiseNot(PythonAST, TerminalSymbol, AST):
    pass


class TypescriptAST(ECMAAST, AST):
    pass


class TypescriptTsAST(TypescriptAST, AST):
    pass


class TypescriptTsLogicalNot(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsNotEqual(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsStrictlyNotEqual(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsDoubleQuote(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsOpenTemplateLiteral(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsModulo(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsModuleAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBitwiseAnd(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsLogicalAnd(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsLogicalAndAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBitwiseAndAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsSingleQuote(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsOpenParenthesis(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsCloseParenthesis(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsMultiply(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsPow(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsPowAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsMultiplyAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsAdd(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsIncrement(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsAddAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsComma(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsSubtract(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsDecrement(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsSubtractAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsOmittingTypeTerminal(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsAutomaticSemicolon(TypescriptTsAST, AST):
    pass


class TypescriptTsFunctionSignatureAutomaticSemicolon(TypescriptTsAST, AST):
    pass


class TypescriptTsPrimaryType(TypescriptTsAST, AST):
    pass


class TypescriptTsTemplateChars(TypescriptTsAST, AST):
    pass


class TypescriptTsTernaryQmark(TypescriptTsAST, AST):
    pass


class TypescriptTsDot(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsEllipsis(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsDivide(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsDivideAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsColon(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsSemicolon(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsLessThan(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBitshiftLeft(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBitshiftLeftAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsLessThanOrEqual(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsEqual(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsStrictlyEqual(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsArrow(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsGreaterThan(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsGreaterThanOrEqual(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBitshiftRight(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBitshiftRightAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsUnsignedBitshiftRight(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsUnsignedBitshiftRightAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsQuestion(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsChaining(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsOptingTypeTerminal(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsNullishCoalescing(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsNullishCoalescingAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsMatrixMultiply(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsAbstract(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsStatement(TypescriptTsAST, AST):
    pass


class TypescriptTsDeclaration(TypescriptTsStatement, AST):
    pass


class TypescriptTsAbstractClassDeclaration(TypescriptTsDeclaration, AST):
    pass


class TypescriptTsAbstractClassDeclaration0(TypescriptTsAbstractClassDeclaration, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsAbstractClassDeclaration1(TypescriptTsAbstractClassDeclaration, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsAbstractMethodSignature(TypescriptTsAST, AST):
    pass


class TypescriptTsAbstractMethodSignature0(TypescriptTsAbstractMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsAbstractMethodSignature1(TypescriptTsAbstractMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsAbstractMethodSignature2(TypescriptTsAbstractMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsAbstractMethodSignature3(TypescriptTsAbstractMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsAccessibilityModifier(TypescriptTsAST, AST):
    pass


class TypescriptTsAmbientDeclaration(TypescriptTsDeclaration, AST):
    pass


class TypescriptTsAmbientDeclaration0(TypescriptTsAmbientDeclaration, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsAmbientDeclaration1(TypescriptTsAmbientDeclaration, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsAmbientDeclaration2(TypescriptTsAmbientDeclaration, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsAny(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsArguments(TypescriptTsAST, ECMAArguments, AST):
    pass


class TypescriptTsArguments0(TypescriptTsArguments, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsArguments1(TypescriptTsArguments, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsArguments2(TypescriptTsArguments, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsExpression(TypescriptTsAST, AST):
    pass


class TypescriptTsPrimaryExpression(TypescriptTsExpression, AST):
    pass


class TypescriptTsArray(TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsArray0(TypescriptTsArray, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsArray1(TypescriptTsArray, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsArray2(TypescriptTsArray, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsPattern(TypescriptTsAST, AST):
    pass


class TypescriptTsArrayPattern(TypescriptTsPattern, AST):
    pass


class TypescriptTsArrayPattern0(TypescriptTsArrayPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsArrayPattern1(TypescriptTsArrayPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsArrayPattern2(TypescriptTsArrayPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptArrayType(AST):
    pass


class TypescriptTsArrayType(TypescriptTsPrimaryType, TypescriptArrayType, AST):
    pass


class TypescriptTsArrowFunction(TypescriptTsPrimaryExpression, LambdaAST, AST):
    pass


class TypescriptTsArrowFunction0(TypescriptTsArrowFunction, AST):
        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsArrowFunction1(TypescriptTsArrowFunction, AST):
        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsAs(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsAsExpression(TypescriptTsExpression, AST):
    pass


class TypescriptTsAsExpression0(TypescriptTsAsExpression, AST):
    pass


class TypescriptTsAsExpression1(TypescriptTsAsExpression, AST):
    pass


class TypescriptTsAsserts(TypescriptTsAST, AST):
    pass


class TypescriptTsAssertsTerminal(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptAssignmentExpression(AST):
    pass


class TypescriptTsAssignmentExpression(TypescriptTsExpression, TypescriptAssignmentExpression, AssignmentAST, ECMAAssignmentExpression, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class TypescriptAssignmentPattern(AST):
    pass


class TypescriptTsAssignmentPattern(TypescriptTsAST, TypescriptAssignmentPattern, AssignmentAST, ECMAAssignmentPattern, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class TypescriptTsAsync(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsAugmentedAssignmentExpression(TypescriptTsExpression, AssignmentAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class TypescriptTsAwait(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsAwaitExpression(TypescriptTsExpression, AST):
    pass


class TypescriptTsBinaryExpression(TypescriptTsExpression, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class TypescriptTsBoolean(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBreak(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBreakStatement(TypescriptTsStatement, AST):
        @cached_property
        def label(self) -> AST:
            return self.child_slot("LABEL")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsCallExpression(TypescriptTsPrimaryExpression, CallAST, ECMACallExpression, AST):
    pass


class TypescriptTsCallExpression0(TypescriptTsCallExpression, AST):
        @cached_property
        def function(self) -> AST:
            return self.child_slot("FUNCTION")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class TypescriptTsCallExpression1(TypescriptTsCallExpression, AST):
        @cached_property
        def function(self) -> AST:
            return self.child_slot("FUNCTION")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class TypescriptTsCallSignature(TypescriptTsAST, AST):
        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")


class TypescriptTsCase(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsCatch(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsCatchClause(TypescriptTsAST, AST):
    pass


class TypescriptTsCatchClause0(TypescriptTsCatchClause, AST):
        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsCatchClause1(TypescriptTsCatchClause, AST):
        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsCatchClause2(TypescriptTsCatchClause, AST):
        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsClass(TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsClass0(TypescriptTsClass, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsClass1(TypescriptTsClass, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsClassBody(TypescriptTsAST, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsClassDeclaration(TypescriptTsDeclaration, ClassAST, AST):
    pass


class TypescriptTsClassDeclaration0(TypescriptTsClassDeclaration, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsClassDeclaration1(TypescriptTsClassDeclaration, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsClassHeritage(TypescriptTsAST, AST):
    pass


class TypescriptTsClassHeritage0(TypescriptTsClassHeritage, AST):
    pass


class TypescriptTsClassHeritage1(TypescriptTsClassHeritage, AST):
    pass


class TypescriptTsClassTerminal(TypescriptTsPrimaryExpression, TerminalSymbol, AST):
    pass


class TypescriptTsComment(TypescriptTsAST, ECMAComment, AST):
    pass


class TypescriptTsComputedPropertyName(TypescriptTsAST, AST):
    pass


class TypescriptTsConditionalType(TypescriptTsPrimaryType, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class TypescriptTsConst(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsConstraint(TypescriptTsAST, AST):
    pass


class TypescriptTsConstructSignature(TypescriptTsAST, AST):
        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsConstructorType(TypescriptTsAST, AST):
        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsContinue(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsContinueStatement(TypescriptTsStatement, AST):
        @cached_property
        def label(self) -> AST:
            return self.child_slot("LABEL")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsDebugger(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsDebuggerStatement(TypescriptTsStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsDeclare(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsDecorator(TypescriptTsAST, AST):
    pass


class TypescriptTsDecorator0(TypescriptTsDecorator, AST):
    pass


class TypescriptTsDecorator1(TypescriptTsDecorator, AST):
    pass


class TypescriptTsDecorator2(TypescriptTsDecorator, AST):
    pass


class TypescriptTsDefault(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsDefaultType(TypescriptTsAST, AST):
    pass


class TypescriptTsDelete(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsDo(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsDoStatement(TypescriptTsStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsElse(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsElseClause(TypescriptTsAST, AST):
    pass


class TypescriptTsEmptyStatement(TypescriptTsStatement, AST):
    pass


class TypescriptTsEnum(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsEnumAssignment(TypescriptTsAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class TypescriptTsEnumBody(TypescriptTsAST, AST):
    pass


class TypescriptTsEnumBody0(TypescriptTsEnumBody, AST):
        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsEnumBody1(TypescriptTsEnumBody, AST):
        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsEnumBody2(TypescriptTsEnumBody, AST):
        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsEnumBody3(TypescriptTsEnumBody, AST):
        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsEnumBody4(TypescriptTsEnumBody, AST):
        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsEnumDeclaration(TypescriptTsDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")


class TypescriptTsError(TypescriptTsAST, ECMAError, ParseErrorAST, AST):
    pass


class TypescriptTsEscapeSequence(TypescriptTsAST, AST):
    pass


class TypescriptTsExistentialType(TypescriptTsPrimaryType, AST):
    pass


class TypescriptTsExport(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsExportClause(TypescriptTsAST, AST):
    pass


class TypescriptTsExportClause0(TypescriptTsExportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsExportClause1(TypescriptTsExportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsExportClause2(TypescriptTsExportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsExportClause3(TypescriptTsExportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsExportSpecifier(TypescriptTsAST, AST):
    pass


class TypescriptTsExportSpecifier0(TypescriptTsExportSpecifier, AST):
    pass


class TypescriptTsExportSpecifier1(TypescriptTsExportSpecifier, AST):
    pass


class TypescriptTsExportStatement(TypescriptTsStatement, AST):
    pass


class TypescriptTsExportStatement0(TypescriptTsExportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declaration(self) -> AST:
            return self.child_slot("DECLARATION")

        @cached_property
        def default(self) -> AST:
            return self.child_slot("DEFAULT")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsExportStatement1(TypescriptTsExportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declaration(self) -> AST:
            return self.child_slot("DECLARATION")

        @cached_property
        def default(self) -> AST:
            return self.child_slot("DEFAULT")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsExportStatement2(TypescriptTsExportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declaration(self) -> AST:
            return self.child_slot("DECLARATION")

        @cached_property
        def default(self) -> AST:
            return self.child_slot("DEFAULT")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsExpressionStatement(TypescriptTsStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsExtends(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsExtendsClause(TypescriptTsAST, AST):
        @cached_property
        def type_arguments(self) -> List[AST]:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def value(self) -> List[AST]:
            return self.child_slot("VALUE")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsExtendsTypeClause(TypescriptTsAST, AST):
        @cached_property
        def type(self) -> List[AST]:
            return self.child_slot("TYPE")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsFalse(TypescriptTsPrimaryExpression, BooleanFalseAST, AST):
    pass


class TypescriptTsFinally(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsFinallyClause(TypescriptTsAST, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptFlowMaybeType(AST):
    pass


class TypescriptTsFlowMaybeType(TypescriptTsPrimaryType, TypescriptFlowMaybeType, AST):
    pass


class TypescriptTsFor(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsForInStatement(TypescriptTsStatement, AST):
    pass


class TypescriptTsForInStatement0(TypescriptTsForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsForInStatement1(TypescriptTsForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsForInStatement2(TypescriptTsForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsForInStatement3(TypescriptTsForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsForInStatement4(TypescriptTsForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsForInStatement5(TypescriptTsForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsForInStatement6(TypescriptTsForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsForInStatement7(TypescriptTsForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsForStatement(TypescriptTsStatement, AST):
        @cached_property
        def initializer(self) -> AST:
            return self.child_slot("INITIALIZER")

        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def increment(self) -> AST:
            return self.child_slot("INCREMENT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsFormalParameters(TypescriptTsAST, AST):
    pass


class TypescriptTsFormalParameters0(TypescriptTsFormalParameters, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsFormalParameters1(TypescriptTsFormalParameters, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsFormalParameters2(TypescriptTsFormalParameters, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsFrom(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsFunction(TypescriptTsPrimaryExpression, FunctionAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptFunctionDeclaration(AST):
    pass


class TypescriptTsFunctionDeclaration(TypescriptTsDeclaration, TypescriptFunctionDeclaration, FunctionDeclarationAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptFunctionSignature(AST):
    pass


class TypescriptTsFunctionSignature(TypescriptTsDeclaration, TypescriptFunctionSignature, FunctionDeclarationAST, AST):
    pass


class TypescriptTsFunctionSignature0(TypescriptTsFunctionSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsFunctionSignature1(TypescriptTsFunctionSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsFunctionTerminal(TypescriptTsPrimaryExpression, FunctionAST, TerminalSymbol, AST):
    pass


class TypescriptTsFunctionType(TypescriptTsAST, AST):
        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")


class TypescriptTsGeneratorFunction(TypescriptTsPrimaryExpression, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsGeneratorFunctionDeclaration(TypescriptTsDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptGenericType(AST):
    pass


class TypescriptTsGenericType(TypescriptTsPrimaryType, TypescriptGenericType, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")


class TypescriptTsGet(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsGlobal(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsHashBangLine(TypescriptTsAST, AST):
    pass


class TypescriptIdentifier(AST):
    pass


class TypescriptTsIdentifier(TypescriptTsPattern, TypescriptTsPrimaryExpression, TypescriptIdentifier, IdentifierAST, AST):
    pass


class TypescriptTsIf(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsIfStatement(TypescriptTsStatement, AST):
    pass


class TypescriptTsIfStatement0(TypescriptTsIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class TypescriptTsIfStatement1(TypescriptTsIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class TypescriptTsImplements(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsImplementsClause(TypescriptTsAST, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsImport(TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsImportAlias(TypescriptTsDeclaration, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsImportClause(TypescriptTsAST, AST):
    pass


class TypescriptTsImportClause0(TypescriptTsImportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsImportClause1(TypescriptTsImportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsImportClause2(TypescriptTsImportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsImportRequireClause(TypescriptTsAST, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")


class TypescriptTsImportSpecifier(TypescriptTsAST, AST):
    pass


class TypescriptTsImportSpecifier0(TypescriptTsImportSpecifier, AST):
    pass


class TypescriptTsImportSpecifier1(TypescriptTsImportSpecifier, AST):
    pass


class TypescriptTsImportStatement(TypescriptTsStatement, AST):
    pass


class TypescriptTsImportStatement0(TypescriptTsImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsImportStatement1(TypescriptTsImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsImportStatement2(TypescriptTsImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsImportStatement3(TypescriptTsImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsImportStatement4(TypescriptTsImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsImportStatement5(TypescriptTsImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsImportTerminal(TypescriptTsPrimaryExpression, TerminalSymbol, AST):
    pass


class TypescriptTsIn(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptIndexSignature(AST):
    pass


class TypescriptTsIndexSignature(TypescriptTsAST, TypescriptIndexSignature, AST):
    pass


class TypescriptTsIndexSignature0(TypescriptTsIndexSignature, AST):
        @cached_property
        def sign(self) -> AST:
            return self.child_slot("SIGN")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def index_type(self) -> AST:
            return self.child_slot("INDEX-TYPE")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsIndexSignature1(TypescriptTsIndexSignature, AST):
        @cached_property
        def sign(self) -> AST:
            return self.child_slot("SIGN")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def index_type(self) -> AST:
            return self.child_slot("INDEX-TYPE")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsIndexSignature2(TypescriptTsIndexSignature, AST):
        @cached_property
        def sign(self) -> AST:
            return self.child_slot("SIGN")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def index_type(self) -> AST:
            return self.child_slot("INDEX-TYPE")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsIndexSignature3(TypescriptTsIndexSignature, AST):
        @cached_property
        def sign(self) -> AST:
            return self.child_slot("SIGN")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def index_type(self) -> AST:
            return self.child_slot("INDEX-TYPE")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsIndexTypeQuery(TypescriptTsPrimaryType, AST):
    pass


class TypescriptTsInfer(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsInferType(TypescriptTsAST, AST):
    pass


class TypescriptTsInnerWhitespace(TypescriptTsAST, InnerWhitespace, AST):
    pass


class TypescriptTsInstanceof(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsInterface(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsInterfaceDeclaration(TypescriptTsDeclaration, AST):
    pass


class TypescriptTsInterfaceDeclaration0(TypescriptTsInterfaceDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsInterfaceDeclaration1(TypescriptTsInterfaceDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsInternalModule(TypescriptTsExpression, TypescriptTsDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptIntersectionType(AST):
    pass


class TypescriptTsIntersectionType(TypescriptTsPrimaryType, TypescriptIntersectionType, AST):
    pass


class TypescriptTsIntersectionType0(TypescriptTsIntersectionType, AST):
    pass


class TypescriptTsIntersectionType1(TypescriptTsIntersectionType, AST):
    pass


class TypescriptTsIs(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsJsxAttribute(TypescriptTsAST, AST):
    pass


class TypescriptTsJsxAttribute0(TypescriptTsJsxAttribute, AST):
    pass


class TypescriptTsJsxAttribute1(TypescriptTsJsxAttribute, AST):
    pass


class TypescriptTsJsxAttribute2(TypescriptTsJsxAttribute, AST):
    pass


class TypescriptTsJsxAttribute3(TypescriptTsJsxAttribute, AST):
    pass


class TypescriptTsJsxAttribute4(TypescriptTsJsxAttribute, AST):
    pass


class TypescriptTsJsxAttribute5(TypescriptTsJsxAttribute, AST):
    pass


class TypescriptTsJsxClosingElement(TypescriptTsAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class TypescriptTsJsxElement(TypescriptTsAST, AST):
        @cached_property
        def open_tag(self) -> AST:
            return self.child_slot("OPEN-TAG")

        @cached_property
        def close_tag(self) -> AST:
            return self.child_slot("CLOSE-TAG")


class TypescriptTsJsxExpression(TypescriptTsAST, AST):
    pass


class TypescriptTsJsxExpression0(TypescriptTsJsxExpression, AST):
    pass


class TypescriptTsJsxExpression1(TypescriptTsJsxExpression, AST):
    pass


class TypescriptTsJsxFragment(TypescriptTsAST, AST):
    pass


class TypescriptTsJsxNamespaceName(TypescriptTsAST, AST):
    pass


class TypescriptTsJsxOpeningElement(TypescriptTsAST, AST):
    pass


class TypescriptTsJsxOpeningElement0(TypescriptTsJsxOpeningElement, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def attribute(self) -> List[AST]:
            return self.child_slot("ATTRIBUTE")


class TypescriptTsJsxOpeningElement1(TypescriptTsJsxOpeningElement, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def attribute(self) -> List[AST]:
            return self.child_slot("ATTRIBUTE")


class TypescriptTsJsxSelfClosingElement(TypescriptTsAST, AST):
    pass


class TypescriptTsJsxSelfClosingElement0(TypescriptTsJsxSelfClosingElement, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def attribute(self) -> List[AST]:
            return self.child_slot("ATTRIBUTE")


class TypescriptTsJsxSelfClosingElement1(TypescriptTsJsxSelfClosingElement, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def attribute(self) -> List[AST]:
            return self.child_slot("ATTRIBUTE")


class TypescriptTsJsxText(TypescriptTsAST, AST):
    pass


class TypescriptTsKeyof(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsLabeledStatement(TypescriptTsStatement, AST):
        @cached_property
        def label(self) -> AST:
            return self.child_slot("LABEL")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsLet(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsLexicalDeclaration(TypescriptTsDeclaration, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptLiteralType(AST):
    pass


class TypescriptTsLiteralType(TypescriptTsPrimaryType, TypescriptLiteralType, AST):
    pass


class TypescriptTsLiteralType0(TypescriptTsLiteralType, AST):
    pass


class TypescriptTsLiteralType1(TypescriptTsLiteralType, AST):
    pass


class TypescriptTsLookupType(TypescriptTsPrimaryType, AST):
    pass


class TypescriptTsMappedTypeClause(TypescriptTsAST, AST):
    pass


class TypescriptTsMappedTypeClause0(TypescriptTsMappedTypeClause, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def alias(self) -> AST:
            return self.child_slot("ALIAS")


class TypescriptTsMappedTypeClause1(TypescriptTsMappedTypeClause, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def alias(self) -> AST:
            return self.child_slot("ALIAS")


class TypescriptTsMemberExpression(TypescriptTsPattern, TypescriptTsPrimaryExpression, ECMAMemberExpression, AST):
    pass


class TypescriptTsMemberExpression0(TypescriptTsMemberExpression, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def property(self) -> AST:
            return self.child_slot("PROPERTY")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class TypescriptTsMemberExpression1(TypescriptTsMemberExpression, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def property(self) -> AST:
            return self.child_slot("PROPERTY")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class TypescriptTsMetaProperty(TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsMethodDefinition(TypescriptTsAST, AST):
    pass


class TypescriptTsMethodDefinition0(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition1(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition10(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition11(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition12(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition13(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition14(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition15(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition2(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition3(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition4(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition5(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition6(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition7(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition8(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodDefinition9(TypescriptTsMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_ts_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TS-ASYNC")


class TypescriptTsMethodSignature(TypescriptTsAST, AST):
    pass


class TypescriptTsMethodSignature0(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature1(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature10(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature11(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature12(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature13(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature14(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature15(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature16(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature17(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature18(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature19(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature2(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature20(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature21(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature22(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature23(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature24(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature25(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature26(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature27(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature28(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature29(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature3(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature30(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature31(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature32(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature33(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature34(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature35(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature36(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature37(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature38(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature39(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature4(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature40(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature41(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature42(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature43(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature44(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature45(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature46(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature47(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature48(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature49(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature5(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature50(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature51(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature52(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature53(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature54(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature55(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature56(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature57(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature58(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature59(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature6(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature60(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature61(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature62(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature63(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature7(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature8(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsMethodSignature9(TypescriptTsMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsModule(TypescriptTsDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsModuleTerminal(TypescriptTsDeclaration, TerminalSymbol, AST):
    pass


class TypescriptTsNamedImports(TypescriptTsAST, AST):
    pass


class TypescriptTsNamedImports0(TypescriptTsNamedImports, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsNamedImports1(TypescriptTsNamedImports, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsNamedImports2(TypescriptTsNamedImports, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsNamedImports3(TypescriptTsNamedImports, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsNamespace(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsNamespaceExport(TypescriptTsAST, AST):
    pass


class TypescriptTsNamespaceImport(TypescriptTsAST, AST):
    pass


class TypescriptTsNamespaceImport0(TypescriptTsNamespaceImport, AST):
    pass


class TypescriptTsNamespaceImport1(TypescriptTsNamespaceImport, AST):
    pass


class TypescriptTsNestedIdentifier(TypescriptTsAST, AST):
    pass


class TypescriptTsNestedTypeIdentifier(TypescriptTsPrimaryType, AST):
        @cached_property
        def module(self) -> AST:
            return self.child_slot("MODULE")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class TypescriptTsNever(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsNew(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsNewExpression(TypescriptTsExpression, AST):
        @cached_property
        def constructor(self) -> AST:
            return self.child_slot("CONSTRUCTOR")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class TypescriptTsNonNullExpression(TypescriptTsPattern, TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsNull(TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsNumber(TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsObject(TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsObject0(TypescriptTsObject, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsObject1(TypescriptTsObject, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsObject2(TypescriptTsObject, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsObject3(TypescriptTsObject, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsObjectAssignmentPattern(TypescriptTsAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class TypescriptTsObjectPattern(TypescriptTsPattern, AST):
    pass


class TypescriptTsObjectPattern0(TypescriptTsObjectPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsObjectPattern1(TypescriptTsObjectPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsObjectPattern2(TypescriptTsObjectPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsObjectPattern3(TypescriptTsObjectPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsObjectTerminal(TypescriptTsPrimaryExpression, TerminalSymbol, AST):
    pass


class TypescriptObjectType(AST):
    pass


class TypescriptTsObjectType(TypescriptTsPrimaryType, TypescriptObjectType, AST):
    pass


class TypescriptTsObjectType0(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType1(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType10(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType11(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType12(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType13(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType14(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType15(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType16(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType17(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType18(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType19(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType2(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType3(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType4(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType5(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType6(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType7(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType8(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsObjectType9(TypescriptTsObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsOf(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsOmittingTypeAnnotation(TypescriptTsAST, AST):
    pass


class TypescriptTsOptingTypeAnnotation(TypescriptTsAST, AST):
    pass


class TypescriptParameter(AST):
    pass


class TypescriptOptionalParameter(AST):
    pass


class TypescriptTsOptionalParameter(TypescriptTsAST, TypescriptOptionalParameter, TypescriptParameter, ParameterAST, AST):
    pass


class TypescriptTsOptionalParameter0(TypescriptTsOptionalParameter, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def pattern(self) -> AST:
            return self.child_slot("PATTERN")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def modifiers(self) -> List[AST]:
            return self.child_slot("MODIFIERS")


class TypescriptTsOptionalParameter1(TypescriptTsOptionalParameter, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def pattern(self) -> AST:
            return self.child_slot("PATTERN")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def modifiers(self) -> List[AST]:
            return self.child_slot("MODIFIERS")


class TypescriptTsOptionalType(TypescriptTsAST, AST):
    pass


class TypescriptTsOverride(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsOverrideModifier(TypescriptTsAST, AST):
    pass


class TypescriptTsPair(TypescriptTsAST, AST):
        @cached_property
        def key(self) -> AST:
            return self.child_slot("KEY")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class TypescriptTsPairPattern(TypescriptTsAST, AST):
        @cached_property
        def key(self) -> AST:
            return self.child_slot("KEY")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class TypescriptTsParenthesizedExpression(TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsParenthesizedExpression0(TypescriptTsParenthesizedExpression, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsParenthesizedExpression1(TypescriptTsParenthesizedExpression, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsParenthesizedType(TypescriptTsPrimaryType, AST):
    pass


class TypescriptPredefinedType(AST):
    pass


class TypescriptTsPredefinedType(TypescriptTsPrimaryType, TypescriptPredefinedType, AST):
    pass


class TypescriptTsPrivate(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsPrivatePropertyIdentifier(TypescriptTsAST, AST):
    pass


class TypescriptProgram(AST):
    pass


class TypescriptTsProgram(TypescriptTsAST, TypescriptProgram, RootAST, AST):
    pass


class TypescriptTsProgram0(TypescriptTsProgram, AST):
    pass


class TypescriptTsProgram1(TypescriptTsProgram, AST):
    pass


class TypescriptPropertyIdentifier(AST):
    pass


class TypescriptTsPropertyIdentifier(TypescriptTsAST, TypescriptPropertyIdentifier, IdentifierAST, AST):
    pass


class TypescriptPropertySignature(AST):
    pass


class TypescriptTsPropertySignature(TypescriptTsAST, TypescriptPropertySignature, AST):
    pass


class TypescriptTsPropertySignature0(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature1(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature10(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature11(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature12(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature13(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature14(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature15(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature2(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature3(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature4(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature5(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature6(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature7(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature8(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPropertySignature9(TypescriptTsPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsProtected(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsPublic(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsPublicFieldDefinition(TypescriptTsAST, AST):
    pass


class TypescriptTsPublicFieldDefinition0(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition1(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition10(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition11(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition12(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition13(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition14(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition15(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition16(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition17(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition18(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition19(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition2(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition20(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition21(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition22(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition23(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition24(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition25(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition26(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition27(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition28(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition29(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition3(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition30(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition31(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition32(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition33(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition34(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition35(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition36(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition37(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition38(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition39(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition4(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition40(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition41(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition42(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition43(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition44(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition45(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition46(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition47(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition5(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition6(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition7(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition8(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsPublicFieldDefinition9(TypescriptTsPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsReadonly(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsReadonlyType(TypescriptTsAST, AST):
    pass


class TypescriptTsRegex(TypescriptTsPrimaryExpression, AST):
        @cached_property
        def pattern(self) -> AST:
            return self.child_slot("PATTERN")

        @cached_property
        def flags(self) -> AST:
            return self.child_slot("FLAGS")


class TypescriptTsRegexFlags(TypescriptTsAST, AST):
    pass


class TypescriptTsRegexPattern(TypescriptTsAST, AST):
    pass


class TypescriptTsRequire(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptRequiredParameter(AST):
    pass


class TypescriptTsRequiredParameter(TypescriptTsAST, TypescriptRequiredParameter, TypescriptParameter, ParameterAST, AST):
    pass


class TypescriptTsRequiredParameter0(TypescriptTsRequiredParameter, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def pattern(self) -> AST:
            return self.child_slot("PATTERN")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def modifiers(self) -> List[AST]:
            return self.child_slot("MODIFIERS")


class TypescriptTsRequiredParameter1(TypescriptTsRequiredParameter, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def pattern(self) -> AST:
            return self.child_slot("PATTERN")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def modifiers(self) -> List[AST]:
            return self.child_slot("MODIFIERS")


class TypescriptRestPattern(AST):
    pass


class TypescriptTsRestPattern(TypescriptTsPattern, TypescriptRestPattern, ECMARestPattern, AST):
    pass


class TypescriptTsRestPattern0(TypescriptTsRestPattern, AST):
    pass


class TypescriptTsRestPattern1(TypescriptTsRestPattern, AST):
    pass


class TypescriptTsRestPattern2(TypescriptTsRestPattern, AST):
    pass


class TypescriptTsRestPattern3(TypescriptTsRestPattern, AST):
    pass


class TypescriptTsRestType(TypescriptTsAST, AST):
    pass


class TypescriptTsReturn(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsReturnStatement(TypescriptTsStatement, ReturnAST, AST):
    pass


class TypescriptTsReturnStatement0(TypescriptTsReturnStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsReturnStatement1(TypescriptTsReturnStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsSequenceExpression(TypescriptTsAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsSet(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsShorthandPropertyIdentifier(TypescriptTsAST, IdentifierAST, AST):
    pass


class TypescriptTsShorthandPropertyIdentifierPattern(TypescriptTsAST, IdentifierAST, AST):
    pass


class TypescriptTsSourceTextFragment(TypescriptTsAST, SourceTextFragment, AST):
    pass


class TypescriptTsSpreadElement(TypescriptTsAST, AST):
    pass


class TypescriptTsStatementBlock(TypescriptTsStatement, AST):
    pass


class TypescriptTsStatementIdentifier(TypescriptTsAST, AST):
    pass


class TypescriptTsStatic(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsString(TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsString0(TypescriptTsString, AST):
    pass


class TypescriptTsString1(TypescriptTsString, AST):
    pass


class TypescriptTsStringFragment(TypescriptTsAST, AST):
    pass


class TypescriptTsStringTerminal(TypescriptTsPrimaryExpression, TerminalSymbol, AST):
    pass


class TypescriptTsSubscriptExpression(TypescriptTsPattern, TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsSubscriptExpression0(TypescriptTsSubscriptExpression, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def index(self) -> AST:
            return self.child_slot("INDEX")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class TypescriptTsSubscriptExpression1(TypescriptTsSubscriptExpression, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def index(self) -> AST:
            return self.child_slot("INDEX")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class TypescriptTsSuper(TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsSwitch(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsSwitchBody(TypescriptTsAST, AST):
    pass


class TypescriptTsSwitchCase(TypescriptTsAST, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def body(self) -> List[AST]:
            return self.child_slot("BODY")


class TypescriptTsSwitchDefault(TypescriptTsAST, AST):
        @cached_property
        def body(self) -> List[AST]:
            return self.child_slot("BODY")


class TypescriptTsSwitchStatement(TypescriptTsStatement, ControlFlowAST, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsSymbol(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsTarget(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsTemplateLiteralType(TypescriptTsPrimaryType, AST):
    pass


class TypescriptTsTemplateString(TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsTemplateSubstitution(TypescriptTsAST, AST):
    pass


class TypescriptTsTemplateType(TypescriptTsAST, AST):
    pass


class TypescriptTsTernaryExpression(TypescriptTsExpression, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class TypescriptTsThis(TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptTsThisType(TypescriptTsPrimaryType, AST):
    pass


class TypescriptTsThrow(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsThrowStatement(TypescriptTsStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsTrue(TypescriptTsPrimaryExpression, BooleanTrueAST, AST):
    pass


class TypescriptTsTry(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsTryStatement(TypescriptTsStatement, AST):
    pass


class TypescriptTsTryStatement0(TypescriptTsTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def handler(self) -> AST:
            return self.child_slot("HANDLER")

        @cached_property
        def finalizer(self) -> AST:
            return self.child_slot("FINALIZER")


class TypescriptTsTryStatement1(TypescriptTsTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def handler(self) -> AST:
            return self.child_slot("HANDLER")

        @cached_property
        def finalizer(self) -> AST:
            return self.child_slot("FINALIZER")


class TypescriptTsTryStatement2(TypescriptTsTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def handler(self) -> AST:
            return self.child_slot("HANDLER")

        @cached_property
        def finalizer(self) -> AST:
            return self.child_slot("FINALIZER")


class TypescriptTsTryStatement3(TypescriptTsTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def handler(self) -> AST:
            return self.child_slot("HANDLER")

        @cached_property
        def finalizer(self) -> AST:
            return self.child_slot("FINALIZER")


class TypescriptTupleType(AST):
    pass


class TypescriptTsTupleType(TypescriptTsPrimaryType, TypescriptTupleType, AST):
    pass


class TypescriptTsTupleType0(TypescriptTsTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsTupleType1(TypescriptTsTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsTupleType2(TypescriptTsTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsTupleType3(TypescriptTsTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsTupleType4(TypescriptTsTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsTupleType5(TypescriptTsTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsTupleType6(TypescriptTsTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsTupleType7(TypescriptTsTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsTupleType8(TypescriptTsTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsTupleType9(TypescriptTsTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsType(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsTypeAliasDeclaration(TypescriptTsDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTypeAnnotation(AST):
    pass


class TypescriptTsTypeAnnotation(TypescriptTsAST, TypescriptTypeAnnotation, AST):
    pass


class TypescriptTypeArguments(AST):
    pass


class TypescriptTsTypeArguments(TypescriptTsAST, TypescriptTypeArguments, AST):
    pass


class TypescriptTsTypeArguments0(TypescriptTsTypeArguments, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsTypeArguments1(TypescriptTsTypeArguments, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsTypeAssertion(TypescriptTsExpression, AST):
    pass


class TypescriptTypeIdentifier(AST):
    pass


class TypescriptTsTypeIdentifier(TypescriptTsPrimaryType, TypeIdentifierAST, TypescriptTypeIdentifier, AST):
    pass


class TypescriptTsTypeParameter(TypescriptTsAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def constraint(self) -> AST:
            return self.child_slot("CONSTRAINT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class TypescriptTsTypeParameters(TypescriptTsAST, AST):
    pass


class TypescriptTsTypeParameters0(TypescriptTsTypeParameters, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsTypeParameters1(TypescriptTsTypeParameters, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsTypePredicate(TypescriptTsAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsTypePredicateAnnotation(TypescriptTsAST, AST):
    pass


class TypescriptTsTypeQuery(TypescriptTsPrimaryType, AST):
    pass


class TypescriptTsTypeQuery0(TypescriptTsTypeQuery, AST):
    pass


class TypescriptTsTypeQuery1(TypescriptTsTypeQuery, AST):
    pass


class TypescriptTsTypeQuery2(TypescriptTsTypeQuery, AST):
    pass


class TypescriptTsTypeQuery3(TypescriptTsTypeQuery, AST):
    pass


class TypescriptTsTypeof(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsUnaryExpression(TypescriptTsExpression, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class TypescriptTsUndefined(TypescriptTsPattern, TypescriptTsPrimaryExpression, AST):
    pass


class TypescriptUnionType(AST):
    pass


class TypescriptTsUnionType(TypescriptTsPrimaryType, TypescriptUnionType, AST):
    pass


class TypescriptTsUnionType0(TypescriptTsUnionType, AST):
    pass


class TypescriptTsUnionType1(TypescriptTsUnionType, AST):
    pass


class TypescriptTsUnknown(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsUpdateExpression(TypescriptTsExpression, AssignmentAST, AST):
    pass


class TypescriptTsUpdateExpression0(TypescriptTsUpdateExpression, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class TypescriptTsUpdateExpression1(TypescriptTsUpdateExpression, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class TypescriptTsVar(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsVariableDeclaration(TypescriptTsDeclaration, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptVariableDeclarator(AST):
    pass


class TypescriptTsVariableDeclarator(TypescriptTsAST, TypescriptVariableDeclarator, ECMAVariableDeclarator, AST):
    pass


class TypescriptTsVariableDeclarator0(TypescriptTsVariableDeclarator, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class TypescriptTsVariableDeclarator1(TypescriptTsVariableDeclarator, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class TypescriptTsVoid(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsWhile(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsWhileStatement(TypescriptTsStatement, ControlFlowAST, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsWith(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsWithStatement(TypescriptTsStatement, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsYield(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsYieldExpression(TypescriptTsExpression, AST):
    pass


class TypescriptTsYieldExpression0(TypescriptTsYieldExpression, AST):
    pass


class TypescriptTsYieldExpression1(TypescriptTsYieldExpression, AST):
    pass


class TypescriptTsYieldExpression2(TypescriptTsYieldExpression, AST):
    pass


class TypescriptTsOpenBracket(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsCloseBracket(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBitwiseXor(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBitwiseXorAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBackQuote(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsOpenBrace(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsObjectTypeOpen(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBitwiseOr(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBitwiseOrAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsLogicalOr(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsLogicalOrAssign(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsObjectTypeClose(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsCloseBrace(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsBitwiseNot(TypescriptTsAST, TerminalSymbol, AST):
    pass


class TypescriptTsxAST(TypescriptAST, AST):
    pass


class TypescriptTsxLogicalNot(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxNotEqual(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxStrictlyNotEqual(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxDoubleQuote(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxOpenTemplateLiteral(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxModulo(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxModuleAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBitwiseAnd(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxLogicalAnd(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxLogicalAndAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBitwiseAndAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxSingleQuote(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxOpenParenthesis(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxCloseParenthesis(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxMultiply(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxPow(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxPowAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxMultiplyAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxAdd(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxIncrement(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxAddAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxComma(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxSubtract(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxDecrement(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxSubtractAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxOmittingTypeTerminal(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxAutomaticSemicolon(TypescriptTsxAST, AST):
    pass


class TypescriptTsxFunctionSignatureAutomaticSemicolon(TypescriptTsxAST, AST):
    pass


class TypescriptTsxPrimaryType(TypescriptTsxAST, AST):
    pass


class TypescriptTsxTemplateChars(TypescriptTsxAST, AST):
    pass


class TypescriptTsxTernaryQmark(TypescriptTsxAST, AST):
    pass


class TypescriptTsxDot(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxEllipsis(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxDivide(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxDivideAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxColon(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxSemicolon(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxLessThan(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBitshiftLeft(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBitshiftLeftAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxLessThanOrEqual(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxEqual(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxStrictlyEqual(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxArrow(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxGreaterThan(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxGreaterThanOrEqual(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBitshiftRight(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBitshiftRightAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxUnsignedBitshiftRight(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxUnsignedBitshiftRightAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxQuestion(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxChaining(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxOptingTypeTerminal(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxNullishCoalescing(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxNullishCoalescingAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxMatrixMultiply(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxAbstract(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxStatement(TypescriptTsxAST, AST):
    pass


class TypescriptTsxDeclaration(TypescriptTsxStatement, AST):
    pass


class TypescriptTsxAbstractClassDeclaration(TypescriptTsxDeclaration, AST):
    pass


class TypescriptTsxAbstractClassDeclaration0(TypescriptTsxAbstractClassDeclaration, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxAbstractClassDeclaration1(TypescriptTsxAbstractClassDeclaration, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxAbstractMethodSignature(TypescriptTsxAST, AST):
    pass


class TypescriptTsxAbstractMethodSignature0(TypescriptTsxAbstractMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxAbstractMethodSignature1(TypescriptTsxAbstractMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxAbstractMethodSignature2(TypescriptTsxAbstractMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxAbstractMethodSignature3(TypescriptTsxAbstractMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxAccessibilityModifier(TypescriptTsxAST, AST):
    pass


class TypescriptTsxAmbientDeclaration(TypescriptTsxDeclaration, AST):
    pass


class TypescriptTsxAmbientDeclaration0(TypescriptTsxAmbientDeclaration, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxAmbientDeclaration1(TypescriptTsxAmbientDeclaration, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxAmbientDeclaration2(TypescriptTsxAmbientDeclaration, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxAny(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxArguments(TypescriptTsxAST, ECMAArguments, AST):
    pass


class TypescriptTsxArguments0(TypescriptTsxArguments, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxArguments1(TypescriptTsxArguments, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxArguments2(TypescriptTsxArguments, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxExpression(TypescriptTsxAST, AST):
    pass


class TypescriptTsxPrimaryExpression(TypescriptTsxExpression, AST):
    pass


class TypescriptTsxArray(TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxArray0(TypescriptTsxArray, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxArray1(TypescriptTsxArray, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxArray2(TypescriptTsxArray, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxPattern(TypescriptTsxAST, AST):
    pass


class TypescriptTsxArrayPattern(TypescriptTsxPattern, AST):
    pass


class TypescriptTsxArrayPattern0(TypescriptTsxArrayPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxArrayPattern1(TypescriptTsxArrayPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxArrayPattern2(TypescriptTsxArrayPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxArrayType(TypescriptTsxPrimaryType, TypescriptArrayType, AST):
    pass


class TypescriptTsxArrowFunction(TypescriptTsxPrimaryExpression, LambdaAST, AST):
    pass


class TypescriptTsxArrowFunction0(TypescriptTsxArrowFunction, AST):
        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxArrowFunction1(TypescriptTsxArrowFunction, AST):
        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxAs(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxAsExpression(TypescriptTsxExpression, AST):
    pass


class TypescriptTsxAsExpression0(TypescriptTsxAsExpression, AST):
    pass


class TypescriptTsxAsExpression1(TypescriptTsxAsExpression, AST):
    pass


class TypescriptTsxAsserts(TypescriptTsxAST, AST):
    pass


class TypescriptTsxAssertsTerminal(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxAssignmentExpression(TypescriptTsxExpression, TypescriptAssignmentExpression, AssignmentAST, ECMAAssignmentExpression, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class TypescriptTsxAssignmentPattern(TypescriptTsxAST, TypescriptAssignmentPattern, AssignmentAST, ECMAAssignmentPattern, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class TypescriptTsxAsync(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxAugmentedAssignmentExpression(TypescriptTsxExpression, AssignmentAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class TypescriptTsxAwait(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxAwaitExpression(TypescriptTsxExpression, AST):
    pass


class TypescriptTsxBinaryExpression(TypescriptTsxExpression, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class TypescriptTsxBoolean(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBreak(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBreakStatement(TypescriptTsxStatement, AST):
        @cached_property
        def label(self) -> AST:
            return self.child_slot("LABEL")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxCallExpression(TypescriptTsxPrimaryExpression, CallAST, ECMACallExpression, AST):
    pass


class TypescriptTsxCallExpression0(TypescriptTsxCallExpression, AST):
        @cached_property
        def function(self) -> AST:
            return self.child_slot("FUNCTION")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class TypescriptTsxCallExpression1(TypescriptTsxCallExpression, AST):
        @cached_property
        def function(self) -> AST:
            return self.child_slot("FUNCTION")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class TypescriptTsxCallSignature(TypescriptTsxAST, AST):
        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")


class TypescriptTsxCase(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxCatch(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxCatchClause(TypescriptTsxAST, AST):
    pass


class TypescriptTsxCatchClause0(TypescriptTsxCatchClause, AST):
        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxCatchClause1(TypescriptTsxCatchClause, AST):
        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxCatchClause2(TypescriptTsxCatchClause, AST):
        @cached_property
        def parameter(self) -> AST:
            return self.child_slot("PARAMETER")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxClass(TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxClass0(TypescriptTsxClass, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxClass1(TypescriptTsxClass, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxClassBody(TypescriptTsxAST, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxClassDeclaration(TypescriptTsxDeclaration, ClassAST, AST):
    pass


class TypescriptTsxClassDeclaration0(TypescriptTsxClassDeclaration, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxClassDeclaration1(TypescriptTsxClassDeclaration, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxClassHeritage(TypescriptTsxAST, AST):
    pass


class TypescriptTsxClassHeritage0(TypescriptTsxClassHeritage, AST):
    pass


class TypescriptTsxClassHeritage1(TypescriptTsxClassHeritage, AST):
    pass


class TypescriptTsxClassTerminal(TypescriptTsxPrimaryExpression, TerminalSymbol, AST):
    pass


class TypescriptTsxComment(TypescriptTsxAST, ECMAComment, AST):
    pass


class TypescriptTsxComputedPropertyName(TypescriptTsxAST, AST):
    pass


class TypescriptTsxConditionalType(TypescriptTsxPrimaryType, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class TypescriptTsxConst(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxConstraint(TypescriptTsxAST, AST):
    pass


class TypescriptTsxConstructSignature(TypescriptTsxAST, AST):
        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsxConstructorType(TypescriptTsxAST, AST):
        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsxContinue(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxContinueStatement(TypescriptTsxStatement, AST):
        @cached_property
        def label(self) -> AST:
            return self.child_slot("LABEL")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxDebugger(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxDebuggerStatement(TypescriptTsxStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxDeclare(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxDecorator(TypescriptTsxAST, AST):
    pass


class TypescriptTsxDecorator0(TypescriptTsxDecorator, AST):
    pass


class TypescriptTsxDecorator1(TypescriptTsxDecorator, AST):
    pass


class TypescriptTsxDecorator2(TypescriptTsxDecorator, AST):
    pass


class TypescriptTsxDefault(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxDefaultType(TypescriptTsxAST, AST):
    pass


class TypescriptTsxDelete(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxDo(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxDoStatement(TypescriptTsxStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxElse(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxElseClause(TypescriptTsxAST, AST):
    pass


class TypescriptTsxEmptyStatement(TypescriptTsxStatement, AST):
    pass


class TypescriptTsxEnum(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxEnumAssignment(TypescriptTsxAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class TypescriptTsxEnumBody(TypescriptTsxAST, AST):
    pass


class TypescriptTsxEnumBody0(TypescriptTsxEnumBody, AST):
        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxEnumBody1(TypescriptTsxEnumBody, AST):
        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxEnumBody2(TypescriptTsxEnumBody, AST):
        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxEnumBody3(TypescriptTsxEnumBody, AST):
        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxEnumBody4(TypescriptTsxEnumBody, AST):
        @cached_property
        def name(self) -> List[AST]:
            return self.child_slot("NAME")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxEnumDeclaration(TypescriptTsxDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")


class TypescriptTsxError(TypescriptTsxAST, ECMAError, ParseErrorAST, AST):
    pass


class TypescriptTsxEscapeSequence(TypescriptTsxAST, AST):
    pass


class TypescriptTsxExistentialType(TypescriptTsxPrimaryType, AST):
    pass


class TypescriptTsxExport(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxExportClause(TypescriptTsxAST, AST):
    pass


class TypescriptTsxExportClause0(TypescriptTsxExportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxExportClause1(TypescriptTsxExportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxExportClause2(TypescriptTsxExportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxExportClause3(TypescriptTsxExportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxExportSpecifier(TypescriptTsxAST, AST):
    pass


class TypescriptTsxExportSpecifier0(TypescriptTsxExportSpecifier, AST):
    pass


class TypescriptTsxExportSpecifier1(TypescriptTsxExportSpecifier, AST):
    pass


class TypescriptTsxExportStatement(TypescriptTsxStatement, AST):
    pass


class TypescriptTsxExportStatement0(TypescriptTsxExportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declaration(self) -> AST:
            return self.child_slot("DECLARATION")

        @cached_property
        def default(self) -> AST:
            return self.child_slot("DEFAULT")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxExportStatement1(TypescriptTsxExportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declaration(self) -> AST:
            return self.child_slot("DECLARATION")

        @cached_property
        def default(self) -> AST:
            return self.child_slot("DEFAULT")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxExportStatement2(TypescriptTsxExportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declaration(self) -> AST:
            return self.child_slot("DECLARATION")

        @cached_property
        def default(self) -> AST:
            return self.child_slot("DEFAULT")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxExpressionStatement(TypescriptTsxStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxExtends(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxExtendsClause(TypescriptTsxAST, AST):
        @cached_property
        def type_arguments(self) -> List[AST]:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def value(self) -> List[AST]:
            return self.child_slot("VALUE")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxExtendsTypeClause(TypescriptTsxAST, AST):
        @cached_property
        def type(self) -> List[AST]:
            return self.child_slot("TYPE")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxFalse(TypescriptTsxPrimaryExpression, BooleanFalseAST, AST):
    pass


class TypescriptTsxFinally(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxFinallyClause(TypescriptTsxAST, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxFlowMaybeType(TypescriptTsxPrimaryType, TypescriptFlowMaybeType, AST):
    pass


class TypescriptTsxFor(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxForInStatement(TypescriptTsxStatement, AST):
    pass


class TypescriptTsxForInStatement0(TypescriptTsxForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxForInStatement1(TypescriptTsxForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxForInStatement2(TypescriptTsxForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxForInStatement3(TypescriptTsxForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxForInStatement4(TypescriptTsxForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxForInStatement5(TypescriptTsxForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxForInStatement6(TypescriptTsxForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxForInStatement7(TypescriptTsxForInStatement, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxForStatement(TypescriptTsxStatement, AST):
        @cached_property
        def initializer(self) -> AST:
            return self.child_slot("INITIALIZER")

        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def increment(self) -> AST:
            return self.child_slot("INCREMENT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxFormalParameters(TypescriptTsxAST, AST):
    pass


class TypescriptTsxFormalParameters0(TypescriptTsxFormalParameters, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxFormalParameters1(TypescriptTsxFormalParameters, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxFormalParameters2(TypescriptTsxFormalParameters, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxFrom(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxFunction(TypescriptTsxPrimaryExpression, FunctionAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxFunctionDeclaration(TypescriptTsxDeclaration, TypescriptFunctionDeclaration, FunctionDeclarationAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxFunctionSignature(TypescriptTsxDeclaration, TypescriptFunctionSignature, FunctionDeclarationAST, AST):
    pass


class TypescriptTsxFunctionSignature0(TypescriptTsxFunctionSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxFunctionSignature1(TypescriptTsxFunctionSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxFunctionTerminal(TypescriptTsxPrimaryExpression, FunctionAST, TerminalSymbol, AST):
    pass


class TypescriptTsxFunctionType(TypescriptTsxAST, AST):
        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")


class TypescriptTsxGeneratorFunction(TypescriptTsxPrimaryExpression, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxGeneratorFunctionDeclaration(TypescriptTsxDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxGenericType(TypescriptTsxPrimaryType, TypescriptGenericType, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")


class TypescriptTsxGet(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxGlobal(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxHashBangLine(TypescriptTsxAST, AST):
    pass


class TypescriptTsxIdentifier(TypescriptTsxPattern, TypescriptTsxPrimaryExpression, TypescriptIdentifier, IdentifierAST, AST):
    pass


class TypescriptTsxIf(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxIfStatement(TypescriptTsxStatement, AST):
    pass


class TypescriptTsxIfStatement0(TypescriptTsxIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class TypescriptTsxIfStatement1(TypescriptTsxIfStatement, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class TypescriptTsxImplements(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxImplementsClause(TypescriptTsxAST, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxImport(TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxImportAlias(TypescriptTsxDeclaration, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxImportClause(TypescriptTsxAST, AST):
    pass


class TypescriptTsxImportClause0(TypescriptTsxImportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxImportClause1(TypescriptTsxImportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxImportClause2(TypescriptTsxImportClause, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxImportRequireClause(TypescriptTsxAST, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")


class TypescriptTsxImportSpecifier(TypescriptTsxAST, AST):
    pass


class TypescriptTsxImportSpecifier0(TypescriptTsxImportSpecifier, AST):
    pass


class TypescriptTsxImportSpecifier1(TypescriptTsxImportSpecifier, AST):
    pass


class TypescriptTsxImportStatement(TypescriptTsxStatement, AST):
    pass


class TypescriptTsxImportStatement0(TypescriptTsxImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxImportStatement1(TypescriptTsxImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxImportStatement2(TypescriptTsxImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxImportStatement3(TypescriptTsxImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxImportStatement4(TypescriptTsxImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxImportStatement5(TypescriptTsxImportStatement, AST):
        @cached_property
        def source(self) -> AST:
            return self.child_slot("SOURCE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxImportTerminal(TypescriptTsxPrimaryExpression, TerminalSymbol, AST):
    pass


class TypescriptTsxIn(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxIndexSignature(TypescriptTsxAST, TypescriptIndexSignature, AST):
    pass


class TypescriptTsxIndexSignature0(TypescriptTsxIndexSignature, AST):
        @cached_property
        def sign(self) -> AST:
            return self.child_slot("SIGN")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def index_type(self) -> AST:
            return self.child_slot("INDEX-TYPE")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsxIndexSignature1(TypescriptTsxIndexSignature, AST):
        @cached_property
        def sign(self) -> AST:
            return self.child_slot("SIGN")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def index_type(self) -> AST:
            return self.child_slot("INDEX-TYPE")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsxIndexSignature2(TypescriptTsxIndexSignature, AST):
        @cached_property
        def sign(self) -> AST:
            return self.child_slot("SIGN")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def index_type(self) -> AST:
            return self.child_slot("INDEX-TYPE")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsxIndexSignature3(TypescriptTsxIndexSignature, AST):
        @cached_property
        def sign(self) -> AST:
            return self.child_slot("SIGN")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def index_type(self) -> AST:
            return self.child_slot("INDEX-TYPE")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsxIndexTypeQuery(TypescriptTsxPrimaryType, AST):
    pass


class TypescriptTsxInfer(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxInferType(TypescriptTsxAST, AST):
    pass


class TypescriptTsxInnerWhitespace(TypescriptTsxAST, InnerWhitespace, AST):
    pass


class TypescriptTsxInstanceof(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxInterface(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxInterfaceDeclaration(TypescriptTsxDeclaration, AST):
    pass


class TypescriptTsxInterfaceDeclaration0(TypescriptTsxInterfaceDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxInterfaceDeclaration1(TypescriptTsxInterfaceDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxInternalModule(TypescriptTsxExpression, TypescriptTsxDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxIntersectionType(TypescriptTsxPrimaryType, TypescriptIntersectionType, AST):
    pass


class TypescriptTsxIntersectionType0(TypescriptTsxIntersectionType, AST):
    pass


class TypescriptTsxIntersectionType1(TypescriptTsxIntersectionType, AST):
    pass


class TypescriptTsxIs(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxJsxAttribute(TypescriptTsxAST, AST):
    pass


class TypescriptTsxJsxAttribute0(TypescriptTsxJsxAttribute, AST):
    pass


class TypescriptTsxJsxAttribute1(TypescriptTsxJsxAttribute, AST):
    pass


class TypescriptTsxJsxAttribute2(TypescriptTsxJsxAttribute, AST):
    pass


class TypescriptTsxJsxAttribute3(TypescriptTsxJsxAttribute, AST):
    pass


class TypescriptTsxJsxAttribute4(TypescriptTsxJsxAttribute, AST):
    pass


class TypescriptTsxJsxAttribute5(TypescriptTsxJsxAttribute, AST):
    pass


class TypescriptTsxJsxClosingElement(TypescriptTsxAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class TypescriptTsxJsxElement(TypescriptTsxExpression, AST):
        @cached_property
        def open_tag(self) -> AST:
            return self.child_slot("OPEN-TAG")

        @cached_property
        def close_tag(self) -> AST:
            return self.child_slot("CLOSE-TAG")


class TypescriptTsxJsxExpression(TypescriptTsxAST, AST):
    pass


class TypescriptTsxJsxExpression0(TypescriptTsxJsxExpression, AST):
    pass


class TypescriptTsxJsxExpression1(TypescriptTsxJsxExpression, AST):
    pass


class TypescriptTsxJsxFragment(TypescriptTsxExpression, AST):
    pass


class TypescriptTsxJsxNamespaceName(TypescriptTsxAST, AST):
    pass


class TypescriptTsxJsxOpeningElement(TypescriptTsxAST, AST):
    pass


class TypescriptTsxJsxOpeningElement0(TypescriptTsxJsxOpeningElement, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def attribute(self) -> List[AST]:
            return self.child_slot("ATTRIBUTE")


class TypescriptTsxJsxOpeningElement1(TypescriptTsxJsxOpeningElement, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def attribute(self) -> List[AST]:
            return self.child_slot("ATTRIBUTE")


class TypescriptTsxJsxSelfClosingElement(TypescriptTsxExpression, AST):
    pass


class TypescriptTsxJsxSelfClosingElement0(TypescriptTsxJsxSelfClosingElement, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def attribute(self) -> List[AST]:
            return self.child_slot("ATTRIBUTE")


class TypescriptTsxJsxSelfClosingElement1(TypescriptTsxJsxSelfClosingElement, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def attribute(self) -> List[AST]:
            return self.child_slot("ATTRIBUTE")


class TypescriptTsxJsxText(TypescriptTsxAST, AST):
    pass


class TypescriptTsxKeyof(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxLabeledStatement(TypescriptTsxStatement, AST):
        @cached_property
        def label(self) -> AST:
            return self.child_slot("LABEL")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxLet(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxLexicalDeclaration(TypescriptTsxDeclaration, AST):
        @cached_property
        def kind(self) -> AST:
            return self.child_slot("KIND")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxLiteralType(TypescriptTsxPrimaryType, TypescriptLiteralType, AST):
    pass


class TypescriptTsxLiteralType0(TypescriptTsxLiteralType, AST):
    pass


class TypescriptTsxLiteralType1(TypescriptTsxLiteralType, AST):
    pass


class TypescriptTsxLookupType(TypescriptTsxPrimaryType, AST):
    pass


class TypescriptTsxMappedTypeClause(TypescriptTsxAST, AST):
    pass


class TypescriptTsxMappedTypeClause0(TypescriptTsxMappedTypeClause, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def alias(self) -> AST:
            return self.child_slot("ALIAS")


class TypescriptTsxMappedTypeClause1(TypescriptTsxMappedTypeClause, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def alias(self) -> AST:
            return self.child_slot("ALIAS")


class TypescriptTsxMemberExpression(TypescriptTsxPattern, TypescriptTsxPrimaryExpression, ECMAMemberExpression, AST):
    pass


class TypescriptTsxMemberExpression0(TypescriptTsxMemberExpression, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def property(self) -> AST:
            return self.child_slot("PROPERTY")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class TypescriptTsxMemberExpression1(TypescriptTsxMemberExpression, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def property(self) -> AST:
            return self.child_slot("PROPERTY")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class TypescriptTsxMetaProperty(TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxMethodDefinition(TypescriptTsxAST, AST):
    pass


class TypescriptTsxMethodDefinition0(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition1(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition10(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition11(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition12(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition13(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition14(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition15(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition2(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition3(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition4(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition5(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition6(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition7(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition8(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodDefinition9(TypescriptTsxMethodDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")

        @cached_property
        def typescript_tsx_async(self) -> AST:
            return self.child_slot("TYPESCRIPT-TSX-ASYNC")


class TypescriptTsxMethodSignature(TypescriptTsxAST, AST):
    pass


class TypescriptTsxMethodSignature0(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature1(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature10(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature11(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature12(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature13(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature14(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature15(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature16(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature17(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature18(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature19(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature2(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature20(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature21(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature22(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature23(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature24(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature25(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature26(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature27(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature28(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature29(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature3(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature30(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature31(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature32(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature33(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature34(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature35(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature36(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature37(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature38(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature39(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature4(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature40(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature41(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature42(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature43(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature44(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature45(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature46(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature47(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature48(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature49(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature5(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature50(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature51(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature52(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature53(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature54(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature55(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature56(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature57(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature58(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature59(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature6(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature60(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature61(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature62(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature63(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature7(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature8(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxMethodSignature9(TypescriptTsxMethodSignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def parameters(self) -> AST:
            return self.child_slot("PARAMETERS")

        @cached_property
        def return_type(self) -> AST:
            return self.child_slot("RETURN-TYPE")

        @cached_property
        def getter_setter(self) -> AST:
            return self.child_slot("GETTER-SETTER")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxModule(TypescriptTsxDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxModuleTerminal(TypescriptTsxDeclaration, TerminalSymbol, AST):
    pass


class TypescriptTsxNamedImports(TypescriptTsxAST, AST):
    pass


class TypescriptTsxNamedImports0(TypescriptTsxNamedImports, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxNamedImports1(TypescriptTsxNamedImports, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxNamedImports2(TypescriptTsxNamedImports, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxNamedImports3(TypescriptTsxNamedImports, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxNamespace(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxNamespaceExport(TypescriptTsxAST, AST):
    pass


class TypescriptTsxNamespaceImport(TypescriptTsxAST, AST):
    pass


class TypescriptTsxNamespaceImport0(TypescriptTsxNamespaceImport, AST):
    pass


class TypescriptTsxNamespaceImport1(TypescriptTsxNamespaceImport, AST):
    pass


class TypescriptTsxNestedIdentifier(TypescriptTsxAST, AST):
    pass


class TypescriptTsxNestedTypeIdentifier(TypescriptTsxPrimaryType, AST):
        @cached_property
        def module(self) -> AST:
            return self.child_slot("MODULE")

        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")


class TypescriptTsxNever(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxNew(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxNewExpression(TypescriptTsxExpression, AST):
        @cached_property
        def constructor(self) -> AST:
            return self.child_slot("CONSTRUCTOR")

        @cached_property
        def type_arguments(self) -> AST:
            return self.child_slot("TYPE-ARGUMENTS")

        @cached_property
        def arguments(self) -> AST:
            return self.child_slot("ARGUMENTS")


class TypescriptTsxNonNullExpression(TypescriptTsxPattern, TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxNull(TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxNumber(TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxObject(TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxObject0(TypescriptTsxObject, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxObject1(TypescriptTsxObject, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxObject2(TypescriptTsxObject, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxObject3(TypescriptTsxObject, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxObjectAssignmentPattern(TypescriptTsxAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")


class TypescriptTsxObjectPattern(TypescriptTsxPattern, AST):
    pass


class TypescriptTsxObjectPattern0(TypescriptTsxObjectPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxObjectPattern1(TypescriptTsxObjectPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxObjectPattern2(TypescriptTsxObjectPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxObjectPattern3(TypescriptTsxObjectPattern, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxObjectTerminal(TypescriptTsxPrimaryExpression, TerminalSymbol, AST):
    pass


class TypescriptTsxObjectType(TypescriptTsxPrimaryType, TypescriptObjectType, AST):
    pass


class TypescriptTsxObjectType0(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType1(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType10(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType11(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType12(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType13(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType14(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType15(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType16(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType17(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType18(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType19(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType2(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType3(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType4(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType5(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType6(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType7(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType8(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxObjectType9(TypescriptTsxObjectType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxOf(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxOmittingTypeAnnotation(TypescriptTsxAST, AST):
    pass


class TypescriptTsxOptingTypeAnnotation(TypescriptTsxAST, AST):
    pass


class TypescriptTsxOptionalParameter(TypescriptTsxAST, TypescriptOptionalParameter, TypescriptParameter, ParameterAST, AST):
    pass


class TypescriptTsxOptionalParameter0(TypescriptTsxOptionalParameter, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def pattern(self) -> AST:
            return self.child_slot("PATTERN")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def modifiers(self) -> List[AST]:
            return self.child_slot("MODIFIERS")


class TypescriptTsxOptionalParameter1(TypescriptTsxOptionalParameter, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def pattern(self) -> AST:
            return self.child_slot("PATTERN")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def modifiers(self) -> List[AST]:
            return self.child_slot("MODIFIERS")


class TypescriptTsxOptionalType(TypescriptTsxAST, AST):
    pass


class TypescriptTsxOverride(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxOverrideModifier(TypescriptTsxAST, AST):
    pass


class TypescriptTsxPair(TypescriptTsxAST, AST):
        @cached_property
        def key(self) -> AST:
            return self.child_slot("KEY")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class TypescriptTsxPairPattern(TypescriptTsxAST, AST):
        @cached_property
        def key(self) -> AST:
            return self.child_slot("KEY")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class TypescriptTsxParenthesizedExpression(TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxParenthesizedExpression0(TypescriptTsxParenthesizedExpression, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsxParenthesizedExpression1(TypescriptTsxParenthesizedExpression, AST):
        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsxParenthesizedType(TypescriptTsxPrimaryType, AST):
    pass


class TypescriptTsxPredefinedType(TypescriptTsxPrimaryType, TypescriptPredefinedType, AST):
    pass


class TypescriptTsxPrivate(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxPrivatePropertyIdentifier(TypescriptTsxAST, AST):
    pass


class TypescriptTsxProgram(TypescriptTsxAST, TypescriptProgram, RootAST, AST):
    pass


class TypescriptTsxProgram0(TypescriptTsxProgram, AST):
    pass


class TypescriptTsxProgram1(TypescriptTsxProgram, AST):
    pass


class TypescriptTsxPropertyIdentifier(TypescriptTsxAST, TypescriptPropertyIdentifier, IdentifierAST, AST):
    pass


class TypescriptTsxPropertySignature(TypescriptTsxAST, TypescriptPropertySignature, AST):
    pass


class TypescriptTsxPropertySignature0(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature1(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature10(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature11(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature12(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature13(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature14(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature15(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature2(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature3(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature4(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature5(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature6(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature7(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature8(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPropertySignature9(TypescriptTsxPropertySignature, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxProtected(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxPublic(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxPublicFieldDefinition(TypescriptTsxAST, AST):
    pass


class TypescriptTsxPublicFieldDefinition0(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition1(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition10(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition11(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition12(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition13(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition14(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition15(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition16(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition17(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition18(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition19(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition2(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition20(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition21(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition22(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition23(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition24(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition25(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition26(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition27(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition28(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition29(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition3(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition30(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition31(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition32(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition33(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition34(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition35(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition36(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition37(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition38(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition39(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition4(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition40(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition41(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition42(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition43(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition44(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition45(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition46(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition47(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition5(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition6(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition7(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition8(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxPublicFieldDefinition9(TypescriptTsxPublicFieldDefinition, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def declare(self) -> AST:
            return self.child_slot("DECLARE")

        @cached_property
        def modifiers(self) -> AST:
            return self.child_slot("MODIFIERS")

        @cached_property
        def optional(self) -> AST:
            return self.child_slot("OPTIONAL")


class TypescriptTsxReadonly(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxReadonlyType(TypescriptTsxAST, AST):
    pass


class TypescriptTsxRegex(TypescriptTsxPrimaryExpression, AST):
        @cached_property
        def pattern(self) -> AST:
            return self.child_slot("PATTERN")

        @cached_property
        def flags(self) -> AST:
            return self.child_slot("FLAGS")


class TypescriptTsxRegexFlags(TypescriptTsxAST, AST):
    pass


class TypescriptTsxRegexPattern(TypescriptTsxAST, AST):
    pass


class TypescriptTsxRequire(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxRequiredParameter(TypescriptTsxAST, TypescriptRequiredParameter, TypescriptParameter, ParameterAST, AST):
    pass


class TypescriptTsxRequiredParameter0(TypescriptTsxRequiredParameter, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def pattern(self) -> AST:
            return self.child_slot("PATTERN")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def modifiers(self) -> List[AST]:
            return self.child_slot("MODIFIERS")


class TypescriptTsxRequiredParameter1(TypescriptTsxRequiredParameter, AST):
        @cached_property
        def decorator(self) -> List[AST]:
            return self.child_slot("DECORATOR")

        @cached_property
        def pattern(self) -> AST:
            return self.child_slot("PATTERN")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def modifiers(self) -> List[AST]:
            return self.child_slot("MODIFIERS")


class TypescriptTsxRestPattern(TypescriptTsxPattern, TypescriptRestPattern, ECMARestPattern, AST):
    pass


class TypescriptTsxRestPattern0(TypescriptTsxRestPattern, AST):
    pass


class TypescriptTsxRestPattern1(TypescriptTsxRestPattern, AST):
    pass


class TypescriptTsxRestPattern2(TypescriptTsxRestPattern, AST):
    pass


class TypescriptTsxRestPattern3(TypescriptTsxRestPattern, AST):
    pass


class TypescriptTsxRestType(TypescriptTsxAST, AST):
    pass


class TypescriptTsxReturn(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxReturnStatement(TypescriptTsxStatement, ReturnAST, AST):
    pass


class TypescriptTsxReturnStatement0(TypescriptTsxReturnStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxReturnStatement1(TypescriptTsxReturnStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxSequenceExpression(TypescriptTsxAST, AST):
        @cached_property
        def left(self) -> AST:
            return self.child_slot("LEFT")

        @cached_property
        def right(self) -> AST:
            return self.child_slot("RIGHT")

        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxSet(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxShorthandPropertyIdentifier(TypescriptTsxAST, IdentifierAST, AST):
    pass


class TypescriptTsxShorthandPropertyIdentifierPattern(TypescriptTsxAST, IdentifierAST, AST):
    pass


class TypescriptTsxSourceTextFragment(TypescriptTsxAST, SourceTextFragment, AST):
    pass


class TypescriptTsxSpreadElement(TypescriptTsxAST, AST):
    pass


class TypescriptTsxStatementBlock(TypescriptTsxStatement, AST):
    pass


class TypescriptTsxStatementIdentifier(TypescriptTsxAST, AST):
    pass


class TypescriptTsxStatic(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxString(TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxString0(TypescriptTsxString, AST):
    pass


class TypescriptTsxString1(TypescriptTsxString, AST):
    pass


class TypescriptTsxStringFragment(TypescriptTsxAST, AST):
    pass


class TypescriptTsxStringTerminal(TypescriptTsxPrimaryExpression, TerminalSymbol, AST):
    pass


class TypescriptTsxSubscriptExpression(TypescriptTsxPattern, TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxSubscriptExpression0(TypescriptTsxSubscriptExpression, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def index(self) -> AST:
            return self.child_slot("INDEX")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class TypescriptTsxSubscriptExpression1(TypescriptTsxSubscriptExpression, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def index(self) -> AST:
            return self.child_slot("INDEX")

        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")


class TypescriptTsxSuper(TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxSwitch(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxSwitchBody(TypescriptTsxAST, AST):
    pass


class TypescriptTsxSwitchCase(TypescriptTsxAST, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def body(self) -> List[AST]:
            return self.child_slot("BODY")


class TypescriptTsxSwitchDefault(TypescriptTsxAST, AST):
        @cached_property
        def body(self) -> List[AST]:
            return self.child_slot("BODY")


class TypescriptTsxSwitchStatement(TypescriptTsxStatement, ControlFlowAST, AST):
        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxSymbol(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxTarget(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxTemplateLiteralType(TypescriptTsxPrimaryType, AST):
    pass


class TypescriptTsxTemplateString(TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxTemplateSubstitution(TypescriptTsxAST, AST):
    pass


class TypescriptTsxTemplateType(TypescriptTsxAST, AST):
    pass


class TypescriptTsxTernaryExpression(TypescriptTsxExpression, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def consequence(self) -> AST:
            return self.child_slot("CONSEQUENCE")

        @cached_property
        def alternative(self) -> AST:
            return self.child_slot("ALTERNATIVE")


class TypescriptTsxThis(TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxThisType(TypescriptTsxPrimaryType, AST):
    pass


class TypescriptTsxThrow(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxThrowStatement(TypescriptTsxStatement, AST):
        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxTrue(TypescriptTsxPrimaryExpression, BooleanTrueAST, AST):
    pass


class TypescriptTsxTry(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxTryStatement(TypescriptTsxStatement, AST):
    pass


class TypescriptTsxTryStatement0(TypescriptTsxTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def handler(self) -> AST:
            return self.child_slot("HANDLER")

        @cached_property
        def finalizer(self) -> AST:
            return self.child_slot("FINALIZER")


class TypescriptTsxTryStatement1(TypescriptTsxTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def handler(self) -> AST:
            return self.child_slot("HANDLER")

        @cached_property
        def finalizer(self) -> AST:
            return self.child_slot("FINALIZER")


class TypescriptTsxTryStatement2(TypescriptTsxTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def handler(self) -> AST:
            return self.child_slot("HANDLER")

        @cached_property
        def finalizer(self) -> AST:
            return self.child_slot("FINALIZER")


class TypescriptTsxTryStatement3(TypescriptTsxTryStatement, AST):
        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")

        @cached_property
        def handler(self) -> AST:
            return self.child_slot("HANDLER")

        @cached_property
        def finalizer(self) -> AST:
            return self.child_slot("FINALIZER")


class TypescriptTsxTupleType(TypescriptTsxPrimaryType, TypescriptTupleType, AST):
    pass


class TypescriptTsxTupleType0(TypescriptTsxTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxTupleType1(TypescriptTsxTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxTupleType2(TypescriptTsxTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxTupleType3(TypescriptTsxTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxTupleType4(TypescriptTsxTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxTupleType5(TypescriptTsxTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxTupleType6(TypescriptTsxTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxTupleType7(TypescriptTsxTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxTupleType8(TypescriptTsxTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxTupleType9(TypescriptTsxTupleType, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxType(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxTypeAliasDeclaration(TypescriptTsxDeclaration, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type_parameters(self) -> AST:
            return self.child_slot("TYPE-PARAMETERS")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxTypeAnnotation(TypescriptTsxAST, TypescriptTypeAnnotation, AST):
    pass


class TypescriptTsxTypeArguments(TypescriptTsxAST, TypescriptTypeArguments, AST):
    pass


class TypescriptTsxTypeArguments0(TypescriptTsxTypeArguments, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxTypeArguments1(TypescriptTsxTypeArguments, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxTypeIdentifier(TypescriptTsxPrimaryType, TypeIdentifierAST, TypescriptTypeIdentifier, AST):
    pass


class TypescriptTsxTypeParameter(TypescriptTsxAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def constraint(self) -> AST:
            return self.child_slot("CONSTRAINT")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class TypescriptTsxTypeParameters(TypescriptTsxAST, AST):
    pass


class TypescriptTsxTypeParameters0(TypescriptTsxTypeParameters, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxTypeParameters1(TypescriptTsxTypeParameters, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")


class TypescriptTsxTypePredicate(TypescriptTsxAST, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")


class TypescriptTsxTypePredicateAnnotation(TypescriptTsxAST, AST):
    pass


class TypescriptTsxTypeQuery(TypescriptTsxPrimaryType, AST):
    pass


class TypescriptTsxTypeQuery0(TypescriptTsxTypeQuery, AST):
    pass


class TypescriptTsxTypeQuery1(TypescriptTsxTypeQuery, AST):
    pass


class TypescriptTsxTypeQuery2(TypescriptTsxTypeQuery, AST):
    pass


class TypescriptTsxTypeQuery3(TypescriptTsxTypeQuery, AST):
    pass


class TypescriptTsxTypeof(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxUnaryExpression(TypescriptTsxExpression, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class TypescriptTsxUndefined(TypescriptTsxPattern, TypescriptTsxPrimaryExpression, AST):
    pass


class TypescriptTsxUnionType(TypescriptTsxPrimaryType, TypescriptUnionType, AST):
    pass


class TypescriptTsxUnionType0(TypescriptTsxUnionType, AST):
    pass


class TypescriptTsxUnionType1(TypescriptTsxUnionType, AST):
    pass


class TypescriptTsxUnknown(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxUpdateExpression(TypescriptTsxExpression, AssignmentAST, AST):
    pass


class TypescriptTsxUpdateExpression0(TypescriptTsxUpdateExpression, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class TypescriptTsxUpdateExpression1(TypescriptTsxUpdateExpression, AST):
        @cached_property
        def operator(self) -> AST:
            return self.child_slot("OPERATOR")

        @cached_property
        def argument(self) -> AST:
            return self.child_slot("ARGUMENT")


class TypescriptTsxVar(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxVariableDeclaration(TypescriptTsxDeclaration, AST):
        @cached_property
        def comma(self) -> List[AST]:
            return self.child_slot("COMMA")

        @cached_property
        def semicolon(self) -> List[AST]:
            return self.child_slot("SEMICOLON")


class TypescriptTsxVariableDeclarator(TypescriptTsxAST, TypescriptVariableDeclarator, ECMAVariableDeclarator, AST):
    pass


class TypescriptTsxVariableDeclarator0(TypescriptTsxVariableDeclarator, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class TypescriptTsxVariableDeclarator1(TypescriptTsxVariableDeclarator, AST):
        @cached_property
        def name(self) -> AST:
            return self.child_slot("NAME")

        @cached_property
        def type(self) -> AST:
            return self.child_slot("TYPE")

        @cached_property
        def value(self) -> AST:
            return self.child_slot("VALUE")


class TypescriptTsxVoid(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxWhile(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxWhileStatement(TypescriptTsxStatement, ControlFlowAST, AST):
        @cached_property
        def condition(self) -> AST:
            return self.child_slot("CONDITION")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxWith(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxWithStatement(TypescriptTsxStatement, AST):
        @cached_property
        def object(self) -> AST:
            return self.child_slot("OBJECT")

        @cached_property
        def body(self) -> AST:
            return self.child_slot("BODY")


class TypescriptTsxYield(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxYieldExpression(TypescriptTsxExpression, AST):
    pass


class TypescriptTsxYieldExpression0(TypescriptTsxYieldExpression, AST):
    pass


class TypescriptTsxYieldExpression1(TypescriptTsxYieldExpression, AST):
    pass


class TypescriptTsxYieldExpression2(TypescriptTsxYieldExpression, AST):
    pass


class TypescriptTsxOpenBracket(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxCloseBracket(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBitwiseXor(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBitwiseXorAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBackQuote(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxOpenBrace(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxObjectTypeOpen(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBitwiseOr(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBitwiseOrAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxLogicalOr(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxLogicalOrAssign(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxObjectTypeClose(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxCloseBrace(TypescriptTsxAST, TerminalSymbol, AST):
    pass


class TypescriptTsxBitwiseNot(TypescriptTsxAST, TerminalSymbol, AST):
    pass


