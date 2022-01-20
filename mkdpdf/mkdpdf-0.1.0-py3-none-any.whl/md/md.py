import os

from mkdpdf import configuration

class MD:
    """
    MD is a Markdown render object.
    """

    def __init__(self, directory_path_templates: str):
        """
        Args:
            directory_path_templates (string): path of templates directory
        """

        # update self
        self.directory_path_templates = directory_path_templates

    def construct(self, header: str, main: str, footer: str) -> str:
        """
        Construct complete document.

        Args:
            footer (string): Markdown partial
            header (string): Markdown partial
            main (string): Markdown partial

        Returns:
            A string representing the complete document in Markdown format.
        """
        
        # construct content
        return "%s%s%s" % (
            header,
            main,
            footer
        )

    def render(self, content: str, file_path: str):
        """
        Render to filesystem as Markdown file.

        Args:
            content (string): markdown document
            file_path (string): ouput file path
        """

        # create file
        with open(file_path, "w") as file:

            # write content to file
            file.write(content)
