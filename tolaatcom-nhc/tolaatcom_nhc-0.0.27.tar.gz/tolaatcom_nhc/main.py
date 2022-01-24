
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED
import json
import logging
import time

from . import logconfig
from . import boto3factory
from . import one_case

class Main:

    def __init__(self):

        self.logger = logging.getLogger('headless.main')

        self.bucket = 'frankfurt-scraping'
        self.prefix = 'by-date/responses'

        self.checkpoint_f = None
        self.MAX_PENDING = 100

        self.work_in_progress = []
        self.head = None
        self.tail = None
        self.sent = 0
        self.pending = 0
        self.finished = 0
        self.futures = set()


    def get_s3(self):
        return boto3factory.client('s3')

    def iterate_date_files(self, start_date=None, end_date=None):
        s3 = self.get_s3()

        paginator = s3.get_paginator('list_objects_v2')

        if start_date is not None:
            prefix = f'{self.prefix}/{start_date}'
        else:
            prefix = f'{self.prefix}/'

        end_date = end_date or '9999'
        lastkey = f'{self.prefix}/{end_date}.txt'

        for r in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for row in r['Contents']:
                key = row['Key']
                if key > lastkey:
                    return
                yield row

    def iterate_cases(self):
        s3 = self.get_s3()
        for k in self.iterate_date_files():
            r = s3.get_object(Bucket=self.bucket, Key=k['Key'])
            body = r['Body'].read()
            body = body.decode('utf-8')
            lines = body.split('\n')
            for line in lines:
                j = json.loads(line)
                yield j

    def checkpoint(self, n):
        if self.checkpoint_f is None:
            self.checkpoint_f = open('checkpoint.txt', 'w')

        self.checkpoint_f.seek(0)
        self.checkpoint_f.write(n)
        self.checkpoint_f.flush()

    def get_checkpoint(self):
        try:
            c = open('checkpoint.txt', 'r').read()
            c = c.replace('\n', '')
            return c
        except:
            return None

    def close_checkpoint(self):
        if self.checkpoint_f is not None:
            self.checkpoint_f.close()
            self.checkpoint_f = None

    def submit(self, f, r):
        k = self.get_key(r)
        self.logger.info('Starting %s', k)
        try:
            s = r, f(r)
        except:
            self.logger.info('Failed %s', k, exc_info=True)
            raise
        self.logger.info('Finished %s', k)
        return s


    def harvest_results(self, completed_futures):
        for future in completed_futures:
            arg, r = future.result()
            key = self.get_key(arg)
            self.logger.info('Finished with  %s', key)
            self.work_in_progress.remove(key)

        self.pending -= len(completed_futures)
        self.finished += len(completed_futures)

        oldest = self.work_in_progress[0]
        if oldest != self.tail:
            self.logger.info('New tail: %s, was: %s', oldest, self.tail)
            self.checkpoint(oldest)
            self.tail = oldest

        elapsed = time.time() - self.started
        speed = round(self.finished / elapsed, 2)

        self.check_group()

        self.logger.info(f'Speed: %s, Harvested %s, Sent %s, Pending %s, Finished %s, Tail %s, Head %s, Work in progress %s',
                         speed, len(completed_futures),
                         self.sent, self.pending, self.finished, self.tail, self.head, len(self.work_in_progress))

    def get_key(self, r):
        return f'[{r["open_date"]},{r["CaseID"]},{r["CaseDisplayIdentifier"]}]'

    def start_thread(self):
        self.logger.info('Starting thread')

    def start_next_group(self):
        self.group_size = 100
        self.group_start = self.finished
        self.group_end = self.group_start + self.group_size

        self.group_started = time.time()

    def check_group(self):
        if self.finished >= self.group_end:
            done = self.finished - self.group_start
            elapsed = time.time() - self.group_started
            speed = round(done/elapsed, 2)
            self.logger.info('Group speed: did %s (from %s to %s) in %s (speed %s/s)', done, self.group_start,
                             self.finished, round(elapsed, 2), speed)
            self.start_next_group()

    def do_all(self):
        checkpoint =self.get_checkpoint()
        self.started = time.time()
        self.start_next_group()

        with ThreadPoolExecutor(max_workers=50, thread_name_prefix='headless_', initializer=self.start_thread) as tp:
            self.futures = set()
            o = one_case.OneCase()

            for r in main.iterate_cases():

                key = self.get_key(r)

                if checkpoint is not None:
                    if key != checkpoint:
                        self.logger.debug('Skipping %s, waiting for %s', key, checkpoint)
                        continue
                    else:
                        self.logger.info('Found checkpoint %s, continuing as usual', key)
                        checkpoint = None
                self.work_in_progress.append(key)
                self.head = key
                future = tp.submit(self.submit, o.handle, r)
                self.futures.add(future)
                self.sent += 1
                self.pending += 1
                while len(self.futures) > self.MAX_PENDING:
                    done, not_done = wait(self.futures, None, FIRST_COMPLETED)
                    self.harvest_results(done)
                    self.futures = not_done


            done, not_done = wait(self.futures, None, ALL_COMPLETED)
            assert len(not_done) == 0
            self.harvest_results(done)
            self.close_checkpoint()

if __name__ == '__main__':
    main = Main()
    main.do_all()
