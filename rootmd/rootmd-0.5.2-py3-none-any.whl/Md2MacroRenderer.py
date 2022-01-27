from mistletoe.base_renderer import BaseRenderer



import rich
import logging
from rich.logging import RichHandler
FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


class Md2MacroRenderer(BaseRenderer):
    def __init__(self, *extras):
        super().__init__(*extras)
        
        self.blockid = 0
        self.embed = False
        self.asset_prefix = ""
        self.asset_dir = ""
        
    
    def set( self, **kwargs ) :
        if "embed" in kwargs :
            self.embed = kwargs.get( "embed" )
        if "asset_dir" in kwargs :
            self.asset_dir = kwargs.get( "asset_dir" )
        if "asset_prefix" in kwargs:
            self.asset_prefix = kwargs.get( "asset_prefix" )

    def render_block_code(self, token):
        template = '// %% ----------ROOTMD_START_BLOCK{id}----------\n{content}\n// %% ----------ROOTMD_END_BLOCK{id}----------\n'

        code =token.children[0].content
        output = template.format( id = self.blockid, content=token.children[0].content )

        self.blockid += 1
        return output

        

        
    
    def render_thematic_break(self, token):
        # inspect( token )
        return "---"

    @staticmethod
    def render_line_break(token):
        log.debug( 'line break' )
        return '\n' if token.soft else '\n'

    def render_inner( self, token ):
        return ''.join(map(self.render_raw_text, token.children))
    def render_raw_text(self, token):
        """
        Default render method for RawText. Simply return token.content.
        """
        if hasattr(token, 'content'):
            return "//" + token.content
        return self.render_inner( token )
    def render_to_plain(self, token):
        log.info( "render_to_plain" )
        # if hasattr(token, 'children'):
        #     inner = [self.render_to_plain(child) for child in token.children]
        #     return ( '//' + ''.join(inner))
        # return ("//" + token.content)
        return ""

    def render_heading(self, token):
        inner = self.render_inner(token)
        out = "#" * int(token.level) + " " + inner
        return out

    def render_document(self, token):
        # inner = '\n'.join([self.render(child) for child in token.children])
        inner = ""
        parts = []
        for child in token.children :
            log.info( child.__class__.__name__ )
            if "CodeFence" == child.__class__.__name__:
                parts.append( self.render( child ) )
            else:
                parts.append( self.render_raw_text( child ) )
            rich.inspect( child )
        inner = '\n'.join( parts )
        return inner
