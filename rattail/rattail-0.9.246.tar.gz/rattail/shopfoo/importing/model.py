# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2020 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Shopfoo model importers
"""

import shutil


class ProductImporterMixin(object):
    """
    Exporter target for Shopfoo product data
    """
    model_name = 'Product'
    allow_delete = False

    @property
    def export_model_class(self):
        raise NotImplementedError("You must define {}.export_model_class".format(
            self.__class__.__name__))

    def init_export(self, session):
        self.current_export = self.export_model_class(created_by=self.runas_user)
        session.add(self.current_export)
        session.flush()
        session.refresh(self.current_export)
        self.current_export.set_filename(self.config)
        self.record_count = 0

    def finalize_export(self):
        export = self.current_export

        # preserve final item count in the export record itself
        export.record_count = self.record_count

        if not self.dry_run:

            # copy output file to export's data path
            path = self.config.export_filepath(export.export_key,
                                               export.uuid,
                                               export.filename,
                                               makedirs=True)
            shutil.copyfile(self.output_file_path, path)
