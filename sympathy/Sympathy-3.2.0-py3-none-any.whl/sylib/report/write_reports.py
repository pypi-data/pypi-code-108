# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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
import os
import json
import sys

marker = '__WRITE_REPORT_MARKER__'


def main():
    """This function should always be run in its own process to avoid polluting
    the worker process with a QApplication.
    """
    (sys_path, template, signal_mapping, data_filename, data_type,
     file_format, save_path, prefix, input_filenames) = json.loads(sys.argv[1])

    sys.path[:] = sys_path

    from sympathy.api import adaf, table
    from sympathy.api import qt2 as qt
    from sylib.report import data_manager
    from sylib.report import models
    from sylib.report import binding
    from sylib.report import plugins
    from PySide2 import QtGui
    # QtGui = qt.QtGui  # noqa
    # Does not provide QtGui.QPageSize.
    QtWidgets = qt.QtWidgets  # noqa
    QtPrintSupport = qt.import_module('QtPrintSupport')

    fs_encoding = sys.getfilesystemencoding()

    def create_pdf(filename, pixmaps):
        printer = QtPrintSupport.QPrinter(
            QtPrintSupport.QPrinter.ScreenResolution)
        printer.setPageSize(QtGui.QPageSize(QtGui.QPageSize.A4))
        printer.setOutputFileName(filename)
        printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
        painter = QtGui.QPainter(printer)
        for i, pixmap in enumerate(pixmaps):
            painter.drawPixmap(0, 0, pixmap)
            if i < len(pixmaps) - 1:
                printer.newPage()
        painter.end()

        if printer.printerState() == QtPrintSupport.QPrinter.Idle:
            return True
        else:
            return False

    def file_type(data_type):
        if data_type == 'adafs':
            return adaf.FileList
        elif data_type == 'tables':
            return table.FileList
        else:
            assert(False)

    def warn(msg):
        sys.stderr.write("__WARNING__ ({})\n".format(msg))

    def error(msg):
        sys.stderr.write("__ERROR__ ({})\n".format(msg))
        sys.exit()

    def check_status(status, filename):
        if not status:
            error("Could not write to file {}".format(filename))
    # In this process it is safe to create a QApplication.
    app = QtWidgets.QApplication([])  # noqa

    # Extract all pages manually to get minimal size images for all pages.
    model = models.Root(json.loads(template))
    page_models = model.find_all_nodes_with_class(models.Page)
    page_count = len(page_models)

    # Create filenames for all pages.
    pdf_file = None
    if input_filenames is None:
        if not save_path:
            error("Please specify a save path.")
        if file_format == 'pdf':
            pdf_file = '{}.{}'.format(prefix, file_format)
        basenames = ['{}_{}.{}'.format(prefix, i, file_format)
                     for i in range(page_count)]
        input_filenames = [os.path.join(save_path, basename)
                           for basename in basenames]
    elif file_format != 'pdf':
        if len(input_filenames) < page_count:
            error("Not enough filenames.")
        elif len(input_filenames) > page_count:
            warn("Too many filenames.")
    # Read the data from the transfer file.
    if isinstance(data_filename, bytes):
        data_filename = data_filename.decode(fs_encoding)

    with file_type(data_type)(filename=data_filename, mode='r') as input_data:

        data_manager.init_data_source(input_data, data_type)
        data_manager.data_source.set_signal_mapping(json.loads(signal_mapping))

        QtWidgets.QApplication.processEvents()

        # Extract widgets.
        backend = plugins.backend_modules['mpl'].backend
        binding_context = binding.BindingContext()
        factory = backend.ItemFactory(binding_context)
        page_widgets = [factory._create_page(m) for m in page_models]

        # This hack is needed for matplotlib>=2.1.0. Without it all graphs
        # are empty when we grab the widgets again later.
        for page_widget in page_widgets:
            page_widget.grab()

        QtWidgets.QApplication.processEvents()

        # Write widgets to file.
        output_filenames = []
        pdf_pixmaps = []
        for i, (page_widget, filename) in enumerate(
                zip(page_widgets, input_filenames)):
            try:
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
            except (OSError, IOError):
                error("Could not create output directory {}".format(
                    os.path.dirname(filename)))
            pixmap = page_widget.grab()

            if file_format == 'pdf':
                pdf_pixmaps.append(pixmap)
            else:
                status = pixmap.save(filename, format=file_format)
                check_status(status, filename)
            output_filenames.append(filename)
        if file_format == 'pdf':
            if pdf_file is None:
                pdf_file = input_filenames[0]
            if os.path.splitext(pdf_file)[1] != '.pdf':
                error('Save filename is not a PDF.')
            status = create_pdf(pdf_file, pdf_pixmaps)
            check_status(status, pdf_file)
            output_filenames = [pdf_file]

        for page_widget in page_widgets:
            page_widget.deleteLater()

        QtWidgets.QApplication.processEvents()

        sys.stdout.write(marker)
        sys.stdout.write(json.dumps(output_filenames))


if __name__ == '__main__':
    main()
