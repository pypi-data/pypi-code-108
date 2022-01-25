# Copyright 2021-2022, Barcelona Supercomputing Center (BSC), Spain
#
# This software was partially supported by the EuroHPC-funded project ADMIRE
#   (Project ID: 956748, https://www.admire-eurohpc.eu).
#
# This file is part of rpcc.
#
# rpcc is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# rpcc is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with rpcc.  If not, see
# <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib
from rpcc.transformers import FileTransformer, FileTransformerFactory


class Rpcc:
    """The main class for the DSL compiler."""
    transformer: FileTransformer

    def __init__(self, input_file: pathlib.Path, copyright_file: pathlib.Path, output_language: str,
                 header_outdir: pathlib.Path, impl_outdir: pathlib.Path) -> None:
        self.transformer = FileTransformerFactory.create_transformer(
            output_language,
            input_file,
            copyright_file,
            header_outdir,
            impl_outdir)

    def transform(self) -> None:
        self.transformer.transform()
