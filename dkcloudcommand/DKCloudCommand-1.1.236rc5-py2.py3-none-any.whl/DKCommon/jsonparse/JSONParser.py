# Generated from JSON.g by ANTLR 4.7.1
# encoding: utf-8
from __future__ import print_function

import sys

from antlr4 import (
    ATNDeserializer,
    DFA,
    NoViableAltException,
    Parser,
    ParserATNSimulator,
    ParserRuleContext,
    PredictionContextCache,
    RecognitionException,
    Token,
)
from collections import OrderedDict
from io import StringIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3")
        buf.write("\16Q\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\3\2\3\2")
        buf.write("\3\2\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\7\3\30\n\3\f\3\16")
        buf.write("\3\33\13\3\3\3\3\3\3\3\3\3\3\3\3\3\5\3#\n\3\3\4\3\4\3")
        buf.write("\4\3\4\3\4\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\7\5\62\n\5")
        buf.write("\f\5\16\5\65\13\5\3\5\3\5\3\5\3\5\3\5\3\5\5\5=\n\5\3")
        buf.write("\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3")
        buf.write("\6\3\6\3\6\5\6O\n\6\3\6\2\2\7\2\4\6\b\n\2\2\2U\2\f\3")
        buf.write('\2\2\2\4"\3\2\2\2\6$\3\2\2\2\b<\3\2\2\2\nN\3\2\2\2\f')
        buf.write("\r\5\n\6\2\r\16\b\2\1\2\16\3\3\2\2\2\17\20\b\3\1\2\20")
        buf.write("\21\7\3\2\2\21\22\5\6\4\2\22\31\b\3\1\2\23\24\7\4\2\2")
        buf.write("\24\25\5\6\4\2\25\26\b\3\1\2\26\30\3\2\2\2\27\23\3\2")
        buf.write("\2\2\30\33\3\2\2\2\31\27\3\2\2\2\31\32\3\2\2\2\32\34")
        buf.write("\3\2\2\2\33\31\3\2\2\2\34\35\7\5\2\2\35\36\b\3\1\2\36")
        buf.write('#\3\2\2\2\37 \7\3\2\2 !\7\5\2\2!#\b\3\1\2"\17\3\2\2')
        buf.write("\2\"\37\3\2\2\2#\5\3\2\2\2$%\7\f\2\2%&\7\6\2\2&'\5\n")
        buf.write("\6\2'(\b\4\1\2(\7\3\2\2\2)*\b\5\1\2*+\7\7\2\2+,\5\n")
        buf.write("\6\2,\63\b\5\1\2-.\7\4\2\2./\5\n\6\2/\60\b\5\1\2\60\62")
        buf.write("\3\2\2\2\61-\3\2\2\2\62\65\3\2\2\2\63\61\3\2\2\2\63\64")
        buf.write("\3\2\2\2\64\66\3\2\2\2\65\63\3\2\2\2\66\67\7\b\2\2\67")
        buf.write("8\b\5\1\28=\3\2\2\29:\7\7\2\2:;\7\b\2\2;=\b\5\1\2<)\3")
        buf.write("\2\2\2<9\3\2\2\2=\t\3\2\2\2>?\7\f\2\2?O\b\6\1\2@A\7\r")
        buf.write("\2\2AO\b\6\1\2BC\5\4\3\2CD\b\6\1\2DO\3\2\2\2EF\5\b\5")
        buf.write("\2FG\b\6\1\2GO\3\2\2\2HI\7\t\2\2IO\b\6\1\2JK\7\n\2\2")
        buf.write("KO\b\6\1\2LM\7\13\2\2MO\b\6\1\2N>\3\2\2\2N@\3\2\2\2N")
        buf.write("B\3\2\2\2NE\3\2\2\2NH\3\2\2\2NJ\3\2\2\2NL\3\2\2\2O\13")
        buf.write('\3\2\2\2\7\31"\63<N')
        return buf.getvalue()


