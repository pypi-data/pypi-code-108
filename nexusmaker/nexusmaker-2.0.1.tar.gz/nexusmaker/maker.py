from collections import defaultdict
from functools import lru_cache

from nexus import NexusWriter

from .CognateParser import CognateParser
from .tools import slugify, parse_parameter


class Record(object):
    def __init__(self, **kwargs):
        defaults = ['ID', 'Language_ID', 'Language', 'Parameter_ID', 'Parameter', 'Item', 'Loan', 'Cognacy']
        for key in defaults:
            setattr(self, key, None)
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __repr__(self):
        return "<Record %s - %s - %s - %s>" % (
            self.ID, self.Language, self.Parameter, self.Item
        )

    @property
    def is_loan(self):
        if self.Loan is None:
            return False
        elif self.Loan in (False, ""):
            return False
        elif self.Loan is True:
            return True
        else:
            return True

    def get_taxon(self):
        if self.Language_ID is None:
            return slugify(self.Language)
        else:
            return "%s_%s" % (slugify(self.Language), str(self.Language_ID))


class NexusMaker(object):

    def __init__(self, data, cogparser=None, remove_loans=True):
        self.data = [self._check(r) for r in data]
        self.cogparser = cogparser if cogparser else CognateParser(strict=True, uniques=True)

        # loans
        self.remove_loans = remove_loans
        if self.remove_loans:
            self.data = [r for r in data if not r.is_loan]

    def _check(self, record):
        """Checks that all records have the keys we need"""
        if getattr(record, 'Language', None) is None:
            raise ValueError("record has no `Language` %r" % record)
        if getattr(record, 'Parameter', None) is None:
            raise ValueError("record has no `Parameter` %r" % record)
        return record

    @lru_cache(maxsize=None)
    def _is_missing_for_parameter(self, language, parameter):
        """Returns True if the given `language` has no cognates for `parameter`"""
        cogs = [
            c for c in self._cognates if c[0] == parameter and language in self._cognates[c]
        ]
        return len(cogs) == 0

    @property
    def languages(self):
        if not hasattr(self, '_languages'):
            self._languages = {r.get_taxon() for r in self.data}
        return self._languages

    @property
    def parameters(self):
        if not hasattr(self, '_parameters'):
            self._parameters = {r.Parameter for r in self.data}
        return self._parameters

    @property
    def cognates(self):
        if not hasattr(self, '_cognates'):
            self._cognates = {}  # cognate sets (parameter, cogstate)
            # unique sets (language, parameter)
            uniques = {}
            # set of (language, parameter) pairs where a language already has a
            # cognate -- used for correct handling of uniques below.
            hascog = set()

            for rec in self.data:
                if self.remove_loans and rec.is_loan:
                    raise ValueError("%r is a loan!" % rec)

                for cog in self.cogparser.parse_cognate(rec.Cognacy):
                    if self.cogparser.is_unique_cognateset(cog):
                        uniques[(rec.get_taxon(), rec.Parameter)] = cog
                    else:
                        # add cognate
                        coglabel = (rec.Parameter, cog)
                        self._cognates[coglabel] = self._cognates.get(coglabel, set())
                        self._cognates[coglabel].add(rec.get_taxon())
                        hascog.add((rec.get_taxon(), rec.Parameter))

            # now handle special casing of uniques.
            # 1. If the language already has an entry for the parameter
            # that is cognate, then do nothing (i.e. we have identified
            # the cognate forms, the new form is something else, but we don’t
            # care).
            #
            # 2. If none of the forms are cognate for that Parameter P then the
            # language is assigned ONE unique cognate set regardless of how many
            # records there are in the database for that parameter in that
            # language i.e. we know it’s evolved a new cognate set, and 
            # it could be any one of the other forms, but we don’t care which
            # form.
            for (lang, parameter) in sorted(uniques):
                if (lang, parameter) not in hascog:
                    cog = uniques[(lang, parameter)]
                    assert (parameter, cog) not in self._cognates
                    self._cognates[(parameter, cog)] = set([lang])
                    hascog.add((lang, parameter))
        return self._cognates

    @lru_cache(maxsize=1024)
    def make_slug(self, parameter):
        return slugify(parameter.lower().replace(" ", "").replace("_", ""))

    def make_coglabel(self, parameter, cog):
        return "%s_%s" % (self.make_slug(parameter), cog)

    def make(self):
        nex = NexusWriter()
        for cog in sorted(self.cognates):
            if self.cogparser.is_unique_cognateset(cog[1]):
                assert len(self.cognates[cog]) == 1, \
                    "Cognate (%s, %s) should be unique but has multiple members" % cog
            else:
                assert len(self.cognates[cog]) >= 1, \
                    "%s = %r" % (cog, self.cognates[cog])

            for lang in self.languages:
                if lang in self.cognates[cog]:
                    value = '1'
                elif self._is_missing_for_parameter(lang, cog[0]):
                    value = '?'
                else:
                    value = '0'

                nex.add(slugify(lang), self.make_coglabel(*cog), value)
        nex = self._add_ascertainment(nex)  # handle ascertainment
        return nex

    def _add_ascertainment(self, nex):  # subclass this to extend
        return nex

    def display_cognates(self):  # pragma: no cover
        for cog in sorted(self.cognates):
            print(cog, sorted(self.cognates[cog]))

    def write(self, nex=None, filename=None):
        if nex is None:
            nex = self.make()

        if filename is None:
            return nex.write(charblock=True)
        else:
            return nex.write_to_file(filename, charblock=True)


