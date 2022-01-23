try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

from omfit_classes.omfit_ascii import *
from omfit_classes.omfit_weblink import OMFITwebLink
import numpy as np

__all__ = ['OMFITbibtex', 'searchdoi']

try:
    import bibtexparser
except Exception as _excp:
    bibtexparser = None
    printe('WARNING! Compromised omfit_bibtex support due to failure to import bibtexparser!')


class OMFITbibtex(OMFITascii, SortedDict):
    r"""
    Class used to parse bibtex files
    The class should be saved as a dictionary or dictionaries (one dictionary for each bibtex entry)
    Each bibtex entry must have defined the keys: `ENTRYTYPE` and `ID`

    :param filename: filename of the .bib file to parse

    :param \**kw: keyword dictionary passed to OMFITascii class

    To generate list of own publications:
    1. Export all of your citations from https://scholar.google.com to a `citation.bib` bibtex file
    2. OMFIT['bib']=OMFITbibtex('.bib')                   # load citations as OMFITbibtex
    3. OMFIT['bib'].doi(deleteNoDOI=True)                 # remove entries which do not have a DOI (ie.conferences)
    4. OMFIT['bib'].sanitize()                            # fix entries where needed
    4. OMFIT['bib'].update_ID(as_author='Meneghini')      # Sort entries and distinguish between first author or contributed
    5. print('\n\n'.join(OMFIT['bib'].write_format()))    # write to whatever format desired

    """

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self, caseInsensitive=True)
        if filename is None:
            from datetime import date

            self[0] = {'ID': os.environ['USER'] + str(date.today().year), 'ENTRYTYPE': 'article'}
        else:
            self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            bibtex_str = f.read()
        bib_database = bibtexparser.loads(bibtex_str)
        for k, item in enumerate(bib_database.get_entry_list()):
            label0 = label = item['ID']
            k = 0
            while label in self:
                k += 1
                label = label0 + '_%d' % k
            self[label] = item

    def write_format(self, form='\\item[]{{{author}; {title}; {journal} {volume} {year}: \\href{{http://dx.doi.org/{doi}}}{{doi:{doi}}}}}'):
        """
        returns list with entries formatted according to `form` string

        :param form: format to use to

        :return: list of strings
        """
        txt = []
        for item in list(self.keys()):
            tmp = self[item].copy()
            tmp['author'] = re.sub('others', 'et al.', ', '.join([re.sub(', *', ' ', x) for x in tmp['author'].split(' and ')]))
            tmp['volume'] = tmp.get('volume', '1')
            txt.append(form.format(**tmp))
        return txt

    @dynaSave
    def save(self):
        tmp = bibtexparser.bibdatabase.BibDatabase()
        tmp.entries = list(self.values())
        writer = bibtexparser.bwriter.BibTexWriter()
        bibtex_str = encode_ascii_ignore(bibtexparser.dumps(tmp))
        if self.filename is not None:
            with open(self.filename, 'w') as f:
                f.write(bibtex_str)
        else:
            return bibtex_str

    def doi(self, deleteNoDOI=False):
        """
        method for adding DOI information to bibtex

        :param deleteNoDOI: delete entries without DOI
        """
        for item in list(self.keys()):
            # only articles
            if (
                'doi' in self[item]
                or np.any([k not in self[item] for k in ['ENTRYTYPE', 'author', 'title', 'journal']])
                or self[item]['journal'].lower() in [x.lower() for x in _noDOIjournals]
                or self[item]['ENTRYTYPE'].lower() != 'article'
            ):
                printi('%s: %s' % (encode_ascii_ignore(item), self[item].get('doi', '')))
                continue

            # search for this paper
            tmp = searchdoi(self[item]['title'], self[item]['author'])
            self[item]['__doi__'] = tmp
            self[item]['doi'] = tmp[0]['DOI']
            self[item]['doi_score'] = tmp[0]['score']

            if self[item]['title'].lower() != tmp[0]['title'][0].lower():
                # if the title does not match exactly this is a bad sign
                printw('%s: %s' % (encode_ascii_ignore(item), self[item]['doi']))
            else:
                if np.all([k in tmp[0] for k in ['container-title', 'issue', 'page', 'publisher']]):
                    # trust the info from crossref.org
                    self[item]['journal'] = tmp[0]['container-title'][0]
                    self[item]['number'] = tmp[0]['issue']
                    self[item]['pages'] = tmp[0]['page']
                    self[item]['publisher'] = tmp[0]['publisher']
                    self[item]['author'] = ' and '.join(
                        [', '.join([_f for _f in [x.get('family', 'others'), x.get('given', '')] if _f]) for x in tmp[0]['author']]
                    )
                printi('%s: %s' % (encode_ascii_ignore(item), self[item]['doi']))

        # create URL entry based on DOI
        for item in list(self.keys()):
            if 'doi' in self[item]:
                self[item]['url'] = OMFITwebLink('doi.org/' + self[item]['doi'])
            elif deleteNoDOI:
                del self[item]

        # finar clearnup
        for item in list(self.keys()):
            if '__doi__' in self[item]:
                del self[item]['__doi__']
            if 'doi_score' in self[item]:
                del self[item]['doi_score']

    def sanitize(self):
        """
        Sanitizes the database entries:
        1. Fix all-caps author names
        2. Fix unicodes
        """
        for item in self:
            # Fix all-caps author names
            authors = self[item]['author'].split()
            for k, a in enumerate(authors):
                if '.' in a or len(a) > 2:
                    authors[k] = a.title()
            self[item]['author'] = ' '.join(authors)
            # Fix unicodes
            for sub in list(self[item].keys()):
                self[item][sub] = encode_ascii_ignore(self[item][sub])

    def filter(self, conditions):
        """
        filter database given a set of conditions

        :param conditions: list of strings (eg. ['int(year)>2012']

        :return: filtered OMFITbibtex object
        """
        conditions = tolist(conditions)
        self = copy.deepcopy(self)
        for condition in conditions:
            for item in list(self.keys()):
                try:
                    if not eval(condition, {}, self[item]):
                        del self[item]
                except Exception:
                    del self[item]
        return self

    def update_ID(self, fmt=['year_1stAuthor_jrnl', 'lower1stAuthor_year'][1], separator=':', as_author=False):
        """
        set bibtex ID

        :param fmt: string with format 'year_1stAuthor_jrnl'

        :param separator: string with separator for fmt

        :param as_author: only keep entries that have `as_author` as author
        """
        for item in list(self.keys()):
            tmp = self[item]
            del self[item]
            try:
                tmp['1stAuthor'] = tmp['author'].split()[0].strip(',')
                tmp['lower1stAuthor'] = tmp['1stAuthor'].lower()
            except Exception:
                pass
            try:
                tmp['jrnl'] = ''.join([x[0] for x in tmp['journal'].split()])
                tmp['lowerjrnl'] = tmp['jrnl'].lower()
            except Exception:
                pass
            label0 = label = separator.join([str(tmp[k]) for k in fmt.split('_')])
            if as_author:
                if as_author.lower() not in tmp['author'].lower():
                    continue
                if tmp['author'].split()[0].strip(',').lower() == as_author.lower():
                    label = label0 = '_' + label
            k = 0
            while label in self:
                k += 1
                label = label0 + '%s' % chr(k + ord('a'))
            for item in ['1stAuthor', 'jrnl', 'lower1stAuthor', 'lowerjrnl']:
                if item in tmp:
                    del tmp[item]
            self[label] = tmp
            self[label]['ID'] = label
        self.sort()
        return self


