'''
parse 'initial_config' (also called as 'config') block
'''

import re

from . import config

class Context():
    def __init__(self):
        self.reset()


    def reset(self):
        self.mobj = {
                'Total Projectiles': 0,
                'Projectiles per Group': 1,
                'Total Groups': 0,
                'TIM_7': True}



class Parser():
    def __init__(self, context, debug=False):
        self.context = context

        # initial/projex.mfs PRJX1700-1760
        self.re_total_projs = re.compile(r'^Primary projectiles to be generated:\s*(?P<count>\d+)$')
        self.re_projs_per_group = re.compile(r'^Primary projectiles per group:\s*(?P<count>\d+)$')
        self.re_total_groups = re.compile(r'^Projectile groups to be generated:\s*(?P<count>\d+)$')

    def reset(self):
        self.context.reset()


    def parse(self, text):
        '''
        text: text block to parse
        '''


        for line in text.split('\n'):
            m = self.re_total_projs.fullmatch(line)
            if m:
                self.context.mobj['Total Projectiles'] = int(m['count'])
                continue

            m = self.re_projs_per_group.fullmatch(line)
            if m:
                self.context.mobj['Projectiles per Group'] = int(m['count'])
                self.context.mobj['TIM_7'] = False
                continue

            m = self.re_total_groups.fullmatch(line)
            if m:
                # this follows 'Primary projectiles per group:' condition
                assert(self.context.mobj['TIM_7'] == False)
                self.context.mobj['Total Groups'] = int(m['count'])
                continue

        # test relationships between Projectiles, Groups, Proj/Group

        if self.context.mobj['TIM_7']:
            assert(self.context.mobj['Projectiles per Group'] == 1)
            self.context.mobj['Total Groups'] = self.context.mobj['Total Projectiles']
        else:
            assert(self.context.mobj['Total Groups'] * self.context.mobj['Projectiles per Group'] \
                    == self.context.mobj['Total Projectiles'])

        return self.context.mobj



_context = Context()
_parser = Parser(_context, debug=config.debug_module_parser)

def _parse_using_prebuild_parser(text, debug=False):
    '''parse input text and returns context object'''
    _parser.reset()
    _parser.parse(text)
    return _context.mobj

parse = _parse_using_prebuild_parser

