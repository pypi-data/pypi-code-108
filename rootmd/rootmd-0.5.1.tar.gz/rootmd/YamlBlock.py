from mistletoe.block_token import BlockToken
from mistletoe.span_token import SpanToken
from mistletoe import span_token 
import re
import rich


from rich.logging import RichHandler
import logging
FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

class YamlFence(BlockToken):
    """
    Yaml fence. (["---\\n", "title: Daniel /", ..., "---"])
    Boundary between span-level and block-level tokens.
    Attributes:
        children (list): contains a single span_token.RawText token.
        language (str): language of code block (default to empty). 
        Format of Code Fence kept so that it can be rendered as a Code Fence
    """
    pattern = re.compile(r'( {0,3})(-{3,}|~{3,}) *(\S*)')
    _open_info = None
    def __init__(self, match):
        log.info( "YsamlFence.__init__" )
        lines, open_info = match
        self.language = span_token.EscapeSequence.strip(open_info[2])
        self.children = (span_token.RawText(''.join(lines)),)

    @classmethod
    def start(cls, line):
        match_obj = cls.pattern.match(line)
        if not match_obj:
            return False
        prepend, leader, lang = match_obj.groups()
        # log.info( "PREPEND:" )
        # rich.inspect( prepend )
        # log.info( "LEADER:" )
        # rich.inspect( leader )
        # log.info( "LANG:" )
        # rich.inspect( lang )
        if leader[0] in lang or leader[0] in line[match_obj.end():]:
            return False
        cls._open_info = len(prepend), leader, lang
        return True

    @classmethod
    def read(cls, lines):
        next(lines)
        line_buffer = []
        for line in lines:
            stripped_line = line.lstrip(' ')
            diff = len(line) - len(stripped_line)
            if (stripped_line.startswith(cls._open_info[1])
                    and len(stripped_line.split(maxsplit=1)) == 1
                    and diff < 4):
                break
            if diff > cls._open_info[0]:
                stripped_line = ' ' * (diff - cls._open_info[0]) + stripped_line
            line_buffer.append(stripped_line)
        return line_buffer, cls._open_info


# class CodeFence(BlockToken):
#     """
#     Code fence. (["```sh\\n", "rm -rf /", ..., "```"])
#     Boundary between span-level and block-level tokens.
#     Attributes:
#         children (list): contains a single span_token.RawText token.
#         language (str): language of code block (default to empty).
#     """
#     pattern = re.compile(r'( {0,3})(`{3,}|~{3,}) *(\S*)')
#     _open_info = None
#     def __init__(self, match):
#         lines, open_info = match
#         self.options = {}
        
#         if len(lines) >= 1 :
#             log.info( lines[0] )
#             for l in lines[0].split() :
#                 m = re.match( "(.*):(.*)", l )
#                 if not m:
#                     continue
#                 self.options[ m.groups()[0] ] = m.groups()[1]

#             lines = lines[1:] # get rid of first line, since it wasnt done earlier in read

#         rich.inspect( lines )
#         rich.inspect( open_info )
#         self.language = span_token.EscapeSequence.strip(open_info[2])
#         self.children = (span_token.RawText(''.join(lines)),)
#         rich.inspect( self.options )
        

#     @classmethod
#     def start(cls, line):
#         match_obj = cls.pattern.match(line)
#         if not match_obj:
#             return False
#         prepend, leader, lang = match_obj.groups()
#         if leader[0] in lang or leader[0] in line[match_obj.end():]:
#             return False
#         cls._open_info = len(prepend), leader, lang
#         return True

#     @classmethod
#     def read(cls, lines):

#         line_buffer = []
#         index = 0
#         for line in lines:
#             if index == 0:
#                 continue
#             index += 1
#             stripped_line = line.lstrip(' ')
#             diff = len(line) - len(stripped_line)
#             if (stripped_line.startswith(cls._open_info[1])
#                     and len(stripped_line.split(maxsplit=1)) == 1
#                     and diff < 4):
#                 break
#             if diff > cls._open_info[0]:
#                 stripped_line = ' ' * (diff - cls._open_info[0]) + stripped_line
#             line_buffer.append(stripped_line)
#         return line_buffer, cls._open_info


class CodeFence(BlockToken):
    """
    Code fence. (["```sh\\n", "rm -rf /", ..., "```"])
    Boundary between span-level and block-level tokens.
    Attributes:
        children (list): contains a single span_token.RawText token.
        language (str): language of code block (default to empty).
    """
    pattern = re.compile(r'( {0,3})(`{3,}|~{3,}) *(\S*)')
    _open_info = None
    _options = {}
    def __init__(self, match):
        lines, open_info, options = match
        self.language = span_token.EscapeSequence.strip(open_info[2])
        self.children = (span_token.RawText(''.join(lines)),)
        self.options = options

    @classmethod
    def start(cls, line):
        match_obj = cls.pattern.match(line)
        if not match_obj:
            return False
        prepend, leader, lang = match_obj.groups()
        if leader[0] in lang or leader[0] in line[match_obj.end():]:
            return False
        cls._open_info = len(prepend), leader, lang
        return True

    @classmethod
    def read(cls, lines):
        ls = lines.lines[ lines._index+1]
        # log.info( ls.split()[0] )
        cls._options = {}
        for l in ls.split()[1:] :
            m = re.match( "(.*):(.*)", l )
            if not m:
                cls._options[ l ] = True
                continue

            cls._options[ m.groups()[0] ] = m.groups()[1]
        next(lines)
        line_buffer = []
        for line in lines:
            stripped_line = line.lstrip(' ')
            diff = len(line) - len(stripped_line)
            if (stripped_line.startswith(cls._open_info[1])
                    and len(stripped_line.split(maxsplit=1)) == 1
                    and diff < 4):
                break
            if diff > cls._open_info[0]:
                stripped_line = ' ' * (diff - cls._open_info[0]) + stripped_line
            line_buffer.append(stripped_line)
        return line_buffer, cls._open_info, cls._options