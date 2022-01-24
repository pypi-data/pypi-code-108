import sys
from beancount import loader
from beancount.core import amount
from beancount.core import data
from beancount.parser import printer
__plugins__ = ['depreciation']

mca_table = {
    "Electronics": {"rate": 25.89, "life": 5, "scrap": 5},
    "Furniture": {"rate": 25.89, "life": 10, "scrap": 5},
    "Server": {"rate": 39.30, "life": 6, "scrap": 5},
    "Laptop": {"rate": 63.16, "life": 3, "scrap": 5},
    "Electrical": {"rate": 25.89, "life": 10, "scrap": 5},
    "Office": {"rate": 25.89, "life": 5, "scrap": 5}

}


def depreciation(entries, options_map):
    errors = []
    #print("entries=%s\n Options=%s\n \n" % (repr(entries), repr(options_map)))
    print("Plugin Invoked")
    for entry in entries:
        if isinstance(entry, data.Transaction):
            if entry.postings:
                for posting in entry.postings:
                    if 'depreciation_type' in posting.meta:
                        print("Depreciation Type=%s" %
                              (posting.meta['depreciation_type']))
                        table = mca_table[posting.meta['depreciation_type']]

    return entries, errors


if __name__ == "__main__":

    entries, errors, options = loader.load_file(
        'test.beancount', log_errors=sys.stderr)
    #depreciation(entries, options)
