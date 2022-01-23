"""
Nozomi
View Template Module
author: hugh@blinkybeach.com
"""
from nozomi.ancillary.configuration import Configuration
from typing import Optional
from nozomi.rendering.context import Context

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    Environment = None
    FileSystemLoader = None


class ViewTemplate:
    """
    An HTML template to be populated by runtime View data. Template rendering
    occurs in two stages. Stage 1 renders data known at application start, such
    as CSS files. Stage 2 renders data known at request time, such as a logged
    in user name . The two are separated by different Jinja2 templating
    markers.
    """

    _CACHED_LOADER: Optional[FileSystemLoader] = None
    _CACHED_S1_ENVIRONMENT: Optional[Environment] = None
    _CACHED_S2_ENVIRONMENT: Optional[Environment] = None
    _CACHED_PATH: Optional[str] = None

    def __init__(
        self,
        template_filename: str,
        static_context: Context,
        configuration: Configuration
    ) -> None:

        if Environment is None:
            raise NotImplementedError('Install jinja2')

        if self._CACHED_PATH is None:
            self._CACHED_PATH = configuration.template_directory
        
        if configuration.template_directory != self._CACHED_PATH:
            raise RuntimeError('template directory was changed')

        if self._CACHED_LOADER is None:
            self._CACHED_LOADER = FileSystemLoader(
                configuration.template_directory
            )

        if self._CACHED_S1_ENVIRONMENT is None:
            self._CACHED_S1_ENVIRONMENT = Environment(  # Static context
                loader=self._CACHED_LOADER,
                block_start_string='{&',
                block_end_string='&}',
                variable_start_string='+{',
                variable_end_string='}+'
            )

        stage_1_environment = self._CACHED_S1_ENVIRONMENT

        if self._CACHED_S2_ENVIRONMENT is None:
            self._CACHED_S2_ENVIRONMENT = Environment(
                loader=self._CACHED_LOADER,
                block_start_string='{%',
                block_end_string='%}',
                variable_start_string='{{',
                variable_end_string='}}'
            )

        stage_2_environment = self._CACHED_S2_ENVIRONMENT

        with open(template_filename) as template_file:
            template_string = template_file.read()
        self._stage_1_render = stage_1_environment.from_string(
            template_string
        ).render(static_context.context)
        self._template = stage_2_environment.from_string(self._stage_1_render)
        return

    def render(self, context: Optional[Context]) -> str:
        """
        Execute stage 2 render, returning a string HTML page for provision to
        a client.
        """
        if context is None:
            return self._template.render(Context().context)
        return self._template.render(**context.context)
