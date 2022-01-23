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

from omfit_classes.harvest_lib import *
import numpy as np

__all__ = [
    'ddb_float',
    'harvest_send',
    'harvest_nc',  # from harvest_lib
    'OMFITharvest',
    'OMFITharvestS3',
    'dynamo_to_S3',
    'upload_harvestS3pickle',
]


class OMFITharvest(SortedDict):
    def __init__(self, table=None, convertDecimal=True, **kw):
        SortedDict.__init__(self)

        kw['table'] = table
        kw['convertDecimal'] = convertDecimal
        if 'Limit' in kw:
            kw['limit'] = kw.pop('Limit')
        kw.setdefault('limit', None)
        self.kw = kw
        self._client = None
        self.dynaLoad = True

    def _connect(self):
        self._client = boto3.resource(service_name='dynamodb', **boto_credentials())

    @dynaLoad
    def load(self):
        if not self._client:
            self._connect()
        self.clear()
        # get tables
        if self.kw['table'] is None:
            try:
                for table in [str(k.name) for k in self._client.tables.all()]:
                    self.kw['table'] = table
                    self[table] = OMFITharvest(**self.kw)
            finally:
                self.kw['table'] = None
        # get records
        else:
            for k, item in enumerate(self._get_table(**self.kw)):
                if item:
                    self[k] = item

    def _paginated_scan(self, verbose=True, **kw):
        import random
        from botocore.exceptions import ClientError

        table = kw.pop('table', self.kw['table'])
        limit = kw.pop('limit', self.kw.setdefault('limit', None))
        if isinstance(table, str):
            table = self._client.Table(table)

        if verbose:
            print('Starting to fetch data from table `%s`' % table.name)
            t0 = time.time()

        items = []
        readDB = 0.0
        scan_generator = None
        locked = False
        t0 = t1 = time.time()
        while readDB >= 0 and (limit is None or len(items) < limit):
            try:
                if scan_generator is None:
                    kw['Limit'] = 1
                    scan_generator = table.scan(ReturnConsumedCapacity='TOTAL', **kw)
                else:
                    ReadCapacityUnits = table.provisioned_throughput['ReadCapacityUnits']
                    if 'Limit' not in kw:
                        kw['Limit'] = max([len(scan_generator['Items']), CapacityUnits])
                    elif np.floor(CapacityUnits) > ReadCapacityUnits:
                        if not locked:
                            kw['Limit'] = max([kw['Limit'] / 2.0, kw['Limit'] * ReadCapacityUnits / CapacityUnits])
                        else:
                            kw['Limit'] -= 1
                    elif np.floor(CapacityUnits) < ReadCapacityUnits:
                        kw['Limit'] += 1
                        locked = True
                    kw['Limit'] = max([1, int(kw['Limit'])])
                    scan_generator = table.scan(ExclusiveStartKey=scan_generator['LastEvaluatedKey'], ReturnConsumedCapacity='TOTAL', **kw)
                CapacityUnits = scan_generator['ConsumedCapacity']['CapacityUnits']
                items.extend(scan_generator['Items'])
                readDB = 0.0
                if 'LastEvaluatedKey' not in scan_generator:
                    readDB = -1
                if verbose:
                    print(
                        'new:%d total:%d (%1.1f capacity - %3.1f records/second)'
                        % (len(scan_generator['Items']), len(items), CapacityUnits, len(scan_generator['Items']) / (time.time() - t1))
                    )
                t1 = time.time()

            except ClientError as _excp:
                if 'ResourceNotFoundException' in str(_excp):
                    raise
                readDB += random.random()
                if readDB > 3:
                    raise
                if verbose:
                    print('wait %3.3f seconds' % readDB)
                time.sleep(readDB)

        if verbose:
            print('Fetching data took %g seconds' % (time.time() - t0))
        if is_int(limit):
            return items[:limit]
        return items

    def _get_table(self, **kw):
        convertDecimal = kw.pop('convertDecimal', self.kw['convertDecimal'])

        items = self._paginated_scan(**kw)

        if convertDecimal:
            for item in items:
                for d in item:
                    if isinstance(item[d], decimal.Decimal) and not d.startswith('_hash'):
                        item[d] = float(item[d])
                    if isinstance(item[d], list):
                        item[d] = np.array(list(map(float, item[d])))

        return items

    def __getstate__(self):
        return {'kw': self.kw, 'dynaLoad': self.dynaLoad}, list(self.items())

    def __setstate__(self, tmp):
        self.__dict__.update(tmp[0])
        for key, value in tmp[1]:
            self[key] = self._setLocation(key, value)

    def _repr(self):
        line = []
        for k, v in list(self.kw.items()):
            if (k == 'table' and v is None) or (k == 'convertDecimal' and v == True):
                continue
            line.append('%s=%s' % (k, repr(v)))
        return ', '.join(line)

    def __repr__(self):
        return self.__class__.__name__ + "(%s)" % (self._repr())

    def __tree_repr__(self):
        if len(self._repr()):
            return self._repr(), []