class JSONParser(Parser):

    grammarFileName = "JSON.g"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [DFA(ds, i) for i, ds in enumerate(atn.decisionToState)]

    sharedContextCache = PredictionContextCache()

    literalNames = [
        "<INVALID>",
        "'{'",
        "','",
        "'}'",
        "':'",
        "'['",
        "']'",
        "'true'",
        "'false'",
        "'null'",
    ]

    symbolicNames = [
        "<INVALID>",
        "<INVALID>",
        "<INVALID>",
        "<INVALID>",
        "<INVALID>",
        "<INVALID>",
        "<INVALID>",
        "<INVALID>",
        "<INVALID>",
        "<INVALID>",
        "STRING",
        "NUMBER",
        "WS",
    ]

    RULE_json = 0
    RULE_obj = 1
    RULE_pair = 2
    RULE_array = 3
    RULE_value = 4

    ruleNames = ["json", "obj", "pair", "array", "value"]

    EOF = Token.EOF
    T__0 = 1
    T__1 = 2
    T__2 = 3
    T__3 = 4
    T__4 = 5
    T__5 = 6
    T__6 = 7
    T__7 = 8
    T__8 = 9
    STRING = 10
    NUMBER = 11
    WS = 12

    def __init__(self, input, output=sys.stdout):
        super(JSONParser, self).__init__(input, output=output)
        self.checkVersion("4.7.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None

    class JsonContext(ParserRuleContext):
        def __init__(self, parser, parent=None, invokingState=-1):
            super(JSONParser.JsonContext, self).__init__(parent, invokingState)
            self.parser = parser
            self.val = None
            self._value = None  # ValueContext

        def value(self):
            return self.getTypedRuleContext(JSONParser.ValueContext, 0)

        def getRuleIndex(self):
            return JSONParser.RULE_json

        def enterRule(self, listener):
            if hasattr(listener, "enterJson"):
                listener.enterJson(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitJson"):
                listener.exitJson(self)

    def json(self):

        localctx = JSONParser.JsonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_json)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 10
            localctx._value = self.value()
            localctx.val = localctx._value.val
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ObjContext(ParserRuleContext):
        def __init__(self, parser, parent=None, invokingState=-1):
            super(JSONParser.ObjContext, self).__init__(parent, invokingState)
            self.parser = parser
            self.val = None
            self._pair = None  # PairContext

        def pair(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(JSONParser.PairContext)
            else:
                return self.getTypedRuleContext(JSONParser.PairContext, i)

        def getRuleIndex(self):
            return JSONParser.RULE_obj

        def enterRule(self, listener):
            if hasattr(listener, "enterObj"):
                listener.enterObj(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitObj"):
                listener.exitObj(self)

    def obj(self):

        localctx = JSONParser.ObjContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_obj)
        self._la = 0  # Token type
        try:
            self.state = 32
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input, 1, self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                a = []
                self.state = 14
                self.match(JSONParser.T__0)
                self.state = 15
                localctx._pair = self.pair()
                a.append(localctx._pair.val)
                self.state = 23
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la == JSONParser.T__1:
                    self.state = 17
                    self.match(JSONParser.T__1)
                    self.state = 18
                    localctx._pair = self.pair()
                    a.append(localctx._pair.val)
                    self.state = 25
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 26
                self.match(JSONParser.T__2)
                localctx.val = OrderedDict(a)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 29
                self.match(JSONParser.T__0)
                self.state = 30
                self.match(JSONParser.T__2)
                localctx.val = OrderedDict()
                pass

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PairContext(ParserRuleContext):
        def __init__(self, parser, parent=None, invokingState=-1):
            super(JSONParser.PairContext, self).__init__(parent, invokingState)
            self.parser = parser
            self.val = None
            self._STRING = None  # Token
            self._value = None  # ValueContext

        def STRING(self):
            return self.getToken(JSONParser.STRING, 0)

        def value(self):
            return self.getTypedRuleContext(JSONParser.ValueContext, 0)

        def getRuleIndex(self):
            return JSONParser.RULE_pair

        def enterRule(self, listener):
            if hasattr(listener, "enterPair"):
                listener.enterPair(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitPair"):
                listener.exitPair(self)

    def pair(self):

        localctx = JSONParser.PairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_pair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 34
            localctx._STRING = self.match(JSONParser.STRING)
            self.state = 35
            self.match(JSONParser.T__3)
            self.state = 36
            localctx._value = self.value()
            localctx.val = (
                (None if localctx._STRING is None else localctx._STRING.text)[1:-1],
                localctx._value.val,
            )
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ArrayContext(ParserRuleContext):
        def __init__(self, parser, parent=None, invokingState=-1):
            super(JSONParser.ArrayContext, self).__init__(parent, invokingState)
            self.parser = parser
            self.val = None
            self._value = None  # ValueContext

        def value(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(JSONParser.ValueContext)
            else:
                return self.getTypedRuleContext(JSONParser.ValueContext, i)

        def getRuleIndex(self):
            return JSONParser.RULE_array

        def enterRule(self, listener):
            if hasattr(listener, "enterArray"):
                listener.enterArray(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitArray"):
                listener.exitArray(self)

    def array(self):

        localctx = JSONParser.ArrayContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_array)
        self._la = 0  # Token type
        try:
            self.state = 58
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input, 3, self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                a = []
                self.state = 40
                self.match(JSONParser.T__4)
                self.state = 41
                localctx._value = self.value()
                a.append(localctx._value.val)
                self.state = 49
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la == JSONParser.T__1:
                    self.state = 43
                    self.match(JSONParser.T__1)
                    self.state = 44
                    localctx._value = self.value()
                    a.append(localctx._value.val)
                    self.state = 51
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 52
                self.match(JSONParser.T__5)
                localctx.val = a
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 55
                self.match(JSONParser.T__4)
                self.state = 56
                self.match(JSONParser.T__5)
                localctx.val = []
                pass

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ValueContext(ParserRuleContext):
        def __init__(self, parser, parent=None, invokingState=-1):
            super(JSONParser.ValueContext, self).__init__(parent, invokingState)
            self.parser = parser
            self.val = None
            self._STRING = None  # Token
            self._NUMBER = None  # Token
            self._obj = None  # ObjContext
            self._array = None  # ArrayContext

        def STRING(self):
            return self.getToken(JSONParser.STRING, 0)

        def NUMBER(self):
            return self.getToken(JSONParser.NUMBER, 0)

        def obj(self):
            return self.getTypedRuleContext(JSONParser.ObjContext, 0)

        def array(self):
            return self.getTypedRuleContext(JSONParser.ArrayContext, 0)

        def getRuleIndex(self):
            return JSONParser.RULE_value

        def enterRule(self, listener):
            if hasattr(listener, "enterValue"):
                listener.enterValue(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitValue"):
                listener.exitValue(self)

    def value(self):

        localctx = JSONParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_value)
        try:
            self.state = 76
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [JSONParser.STRING]:
                self.enterOuterAlt(localctx, 1)
                self.state = 60
                localctx._STRING = self.match(JSONParser.STRING)
                localctx.val = (None if localctx._STRING is None else localctx._STRING.text)[1:-1]
                pass
            elif token in [JSONParser.NUMBER]:
                self.enterOuterAlt(localctx, 2)
                self.state = 62
                localctx._NUMBER = self.match(JSONParser.NUMBER)
                localctx.val = int((None if localctx._NUMBER is None else localctx._NUMBER.text))
                pass
            elif token in [JSONParser.T__0]:
                self.enterOuterAlt(localctx, 3)
                self.state = 64
                localctx._obj = self.obj()
                localctx.val = localctx._obj.val
                pass
            elif token in [JSONParser.T__4]:
                self.enterOuterAlt(localctx, 4)
                self.state = 67
                localctx._array = self.array()
                localctx.val = localctx._array.val
                pass
            elif token in [JSONParser.T__6]:
                self.enterOuterAlt(localctx, 5)
                self.state = 70
                self.match(JSONParser.T__6)
                localctx.val = True
                pass
            elif token in [JSONParser.T__7]:
                self.enterOuterAlt(localctx, 6)
                self.state = 72
                self.match(JSONParser.T__7)
                localctx.val = False
                pass
            elif token in [JSONParser.T__8]:
                self.enterOuterAlt(localctx, 7)
                self.state = 74
                self.match(JSONParser.T__8)
                localctx.val = None
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx
