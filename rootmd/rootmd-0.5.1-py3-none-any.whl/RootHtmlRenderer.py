
from mistletoe.html_renderer import HTMLRenderer
# from subprocess import Popen, PIPE
# import select
import base64
from shutil import copyfile
import rich
import re
import os
import logging
from .Executor import RootExecutor
from .Executor import GnuPlotExecutor
# from . import log
from rich.logging import RichHandler
from .YamlBlock import YamlFence, CodeFence
import yaml

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

"""
HTML renderer for mistletoe with ROOT code execution and asset injection.
"""

core_css = """

html {
        font-family: 'Roboto', sans-serif;
    }

    .content {
            max-width: 95%;
            margin: auto;
        }
    @media (min-width:1200px) {
        .content {
            max-width: 75%;
        }
    }

    @media (min-width:1900px) {
        .content {
            max-width: 60%;
        }
    }

    .png {
        display: inline-block;
        margin-left: auto;
        margin-right: auto;
        max-width: 100%;
    }

    pre {
        font-size: 0.9em!important;
        line-height: 0.9!important;
    }


    .svg {
        width: 100%;
    }

div.root-block pre {
    margin-top: 0px!important;
    /* margin-bottom: 0px!important; */
    border-left: 5px solid grey;
    border-right: 5px solid grey;
    border-bottom: 2px solid grey;
    border-top: 2px solid grey;
}

div.root-block-green pre {
    margin-top: 0px!important;
    margin-bottom: 0px!important;

    border-left: 5px solid #64dd17;
    border-right: 5px solid #64dd17;
    /* border-bottom: 2px solid #64dd17; */
    /* border-top: 2px solid #64dd17; */
}
"""

pygments_extra_css = """
pre {
  line-height: 1.5em !important;
  font-size: 1.1em !important;
}
"""


doct = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <meta name="author" content="{author}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>{title}</title>


    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto" rel="stylesheet"> 
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3.0.1/es5/tex-mml-chtml.js"></script>
    


    <!-- PRISM JS -->
        <!-- PRISM JS : core -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.26.0/prism.min.js" integrity="sha512-pSVqGtpGygQlhN8ZTHXx1kqkjQr30eM+S6OoSzhHGTjh6DKdfy7WZlo1DNO9bhtM0Imf6xNLznZ7iVC2YUMwJQ==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
        <!-- <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.26.0/themes/prism-okaidia.min.css" integrity="sha512-mIs9kKbaw6JZFfSuo+MovjU+Ntggfoj8RwAmJbVXQ5mkAX5LlgETQEweFPI18humSPHymTb5iikEOKWF7I8ncQ==" crossorigin="anonymous" referrerpolicy="no-referrer" /> -->


        <!-- PRISM JS : autoloader JS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.26.0/plugins/autoloader/prism-autoloader.min.js" integrity="sha512-GP4x8UWxWyh4BMbyJGOGneiTbkrWEF5izsVJByzVLodP8CuJH/n936+yQDMJJrOPUHLgyPbLiGw2rXmdvGdXHA==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>

        <!-- PRISM JS : inline -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.26.0/plugins/inline-color/prism-inline-color.min.css" integrity="sha512-jPGdTBr51+zDG6sY0smU+6rV19GOIN9RXAdVT8Gyvb55dToNJwq2n9SgCa764+z0xMuGA3/idik1tkQQhmALSA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.26.0/plugins/inline-color/prism-inline-color.min.js" integrity="sha512-U2u7V7F0Yk6Cw3LrZMYBDKQ+FbGigq+Z0JhHI04iKjtNXZUm4RdHsJ4xVbJLTiIFhNZ/5/3M12I1wXQtvxXB/w==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>

        <!-- PRISM JS : line-numbers -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.26.0/plugins/line-numbers/prism-line-numbers.min.js" integrity="sha512-dubtf8xMHSQlExGRQ5R7toxHLgSDZ0K7AunqPWHXmJQ8XyVIG19S1T95gBxlAeGOK02P4Da2RTnQz0Za0H0ebQ==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.26.0/plugins/line-numbers/prism-line-numbers.min.css" integrity="sha512-cbQXwDFK7lj2Fqfkuxbo5iD1dSbLlJGXGpfTDqbggqjHJeyzx88I3rfwjS38WJag/ihH7lzuGlGHpDBymLirZQ==" crossorigin="anonymous" referrerpolicy="no-referrer" />

    <style>
    {css}
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
imgtemplate = '<img src="{src}" class="{ext}  {ucls}"/>'