class OMFITharvestS3(SortedDict):
    def __init__(
        self, table, verbose=-1, limit=None, long_term_storage=True, by_column=True, skip_underscores=True, numpy_arrays=False, **kw
    ):
        SortedDict.__init__(self)
        self.kw = {
            'table': table,
            'verbose': verbose,
            'limit': limit,
            'long_term_storage': long_term_storage,
            'by_column': by_column,
            'skip_underscores': skip_underscores,
            'numpy_arrays': numpy_arrays,
        }
        self.dynaLoad = True
        self._client = None

    def _connect(self):
        import boto3

        self._client = boto3.client('s3', **boto_credentials())

    def long_term_storage(self):
        if isinstance(self.kw['long_term_storage'], str):
            directory = self.kw['long_term_storage']
        elif self.kw['long_term_storage']:
            directory = (
                os.path.split(tolist(OMFIT['MainSettings']['SETUP']['projectsDir'])[0].rstrip(os.sep))[0] + os.sep + 'harvestS3storage'
            )
        else:
            directory = OMFITtmpDir + os.sep + 'harvestS3storage'
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory

    def list_items(self):
        if not self._client:
            self._connect()
        table = self.kw['table'].strip()
        if '/' not in table:
            table += '/'
        paginator = self._client.get_paginator('list_objects')
        operation_parameters = {'Bucket': 'gadb-harvest', 'Prefix': table}
        files = []
        page_iterator = paginator.paginate(**operation_parameters)
        for page in page_iterator:
            if 'Contents' in page:
                for item in page['Contents']:
                    if re.match(r'.*[0-9]+-[0-9]+\.[0-9]+$', item['Key']):
                        files.append(item['Key'])
                        if self.kw['verbose'] > 1:
                            printi('harvestS3 list: ' + item['Key'])
                    else:
                        if self.kw['verbose'] > 1:
                            printw('harvestS3 list: ' + item['Key'])
            else:
                raise ValueError('There are no S3 items that match: ' + self.kw['table'])
        return files

    def get(self, key):
        limit = 1e10
        if self.kw['limit'] and self.kw['limit'] >= 0:
            limit = self.kw['limit'] - len(self)
        if limit <= 0:
            return []

        filename = self.long_term_storage() + os.sep + key
        if not os.path.exists(os.path.split(filename)[0]):
            os.makedirs(os.path.split(filename)[0])

        # get details of the file
        if self.kw['verbose'] > 1:
            printi('harvestS3 querying %s' % key)
        response = self._client.get_object(Bucket='gadb-harvest', Key=key)

        # if the file is already in long-term storage directory
        if os.path.exists(filename) and os.stat(filename).st_size == response['ContentLength']:
            if self.kw['verbose'] > 0:
                printi('harvestS3 lts %s (%s)' % (key, sizeof_fmt(response['ContentLength'])))
            objs = OMFITpickle(filename, 'filename', limit, False)

        # if the file needs to be downloaded
        else:
            if self.kw['verbose'] > 0:
                printi('harvestS3 fetching %s (%s)' % (key, sizeof_fmt(response['ContentLength'])))
            pkl = response['Body'].read()
            with open(filename, 'wb') as f:
                f.write(pkl)
            objs = OMFITpickle(pkl, 'string', limit, False)

        # convert lists to np arrays
        if self.kw['numpy_arrays']:
            for item in objs:
                for key in item:
                    if isinstance(item[key], list):
                        item[key] = np.array(item[key])

        return objs

    @dynaLoad
    def load(self):
        """
        Download the data and unpack the nested pickle files
        """
        objs = []
        files = sorted(self.list_items())
        if self.kw['limit'] and self.kw['limit'] >= 0:
            files = files[: self.kw['limit']]
        elif self.kw['limit'] and self.kw['limit'] < 0:
            files = files[self.kw['limit'] :]
        if self.kw['verbose'] == -1:
            ascii_progress_bar(0, 0, len(files) - 1, newline=False, mess='harvestS3 [%d] %s' % (0, '---'))
        for k, key in enumerate(files):
            objs.extend(self.get(key))
            if self.kw['verbose'] == -1:
                ascii_progress_bar(k + 1, 0, len(files), newline=False, mess='harvestS3 [%d] %s' % (len(objs), key))
            if self.kw['limit'] and len(objs) >= self.kw['limit']:
                break
        self.clear()
        if self.kw['by_column']:
            self.update(self.get_array_form(var=None, datain=objs))
        else:
            self.update({k: v for k, v in enumerate(objs)})

    def get_array_form(self, var=None, datain=None):
        """
        Iterate over the table rows to get the values of :param var: or all variables if :param var: is ``None``

        :param var: Parameter to return (accumulated over all rows) or all variables if ``None``
        """
        if datain is None:
            datain = self
        if self.kw['by_column'] and datain is None and len(self) and not is_int(list(self.keys())[0]):
            if var is None:
                return {key: value for key, value in list(self.items()) if not self.kw['skip_underscores'] or not key.startswith('_')}
            elif var in self and isinstance(var, str):
                return self[var]
        data = {}
        for i in range(len(datain)):
            for k in set(list(datain[i].keys()) + list(data.keys())):
                if var is None and self.kw['skip_underscores'] and k.startswith('_'):
                    continue
                if k in datain[i]:
                    val = datain[i][k]
                else:
                    val = None
                if var is None:
                    if k in data:
                        data[k].append(val)
                    else:
                        data[k] = [None] * i
                        data[k].append(val)
                elif var == k:
                    if k in data:
                        data[k].append(val)
                    else:
                        data[k] = [None] * i
                        data[k].append(val)
        for k in data:
            try:
                data[k] = np.array(data[k], dtype=float)
            except ValueError:
                data[k] = np.array(data[k])
        if var is None:
            return data
        else:
            return data[k]

    def __repr__(self):
        return self.__class__.__name__ + "(%s)" % (', '.join(['%s=%s' % (x, repr(self.kw[x])) for x in self.kw]))

    def __tree_repr__(self):
        if self.dynaLoad:
            counts = '?'
        elif not len(self):
            counts = '!'
        elif self.kw['by_column']:
            counts = str(len(list(self.values())[0]))
        else:
            counts = str(len(self))
        return ['%s (%s)' % (self.kw['table'], counts), []]

    def __getstate__(self):
        tmp = SortedDict.__getstate__(self)
        tmp[0].pop('_client', None)
        return tmp

    def __setstate__(self, tmp):
        SortedDict.__setstate__(self, tmp)
        self._client = None

    def __deepcopy__(self, memo):
        return pickle.loads(pickle.dumps(self, pickle.HIGHEST_PROTOCOL))


