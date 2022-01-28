#
# jomiel
#
# Copyright
#  2019 Toni Gündoğdu
#
#
# SPDX-License-Identifier: Apache-2.0
#
"""TODO."""
from jomiel.plugin.uri import PluginURIRefiner


class URIRefiner(PluginURIRefiner):
    """URI refiner implementation for YouTube."""

    __slots__ = ["regex"]

    def __init__(self):
        """Initializes the refiner object."""
        super().__init__()
        self.compile_regexes()

    def refine(self, uri_components):
        """The handler calls this class method to "demangle" the input
        URI before it sees if it can handle the URI.

        Args:
            uri_components (dict): The input URI components

        Returns:
            dict: The updated URI components

        """

        def is_youtube_uri():
            """Check if the given URI is a shortened YouTube URI."""
            netloc = uri.netloc.lower()
            return self.regex["netloc"].match(netloc)

        def capture_components():
            """Match and return the relevant URI components."""

            def match(pattern, in_string):
                """Return the captured text from a string."""
                result = self.regex[pattern].match(in_string)
                if result:
                    return result.group(1)
                raise ValueError

            result = {}
            for pattern in ["scheme", "netloc", "path"]:
                result[pattern] = match(pattern, getattr(uri, pattern))
            return result

        uri = uri_components
        if is_youtube_uri():
            try:
                result = capture_components()
                netloc = result["netloc"] if result["netloc"] else ""

                def replace(uri, **kwargs):
                    """Replace a component in the parsed URI."""
                    for name, value in kwargs.items():
                        uri = uri._replace(**{name: value})
                    return uri

                uri = replace(uri, netloc=netloc + "youtube.com")
                uri = replace(uri, scheme=result["scheme"])
                uri = replace(uri, path="/watch")
                uri = replace(uri, query="v=" + result["path"])
            except ValueError:  # Failed to match a pattern
                pass
        return uri

    def compile_regexes(self):
        """Compiles and caches the regexes used to match and modify the
        input URI.

        """
        from re import compile as rxc

        self.regex = {
            "scheme": rxc(r"(https?)$"),
            "netloc": rxc(r"(\w+\.)?youtu\.be$"),
            "path": rxc(r"/([\w\-_]{11})"),
        }


# vim: set ts=4 sw=4 tw=72 expandtab:
