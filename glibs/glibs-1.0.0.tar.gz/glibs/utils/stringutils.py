import six
import unicodedata


def remove_accents(text):
    nkfd_form = unicodedata.normalize("NFKD", six.ensure_text(text))
    only_ascii = nkfd_form.encode("ascii", "ignore")
    return only_ascii.decode("utf-8")
