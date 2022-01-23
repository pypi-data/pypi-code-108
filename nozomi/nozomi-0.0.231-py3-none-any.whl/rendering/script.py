"""
Nozomi
Script Module
Author: hugh@blinkybeach.com
"""

from nozomi.rendering.render_dependency import RenderDependency


class Script(RenderDependency):
    """
    A javascript (.js) file required by a template
    """
    _EXTENSION = '.js'
    _NAME = 'Script'

    def __init__(
        self,
        filename: str,
        path: str = 'javascript/scripts/'
    ) -> None:

        super().__init__(
            script_name=filename,
            path=path,
            extension=self._EXTENSION,
            name=self._NAME
        )
        return
