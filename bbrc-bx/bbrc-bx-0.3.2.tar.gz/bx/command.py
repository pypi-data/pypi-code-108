from datetime import datetime
import os.path as op
import logging as log
import os


class Command(object):
    def __init__(self, command, args, xnat_instance, destdir):
        self.command = command
        self.args = args
        self.xnat = xnat_instance
        self.destdir = destdir

    def run_id(self, id, func, **kwargs):
        from bx import xnat

        is_max_rows = False
        if 'max_rows' in kwargs:
            max_rows = kwargs['max_rows']
            kwargs.pop('max_rows')
            is_max_rows = True
        if 'CI_TEST' not in os.environ.keys():
            max_rows = None
            is_max_rows = True
        if is_max_rows:
            experiments = xnat.collect_experiments(self.xnat, id,
                                                   max_rows=max_rows)
        else:
            experiments = xnat.collect_experiments(self.xnat, id)
        return func(self.xnat, experiments, **kwargs)

    def to_excel(self, df):
        dt = datetime.today().strftime('%Y%m%d_%H%M%S')
        args = ''
        if len(self.args) != 0:
            args = '_' + '_'.join(self.args)

        fn = 'bx_%s%s_%s.xlsx' % (self.command, args, dt)
        fp = op.join(self.destdir, fn)
        log.info('Saving it in %s' % fp)
        df.to_excel(fp)
