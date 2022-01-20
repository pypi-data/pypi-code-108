import glob
import os
import subprocess

import publisher.settings as settings
from publisher.translations.utils import get_locale_directory


def build_mo_files():

    for locale in settings.LOCALE_DIRECTORIES.keys():

        locale_directory = get_locale_directory(locale)
        if os.path.exists(locale_directory):
            django_po_file = os.path.join(locale_directory, 'django.po')
            django_mo_file = os.path.join(locale_directory, 'django.mo')

            if os.path.exists(django_po_file):
                os.remove(django_po_file)

            po_files = glob.glob(os.path.join(locale_directory, '*.po'))

            subprocess.check_output(['msgcat'] + po_files + ['-o', django_po_file])
            subprocess.check_output(['msgfmt', '-o', django_mo_file, django_po_file])
