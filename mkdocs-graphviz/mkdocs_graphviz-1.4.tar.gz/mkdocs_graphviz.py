"""
Graphviz extension for Markdown (e.g. for mkdocs) :
Renders the output inline, eliminating the need to configure an output
directory.

Supports outputs types of SVG and PNG. The output will be taken from the
filename specified in the tag, if given, or. Example:

in SVG:

```dot
digraph G {
    rankdir=LR
    Earth [peripheries=2]
    Mars
    Earth -> Mars
}
```

```graphviz dot attack_plan.svg
digraph G {
    rankdir=LR
    Earth [peripheries=2]
    Mars
    Earth -> Mars
}
```

in PNG:

```graphviz dot attack_plan.png
digraph G {
    rankdir=LR
    Earth [peripheries=2]
    Mars
    Earth -> Mars
}
```

Requires the graphviz library (http://www.graphviz.org/) and python 3

Inspired by jawher/markdown-dot (https://github.com/jawher/markdown-dot)
Forked from  cesaremorel/markdown-inline-graphviz (https://github.com/cesaremorel/markdown-inline-graphviz)
"""

import re
import markdown
import subprocess
import base64
import matplotlib

# Global vars
BLOCK_RE_GRAVE_ACCENT = re.compile(
        r'^[\s]*```graphviz[\s]+(?P<command>\w+)\s+(?P<filename>[^\s]+)\s*\n(?P<content>.*?)```\n$',
    re.MULTILINE | re.DOTALL)

BLOCK_RE_GRAVE_ACCENT_DOT = re.compile(
        r'^[ 	]*```dot\n(?P<content>.*?)```\s*$',
    re.MULTILINE | re.DOTALL)

GRAPHVIZ_COMMAND = 0

# Command whitelist
SUPPORTED_COMMAMDS = ['dot', 'neato', 'fdp', 'sfdp', 'twopi', 'circo']

# DEFAULT COLOR OF NODES, EDGES AND FONT TEXTS (MUST BE LOWER CASES)
DEFAULT_COLOR = '789abc'
DEFAULT_LIGHTTHEME_COLOR = '000000'
DEFAULT_DARKTHEME_COLOR = 'ffffff'

HTML_COLORS = {}
for name, hex in matplotlib.colors.cnames.items():
    HTML_COLORS[name] = matplotlib.colors.to_hex(hex, False)

