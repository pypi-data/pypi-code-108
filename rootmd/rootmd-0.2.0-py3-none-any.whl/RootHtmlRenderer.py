
from mistletoe.html_renderer import HTMLRenderer
# from subprocess import Popen, PIPE
# import select
import base64
from shutil import copyfile
# import re
import os
import logging
from .Executor import RootExecutor
# from . import log
from rich.logging import RichHandler
FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

"""
HTML renderer for mistletoe with ROOT code execution and asset injection.
"""

prismjs = """<script src="{}"></script>\n""".format( "https://cdnjs.cloudflare.com/ajax/libs/prism/1.26.0/prism.min.js" )
prismcss = """<link href="{}" rel="stylesheet" />\n""".format( "https://cdnjs.cloudflare.com/ajax/libs/prism/1.26.0/themes/prism-tomorrow.min.css" )
prismajs = '<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.26.0/plugins/autoloader/prism-autoloader.min.js" integrity="sha512-GP4x8UWxWyh4BMbyJGOGneiTbkrWEF5izsVJByzVLodP8CuJH/n936+yQDMJJrOPUHLgyPbLiGw2rXmdvGdXHA==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>'



doct = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>{title}</title>
    
    {head}

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto" rel="stylesheet"> 
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3.0.1/es5/tex-mml-chtml.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.26.0/plugins/inline-color/prism-inline-color.min.css" integrity="sha512-jPGdTBr51+zDG6sY0smU+6rV19GOIN9RXAdVT8Gyvb55dToNJwq2n9SgCa764+z0xMuGA3/idik1tkQQhmALSA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.26.0/plugins/inline-color/prism-inline-color.min.js" integrity="sha512-U2u7V7F0Yk6Cw3LrZMYBDKQ+FbGigq+Z0JhHI04iKjtNXZUm4RdHsJ4xVbJLTiIFhNZ/5/3M12I1wXQtvxXB/w==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>

    <style>
    html {{
        font-family: 'Roboto', sans-serif;
    }}

    .content {{
            max-width: 90%;
            margin: auto;
        }}
    @media (min-width:1200px) {{
        .content {{
            max-width: 75%;
        }}
    }}

    @media (min-width:1900px) {{
        .content {{
            max-width: 60%;
        }}
    }}

    .png {{
        display: inline-block;
        margin-left: auto;
        margin-right: auto;
        max-width: 100%;
    }}

    pre {{
        font-size: 0.9em!important;
        line-height: 0.9!important;
    }}


    .svg {{
        width: 100%;
    }}

    </style>
  </head>
  <body>
    <div class="content" >
    {body}
    </div>
  </body>
</html>"""

codetemplate = '<pre class="languag-{lang}"><code class="language-{lang}">{inner}</code></pre>'
divtemplate = '<div class="output" >' + codetemplate + '</div>'
imgtemplate = '<img src="{src}" class="{ext}"/>'




class RootHtmlRenderer(HTMLRenderer, RootExecutor):
    def __init__(self, *extras):
        RootExecutor.__init__(self, *extras)
        super().__init__(*extras)
        log.debug("RootHtmlRenderer")
        self.blockid = 0
        self.embed = False
        self.asset_prefix = ""
        self.asset_dir = ""
        self.title = ""
    
    def set( self, **kwargs ) :
        if "embed" in kwargs :
            self.embed = kwargs.get( "embed" )
        if "asset_dir" in kwargs :
            self.asset_dir = kwargs.get( "asset_dir" )
        if "asset_prefix" in kwargs:
            self.asset_prefix = kwargs.get( "asset_prefix" )
    
    def process_image_output(self, path):
        path = path.strip()
        _, ext = os.path.splitext( path )
        ext = ext.replace( ".", "" )

        if self.asset_dir != "" and not self.embed:
            print( "cp %s %s" % (path, self.asset_dir) )
            try :
                copyfile( path, self.asset_dir )
            except Exception as e:
                log.error( e )


        if self.embed:
            with open(path, "rb") as image_file:
                b64_encoded = base64.b64encode(image_file.read())
                template = '<img src="data:image/{ext};charset=utf-8;base64,{data}" class="{cls}"/>'

                if "svg" == ext:
                    ext = "svg+xml"

                return template.format( ext=ext, data=b64_encoded.decode(), cls=ext )
        else:
            return "\n" + imgtemplate.format( src=path, ext=ext )
    
    def divWrap(self, inner, cls="", id=""):
        output = "<div "
        if "" != cls:
            output = output + 'class="%s" ' % cls
        if "" != id:
            output = output + 'id="%s" ' % id
        output = output + ">\n"
        output = output + inner + "\n"
        output = output + "</div>"
        return output

    def render_block_code(self, token):
        # print( "CODE_BLOCK")
        code_block =  super().render_block_code(token)
        code =token.children[0].content
        if token.language:
            attr = ' class="{}"'.format('language-{}'.format(self.escape_html(token.language)))
        else:
            attr = ''
        if "cpp" == self.escape_html(token.language) :
            if "//noexec" in code:
                return code_block
            
            code_block = self.divWrap( code_block, "root-block-green")

            output, err, imgs = self.run_cmd( code )
            output = ("# Block [%d]\n" % self.blockid) + output

            # CONTROL OPTIONS
            if "noout" in code:
                output = ""
            if "noerr" in code:
                err = ""
            if "quiet" in code or "//q" in code:
                output = ""
                err = ""
            if "//qin" in code:
                code_block = "" # dont output the code
            
            # inject stdoutput 
            divout = '<div id="{id}" class="root-output" style="text-align: center;">'.format( id="root-output-%d" % (self.blockid) )
            if len( output + err ):
                divout += "\n" + divtemplate.format( lang="sh", inner=self.escape_html(output + err) )
            divout += '</div>'

            # inject images
            imgout = '<div id="{id}" class="root-images" style="text-align: center;">'.format( id="root-images-%d" % (self.blockid) )
            for i in imgs:
                imgout += self.process_image_output( i )
            imgout += '</div>'

            if "//qimg" in code or "//!img" in code:
                imgout = ""

            self.blockid = self.blockid + 1
            return code_block + self.divWrap( divout + imgout, "root-block", "root-output-block-%d" % (self.blockid - 1) )
        
        if "js" == token.language:
            template = '<script>\n{content}\n</script>'
            if "//qin" in code:
                code_block = "" # dont output the code
            if "//noexec" in code:
                return code_block
            code_block = self.divWrap( code_block, "root-block-green")
            return code_block + template.format(content=code)
        if "css" == token.language:
            template = '<style>\n{content}\n</style>'
            if "/* qin */" in code or "/*qin*/" in code:
                code_block = "" # dont output the code
            if "/*noexec*/" in code or "/* noexec */" in code:
                return code_block
            code_block = self.divWrap( code_block, "root-block-green")
            return code_block + template.format(content=code)
        if "html" == token.language:
            template = '<div>\n{content}\n</div>'
            if "<!--qin-->" in code or "<!-- qin -->" in code:
                code_block = "" # dont output the code
            if "<!--noexec-->" in code or "<!-- noexec -->" in code:
                return code_block
            code_block = self.divWrap( code_block, "root-block-green")
            return code_block + template.format(content=code)

        return code_block
        
    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        inner = '\n'.join([self.render(child) for child in token.children])
        return doct.format( title=self.title, head=(prismjs + prismcss + prismajs), body= '\n\n{}\n'.format(inner) if inner else '' )
