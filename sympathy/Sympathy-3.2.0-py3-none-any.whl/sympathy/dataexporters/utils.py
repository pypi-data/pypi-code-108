# This file is part of Sympathy for Data.
# Copyright (c) 2016, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from . base import (
    DataExporterLocator, TableDataExporterBase, TextDataExporterBase,
    ADAFDataExporterBase, DatasourceDataExporterBase, FigureDataExporterBase)


def table_exporter_factory(exporter_type):
    dil = DataExporterLocator(TableDataExporterBase)
    exporter = dil.exporter_from_name(exporter_type)
    return exporter


def text_exporter_factory(exporter_type):
    dil = DataExporterLocator(TextDataExporterBase)
    exporter = dil.exporter_from_name(exporter_type)
    return exporter


def adaf_exporter_factory(exporter_type):
    dil = DataExporterLocator(ADAFDataExporterBase)
    exporter = dil.exporter_from_name(exporter_type)
    return exporter


def datasource_exporter_factory(exporter_type):
    dil = DataExporterLocator(DatasourceDataExporterBase)
    exporter = dil.exporter_from_name(exporter_type)
    return exporter


def figure_exporter_factory(exporter_type):
    dil = DataExporterLocator(FigureDataExporterBase)
    exporter = dil.exporter_from_name(exporter_type)
    return exporter


def available_table_exporters():
    exporter_locator = DataExporterLocator(TableDataExporterBase)
    return exporter_locator.available_exporters()


def available_text_exporters():
    exporter_locator = DataExporterLocator(TextDataExporterBase)
    return exporter_locator.available_exporters()


def available_adaf_exporters():
    exporter_locator = DataExporterLocator(ADAFDataExporterBase)
    return exporter_locator.available_exporters()


def available_datasource_exporters():
    exporter_locator = DataExporterLocator(DatasourceDataExporterBase)
    return exporter_locator.available_exporters()


def available_figure_exporters():
    exporter_locator = DataExporterLocator(FigureDataExporterBase)
    return exporter_locator.available_exporters()