class MkdocsGraphvizExtension(markdown.Extension):

    def __init__(self, **kwargs):
        self.config = {
            'color' :           [DEFAULT_COLOR, 'Default color for Nodes & Edges'],
            'lightcolor' :      [DEFAULT_LIGHTTHEME_COLOR, 'Default Light Color for Nodes & Edges'],
            'darkcolor' :       [DEFAULT_DARKTHEME_COLOR, 'Default Dark color for Nodes & Edges'],
            'bgcolor' :         ['none', 'Default bgcolor for Graph'],
            'graph_color' :     [DEFAULT_COLOR, 'Default color for Graphs & Subgraphs/Clusters Roundings'], 
            'graph_fontcolor' : [DEFAULT_COLOR, 'Default color for Graphs & Subgraphs/Clusters Titles'], 
            'node_color' :      [DEFAULT_COLOR, 'Default color for Node Roundings'], 
            'node_fontcolor' :  [DEFAULT_COLOR, 'Default color for Node Texts'],
            'edge_color' :      [DEFAULT_COLOR, 'Default color for Edge Roundings'],
            'edge_fontcolor' :  [DEFAULT_COLOR, 'Default color for Edge Texts']
        }
        super(MkdocsGraphvizExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """ Add MkdocsGraphvizPreprocessor to the Markdown instance. """
        md.registerExtension(self)

        md.preprocessors.add('graphviz_block',
                             MkdocsGraphvizPreprocessor(md, self.config),
                             "_begin")

class MkdocsGraphvizPreprocessor(markdown.preprocessors.Preprocessor):

    def __init__(self, md, config):
        super(MkdocsGraphvizPreprocessor, self).__init__(md)
        self.config = config
        self.set_html_colors()

    def set_html_colors(self):
        colorDict = self.config.keys()
        for colorKey in self.config.keys():
            self.config[colorKey][0] = self.config[colorKey][0].lower()
        if self.config['color'][0] in HTML_COLORS.keys():
            self.config['color'][0] = HTML_COLORS[self.config['color'][0]]
        else: # SET DEFAULT to #+'color'
            self.config['color'][0] = "#"+self.config['color'][0]
        for colorKey in colorDict:
            if colorKey in ['color', 'bgcolor', 'lightcolor', 'darkcolor']: # Special Keys
                continue
            if self.config[colorKey][0] in HTML_COLORS.keys():
                self.config[colorKey][0] = HTML_COLORS[self.config[colorKey][0]]
            elif self.config[colorKey][0] != DEFAULT_COLOR: # If more specific, set specific
                    self.config[colorKey][0] = "#"+self.config[colorKey][0]
            else: # otherwise set default to 'color' default
                self.config[colorKey][0] = self.config['color'][0]
            # print("colorKey=",colorKey,"=",self.config[colorKey][0])
        # SPECIAL KEYS:
        if self.config['lightcolor'][0] in HTML_COLORS.keys():
            self.config['lightcolor'][0] = HTML_COLORS[self.config['lightcolor'][0]]
        else: # SET DEFAULT to 'lightcolor'
            self.config['lightcolor'][0] = "#"+self.config['lightcolor'][0]
        if self.config['darkcolor'][0] in HTML_COLORS.keys():
            self.config['darkcolor'][0] = HTML_COLORS[self.config['darkcolor'][0]]
        else:
            self.config['darkcolor'][0] = "#"+self.config['darkcolor'][0]        
        if self.config['bgcolor'][0] in HTML_COLORS.keys():
            self.config['bgcolor'][0] = HTML_COLORS[self.config['bgcolor'][0]]
        elif self.config['bgcolor'][0] != 'None' and self.config['bgcolor'][0] != 'none': 
            self.config['bgcolor'][0] = "#"+self.config['bgcolor'][0]

    def repair_broken_svg_in(self, output):
        """Returns a repaired svg output. Indeed:
        The Original svg ouput is broken in several places:
        - in the DOCTYPE, after "\\EN". Does not break the code, but still
        - every "\n" line-end breaks admonitions: svg has to be inline in this function
        - "http://.." attribute in <!DOCTYPE svg PUBLIC ...> breaks mkdocs, which adds an '<a>' tag around it
        - in the comment tag, after '<!-- Generated by graphviz'. THIS BREAKS THE CODE AND HAS TO BE REPAIRED
        - in the svg tag, after the 'height' attribute; THIS BREAKS THE CODE AND HAS TO BE REPAIRED
        - first line "<!-- Title: ...  -->" breaks some graphs, it is totally removed"
        """
        encoding='utf-8'
        output = output.decode(encoding)
        lines = output.split("\n")
        newLines = []
        searchText = "Generated by graphviz"
        for i in range(len(lines)):
            if i+3 <= len(lines)-1 and ( (searchText in lines[i-1]) or (searchText in lines[i]) or (searchText in lines[i+1]) or (searchText in lines[i+2]) or (searchText in lines[i+3]) ) :
                continue
            if i>=3 and ("<svg" in lines[i-1] and searchText in lines[i-4]):
                continue
            if i>=3 and ("<svg" in lines[i] and searchText in lines[i-3]):
                s = lines[i]+lines[i+1]
                s = s[:-1]+""" class="graphviz dot">"""
                newLines.append(s)
            else:
                newLines.append(lines[i])
        newLines = newLines[1:]
        newOutput = "\n".join(newLines)
        xmlHeaders = f"""<span class="graphviz-light-dark" data-library-default="#{DEFAULT_COLOR}" data-default="{self.config['color'][0]}" data-light="{self.config['lightcolor'][0]}" data-dark="{self.config['darkcolor'][0]}"></span>"""
        # xmlHeaders += f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>"""
        # xmlHeaders += f"""<!-- Generated by graphviz {graphvizVersion} -->"""
        newOutput = xmlHeaders + newOutput
        newOutput = newOutput.replace("\n", "")

        return newOutput

    def read_block(self, text:str)->(str, int) or (None, -1):
        """Returns a tuple:
        - the graphviz or dot block, if exists, and
        - a code integer to caracterize the command : 
            0 for a'grapvhiz' command, 
            1 if 'dot' command)  
        or (None, None), if not a graphviz or dot command block"""
        blocks = [BLOCK_RE_GRAVE_ACCENT.search(text),
                  BLOCK_RE_GRAVE_ACCENT_DOT.search(text)]
        for i in range(len(blocks)):
            if blocks[i] is not None:
                return blocks[i], i
        return None, -1

    def get_decalage(self, command:str, text:str)->int:
        """Renvoie le décalage (nombre d'espaces) où commencent les ``` dans la ligne ```command ...
        Cela suppose que le 'text' réellement la commande, ce qui est censé être le cas lros de l'utilisation de cette fonction
        """
        # command = 'dot' or 'graphviz dot' or 'graphviz neato' or etc..
        i_command = text.find("```"+command)
        i_previous_linefeed = text[:i_command].rfind("\n")
        decalage = i_command - i_previous_linefeed-1
        return decalage

    def run(self, lines):
        """ Match and generate dot code blocks."""

        text = "\n".join(lines)
        while 1:
            m, block_type = self.read_block(text)
            if not m:
                break
            else:
                if block_type == GRAPHVIZ_COMMAND: # General Graphviz command
                    command = m.group('command')
                     # Whitelist command, prevent command injection.
                    if command not in SUPPORTED_COMMAMDS:
                        raise Exception('Command not supported: %s' % command)
                    filename = m.group('filename')
                    decalage = self.get_decalage("graphviz "+command, text)
                else: # DOT command
                    filename = "noname.svg"
                    command = "dot"
                    decalage = self.get_decalage(command, text)

                filetype = filename[filename.rfind('.')+1:]

                # RAW GRAPHVIZ BLOCK CONTENT
                content = m.group('content')
                args = [command, '-T'+filetype]

                try:
                    bgcolor = self.config['bgcolor'][0]
                    graph_color = self.config['graph_color'][0]
                    graph_fontcolor = self.config['graph_fontcolor'][0]
                    node_color = self.config['node_color'][0]
                    node_fontcolor = self.config['node_fontcolor'][0]
                    edge_color = self.config['edge_color'][0]
                    edge_fontcolor = self.config['edge_fontcolor'][0]

                    if self.config['bgcolor'][0] == 'None' or self.config['bgcolor'][0] == 'none':
                        args = [command, '-Gbgcolor=none', f'-Gcolor={graph_color}', f'-Gfontcolor={graph_fontcolor}', f'-Ncolor={node_color}', f'-Nfontcolor={node_fontcolor}', f'-Ecolor={edge_color}', f'-Efontcolor={edge_fontcolor}', '-T'+filetype]
                    else:
                        args = [command, f'-Gcolor={graph_color}', f'-Gfontcolor={graph_fontcolor}', f'-Gbgcolor={bgcolor}', f'-Ncolor={node_color}', f'-Nfontcolor={node_fontcolor}', f'-Ecolor={edge_color}', f'-Efontcolor={edge_fontcolor}', '-T'+filetype]

                    proc = subprocess.Popen(
                        args,
                        stdin=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE)
                    proc.stdin.write(content.encode('utf-8'))
                    output, err = proc.communicate()

                    if filetype == 'svg':
                        # OLD VERSION
                        # data_url_filetype = 'svg+xml'
                        # encoding = 'base64'
                        # output = self.repair_broken_svg_in(output)
                        # output = output.encode('utf-8')
                        # output = base64.b64encode(output).decode('utf-8')
                        # data_path = f"""data:image/{data_url_filetype};{encoding},{output}"""
                        # #img = " "*decalage+"![" + filename + "](" + data_path + ")"
                        # img = " "*decalage+f"""<img src="{data_path}" class="dot graphviz" />"""

                        # NEW VERSION
                        output = self.repair_broken_svg_in(output)
                        img = " "*decalage+f"""{output}"""

                    if filetype == 'png':
                        data_url_filetype = 'png'
                        encoding = 'base64'
                        output = base64.b64encode(output).decode('utf-8')
                        data_path = f"""data:image/{data_url_filetype};{encoding},{output}"""
                        img = " "*decalage+"<img src=\""+ data_path + "\" />"

                    text = '%s\n%s\n%s' % (
                        text[:m.start()], img, text[m.end():])

                except Exception as e:
                        err = str(e) + ' : ' + str(args)
                        return (
                            '<pre>Error : ' + err + '</pre>'
                            '<pre>' + content + '</pre>').split('\n')

        return text.split("\n")

def makeExtension(*args, **kwargs):
    return MkdocsGraphvizExtension(*args, **kwargs)