class NexusMakerAscertained(NexusMaker):
    ASCERTAINMENT_LABEL = '_ascertainment_0'

    def _add_ascertainment(self, nex):
        """Adds an overall ascertainment character"""
        if self.ASCERTAINMENT_LABEL in nex.data:
            raise ValueError(
                'Duplicate ascertainment key "%s"!' % self.ASCERTAINMENT_LABEL
            )

        for lang in self.languages:
            nex.add(lang, self.ASCERTAINMENT_LABEL, '0')
        return nex


class NexusMakerAscertainedParameters(NexusMaker):

    ASCERTAINMENT_LABEL = '0ascertainment'

    def _add_ascertainment(self, nex):
        """Adds an ascertainment character per parameter"""
        for parameter in self.parameters:
            coglabel = self.make_coglabel(parameter, self.ASCERTAINMENT_LABEL)
            if coglabel in nex.data:  # pragma: no cover
                raise ValueError('Duplicate ascertainment key "%s"!' % coglabel)

            for lang in self.languages:
                if self._is_missing_for_parameter(lang, parameter):
                    nex.add(slugify(lang), coglabel, '?')
                else:
                    nex.add(slugify(lang), coglabel, '0')
        return nex

    def _get_characters(self, nex, delimiter="_"):
        """Find all characters"""
        chars = defaultdict(list)
        for site_id, label in enumerate(sorted(nex.data.keys())):
            parameter, cogid = parse_parameter(label, delimiter)
            chars[parameter].append(site_id)
        return chars

    def _is_sequential(self, siteids):
        return sorted(siteids) == list(range(min(siteids), max(siteids) + 1))

    def create_assumptions(self, nex):
        chars = self._get_characters(nex)
        buffer = []
        buffer.append("begin assumptions;")
        for char in sorted(chars):
            siteids = sorted(chars[char])
            # increment by one as these are siteids not character positions
            siteids = [s + 1 for s in siteids]
            assert self._is_sequential(siteids), 'char is not sequential %s' % char
            if min(siteids) == max(siteids):  # pragma: no cover
                # should not happen as we always have +1 for the
                # ascertainment character
                out = "\tcharset %s = %d;" % (char, min(siteids))
            else:
                out = "\tcharset %s = %d-%d;" % (char, min(siteids), max(siteids))
            buffer.append(out)
        buffer.append("end;")
        return buffer

    def write(self, nex=None, filename=None):
        if nex is None:
            nex = self.make()

        if filename is None:
            return nex.write(charblock=True) + "\n\n" + "\n".join(self.create_assumptions(nex))
        else:  # pragma: no cover
            nex.write_to_file(filename, charblock=True)
            with open(filename, 'a', encoding='utf8') as handle:
                handle.write("\n")
                for line in self.create_assumptions(nex):
                    handle.write(line + "\n")
                handle.write("\n")
            return True