def dynamo_to_S3(table, pickle_main_directory=os.environ['HOME'] + os.sep + 'harvest_database', upload=True, **kw):
    r"""
    This function fetches data in a OMFITharvest databases and saves it as OMFITharvestS3 pickle files

    :param table: dynamodb table to query

    :param pickle_main_directory: where to save the pickled files

    :param upload: upload pickle files to harvest S3 server

    :param \**kw: keyword arguments passed to the OMFITharvest call

    :return: list of strings with filenames that were created
    """
    verbose = kw.get('verbose', True)

    if isinstance(table, str):
        DB = OMFITharvest(table=table, **kw)
    else:
        DB = table
        table = DB.kw['table']

    pickle_main_directory = os.path.abspath(pickle_main_directory)

    def force_symlink(file1, file2):
        try:
            os.symlink(file1, file2)
        except OSError as _excp:
            if _excp.errno == errno.EEXIST:
                os.remove(file2)
                os.symlink(file1, file2)

    max_file_size_bytes = 10 * 1024 * 1024  # 10 MB

    for k, key in enumerate(sorted(list(DB.keys()), key=lambda x: DB[x]['_date'])):

        data = DB[key]

        tag = data.get('_tag', None)
        if tag is None:
            tag = '__untagged__'
        protocol = 'DYN'
        directory = os.sep.join([pickle_main_directory, table, tag, protocol])

        if not os.path.exists(directory):
            os.makedirs(directory)

        current = directory + os.sep + 'current'
        hash = directory + os.sep + 'hash'
        hash_history = {}
        if hash not in hash_history and os.path.exists(hash):
            hash_history[hash] = tolist(OMFITpickle(hash))
        else:
            hash_history[hash] = []

        if data['_hash_values'] in hash_history[hash]:
            if verbose:
                printw('skipped (%3.3f): %d' % (k / float(len(DB)), data['_hash_values']))
            continue
        else:
            if verbose:
                printi('added   (%3.3f): %d' % (k / float(len(DB)), data['_hash_values']))
        now_filename = directory + os.sep + datetime.datetime.fromtimestamp(data['_date']).strftime("%Y%m%d-%H%M%S.%f")
        if os.path.exists(current) and os.stat(current).st_size > max_file_size_bytes:
            os.remove(current)
        if not os.path.exists(current):
            open(now_filename, 'wb').close()
            force_symlink(now_filename, current)
        with open(os.path.realpath(current), 'ab') as file_data:
            pickle.dump(data, file_data)
        with open(hash, 'ab') as file_hash:
            pickle.dump(data['_hash_values'], file_hash)
        hash_history[hash].append(data['_hash_values'])

    files = glob.glob(pickle_main_directory + '/%s/*/*/*' % table)

    if upload:
        for filename in files:
            upload_harvestS3pickle(filename)

    return files


def upload_harvestS3pickle(filename):
    """
    Upload pickle file to harvest S3
    """
    import boto3

    s3connection = boto3.resource('s3', **boto_credentials())
    bucket = s3connection.Bucket('gadb-harvest')
    if os.path.split(filename)[1] != 'current':
        filename.split('/')[-4:]
        table, tag, protocol, file = filename.split('/')[-4:]
        s3key = os.sep.join([table, tag, protocol, file])
        printi('Uploading %s to S3' % s3key)
        with open(filename, 'rb') as f:
            bucket.put_object(Key=s3key, Body=f.read(), Metadata={'table': table, 'tag': tag}, ACL='public-read')


_harvest_send = harvest_send


def harvest_send(*args, **kw):
    return _harvest_send(*args, process=evalExpr, **kw)


harvest_send.__doc__ = _harvest_send.__doc__

# ========================
# Bug fix for boto3
# ========================

# from boto3.dynamodb import types
# _create_decimal=types.DYNAMODB_CONTEXT.create_decimal
# def create_decimal(value):
#     try:
#         return _create_decimal(value)
#     except Exception:
#         return _create_decimal(0)
# types.DYNAMODB_CONTEXT.create_decimal=create_decimal
