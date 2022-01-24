# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Parse Git commit messages."""

# import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

from lark import Lark
from versioning.config import GRAMMAR_PATH


class CommitMessageParser:
    """Parse commit messages."""

    def __init__(
        self,
        grammar_path: str = GRAMMAR_PATH,
        start: str = 'message',
        **kwargs: Any
    ) -> None:
        """Initialize commit message parser."""
        # TODO: need to limit messages to 100 characters
        self.types = kwargs.pop('types', ['feat', 'fix'])
        self.scopes = kwargs.pop('scopes', [])
        self.__parser = Lark.open(grammar_path, start=start, **kwargs)

    def parse(
        self,
        text: str,
        start: Optional[str] = None,
        on_error: Optional[Callable] = None
    ) -> None:
        """Parse commit message."""
        self.__tree = self.__parser.parse(  # type: ignore
            text, start=start, on_error=on_error
        )

    def _get_section(self, name: str) -> Optional[Any]:
        """Get commit message section."""
        for arg in self.__tree.children:
            # NOTE: will not have parse tree for non-match
            if (
                hasattr(arg, '__dict__')
                and vars(arg)['data'] == name
            ):
                return arg
        return None

    @property
    def title(self) -> Dict[str, Any]:
        """Get title section of commit message."""
        title: Dict[str, Any] = defaultdict(lambda: None)
        section = self._get_section('title')
        if section:
            for arg in section.children:
                title[arg.data] = next((x.value for x in arg.children), True)
        return title

    @property
    def body(self) -> List[str]:
        """Get body section of commit message."""
        section = self._get_section('body')
        if section:
            return [arg.value for arg in section.children]
        else:
            return []

    @property
    def footer(self) -> Dict[str, Any]:
        """Get footer section of commit message."""
        footer: Dict[str, Any] = defaultdict(lambda: None)
        footer['issues'] = []

        section = self._get_section('footer')
        if section:
            for arg in section.children:
                if arg.data == 'trailer':
                    footer['trailer'] = {}
                    for x, y in enumerate(arg.children):
                        if x == 0:
                            footer['trailer']['token'] = y.value
                        if x == 1:
                            footer['trailer']['name'] = y.value
                        if x == 2:
                            footer['trailer']['email'] = y.value
                if arg.data == 'issue':
                    footer['issues'].append(
                        {arg.children[0].value: arg.children[1].value}
                    )
                if arg.data == 'breaking_change':
                    footer['breaking_change'] = next(
                        (x.value for x in arg.children),
                        'Unknown'
                    )
        return footer
