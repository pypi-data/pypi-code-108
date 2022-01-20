import os
import re

from mkdpdf import configuration
from mkdpdf.document.document import Document
from mkdpdf.md.md import MD
from mkdpdf.pdf.pdf import PDF

class Documentation(Document):
    """
    Documentation is a Markdown or Portable Document Format document.
    """

    def __init__(self, format: str = configuration.FORMAT, filename: str = configuration.FILENAME, directory_path_output: str = configuration.DIRECTORY_PATH_OUTPUT, directory_name_templates: str = None):
        """
        Args:
            directory_name_templates (string): directory name of sub directory inside base templates directory
            directory_path_output (string): path of output directory
            filename (string): name of output file
            format (enum): md || pdf
        """

        # initialize inheritance
        super(Documentation, self).__init__(
            directory_name_templates=directory_name_templates,
            directory_path_output=directory_path_output,
            filename=filename,
            format=format
        )

    def SUBTEMPLATE_FUNCTIONS(self, functions):
        """
        Construct the methods section of a single markdown file.

        Args:
            functions (list): list of Python Function objects

        Returns:
             A string of markdown content for the class functions part.
        """

        return "%s%s" % (
            "### Methods%s" % configuration.GITFLAVOR_RETURN if functions[0].is_method else str(),
            configuration.GITFLAVOR_RETURN.join([
                "%s %s%s%s%s%s%s%s%s" % (
                    "#### _[method]_" if d.is_method else "## _[function]_",
                    d.function_name,
                    configuration.GITFLAVOR_RETURN,
                    "```python%sfrom %s import %s%s```" % (
                        configuration.GITFLAVOR_BREAK_RETURN,
                        ".".join(d.object_path.split(".")[0:-1]),
                        d.function_name,
                        configuration.GITFLAVOR_BREAK_RETURN
                    ) if not d.is_method else str(),
                    configuration.GITFLAVOR_RETURN,
                    configuration.GITFLAVOR_BREAK_RETURN.join(["_%s_" % f for f in d.descriptions]) if d.descriptions else str(),
                    "".join([
                        "%s**%s**: %s" % (
                            configuration.GITFLAVOR_RETURN,
                            d["key"],
                            d["value"]
                        ) for d in d.notes
                    ]) if d.notes else str(),
                    "%s%s" % (
                        configuration.GITFLAVOR_RETURN,
                        "_**Returns**_: %s" % d.returns
                    ) if d.returns else str(),
                    "".join([
                        "%s%s %s%s%s" % (
                            configuration.GITFLAVOR_RETURN,
                            "#####" if functions[0].is_method else "###",
                            d["key"],
                            configuration.GITFLAVOR_RETURN,
                            "| label | required | type | description | default |%s| :-- | :-- | :-- | :-- | :-- |%s" % (
                                configuration.GITFLAVOR_BREAK_RETURN,
                                "".join([
                                    "%s| %s | %s | %s | %s | %s |" % (
                                        configuration.GITFLAVOR_BREAK_RETURN,
                                        "`%s`" % v["key"] if v["key"] else str(),
                                        "✔" if v["required"] else str(),
                                        "**%s**" % v["type"] if v["type"] else str(),
                                        "<br>".join([
                                            "`%s`" % d.strip() for d in v["value"].split("|")
                                        ]) if "|" in v["value"] else v["value"],
                                        v["default"]
                                    )
                                    for v in d["values"]
                                ])
                            ) if d["values"] else str()
                        )
                        for d in d.attrs
                    ]) if d.attrs else str()
                )
                for d in functions
            ])
        ) if functions else str()

    def SUBTEMPLATE_INIT(self, pyclass):
        """
        Construct the class initialization.

        Args:
            pyclass (class): Python class object

        Returns:
             A string of markdown content for the class initialization.
        """

        return "### Initialization%s" % (
            "".join([
                "%s#### %s%s%s" % (
                    configuration.GITFLAVOR_RETURN,
                    d["key"],
                    configuration.GITFLAVOR_RETURN,
                    "| label | required | type | description | default |%s| :-- | :-- | :-- | :-- | :-- |%s" % (
                        configuration.GITFLAVOR_BREAK_RETURN,
                        "".join([
                            "%s| %s | %s | %s | %s | %s |" % (
                                configuration.GITFLAVOR_BREAK_RETURN,
                                "`%s`" % v["key"] if v["key"] else str(),
                                "✔" if v["required"] else str(),
                                "**%s**" % v["type"] if v["type"] else str(),
                                "<br>".join([
                                            "`%s`" % d.strip() for d in v["value"].split("|")
                                        ]) if "|" in v["value"] else v["value"],
                                v["default"]
                            )
                            for v in d["values"]
                        ])
                    ) if d["values"] else str()
                )
                for d in pyclass.init.attrs
            ])
        ) if pyclass.init and pyclass.init.attrs else str()

    def transpile(self, section: dict, template: str) -> str:
        """
        Replace placeholders in templates with provided content.

        Args:
            section (dictionary): key/value pairs to find/replace in package template
            template (string): partial section of document

        Returns:
            A string representing a partial in the file format of the template.
        """

        result = template

        # check if subtemplates are in result
        if result and "SUBTEMPLATE_" in result:

            # get subtemplates
            subtemplates = re.findall(r"SUBTEMPLATE_.+", result)

            # loop through subtemplates
            for placeholder in subtemplates:

                # get subtemplate method
                subtemplate_method = getattr(self, placeholder)

                # generate content for subtemplate
                subtemplate = subtemplate_method(section[placeholder])

                # update reference dictionary
                section[placeholder] = subtemplate

        # loop through keys
        for key in section:

            # set replacement content
            replacement = section[key]

            # look for markdown table format when processing pdf format
            if self.format == "pdf" and "| :-- |" in section[key]:

                # convert markdown to html
                replacement = self.document.table(section[key])

            # replace in template
            result = result.replace(key, replacement)

        return result
