#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2014-2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2015-2016, 2018-2021 Chris Lamb <lamby@debian.org>
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <https://www.gnu.org/licenses/>.

import re

from diffoscope.tools import python_module_missing, tool_required
from diffoscope.difference import Difference

from .utils.file import File
from .utils.command import Command

try:
    import PyPDF2
except ImportError:  # noqa
    python_module_missing("PyPDF2")
    PyPDF2 = None


class Pdftotext(Command):
    @tool_required("pdftotext")
    def cmdline(self):
        return ["pdftotext", self.path, "-"]


class Dumppdf(Command):
    @tool_required("dumppdf")
    def cmdline(self):
        return ["dumppdf", "-adt", self.path]


class PdfFile(File):
    DESCRIPTION = "PDF documents"
    FILE_TYPE_RE = re.compile(r"^PDF document\b")

    def compare_details(self, other, source=None):
        xs = []

        if PyPDF2 is None:
            self.add_comment(
                "Installing the 'PyPDF2' package may produce a better output."
            )
        else:
            difference = Difference.from_text(
                self.dump_pypdf2_metadata(self),
                self.dump_pypdf2_metadata(other),
                self.path,
                other.path,
            )
            if difference:
                difference.add_comment("Document info")
            xs.append(difference)

            difference = Difference.from_text(
                self.dump_pypdf2_annotations(self),
                self.dump_pypdf2_annotations(other),
                self.path,
                other.path,
            )
            if difference:
                difference.add_comment("Annotations")
            xs.append(difference)

        xs.append(Difference.from_operation(Pdftotext, self.path, other.path))

        # Don't include verbose dumppdf output unless we won't see any any
        # differences without it.
        if not any(xs):
            xs.append(
                Difference.from_operation(Dumppdf, self.path, other.path)
            )

        return xs

    @staticmethod
    def dump_pypdf2_metadata(file):
        try:
            pdf = PyPDF2.PdfFileReader(file.path)
            document_info = pdf.getDocumentInfo()
        except PyPDF2.utils.PdfReadError as e:
            return f"(Could not extract metadata: {e})"

        if document_info is None:
            return ""

        xs = []
        for k, v in sorted(document_info.items()):
            xs.append("{}: {!r}".format(k.lstrip("/"), v))

        return "\n".join(xs)

    @staticmethod
    def dump_pypdf2_annotations(file):
        try:
            pdf = PyPDF2.PdfFileReader(file.path)
        except PyPDF2.utils.PdfReadError as e:
            return f"(Could not open file: {e})"

        xs = []
        for x in range(pdf.getNumPages()):
            page = pdf.getPage(x)

            try:
                for annot in page["/Annots"]:
                    subtype = annot.getObject()["/Subtype"]
                    if subtype == "/Text":
                        xs.append(annot.getObject()["/Contents"])
            except:
                pass

        return "\n".join(xs)
