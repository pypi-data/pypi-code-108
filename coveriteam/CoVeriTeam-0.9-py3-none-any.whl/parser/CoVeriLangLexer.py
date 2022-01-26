# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2022 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

# Generated from CoVeriLang.g4 by ANTLR 4.8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\61")
        buf.write("\u01ef\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write("\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4\23")
        buf.write("\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30")
        buf.write("\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36")
        buf.write('\t\36\4\37\t\37\4 \t \4!\t!\4"\t"\4#\t#\4$\t$\4%\t%')
        buf.write("\4&\t&\4'\t'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t,\4-\t-\4.")
        buf.write("\t.\4/\t/\4\60\t\60\3\2\3\2\3\2\3\2\3\3\3\3\3\4\3\4\3")
        buf.write("\5\3\5\3\6\3\6\3\7\3\7\3\b\3\b\3\t\3\t\3\t\3\t\3\t\3\t")
        buf.write("\3\t\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\13\3\13\3\13")
        buf.write("\3\13\3\13\3\13\3\13\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3")
        buf.write("\f\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\r\3\r\3\16\3\16\3\16")
        buf.write("\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16")
        buf.write("\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\17\3\17\3\17\3\17")
        buf.write("\3\17\3\17\3\17\3\17\3\17\3\20\3\20\3\20\3\20\3\21\3\21")
        buf.write("\3\21\3\21\3\21\3\21\3\21\3\22\3\22\3\22\3\22\3\22\3\22")
        buf.write("\3\22\3\22\3\22\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\23")
        buf.write("\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\24")
        buf.write("\3\24\3\24\3\24\3\24\3\24\3\24\3\25\3\25\3\25\3\25\3\25")
        buf.write("\3\25\3\25\3\26\3\26\3\26\3\26\3\26\3\26\3\26\3\26\3\26")
        buf.write("\3\26\3\26\3\27\3\27\3\27\3\27\3\27\3\30\3\30\3\30\3\30")
        buf.write("\3\30\3\30\3\30\3\31\3\31\3\31\3\31\3\31\3\31\3\31\3\31")
        buf.write("\3\31\3\31\3\31\3\31\3\31\3\31\3\31\3\31\3\31\3\32\3\32")
        buf.write("\3\32\3\32\3\32\3\32\3\32\3\32\3\32\3\32\3\32\3\32\3\32")
        buf.write("\3\32\3\32\3\32\3\32\3\33\3\33\3\33\3\33\3\33\3\33\3\33")
        buf.write("\3\33\3\33\3\33\3\33\3\33\3\33\3\33\3\33\3\33\3\33\3\33")
        buf.write("\3\33\3\33\3\33\3\33\3\33\3\33\3\33\3\33\3\33\3\33\3\33")
        buf.write("\3\33\3\33\3\33\3\33\3\33\3\34\3\34\3\34\3\34\3\34\3\34")
        buf.write("\3\34\3\34\3\34\3\35\3\35\3\35\3\35\3\35\3\35\3\35\3\35")
        buf.write("\3\35\3\35\3\35\3\35\3\35\3\35\3\35\3\35\3\35\3\35\3\35")
        buf.write("\3\35\3\35\3\35\3\35\3\35\3\36\3\36\3\37\3\37\3\37\3\37")
        buf.write("\3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3!\3!\3!\3!\3!\3!\3")
        buf.write('!\3!\3!\3!\3"\3"\3"\3"\3"\3"\3"\3"\3#\3#\3$\3')
        buf.write("$\3$\3$\3$\3$\3$\3$\3$\3$\3$\3$\3$\3$\3$\3$\3$\3$\3$\3")
        buf.write("$\3$\3$\5$\u01a4\n$\3%\3%\3%\3%\3%\3%\3%\3%\3%\5%\u01af")
        buf.write("\n%\3&\3&\3&\3&\7&\u01b5\n&\f&\16&\u01b8\13&\3'\3'\7")
        buf.write("'\u01bc\n'\f'\16'\u01bf\13'\3'\3'\3(\3(\3(\7(\u01c6")
        buf.write("\n(\f(\16(\u01c9\13(\3)\3)\5)\u01cd\n)\3*\3*\3+\3+\3,")
        buf.write("\3,\3-\5-\u01d6\n-\3-\3-\3-\3-\3.\6.\u01dd\n.\r.\16.\u01de")
        buf.write("\3.\3.\3/\3/\3\60\3\60\3\60\3\60\7\60\u01e9\n\60\f\60")
        buf.write("\16\60\u01ec\13\60\3\60\3\60\2\2\61\3\3\5\4\7\5\t\6\13")
        buf.write("\7\r\b\17\t\21\n\23\13\25\f\27\r\31\16\33\17\35\20\37")
        buf.write("\21!\22#\23%\24'\25)\26+\27-\30/\31\61\32\63\33\65\34")
        buf.write("\67\359\36;\37= ?!A\"C#E$G%I&K'M(O)Q*S+U,W-Y.[/]\60_")
        buf.write('\61\3\2\t\3\2aa\3\2$$\3\2c|\3\2C\\\3\2\62;\4\2\13\13"')
        buf.write('"\4\2\f\f\17\17\2\u01fd\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3')
        buf.write("\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2\17\3\2\2")
        buf.write("\2\2\21\3\2\2\2\2\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2\2\2")
        buf.write("\2\31\3\2\2\2\2\33\3\2\2\2\2\35\3\2\2\2\2\37\3\2\2\2\2")
        buf.write("!\3\2\2\2\2#\3\2\2\2\2%\3\2\2\2\2'\3\2\2\2\2)\3\2\2\2")
        buf.write("\2+\3\2\2\2\2-\3\2\2\2\2/\3\2\2\2\2\61\3\2\2\2\2\63\3")
        buf.write("\2\2\2\2\65\3\2\2\2\2\67\3\2\2\2\29\3\2\2\2\2;\3\2\2\2")
        buf.write("\2=\3\2\2\2\2?\3\2\2\2\2A\3\2\2\2\2C\3\2\2\2\2E\3\2\2")
        buf.write("\2\2G\3\2\2\2\2I\3\2\2\2\2K\3\2\2\2\2M\3\2\2\2\2O\3\2")
        buf.write("\2\2\2Q\3\2\2\2\2S\3\2\2\2\2U\3\2\2\2\2W\3\2\2\2\2Y\3")
        buf.write("\2\2\2\2[\3\2\2\2\2]\3\2\2\2\2_\3\2\2\2\3a\3\2\2\2\5e")
        buf.write("\3\2\2\2\7g\3\2\2\2\ti\3\2\2\2\13k\3\2\2\2\rm\3\2\2\2")
        buf.write("\17o\3\2\2\2\21q\3\2\2\2\23x\3\2\2\2\25\u0081\3\2\2\2")
        buf.write("\27\u0088\3\2\2\2\31\u0098\3\2\2\2\33\u009a\3\2\2\2\35")
        buf.write("\u00af\3\2\2\2\37\u00b8\3\2\2\2!\u00bc\3\2\2\2#\u00c3")
        buf.write("\3\2\2\2%\u00cc\3\2\2\2'\u00de\3\2\2\2)\u00e5\3\2\2\2")
        buf.write("+\u00ec\3\2\2\2-\u00f7\3\2\2\2/\u00fc\3\2\2\2\61\u0103")
        buf.write("\3\2\2\2\63\u0114\3\2\2\2\65\u0125\3\2\2\2\67\u0147\3")
        buf.write("\2\2\29\u0150\3\2\2\2;\u0168\3\2\2\2=\u016a\3\2\2\2?\u016e")
        buf.write("\3\2\2\2A\u0179\3\2\2\2C\u0183\3\2\2\2E\u018b\3\2\2\2")
        buf.write("G\u01a3\3\2\2\2I\u01ae\3\2\2\2K\u01b0\3\2\2\2M\u01b9\3")
        buf.write("\2\2\2O\u01c2\3\2\2\2Q\u01cc\3\2\2\2S\u01ce\3\2\2\2U\u01d0")
        buf.write("\3\2\2\2W\u01d2\3\2\2\2Y\u01d5\3\2\2\2[\u01dc\3\2\2\2")
        buf.write("]\u01e2\3\2\2\2_\u01e4\3\2\2\2ab\7h\2\2bc\7w\2\2cd\7p")
        buf.write("\2\2d\4\3\2\2\2ef\7*\2\2f\6\3\2\2\2gh\7+\2\2h\b\3\2\2")
        buf.write("\2ij\7}\2\2j\n\3\2\2\2kl\7\177\2\2l\f\3\2\2\2mn\7.\2\2")
        buf.write("n\16\3\2\2\2op\7?\2\2p\20\3\2\2\2qr\7r\2\2rs\7t\2\2st")
        buf.write("\7k\2\2tu\7p\2\2uv\7v\2\2vw\7*\2\2w\22\3\2\2\2xy\7g\2")
        buf.write("\2yz\7z\2\2z{\7g\2\2{|\7e\2\2|}\7w\2\2}~\7v\2\2~\177\7")
        buf.write("g\2\2\177\u0080\7*\2\2\u0080\24\3\2\2\2\u0081\u0082\7")
        buf.write("t\2\2\u0082\u0083\7g\2\2\u0083\u0084\7v\2\2\u0084\u0085")
        buf.write("\7w\2\2\u0085\u0086\7t\2\2\u0086\u0087\7p\2\2\u0087\26")
        buf.write("\3\2\2\2\u0088\u0089\7u\2\2\u0089\u008a\7g\2\2\u008a\u008b")
        buf.write("\7v\2\2\u008b\u008c\7a\2\2\u008c\u008d\7c\2\2\u008d\u008e")
        buf.write("\7e\2\2\u008e\u008f\7v\2\2\u008f\u0090\7q\2\2\u0090\u0091")
        buf.write("\7t\2\2\u0091\u0092\7a\2\2\u0092\u0093\7p\2\2\u0093\u0094")
        buf.write("\7c\2\2\u0094\u0095\7o\2\2\u0095\u0096\7g\2\2\u0096\u0097")
        buf.write("\7*\2\2\u0097\30\3\2\2\2\u0098\u0099\7<\2\2\u0099\32\3")
        buf.write("\2\2\2\u009a\u009b\7C\2\2\u009b\u009c\7e\2\2\u009c\u009d")
        buf.write("\7v\2\2\u009d\u009e\7q\2\2\u009e\u009f\7t\2\2\u009f\u00a0")
        buf.write("\7H\2\2\u00a0\u00a1\7c\2\2\u00a1\u00a2\7e\2\2\u00a2\u00a3")
        buf.write("\7v\2\2\u00a3\u00a4\7q\2\2\u00a4\u00a5\7t\2\2\u00a5\u00a6")
        buf.write("\7{\2\2\u00a6\u00a7\7\60\2\2\u00a7\u00a8\7e\2\2\u00a8")
        buf.write("\u00a9\7t\2\2\u00a9\u00aa\7g\2\2\u00aa\u00ab\7c\2\2\u00ab")
        buf.write("\u00ac\7v\2\2\u00ac\u00ad\7g\2\2\u00ad\u00ae\7*\2\2\u00ae")
        buf.write("\34\3\2\2\2\u00af\u00b0\7U\2\2\u00b0\u00b1\7G\2\2\u00b1")
        buf.write("\u00b2\7S\2\2\u00b2\u00b3\7W\2\2\u00b3\u00b4\7G\2\2\u00b4")
        buf.write("\u00b5\7P\2\2\u00b5\u00b6\7E\2\2\u00b6\u00b7\7G\2\2\u00b7")
        buf.write("\36\3\2\2\2\u00b8\u00b9\7K\2\2\u00b9\u00ba\7V\2\2\u00ba")
        buf.write("\u00bb\7G\2\2\u00bb \3\2\2\2\u00bc\u00bd\7T\2\2\u00bd")
        buf.write("\u00be\7G\2\2\u00be\u00bf\7R\2\2\u00bf\u00c0\7G\2\2\u00c0")
        buf.write('\u00c1\7C\2\2\u00c1\u00c2\7V\2\2\u00c2"\3\2\2\2\u00c3')
        buf.write("\u00c4\7R\2\2\u00c4\u00c5\7C\2\2\u00c5\u00c6\7T\2\2\u00c6")
        buf.write("\u00c7\7C\2\2\u00c7\u00c8\7N\2\2\u00c8\u00c9\7N\2\2\u00c9")
        buf.write("\u00ca\7G\2\2\u00ca\u00cb\7N\2\2\u00cb$\3\2\2\2\u00cc")
        buf.write("\u00cd\7R\2\2\u00cd\u00ce\7c\2\2\u00ce\u00cf\7t\2\2\u00cf")
        buf.write("\u00d0\7c\2\2\u00d0\u00d1\7n\2\2\u00d1\u00d2\7n\2\2\u00d2")
        buf.write("\u00d3\7g\2\2\u00d3\u00d4\7n\2\2\u00d4\u00d5\7R\2\2\u00d5")
        buf.write("\u00d6\7q\2\2\u00d6\u00d7\7t\2\2\u00d7\u00d8\7v\2\2\u00d8")
        buf.write("\u00d9\7h\2\2\u00d9\u00da\7q\2\2\u00da\u00db\7n\2\2\u00db")
        buf.write("\u00dc\7k\2\2\u00dc\u00dd\7q\2\2\u00dd&\3\2\2\2\u00de")
        buf.write("\u00df\7L\2\2\u00df\u00e0\7q\2\2\u00e0\u00e1\7k\2\2\u00e1")
        buf.write("\u00e2\7p\2\2\u00e2\u00e3\7g\2\2\u00e3\u00e4\7t\2\2\u00e4")
        buf.write("(\3\2\2\2\u00e5\u00e6\7U\2\2\u00e6\u00e7\7g\2\2\u00e7")
        buf.write("\u00e8\7v\2\2\u00e8\u00e9\7v\2\2\u00e9\u00ea\7g\2\2\u00ea")
        buf.write("\u00eb\7t\2\2\u00eb*\3\2\2\2\u00ec\u00ed\7E\2\2\u00ed")
        buf.write("\u00ee\7q\2\2\u00ee\u00ef\7o\2\2\u00ef\u00f0\7r\2\2\u00f0")
        buf.write("\u00f1\7c\2\2\u00f1\u00f2\7t\2\2\u00f2\u00f3\7c\2\2\u00f3")
        buf.write("\u00f4\7v\2\2\u00f4\u00f5\7q\2\2\u00f5\u00f6\7t\2\2\u00f6")
        buf.write(",\3\2\2\2\u00f7\u00f8\7E\2\2\u00f8\u00f9\7q\2\2\u00f9")
        buf.write("\u00fa\7r\2\2\u00fa\u00fb\7{\2\2\u00fb.\3\2\2\2\u00fc")
        buf.write("\u00fd\7T\2\2\u00fd\u00fe\7g\2\2\u00fe\u00ff\7p\2\2\u00ff")
        buf.write("\u0100\7c\2\2\u0100\u0101\7o\2\2\u0101\u0102\7g\2\2\u0102")
        buf.write("\60\3\2\2\2\u0103\u0104\7V\2\2\u0104\u0105\7g\2\2\u0105")
        buf.write("\u0106\7u\2\2\u0106\u0107\7v\2\2\u0107\u0108\7U\2\2\u0108")
        buf.write("\u0109\7r\2\2\u0109\u010a\7g\2\2\u010a\u010b\7e\2\2\u010b")
        buf.write("\u010c\7V\2\2\u010c\u010d\7q\2\2\u010d\u010e\7U\2\2\u010e")
        buf.write("\u010f\7r\2\2\u010f\u0110\7g\2\2\u0110\u0111\7e\2\2\u0111")
        buf.write("\u0112\7*\2\2\u0112\u0113\7+\2\2\u0113\62\3\2\2\2\u0114")
        buf.write("\u0115\7U\2\2\u0115\u0116\7r\2\2\u0116\u0117\7g\2\2\u0117")
        buf.write("\u0118\7e\2\2\u0118\u0119\7V\2\2\u0119\u011a\7q\2\2\u011a")
        buf.write("\u011b\7V\2\2\u011b\u011c\7g\2\2\u011c\u011d\7u\2\2\u011d")
        buf.write("\u011e\7v\2\2\u011e\u011f\7U\2\2\u011f\u0120\7r\2\2\u0120")
        buf.write("\u0121\7g\2\2\u0121\u0122\7e\2\2\u0122\u0123\7*\2\2\u0123")
        buf.write("\u0124\7+\2\2\u0124\64\3\2\2\2\u0125\u0126\7E\2\2\u0126")
        buf.write("\u0127\7n\2\2\u0127\u0128\7c\2\2\u0128\u0129\7u\2\2\u0129")
        buf.write("\u012a\7u\2\2\u012a\u012b\7k\2\2\u012b\u012c\7h\2\2\u012c")
        buf.write("\u012d\7k\2\2\u012d\u012e\7e\2\2\u012e\u012f\7c\2\2\u012f")
        buf.write("\u0130\7v\2\2\u0130\u0131\7k\2\2\u0131\u0132\7q\2\2\u0132")
        buf.write("\u0133\7p\2\2\u0133\u0134\7V\2\2\u0134\u0135\7q\2\2\u0135")
        buf.write("\u0136\7C\2\2\u0136\u0137\7e\2\2\u0137\u0138\7v\2\2\u0138")
        buf.write("\u0139\7q\2\2\u0139\u013a\7t\2\2\u013a\u013b\7F\2\2\u013b")
        buf.write("\u013c\7g\2\2\u013c\u013d\7h\2\2\u013d\u013e\7k\2\2\u013e")
        buf.write("\u013f\7p\2\2\u013f\u0140\7k\2\2\u0140\u0141\7v\2\2\u0141")
        buf.write("\u0142\7k\2\2\u0142\u0143\7q\2\2\u0143\u0144\7p\2\2\u0144")
        buf.write("\u0145\7*\2\2\u0145\u0146\7+\2\2\u0146\66\3\2\2\2\u0147")
        buf.write("\u0148\7K\2\2\u0148\u0149\7f\2\2\u0149\u014a\7g\2\2\u014a")
        buf.write("\u014b\7p\2\2\u014b\u014c\7v\2\2\u014c\u014d\7k\2\2\u014d")
        buf.write("\u014e\7v\2\2\u014e\u014f\7{\2\2\u014f8\3\2\2\2\u0150")
        buf.write("\u0151\7C\2\2\u0151\u0152\7t\2\2\u0152\u0153\7v\2\2\u0153")
        buf.write("\u0154\7k\2\2\u0154\u0155\7h\2\2\u0155\u0156\7c\2\2\u0156")
        buf.write("\u0157\7e\2\2\u0157\u0158\7v\2\2\u0158\u0159\7H\2\2\u0159")
        buf.write("\u015a\7c\2\2\u015a\u015b\7e\2\2\u015b\u015c\7v\2\2\u015c")
        buf.write("\u015d\7q\2\2\u015d\u015e\7t\2\2\u015e\u015f\7{\2\2\u015f")
        buf.write("\u0160\7\60\2\2\u0160\u0161\7e\2\2\u0161\u0162\7t\2\2")
        buf.write("\u0162\u0163\7g\2\2\u0163\u0164\7c\2\2\u0164\u0165\7v")
        buf.write("\2\2\u0165\u0166\7g\2\2\u0166\u0167\7*\2\2\u0167:\3\2")
        buf.write("\2\2\u0168\u0169\7\60\2\2\u0169<\3\2\2\2\u016a\u016b\7")
        buf.write("P\2\2\u016b\u016c\7Q\2\2\u016c\u016d\7V\2\2\u016d>\3\2")
        buf.write("\2\2\u016e\u016f\7K\2\2\u016f\u0170\7P\2\2\u0170\u0171")
        buf.write("\7U\2\2\u0171\u0172\7V\2\2\u0172\u0173\7C\2\2\u0173\u0174")
        buf.write("\7P\2\2\u0174\u0175\7E\2\2\u0175\u0176\7G\2\2\u0176\u0177")
        buf.write("\7Q\2\2\u0177\u0178\7H\2\2\u0178@\3\2\2\2\u0179\u017a")
        buf.write("\7G\2\2\u017a\u017b\7N\2\2\u017b\u017c\7G\2\2\u017c\u017d")
        buf.write("\7O\2\2\u017d\u017e\7G\2\2\u017e\u017f\7P\2\2\u017f\u0180")
        buf.write("\7V\2\2\u0180\u0181\7Q\2\2\u0181\u0182\7H\2\2\u0182B\3")
        buf.write("\2\2\2\u0183\u0184\7V\2\2\u0184\u0185\7Q\2\2\u0185\u0186")
        buf.write("\7F\2\2\u0186\u0187\7Q\2\2\u0187\u0188\7/\2\2\u0188\u0189")
        buf.write("\7/\2\2\u0189\u018a\7/\2\2\u018aD\3\2\2\2\u018b\u018c")
        buf.write("\7)\2\2\u018cF\3\2\2\2\u018d\u018e\7H\2\2\u018e\u018f")
        buf.write("\7C\2\2\u018f\u0190\7N\2\2\u0190\u0191\7U\2\2\u0191\u0192")
        buf.write("\7G\2\2\u0192\u0193\3\2\2\2\u0193\u01a4\b$\2\2\u0194\u0195")
        buf.write("\7V\2\2\u0195\u0196\7T\2\2\u0196\u0197\7W\2\2\u0197\u0198")
        buf.write("\7G\2\2\u0198\u0199\3\2\2\2\u0199\u01a4\b$\3\2\u019a\u019b")
        buf.write("\7W\2\2\u019b\u019c\7P\2\2\u019c\u019d\7M\2\2\u019d\u019e")
        buf.write("\7P\2\2\u019e\u019f\7Q\2\2\u019f\u01a0\7Y\2\2\u01a0\u01a1")
        buf.write("\7P\2\2\u01a1\u01a2\3\2\2\2\u01a2\u01a4\b$\4\2\u01a3\u018d")
        buf.write("\3\2\2\2\u01a3\u0194\3\2\2\2\u01a3\u019a\3\2\2\2\u01a4")
        buf.write("H\3\2\2\2\u01a5\u01a6\7C\2\2\u01a6\u01a7\7P\2\2\u01a7")
        buf.write("\u01af\7F\2\2\u01a8\u01a9\7Q\2\2\u01a9\u01af\7T\2\2\u01aa")
        buf.write("\u01ab\7?\2\2\u01ab\u01af\7?\2\2\u01ac\u01ad\7#\2\2\u01ad")
        buf.write("\u01af\7?\2\2\u01ae\u01a5\3\2\2\2\u01ae\u01a8\3\2\2\2")
        buf.write("\u01ae\u01aa\3\2\2\2\u01ae\u01ac\3\2\2\2\u01afJ\3\2\2")
        buf.write("\2\u01b0\u01b6\5S*\2\u01b1\u01b5\5Q)\2\u01b2\u01b5\5W")
        buf.write(",\2\u01b3\u01b5\t\2\2\2\u01b4\u01b1\3\2\2\2\u01b4\u01b2")
        buf.write("\3\2\2\2\u01b4\u01b3\3\2\2\2\u01b5\u01b8\3\2\2\2\u01b6")
        buf.write("\u01b4\3\2\2\2\u01b6\u01b7\3\2\2\2\u01b7L\3\2\2\2\u01b8")
        buf.write("\u01b6\3\2\2\2\u01b9\u01bd\7$\2\2\u01ba\u01bc\n\3\2\2")
        buf.write("\u01bb\u01ba\3\2\2\2\u01bc\u01bf\3\2\2\2\u01bd\u01bb\3")
        buf.write("\2\2\2\u01bd\u01be\3\2\2\2\u01be\u01c0\3\2\2\2\u01bf\u01bd")
        buf.write("\3\2\2\2\u01c0\u01c1\7$\2\2\u01c1N\3\2\2\2\u01c2\u01c7")
        buf.write("\5U+\2\u01c3\u01c6\5Q)\2\u01c4\u01c6\5W,\2\u01c5\u01c3")
        buf.write("\3\2\2\2\u01c5\u01c4\3\2\2\2\u01c6\u01c9\3\2\2\2\u01c7")
        buf.write("\u01c5\3\2\2\2\u01c7\u01c8\3\2\2\2\u01c8P\3\2\2\2\u01c9")
        buf.write("\u01c7\3\2\2\2\u01ca\u01cd\5S*\2\u01cb\u01cd\5U+\2\u01cc")
        buf.write("\u01ca\3\2\2\2\u01cc\u01cb\3\2\2\2\u01cdR\3\2\2\2\u01ce")
        buf.write("\u01cf\t\4\2\2\u01cfT\3\2\2\2\u01d0\u01d1\t\5\2\2\u01d1")
        buf.write("V\3\2\2\2\u01d2\u01d3\t\6\2\2\u01d3X\3\2\2\2\u01d4\u01d6")
        buf.write("\7\17\2\2\u01d5\u01d4\3\2\2\2\u01d5\u01d6\3\2\2\2\u01d6")
        buf.write("\u01d7\3\2\2\2\u01d7\u01d8\7\f\2\2\u01d8\u01d9\3\2\2\2")
        buf.write("\u01d9\u01da\b-\5\2\u01daZ\3\2\2\2\u01db\u01dd\t\7\2\2")
        buf.write("\u01dc\u01db\3\2\2\2\u01dd\u01de\3\2\2\2\u01de\u01dc\3")
        buf.write("\2\2\2\u01de\u01df\3\2\2\2\u01df\u01e0\3\2\2\2\u01e0\u01e1")
        buf.write("\b.\5\2\u01e1\\\3\2\2\2\u01e2\u01e3\7=\2\2\u01e3^\3\2")
        buf.write("\2\2\u01e4\u01e5\7\61\2\2\u01e5\u01e6\7\61\2\2\u01e6\u01ea")
        buf.write("\3\2\2\2\u01e7\u01e9\n\b\2\2\u01e8\u01e7\3\2\2\2\u01e9")
        buf.write("\u01ec\3\2\2\2\u01ea\u01e8\3\2\2\2\u01ea\u01eb\3\2\2\2")
        buf.write("\u01eb\u01ed\3\2\2\2\u01ec\u01ea\3\2\2\2\u01ed\u01ee\b")
        buf.write("\60\5\2\u01ee`\3\2\2\2\16\2\u01a3\u01ae\u01b4\u01b6\u01bd")
        buf.write("\u01c5\u01c7\u01cc\u01d5\u01de\u01ea\6\3$\2\3$\3\3$\4")
        buf.write("\b\2\2")
        return buf.getvalue()


class CoVeriLangLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [DFA(ds, i) for i, ds in enumerate(atn.decisionToState)]

    T__0 = 1
    T__1 = 2
    T__2 = 3
    T__3 = 4
    T__4 = 5
    T__5 = 6
    T__6 = 7
    T__7 = 8
    T__8 = 9
    T__9 = 10
    T__10 = 11
    T__11 = 12
    T__12 = 13
    T__13 = 14
    T__14 = 15
    T__15 = 16
    T__16 = 17
    T__17 = 18
    T__18 = 19
    T__19 = 20
    T__20 = 21
    T__21 = 22
    T__22 = 23
    T__23 = 24
    T__24 = 25
    T__25 = 26
    T__26 = 27
    T__27 = 28
    T__28 = 29
    T__29 = 30
    T__30 = 31
    T__31 = 32
    T__32 = 33
    T__33 = 34
    VERDICT = 35
    BIN_OP = 36
    ID = 37
    STRING = 38
    TYPE_NAME = 39
    LETTER = 40
    LOWER_CASE = 41
    UPPER_CASE = 42
    DIGIT = 43
    NEWLINE = 44
    WS = 45
    DELIMITER = 46
    COMMENT = 47

    channelNames = [u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN"]

    modeNames = ["DEFAULT_MODE"]

    literalNames = [
        "<INVALID>",
        "'fun'",
        "'('",
        "')'",
        "'{'",
        "'}'",
        "','",
        "'='",
        "'print('",
        "'execute('",
        "'return'",
        "'set_actor_name('",
        "':'",
        "'ActorFactory.create('",
        "'SEQUENCE'",
        "'ITE'",
        "'REPEAT'",
        "'PARALLEL'",
        "'ParallelPortfolio'",
        "'Joiner'",
        "'Setter'",
        "'Comparator'",
        "'Copy'",
        "'Rename'",
        "'TestSpecToSpec()'",
        "'SpecToTestSpec()'",
        "'ClassificationToActorDefinition()'",
        "'Identity'",
        "'ArtifactFactory.create('",
        "'.'",
        "'NOT'",
        "'INSTANCEOF'",
        "'ELEMENTOF'",
        "'TODO---'",
        "'''",
        "';'",
    ]

    symbolicNames = [
        "<INVALID>",
        "VERDICT",
        "BIN_OP",
        "ID",
        "STRING",
        "TYPE_NAME",
        "LETTER",
        "LOWER_CASE",
        "UPPER_CASE",
        "DIGIT",
        "NEWLINE",
        "WS",
        "DELIMITER",
        "COMMENT",
    ]

    ruleNames = [
        "T__0",
        "T__1",
        "T__2",
        "T__3",
        "T__4",
        "T__5",
        "T__6",
        "T__7",
        "T__8",
        "T__9",
        "T__10",
        "T__11",
        "T__12",
        "T__13",
        "T__14",
        "T__15",
        "T__16",
        "T__17",
        "T__18",
        "T__19",
        "T__20",
        "T__21",
        "T__22",
        "T__23",
        "T__24",
        "T__25",
        "T__26",
        "T__27",
        "T__28",
        "T__29",
        "T__30",
        "T__31",
        "T__32",
        "T__33",
        "VERDICT",
        "BIN_OP",
        "ID",
        "STRING",
        "TYPE_NAME",
        "LETTER",
        "LOWER_CASE",
        "UPPER_CASE",
        "DIGIT",
        "NEWLINE",
        "WS",
        "DELIMITER",
        "COMMENT",
    ]

    grammarFileName = "CoVeriLang.g4"

    def __init__(self, input=None, output: TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = LexerATNSimulator(
            self, self.atn, self.decisionsToDFA, PredictionContextCache()
        )
        self._actions = None
        self._predicates = None

    def action(self, localctx: RuleContext, ruleIndex: int, actionIndex: int):
        if self._actions is None:
            actions = dict()
            actions[34] = self.VERDICT_action
            self._actions = actions
        action = self._actions.get(ruleIndex, None)
        if action is not None:
            action(localctx, actionIndex)
        else:
            raise Exception("No registered action for:" + str(ruleIndex))

    def VERDICT_action(self, localctx: RuleContext, actionIndex: int):
        if actionIndex == 0:
            self.text = "RESULT_CLASS_FALSE"

        if actionIndex == 1:
            self.text = "RESULT_CLASS_TRUE"

        if actionIndex == 2:
            self.text = "RESULT_CLASS_OTHER"
