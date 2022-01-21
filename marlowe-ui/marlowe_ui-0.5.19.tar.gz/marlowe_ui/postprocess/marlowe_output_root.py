"""
Parse all marlowe output
"""

from .abstractparser import testframe
from .parserchain import ParserChain
from . import look
from . import cascade_group_number
from . import radial_range
from . import penetration
from . import slowing_down_time
from . import analysis_of_primary_recoil_ranges
from . import statistical_analysis_of_data


class Parser(ParserChain):
    def __init__(self):
        ParserChain.__init__(self)
        # (section name, parser, postprocess, number of iterations)
        self.parsers = [
            ('Look', look.Parser(), self.look_after, 1),
            ('Cascade', cascade_group_number.Parser(), self.cascade_group_number_after,
                '*'),
            ('Radial Range', radial_range.Parser(), self.radial_range_after, 1),
            ('Penetration', penetration.Parser(), self.penetration_after, 1),
            ('Slowing Down Time', slowing_down_time.Parser(),
                self.slowing_down_time_after, 1),
            ('Analysis of Primary Recoil Ranges',
                analysis_of_primary_recoil_ranges.Parser(),
                self.analysis_of_primary_recoil_ranges_after, 1),
            ('Statiatical Analysis of Data', statistical_analysis_of_data.Parser(),
                self.statistical_analysis_of_data_after, 1)]

    def look_after(self, mobj):
        self.mobj['Look'] = mobj

    def cascade_group_number_after(self, mobj):
        if 'Cascade' not in self.mobj:
            self.mobj['Cascade'] = []
        self.mobj['Cascade'].append(mobj)

    def radial_range_after(self, mobj):
        self.mobj['Radial Range'] = mobj

    def penetration_after(self, mobj):
        self.mobj['Penetration'] = mobj

    def slowing_down_time_after(self, mobj):
        self.mobj['Slowing Down Time'] = mobj

    def analysis_of_primary_recoil_ranges_after(self, mobj):
        self.mobj['Analysis of Primary Recoil Ranges'] = mobj

    def statistical_analysis_of_data_after(self, mobj):
        self.mobj['Statiatical Analysis of Data'] = mobj

    def match(self, strippedline):
        """always match"""
        return True

    def parse(self, einput, mobj=None):
        self.mobj = {}
        ParserChain.parse(self, einput)
        return self.mobj

if __name__ == '__main__':
    import sys
    testframe(Parser(), sys.stdin, sys.stdout)
