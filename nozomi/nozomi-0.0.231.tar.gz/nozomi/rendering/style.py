"""
Nozomi
Style Module
Author: hugh@blinkybeach.com
"""
from nozomi.rendering.render_dependency import RenderDependency


class Style(RenderDependency):
    """
    A cascading style sheet (.css) file required by a template
    """
    _EXTENSION = '.css'
    _NAME = 'Style'

    def __init__(
        self,
        filename: str,
        path: str = 'styles/'
    ) -> None:

        super().__init__(
            script_name=filename,
            path=path,
            extension=self._EXTENSION,
            name=self._NAME
        )
        return
