#! /usr/bin/env python3

import curio
import hashlib
import os
import re
import zipfile


__all__ = ['Nidf', 'generate_hash', 'search_zipfile']


class Nidf:

    def __init__(self):
        self.items_queue = curio.Queue()
        self.paths_queue = curio.Queue()
        self.check_hash, self.check_zips, self.ignore_errors = False, False, False
        self.name_re, self._type = None, None
        self.master_hash = None

    async def __call__(
            self,
            root,
            *,
            name=None,
            _type=None,
            _hash=False,
            check_zips=False,
            ignore_errors=False,
        ):
        """
        An asyncrounus search file and/or directory search.

        Required:
            root (arg): a pathlike object for root. This is the initial starting point.
        Optional:
            name (kwarg): Regular expression to be used for matching
            _type (kwarg): "f" for file; "d" for directory
            _hash (kwarg): Filepath for hash to check
            check_zips (kwarg): If True, archives will be searched, too
            ignore_errors (kwarg): Suppress OSErrors. Default is False
        """
        self.ignore_errors = ignore_errors
        self.check_hash = True if _hash else False
        self.check_zips = check_zips
        self.name_re, self._type = name, _type
        await self.paths_queue.put(root)
        cpus = len(os.sched_getaffinity(0))
        cpus = cpus - 1 if cpus > 1 else 1
        async with curio.TaskGroup() as producers:
            await producers.spawn(self.delayed_producers, producers)
            for _ in range(10):
                await producers.spawn(self.crawler)
            if _hash:
                self.master_hash = generate_hash(name)
            async with curio.TaskGroup() as consumers:
                for _ in range(cpus):
                    await consumers.spawn(self.search)
                await self.paths_queue.join()
                await producers.cancel_remaining()
                await self.items_queue.join()
                await consumers.cancel_remaining()

    async def scan(self, root):
        """
        Producer for both the self.paths_queue and self.items_queue

        Required:
            root (arg): a pathlike object to scan with scandir
        """
        try:
            with os.scandir(root) as scanner:
                for entry in scanner:
                    if entry.is_dir():
                        await self.paths_queue.put(entry.path)
                    await self.items_queue.put(entry)
        except OSError as e:
            if not self.ignore_errors:
                print(e)

    async def crawler(self):
        """
        Initiator for the producer, `scan`

        Should not be interacted with directly.
        """
        while True:
            item = await self.paths_queue.get()
            crawl_task = await curio.spawn(self.scan, item)
            await crawl_task.join()
            await self.paths_queue.task_done()

    async def search(self):
        """
        Consumer for self.items_queue.

        Should not be interacted with directly.
        """
        while True:
            item = await self.items_queue.get()
            if self.check_zips and zipfile.is_zipfile(item.path):
                results = await curio.run_in_process(
                    search_zipfile, item.path, self.name_re, self.check_hash, self.master_hash
                )
                for result in results:
                    print(result)
            else:
                is_match = await self.match(item)
                if is_match:
                    print(item.path)
            await self.items_queue.task_done()

    async def match(self, item):
        """
        Checks PathLike item against specified filters. Returns item if match
        is found; else, None.

        Required:
            item (arg): PathLike object to test against
        """
        if self._type == 'd':
            if item.is_dir() and re.match(self.name_re, item.name):
                return item
        elif self._type == 'f':
            if item.is_file():
                if self.check_hash:
                    f_hash = await curio.run_in_process(generate_hash, item.path)
                    if f_hash == self.master_hash:
                        return item
                else:
                    if re.match(self.name_re, item.name):
                        return item
        else:
            if self.check_hash:
                f_hash = await curio.run_in_process(generate_hash, item.path)
                if f_hash == self.master_hash:
                    return item
            elif re.match(self.name_re, item.name):
                return item

    async def delayed_producers(self, group, sleep=.25, max_workers=1_000):
        """
        Produces additional consumers for the specified group every
        so may seconds as specified by sleep.
        Default number of max workers is 1_000

        Required:
            group (arg): The already created TaskGroup to attach the spawn to
        Optional:
            sleep (kwarg): The amount to wait between each cycle
            max_workers (kwarg): Maximum number of workers to create
        """
        worker_count = 0
        while worker_count <= max_workers - 100:
            for _ in range(100):
                worker_count += 1
                # These are daemons to prevent hangs while queues are joined
                await group.spawn(self.crawler, daemon=True)
            await curio.sleep(sleep)


