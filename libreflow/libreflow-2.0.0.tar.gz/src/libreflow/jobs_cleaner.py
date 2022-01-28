import sys
import time
import argparse
from datetime import datetime, date, timedelta

from kabaret.app.session import KabaretSession
from kabaret.app.actors.flow import Flow

from libreflow.utils.kabaret.jobs.jobs_actor import Jobs


class CleanJobsSession(KabaretSession):

    @staticmethod
    def parse_command_line_args(args):
        base_args = KabaretSession.parse_command_line_args(args)
        base_args, remaining_args = base_args[:-1], base_args[-1]

        parser = argparse.ArgumentParser(
            description='Jobs Cleaning Session Arguments'
        )
        parser.add_argument(
            '-c', '--clean-time', type=str, default='13:00:00', dest='clean_time'
        )
        parser.add_argument(
            '-n', '--nb-days-before', type=int, default=1, dest='nb_days_before'
        )
        parser.add_argument(
            '-l', '--limit-time', type=str, default='19:00:00', dest='limit_time'
        )
        parser.add_argument(
            '-e', '--exclude-day', action='append', type=int, dest='exclude_days'
        )
        parser.add_argument(
            '-v', '--verbose', action='store_true', dest='verbose'
        )

        values, remaining_args = parser.parse_known_args(remaining_args)
        
        return base_args + (
            values.clean_time,
            values.nb_days_before, 
            values.limit_time,
            values.exclude_days,
            values.verbose,
            remaining_args
         )
    
    def __init__(self, session_name=None, debug=False, clean_time='13:00:00', nb_days_before=1, limit_time='19:00:00', exclude_days=None, verbose=False):
        super(CleanJobsSession, self).__init__(session_name, debug)
        self._clean_time = clean_time
        self._nb_days_before = nb_days_before
        self._limit_time = limit_time
        self._verbose = verbose

        if exclude_days is None:
            self._exclude_days = []
        else:
            self._exclude_days = exclude_days
    
    def _create_actors(self):
        Flow(self)
        Jobs(self)
    
    def start(self):
        if self._verbose:
            self.log_info('CLEANED JOBS')
            self.log_info(' %s | %s | %s | %s' % (
                'JOB ID'.center(36),
                'EMITTED ON'.center(17),
                'BY'.center(20),
                'DESCRIPTION'.center(97)
            ))
            self.log_info('-' * 180)
        
        try:
            if time.time() > self.get_clean_time_of_current_day():
                self.clean_jobs(self.get_limit_time())

            while True:
                time.sleep(self.get_next_clean_time() - time.time())

                if self.current_day_is_valid():
                    self.clean_jobs(self.get_limit_time())
        except KeyboardInterrupt:
            self.log_info('Cleaner stopped. Exiting...')
            return
    
    def get_limit_time(self):
        today = date.today()
        limit_day = (today - timedelta(days=self._nb_days_before)).strftime('%y-%m-%d')
        limit_timestamp = time.mktime(time.strptime('%s %s' % (limit_day, self._limit_time), '%y-%m-%d %H:%M:%S'))

        return limit_timestamp
    
    def get_clean_time_of_current_day(self):
        day = date.today()
        clean_timestamp = time.mktime(time.strptime('%s %s' % (day.strftime('%y-%m-%d'), self._clean_time), '%y-%m-%d %H:%M:%S'))
        
        return clean_timestamp

    def get_next_clean_time(self):
        clean_timestamp = self.get_clean_time_of_current_day()

        if time.time() > clean_timestamp:
            clean_timestamp += 86400.0
        
        return clean_timestamp
    
    def current_day_is_valid(self):
        return date.today().weekday() not in self._exclude_days
    
    def clean_jobs(self, timestamp):
        if self._verbose:
            last = datetime.fromtimestamp(time.time()).strftime('%y-%m-%d %H:%M:%S')
            next = datetime.fromtimestamp(self.get_next_clean_time()).strftime('%y-%m-%d %H:%M:%S')
            self.log_info(('Last clean: %s' % last).rjust(180))
            self.log_info(('Next clean: %s' % next).rjust(180))
        
        for j in self.cmds.Jobs.list_jobs():
            if j['created_on'] < timestamp:
                if self._verbose:
                    self.log_info(' %s | %s | %s | %s' % (
                        j['jid'],
                        datetime.fromtimestamp(j['created_on']).strftime('%y-%m-%d %H:%M:%S'),
                        j['creator'].center(20),
                        j['job_label']
                    ))
                
                self.cmds.Jobs.delete_job(j['jid'])


def main(argv):
    (
        session_name,
        host,
        port,
        cluster_name,
        db,
        password,
        debug,
        clean_time,
        nb_days_before,
        limit_time,
        exclude_days,
        verbose,
        _,
    ) = CleanJobsSession.parse_command_line_args(argv)

    session = CleanJobsSession(session_name=session_name, debug=debug, clean_time=clean_time, nb_days_before=nb_days_before, limit_time=limit_time, exclude_days=exclude_days, verbose=verbose)
    session.cmds.Cluster.connect(host, port, cluster_name, db, password)

    session.start()


if __name__ == "__main__":
    main(sys.argv[1:])