# autocanvast = 'TCanvas *canvas = new TCanvas( "c", "c", 1200, 900 )'
# autodrawt = 'if (canvas) { canvas->cd(0); canvas->Print("auto.svg"); }\n'



class RootHtmlRenderer(HTMLRenderer, RootExecutor):
    def __init__(self, *extras):
        RootExecutor.__init__(self, *extras)
        super().__init__(YamlFence, CodeFence)
        log.debug("RootHtmlRenderer")
        self.blockid = 0
        self.embed = False
        self.asset_prefix = ""
        self.asset_dir = ""
        self.clean = False
        self.no_exec = False

        # document meta
        self.title = ""
        self.author = ""
        self.description = ""
        self.keywords = ""
        self.theme = "light"
        self.prismjs_theme = "okaidia"
        self.yaml = {}

        # Control metadata
        self.autodraw = False

        # additional executors
        self.gnuplot = GnuPlotExecutor()
    
    def set( self, **kwargs ) :
        if "embed" in kwargs :
            self.embed = kwargs.get( "embed" )
        if "asset_dir" in kwargs :
            self.asset_dir = kwargs.get( "asset_dir" )
        if "asset_prefix" in kwargs:
            self.asset_prefix = kwargs.get( "asset_prefix" )
        if "clean"  in kwargs:
            self.clean = kwargs.get( "clean", False )
        if "no_exec"  in kwargs:
            self.no_exec = kwargs.get( "no_exec", False )

    def process_image_output(self, path, **kwargs):
        path = path.strip()
        _, ext = os.path.splitext( path )
        ext = ext.replace( ".", "" )

        if self.asset_dir != "" and not self.embed:
            print( "cp %s %s" % (path, self.asset_dir) )
            try :
                copyfile( path, os.path.join( self.asset_dir, path) )
            except Exception as e:
                log.error( 'Tried copyfile( "%s", "%s" ) ' % (path, self.asset_dir) )
                log.error( e )

        template = '<img src="data:image/{ext};charset=utf-8;base64,{data}" class="{cls} {ucls}"/>'
        if self.embed:
            with open(path, "rb") as image_file:
                b64_encoded = base64.b64encode(image_file.read())
                template = '<img src="data:image/{ext};charset=utf-8;base64,{data}" class="{cls} {ucls}"/>'

                if "svg" == ext:
                    ext = "svg+xml"

                return template.format( ext=ext, data=b64_encoded.decode(), cls=ext, ucls=kwargs.get("ucls", "") )
        

        if self.clean:
            try:
                os.remove( path )
            except Exception as e:
                rich.inspect(e)

        return "\n" + imgtemplate.format( src=path, ext=ext, ucls=kwargs.get("ucls", "") )
    
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

    def render_yaml_fence(self, token):
        log.info("YAML Fence")
        try:
            y = yaml.safe_load( token.children[0].content )
            self.process_yaml( y )
            # Do something here
        except yaml.YAMLError as e:
            log.error( e )

        token.language = "yaml"
        if self.yaml.get( "hide", False ) == True or self.yaml.get( "hide", False ) == "1" or self.yaml.get( "hide", False ) == 1 :
            return ""
        return super().render_block_code(token)

    def process_yaml( self, yaml ):
        self.yaml = yaml
        self.title = yaml.get( "title", self.title )
        self.author = yaml.get( "author", self.author )
        self.description = yaml.get( "description", self.description )
        self.keywords = yaml.get( "keywords", self.keywords )
        self.autodraw = yaml.get( "auto-draw", self.autodraw )


        # if self.autodraw:
        #     self.run_cmd( autocanvast )

    def process_gnuplot( self, token ):
        log.info( "gnuplot" )
        token.language = "python" # just for output syntax highlighting
        code_block =  super().render_block_code(token)
        code =token.children[0].content
        imgs = self.gnuplot.find_output( code )
        img_class = ""

        log.info( "Executing gnuplot" )
        self.gnuplot.run( code )

        # inject images
        imgout = '<div id="{id}" class="root-images" style="text-align: center;">'.format( id="root-images-%d" % (self.blockid))
        for i in imgs:
            imgout += self.process_image_output( i, ucls=img_class )
        imgout += '</div>'

        return code_block + self.divWrap(imgout, "gnuplot-block", "gnuplot-output-block-%d" % (self.blockid - 1) )
    

    """
    Code Fence is a custom Code Block token that accepts optional arguments after the language id
    example:
    ```cpp in:0
    ...
    ```

    the above turns off echoing the input to rendered document
    """
    def render_code_fence( self, token ):
        log.info( "render_code_fence" )
        return self.render_block_code( token )

    
    def optionAsBool( self, options, n, default = False ):
        # option is false by default
        if n not in options :
            return default
        return  not (options.get( n, "" ).lower() == 'false' or options.get( n, "" ) == '0')

    def process_cpp( self, token ):
        code_block =  super().render_block_code(token)
        code = token.children[0].content
        
        log.info( "exec: %r" % self.optionAsBool( token.options, "exec", True ) )
        log.info ("no-exec: %r" % self.no_exec)
        if self.optionAsBool( token.options, "exec", True ) == False or self.no_exec:
            log.info( "skipping execution of cpp code block" )
            return code_block

        # rich.inspect( token.options )
        # optional class for input code block
        input_class = token.options.get( ".in", "" ) + " root-block root-block-green"
        code_block = self.divWrap( code_block, input_class)

        # Execute the codez!
        output, err, imgs = self.run_cmd( code )
        output = ("# Block [%d]\n" % self.blockid) + output

        # output controls
        if self.optionAsBool( token.options, "out", True) == False or self.optionAsBool( token.options, "stdout", True) == False:
            output = ""
        elif "out" in token.options or "stdout" in token.options:
            stdout_filename = token.options.get("out", token.options.get( "stdout", "stdout.dat" ))
            log.info( "Writing block %d stdout to file: %s" % ( self.blockid, stdout_filename ) )
            with open( stdout_filename, "w" ) as wf:
                wf.writelines( output.split() )
        if self.optionAsBool( token.options, "err", True) == False or self.optionAsBool( token.options, "stderr", True) == False:
            err = ""
        elif "err" in token.options or "stderr" in token.options:
            stderr_filename = token.options.get("err", token.options.get( "stderr", "stderr.dat" ))
            log.info( "Writing block %d stderr to file: %s" % ( self.blockid, stderr_filename ) )
            with open( stderr_filename, "w" ) as wf:
                wf.writelines( err.split() )
        
        log.info( "silent? %r" % ('silent' in token.options) )
        if 'silent' in token.options or 'quiet' in token.options:
            output = ""
            err = ""

        if self.optionAsBool( token.options,'in', True) == False:
            code_block = ""
        
        img_class = token.options.get( ".image", "" )
        if self.optionAsBool( token.options, 'img', True ) == False:
            imgs = []

        # inject stdoutput 
        divout = '<div id="{id}" class="root-output" style="text-align: center;">'.format( id="root-output-%d" % (self.blockid) )
        if len( output + err ):
            divout += "\n" + divtemplate.format( lang="sh", inner=self.escape_html(output + err) )
        divout += '</div>'

        # inject images
        imgout = '<div id="{id}" class="root-images" style="text-align: center;">'.format( id="root-images-%d" % (self.blockid))
        for i in imgs:
            imgout += self.process_image_output( i, ucls=img_class )
        imgout += '</div>'

        lexer = get_lexer_by_name("c++")
        formatter = HtmlFormatter( style=self.yaml.get( "pygments-theme", "dracula" ))
        if code_block != ""  and self.yaml.get("highlight", "prismjs").lower() == "pygments" :
            code_block = highlight(code, lexer, formatter)

        self.blockid = self.blockid + 1
        return code_block + self.divWrap( divout + imgout, "root-block", "root-output-block-%d" % (self.blockid - 1) )

    def process_js(self, token):
        code =token.children[0].content
        template = '<script>\n{content}\n</script>'
        if "//qin" in code:
            code_block = "" # dont output the code
        if "//noexec" in code:
            return code_block
        code_block = self.divWrap( code_block, "root-block-green")
        return code_block + template.format(content=code)

    def process_css(self, token):
        code =token.children[0].content
        template = '<style>\n{content}\n</style>'
        if "/* qin */" in code or "/*qin*/" in code:
            code_block = "" # dont output the code
        if "/*noexec*/" in code or "/* noexec */" in code:
            return code_block
        code_block = self.divWrap( code_block, "root-block-green")
        return code_block + template.format(content=code)

    def process_html(self, token):
        code =token.children[0].content
        template = '<div>\n{content}\n</div>'
        if "<!--qin-->" in code or "<!-- qin -->" in code:
            code_block = "" # dont output the code
        if "<!--noexec-->" in code or "<!-- noexec -->" in code:
            return code_block
        code_block = self.divWrap( code_block, "root-block-green")

        return code_block + template.format(content=code)

    def render_block_code(self, token):
        log.info( 'block_code' )
        
        # code =token.children[0].content
        # if self.autodraw :
        #     code += autodrawt
        # rich.inspect( token )
        # log.info( code )
        # if token.language:
        #     attr = ' class="{}"'.format('language-{}'.format(self.escape_html(token.language)))
        # else:
        #     attr = ''

        if "gnuplot" == token.language or token.options.get( "exec", "" ) == "gnuplot":
            return self.process_gnuplot( token )

        if "cpp" == self.escape_html(token.language) or token.options.get( "exec", "" ) == "cpp":
            return self.process_cpp( token )
        
        if "js" == token.language:
            return self.process_js(token)

        if "css" == token.language:
            return self.process_css(token)

        if "html" == token.language:
            return self.process_html(token)

        code_block =  super().render_block_code(token)
        return code_block
    
    def loadCSS( self ):
        mycss = ""
        mydir = os.path.dirname(os.path.abspath(__file__))
        # log.info( mydir)
        prismjs_theme = self.yaml.get("prismjs_theme", self.yaml.get( "prismjs-theme", "okaidia" ))
        if  prismjs_theme in [ "a11y-dark","atom-dark","base16-ateliersulphurpool.light","cb","coldark-cold","coldark-dark","coy-without-shadows","darcula","dracula","duotone-dark","duotone-earth","duotone-forest","duotone-light","duotone-sea","duotone-space","ghcolors","gruvbox-dark","gruvbox-light","holi-theme","hopscotch","lucario","material-dark","material-light","material-oceanic","night-owl","nord","one-dark","one-light","pojoaque","shades-of-purple","solarized-dark-atom","synthwave84","vs","vsc-dark-plus","xonokai","z-touch", "coy","dark","funky","okaidia","solarizedlight","tomorrow","twilight" ]:
            with open( mydir + "/data/css/prismjs/prism-%s.css" % prismjs_theme ) as f:
                ncss = "".join(f.readlines())
                # log.info( ncss )
                mycss += "\n" + ncss
        return mycss

    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        inner = '\n'.join([self.render(child) for child in token.children])
        css = core_css
        if self.yaml.get("highlight", "prismjs").lower() == "prismjs" :
            try:
                css =css + self.loadCSS()
            except Exception as e:
                log.error( e )
        
        if self.yaml.get("highlight", "prismjs").lower() == "pygments":
            css = css + HtmlFormatter(style=self.yaml.get( "pygments-theme", "dracula" )).get_style_defs('.highlight') + pygments_extra_css
        return doct.format( 
                title=self.title, 
                description=self.description,
                author=self.author,
                keywords=self.keywords,
                css=css, 
                body= '\n\n{}\n'.format(inner) if inner else '' 
            )