def generate_hash(path, is_zip=False):
    """
    Generates an MD5 hash for the specified file

    Required:
        path (arg): A filepath or a PathLike object
    Optional:
        is_zip (kwarg): A Boolean for sending PathLike objects from ZIPs
    """
    if is_zip:
        with path.open('rb') as f:
            f_hash = hashlib.md5()
            while chunk := f.read(8192):
                f_hash.update(chunk)
    else:
        with open(path, 'rb') as f:
            f_hash = hashlib.md5()
            while chunk := f.read(8192):
                f_hash.update(chunk)
    return f_hash.digest()

def search_zipfile(zip_name, name_re, check_hash, master_hash):
    """
    Returns a list of matched items

    Required:
        zip_name (arg): ZIP-like object path
        name_Re (arg): Regex to match
        check_hash (arg): A Boolean to check for file hashes
        mster_hash (arg): The hash to check further files against
    """
    results = []
    def _iter_zip(path):
        _p = p.joinpath(path)
        for i in _p.iterdir():
            if i.is_dir():
                yield from _iter_zip(i.at)  # ".at" is undocumented :/
            yield i

    p = zipfile.Path(zip_name)
    for item in _iter_zip(''):
        if check_hash:
            f_hash = generate_hash(item, is_zip=True)
            if f_hash == master_hash:
               results.append(str(p.joinpath(item.name)))
        else:
            if re.match(name_re, item.name):
               results.append(str(p.joinpath(item.name)))
    return results

def clean_re_chars(name):
    # TODO: Make this handle the full gambit of re special chars
    return '^' + name.replace('.', '\.').replace('*', '.*') + "$"

async def main():
    import argparse, textwrap

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent('''\
Simple, striped down `find` replacement for use on NAS or slow disk drives. Results may be faster than `find` on SSDs for deep but not shallow searches. 
        \nThe "-z/--zips" flag will allow you to search inside zip-like objects.
        \nThe "--hash" option accepts an absolute filepath to generate a has to search.
        '''
        )
    )
    parser.add_argument(
            'path',
            nargs='?',
            help='Root location for the search. Default is cwd.',
        )
    name_group = parser.add_mutually_exclusive_group()
    name_group.add_argument(
            '-name',
            help='Case sensitive search. Accepts basic regular expressions.'
        )
    name_group.add_argument(
            '-iname',
            help='Case insensitive search. Accepts basic regular expressions.'
        )
    name_group.add_argument(
            '--hash',
            default=False,
            help='Flag for searching in archives. Default is False.',
        )
    parser.add_argument(
            '-type',
            choices=['d', 'f'],
            help='"f" for file; "d" for directory. Ignore for either.',
        )
    parser.add_argument(
            '-z',
            '--zips',
            action='store_true',
            default=False,
            help='Flag for searching in archives. Default is False.',
        )
    parser.add_argument(
            '--ignore_errors',
            action='store_true',
            default=False,
            help='Flag for suppressing OSErrors. Default is False.',
        )
    args = parser.parse_args()

    path = args.path if args.path else os.getcwd()
    if args.name:
        name = re.compile(clean_re_chars(args.name))
    elif args.iname:
        name = re.compile(clean_re_chars(args.iname), re.IGNORECASE)
    elif args.hash:
        name = args.hash
    else:
        name = re.compile('.*')
    kwargs = {
            'name': name,
            '_type': args.type,
            'ignore_errors': args.ignore_errors,
            'check_zips': args.zips,
            '_hash': args.hash,
        }
    find = Nidf()
    await find(path, **kwargs)


if __name__ == '__main__':
    curio.run(main)