def searchdoi(title, author):
    """
    This function returns a list of dictionaries containing the best matching papers
    for the title and authors according to the crossref.org website

    :param title: string with the title

    :param author: string with the authors

    :return: list of dictionaries with info about the papers found
    """
    data = {"query.author": author.encode('utf-8'), "query.title": title.encode('utf-8')}
    url = "http://api.crossref.org/works?"

    import requests
    import json

    response = requests.get(url, data, verify=False)

    try:
        response.raise_for_status()
        return json.loads(response.text)['message']['items']
    except Exception:
        raise


_noDOIjournals = ['Bulletin of the American Physical Society', 'Bull. Am. Phys. Soc.']

############################################
if __name__ == '__main__':
    test_classes_main_header()
    import requests

    bibtex_text = '''
@article{meneghini2013integrated,
  title={Integrated modeling of tokamak experiments with OMFIT},
  author={Meneghini, Orso and Lao, Lang},
  journal={Plasma and Fusion Research},
  volume={8},
  pages={2403009--2403009},
  year={2013},
  publisher={The Japan Society of Plasma Science and Nuclear Fusion Research}
}

@article{meneghini2015integrated,
  title={Integrated modeling applications for tokamak experiments with OMFIT},
  author={Meneghini, O and Smith, SP and Lao, LL and Izacard, O and Ren, Q and Park, JM and Candy, J and Wang, Z and Luna, CJ and Izzo, VA and others},
  journal={Nuclear Fusion},
  volume={55},
  number={8},
  pages={083008},
  year={2015},
  publisher={IOP Publishing}
}
'''

    bib = OMFITbibtex('OMFIT_bibtex', fromString=bibtex_text)
    # filter
    filtered_bib = bib.filter(['int(year)>2014'])
    # sanitize
    filtered_bib.sanitize()
    # get the DOI (can take some time, and is thus best done after filtering)
    try:
        bib.doi()
    except requests.exceptions.HTTPError:
        pass
    pprint(filtered_bib)
