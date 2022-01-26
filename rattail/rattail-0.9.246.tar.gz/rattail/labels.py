# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
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
Label Printing
"""

from __future__ import unicode_literals, absolute_import

import os
import os.path
import socket
import shutil

import six

from rattail.app import GenericHandler
from rattail.core import Object
from rattail.files import temp_path
from rattail.exceptions import LabelPrintingError
from rattail.time import localtime
from rattail.util import OrderedDict


class LabelHandler(GenericHandler):
    """
    Base class and default implementation for label handlers.
    """

    def get_formatter(self, profile, ignore_errors=False):
        """
        Return the label formatter for the given profile.

        :param profile: A
           :class:`~rattail.db.model.labels.LabelProfile` instance.

        :returns: A :class:`~rattail.labels.LabelFormatter` instance.
        """
        if not hasattr(self, 'label_formatters'):
            self.label_formatters = {}

        if not profile.formatter_spec:
            if ignore_errors:
                return
            raise ValueError("label profile has no formatter_spec: {}".format(
                profile))

        if profile.uuid not in self.label_formatters:
            factory = self.app.load_object(profile.formatter_spec)
            formatter = factory(self.config, template=profile.format)
            self.label_formatters[profile.uuid] = formatter

        return self.label_formatters[profile.uuid]

    def get_printer(self, profile, ignore_errors=False):
        """
        Return the label printer for the given profile.

        :param profile: A
           :class:`~rattail.db.model.labels.LabelProfile` instance.

        :returns: A :class:`~rattail.labels.LabelPrinter` instance.
        """
        if not hasattr(self, 'label_printers'):
            self.label_printers = {}

        if not profile.printer_spec:
            if ignore_errors:
                return
            raise ValueError("label profile has no printer_spec: {}".format(
                profile))

        if profile.uuid not in self.label_printers:

            # create the printer
            factory = self.app.load_object(profile.printer_spec)
            printer = factory(self.config)

            # establish settings for it
            for name in printer.required_settings:
                value = self.get_printer_setting(profile, name)
                setattr(printer, name, value)

            # give it a formatter
            printer.formatter = self.get_formatter(profile,
                                                   ignore_errors=ignore_errors)

            self.label_printers[profile.uuid] = printer

        return self.label_printers[profile.uuid]

    def get_printer_setting(self, profile, name):
        """
        Read a printer setting from the DB.
        """
        from rattail.db.api import get_setting

        if not profile.uuid:
            return
        session = self.app.get_session(profile)
        name = 'labels.{}.printer.{}'.format(profile.uuid, name)
        return get_setting(session, name)

    def save_printer_setting(self, profile, name, value):
        """
        Write a printer setting to the DB.
        """
        from rattail.db.api import save_setting

        session = self.app.get_session(profile)
        if not profile.uuid:
            session.flush()
        name = 'labels.{}.printer.{}'.format(profile.uuid, name)
        save_setting(session, name, value)

    def get_product_label_data(self, product, **kwargs):
        """
        Return a data dict with common product fields, suitable for
        use with formatting labels for printing.

        The intention is that this method should be able to provide
        enough data to make basic label printing possible.  In fact
        when printing is done "ad-hoc" for one product at a time, the
        data used for printing comes only from this method.

        :param product: A :class:`~rattail.db.model.products.Product`
           instance from which field values will come.

        :returns: Data dict containing common product fields.
        """
        data = {
            'description': product.description,
            'size': product.size,
        }

        brand = product.brand
        data['brand_name'] = brand.name if brand else None

        regprice = product.regular_price
        data['regular_price'] = regprice.price if regprice else None
        data['regular_pack_price'] = regprice.pack_price if regprice else None

        tprprice = product.tpr_price
        data['tpr_price'] = tprprice.price if tprprice else None
        data['tpr_starts'] = None
        if tprprice and tprprice.starts:
            starts = self.app.localtime(tprprice.starts, from_utc=True)
            data['tpr_starts'] = self.app.render_datetime(tprprice.starts)
        data['tpr_ends'] = None
        if tprprice and tprprice.ends:
            ends = self.app.localtime(tprprice.ends, from_utc=True)
            data['tpr_ends'] = self.app.render_datetime(tprprice.ends)

        salprice = product.sale_price
        data['sale_price'] = salprice.price if salprice else None
        data['sale_starts'] = None
        if salprice and salprice.starts:
            starts = self.app.localtime(salprice.starts, from_utc=True)
            data['sale_starts'] = self.app.render_datetime(salprice.starts)
        data['sale_ends'] = None
        if salprice and salprice.ends:
            ends = self.app.localtime(salprice.ends, from_utc=True)
            data['sale_ends'] = self.app.render_datetime(salprice.ends)

        curprice = product.current_price
        data['current_price'] = curprice.price if curprice else None
        data['current_starts'] = None
        if curprice and curprice.starts:
            starts = self.app.localtime(curprice.starts, from_utc=True)
            data['current_starts'] = self.app.render_datetime(curprice.starts)
        data['current_ends'] = None
        if curprice and curprice.ends:
            ends = self.app.localtime(curprice.ends, from_utc=True)
            data['current_ends'] = self.app.render_datetime(curprice.ends)

        sugprice = product.suggested_price
        data['suggested_price'] = sugprice.price if sugprice else None

        vendor = product.vendor
        data['vendor_name'] = vendor.name if vendor else None

        return data


class LabelPrinter(object):
    """
    Base class for all label printers.

    Label printing devices which are "natively" supported by Rattail will each
    derive from this class in order to provide implementation details specific
    to the device.  You will typically instantiate one of those subclasses (or
    one of your own design) in order to send labels to your physical printer.
    """

    profile_name = None
    formatter = None
    required_settings = None

    def __init__(self, config):
        self.config = config

    def print_labels(self, labels, *args, **kwargs):
        """
        Prints labels found in ``labels``.
        """
        raise NotImplementedError


class CommandPrinter(LabelPrinter):
    """
    Generic :class:`LabelPrinter` class which "prints" labels via native
    printer (textual) commands.  It does not directly implement any method for
    sending the commands to a printer; a subclass must be used for that.
    """

    def batch_header_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will be the first
        which are written to the file.
        """

        return None

    def batch_footer_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will be the last
        which are written to the file.
        """

        return None


class CommandFilePrinter(CommandPrinter):
    """
    Generic :class:`LabelPrinter` implementation which "prints" labels to a
    file in the form of native printer (textual) commands.  The output file is
    then expected to be picked up by a file monitor, and finally sent to the
    printer from there.
    """

    required_settings = {'output_dir': "Output Folder"}
    output_dir = None

    def print_labels(self, labels, output_dir=None, progress=None):
        """
        "Prints" ``labels`` by generating a command file in the output folder.
        The full path of the output file to which commands are written will be
        returned to the caller.

        If ``output_dir`` is not specified, and the printer instance is
        associated with a :class:`LabelProfile` instance, then config will be
        consulted for the output path.  If a path still is not found, the
        current (working) directory will be assumed.
        """

        if not output_dir:
            output_dir = self.output_dir
        if not output_dir:
            raise LabelPrintingError("Printer does not have an output folder defined")

        labels_path = temp_path(prefix='rattail.', suffix='.labels')
        labels_file = open(labels_path, 'w')

        header = self.batch_header_commands()
        if header:
            labels_file.write('%s\n' % '\n'.join(header))

        commands = self.formatter.format_labels(labels, progress=progress)
        if commands is None:
            labels_file.close()
            os.remove(labels_path)
            return None

        labels_file.write(commands)

        footer = self.batch_footer_commands()
        if footer:
            labels_file.write('%s\n' % '\n'.join(footer))

        labels_file.close()
        fn = '{0}_{1}.labels'.format(
            socket.gethostname(),
            localtime(self.config).strftime('%Y-%m-%d_%H-%M-%S'))
        final_path = os.path.join(output_dir, fn)
        shutil.move(labels_path, final_path)
        return final_path


# Force ordering for network printer required settings.
settings = OrderedDict()
settings['address'] = "IP Address"
settings['port'] = "Port"
settings['timeout'] = "Timeout"

class CommandNetworkPrinter(CommandPrinter):
    """
    Generic :class:`LabelPrinter` implementation which "prints" labels to a
    network socket in the form of native printer (textual) commands.  The
    socket is assumed to exist on a networked label printer.
    """

    required_settings = settings
    address = None
    port = None
    timeout = None

    def print_labels(self, labels, progress=None):
        """
        Prints ``labels`` by generating commands and sending directly to a
        socket which exists on a networked printer.
        """

        if not self.address:
            raise LabelPrintingError("Printer does not have an IP address defined")
        if not self.port:
            raise LabelPrintingError("Printer does not have a port defined.")

        data = six.StringIO()

        header = self.batch_header_commands()
        if header:
            header = "{0}\n".format('\n'.join(header))
            data.write(header.encode('utf_8'))

        commands = self.formatter.format_labels(labels, progress=progress)
        if commands is None: # process canceled?
            data.close()
            return None
        data.write(commands.encode('utf_8'))

        footer = self.batch_footer_commands()
        if footer:
            footer = "{0}\n".format('\n'.join(footer))
            data.write(footer.encode('utf_8'))

        try:
            timeout = int(self.timeout)
        except ValueError:
            timeout = socket.getdefaulttimeout()

        try:
            # Must pass byte-strings (not unicode) to this function.
            sock = socket.create_connection((self.address.decode('utf_8'), int(self.port)), timeout)
            bytes = sock.send(data.getvalue())
            sock.close()
            return bytes
        finally:
            data.close()


class LabelFormatter(Object):
    """
    Base class for all label formatters.
    """
    template = None

    def __init__(self, config, template=None):
        self.config = config
        self.app = self.config.get_app()
        if template:
            self.template = template

    @property
    def default_template(self):
        """
        Default formatting template.  This will be used if no template
        is defined within the label profile; see also
        :attr:`rattail.db.model.labels.LabelProfile.format`.
        """
        raise NotImplementedError

    def format_labels(self, labels, progress=None, **kwargs):
        """
        Formats a set of labels and returns the result.

        :param labels: Sequence of 2-tuples representing labels to be
           formatted, and ultimately printed.
        """
        raise NotImplementedError


class CommandFormatter(LabelFormatter):
    """
    Base class and default implementation for label formatters which
    generate raw printer commands for sending (in)directly to the
    printer device.

    There are various printer command languages out there; this class
    is not language-specific and should work for any of them.

    .. attribute:: template

       Formatting template.  This is a string containing a template of
       raw printer commands, suitable for printing a single label
       record.  Value for this normally comes from
       :attr:`rattail.db.model.labels.LabelProfile.format`.

       Normally these commands would print a "complete" label in terms
       of physical media, but not so for 2-up, in which case the
       template should only contain commands for "half" the label,
       i.e. only the commands to print one "record".

       There are 2 "languages" at play within the template:

       * template language
       * printer command language

       The template language refers to the syntax of the template
       itself, which ultimately will be "rendered" into a final result
       which should contain valid printer command language.  (See also
       :class:`~rattail.labels.CommandFormatter.format_labels()`.)
       Thus far there is only one template language supported,
       although it is likely more will be added in the future:

       * :ref:`python:old-string-formatting`

       The printer command language refers to the syntax of commands
       which can be sent to the printer in order to cause it to
       produce desired physical media, i.e. "formatted printed label".
       There are a number of printer command languages out there; the
       one you need to use will depend on the make and/or model and/or
       settings for your printer device.  Thus far the following
       languages have been used successfully:

       * `Cognitive Programming Language (CPL) <http://cognitivetpg.com/assets/downloads/105-008-04%20F(CPL%20ProgrammersGuide).pdf>`_
       * `Zebra Programming Language (ZPL) <https://en.wikipedia.org/wiki/Zebra_Programming_Language>`_

       A template example using ZPL:

       .. code-block:: none

          ^XA
          ^FO035,65^A0N,40,30^FD%(brand)-17.17s^FS
          ^FO035,110^A0N,30,30^FD%(description)s %(size)s^FS
          ^FO163,36^A0N,80,55^FB230,1,0,R,0^FD$%(price)0.2f^FS
          ^FO265,170,0^A0N,25,20^FD%(vendor)-14.14s^FS
          ^FO050,144^BY2%(barcode)s^FS
          ^XZ

       A template example using CPL for a 2-up layout:

       .. code-block:: none

          STRING 5X7 %(description_x)d 5 %(description1)s
          STRING 5X7 %(description_x)d 15 %(description2)s
          BARCODE %(barcode_type)s %(barcode_x)d 60 20 %(barcode)s
    """

    def format_labels(self, labels, progress=None, **kwargs):
        """
        Format a set of labels and return the result.  By "formatting"
        here we really mean generating a set of commands which
        ultimately will be submitted directly to a label printer
        device.

        Each of the ``labels`` specified should be a 2-tuple like
        ``(data, quantity)``, where ``data`` is a dict of record data
        (e.g. product description, price etc.) and ``quantity`` is the
        number of labels to be printed for that record.

        The formatter's :attr:`template` is "rendered" by feeding it
        the data dict from a single label record.  That process is
        repeated until all labels have been rendered.

        Note that the formatting template is only able to reference
        fields present in the ``data`` dict for any given label
        record.  If the incoming data is incomplete then you can add
        to it by overriding :meth:`get_all_data()`.

        :param labels: Sequence of 2-tuples representing labels to be
           formatted for printing.

        :param progress: Optional progress factory.

        :returns: Unicode string containing the formatted label data,
           i.e. commands to print the labels.
        """
        fmt = six.StringIO()

        def format_label(record, i):
            data, quantity = record
            product = data.get('product')
            if not product:
                return
            for j in range(quantity):
                header = self.label_header_commands()
                if header:
                    header = "{0}\n".format('\n'.join(header))
                    fmt.write(header.encode('utf_8'))
                data = self.get_all_data(data)
                body = "{}\n".format('\n'.join(self.label_body_commands(product, data)))
                if six.PY3:
                    fmt.write(body)
                else: # PY2
                    fmt.write(body.encode('utf_8'))
                footer = self.label_footer_commands()
                if footer:
                    footer = "{0}\n".format('\n'.join(footer))
                    fmt.write(footer.encode('utf_8'))

        self.app.progress_loop(format_label, labels, progress,
                               message="Formatting labels")

        if six.PY3:
            val = fmt.getvalue()
        else: # PY2
            val = fmt.getvalue().decode('utf_8')
        fmt.close()
        return val

    def get_all_data(self, data, **kwargs):
        """
        Returns the "complete' data dict for a given label record.

        When the caller asks us to format labels, it provides a data
        dict for each label to be printed.  This method is able to add
        more things to that data dict, if needed.

        Note that which fields are actually needed will depend on the
        contents of :attr:`template`.

        By default this will check the data dict for a ``'product'``
        key, and if there is a value, calls :meth:`get_product_data()`
        to add common product fields.

        :param data: Dict of data for a label record, as provided by
           the caller.

        :returns: Final data dict with all necessary fields.
        """
        if data.get('product'):
            data = self.get_product_data(data, data['product'])
        return data

    def get_product_data(self, data, product, **kwargs):
        """
        Add common product fields to the given data dict.

        The intention is that even if ``data`` is an empty dict, this
        method should be able to add enough data to make basic label
        printing possible.

        Default logic for this will call
        :meth:`rattail.labels.LabelHandler.get_product_label_data()`
        to get the product data dict, and then use ``data`` from the
        caller to override anything as needed, and return the result.

        :param data: Dict of data for a label record.

        :param product: A :class:`~rattail.db.model.products.Product`
           instance to which the label record applies, and from which
           additional field values will come.

        :returns: Final data dict including common product fields.
        """
        label_handler = self.app.get_label_handler()
        final_data = label_handler.get_product_label_data(product)
        final_data.update(data)
        return final_data

    def label_header_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will immediately
        precede each *label* in one-up printing, and immediately precede each
        *label pair* in two-up printing.
        """

    def label_body_commands(self, product, data, **kwargs):
        raise NotImplementedError

    def label_footer_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will immedately
        follow each *label* in one-up printing, and immediately follow each
        *label pair* in two-up printing.
        """


class TwoUpCommandFormatter(CommandFormatter):
    """
    Generic subclass of :class:`LabelFormatter` which generates native printer
    (textual) commands.

    This class contains logic to implement "two-up" label printing.
    """

    @property
    def half_offset(self):
        """
        The X-coordinate value by which the second label should be offset, when
        two labels are printed side-by-side.
        """
        raise NotImplementedError

    def format_labels(self, labels, progress=None, **kwargs):
        ""                      # avoid auto-generated docs
        fmt = six.StringIO()
        self.half_started = False

        def format_label(record, i):
            data, quantity = record
            product = data.get('product')
            if not product:
                return
            for j in range(quantity):
                kw = self.get_all_data(data)
                if self.half_started:
                    kw['x'] = self.half_offset
                    fmt.write('{}\n'.format('\n'.join(self.label_body_commands(product, kw))))
                    footer = self.label_footer_commands()
                    if footer:
                        fmt.write('{}\n'.format('\n'.join(footer)))
                    self.half_started = False
                else:
                    header = self.label_header_commands()
                    if header:
                        fmt.write('{}\n'.format('\n'.join(header)))
                    kw['x'] = 0
                    fmt.write('{}\n'.format('\n'.join(self.label_body_commands(product, kw))))
                    self.half_started = True

        self.app.progress_loop(format_label, labels, progress,
                               message="Formatting labels")

        if self.half_started:
            footer = self.label_footer_commands()
            if footer:
                fmt.write('{}\n'.format('\n'.join(footer)))

        val = fmt.getvalue()
        fmt.close()
        return val
