import time
import threading
import json
import logging
import datetime

from tolaatcom_nhc import boto3factory
from tolaatcom_nhc import nethamishpat
from tolaatcom_nhc.diff  import Diff

from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED


class OneCase:

    def __init__(self, master_table=None, config=None):
        self.config = config or {}
        self.master = master_table or 'master_table'
        self.bucket = 'cloud-eu-central-1-q97dt1m5d4rndek'
        self.prefix = 'documents_v2/decision_documents'
        self.local = threading.local()
        self.nhc = None
        self.default_storage = 'ONEZONE_IA'
        self.storage = self.config.get('storage_class', self.default_storage)


        self.logger = logging.getLogger('onecase')
        self.skip_documents = self.config.get('skip_documents', False)
        self.timeout = self.config.get('timeout', 25)
        self.only_one = self.config.get('only_one', False)


    def map_to_dynamo(self, m):
        d = {}
        for k, v in m.items():
            if v:
                d[k] = {'S': str(v)}
        return {'M': d}

    def list_to_dynamo(self, l):
        dl = []
        for s in l:
            del s['__type']
            dl.append(self.map_to_dynamo(s))

        return {'L': dl}

    def dynamo_to_list_of_maps(self, m):
        if not m or 'L' not in m:
            return []
        r = []
        for entry in m['L']:
            o = self.dynamo_to_map(entry)
            r.append(o)
        return r

    def dynamo_to_map(self, m):
        if not m or 'M' not in m:
            return []
        o = {}
        for k, v in m['M'].items():
            first = next(iter(v.values()))
            o[k] = first
        return o

    def upload_decisions(self, caseid, type, decisions, offset=0):
        s3 = boto3factory.client('s3')
        st = self.storage
        for index, decision in enumerate(decisions, offset):
            i = str(index).zfill(3)

            if decision.get('not-scraped'):
                self.logger.info('Not scraped')
                continue

            key = f'{self.prefix}/{caseid}/{type}/{i}.json'
            if 'images' in decision:
                j = json.dumps(decision['images'])
                self.logger.info('Writing to s3://%s/%s', self.bucket, key)
                s3.put_object(Bucket=self.bucket, Key=key, ContentType='application/json', Body=j, StorageClass=st)
                del decision['images']
            else:
                s3.delete_object(Bucket=self.bucket, Key=key)

            if 'pdf' in decision:
                key = f'{self.prefix}/{caseid}/{type}/{i}.pdf'
                self.logger.info('Writing to s3://%s/%s', self.bucket, key)
                s3.put_object(Bucket=self.bucket, Key=key, ContentType='application/pdf', Body=decision['pdf'],
                              StorageClass=st)
                decision['pdf'].close()
                del decision['pdf']

    def get_nhc(self):
        if not self.nhc:
            self.nhc = nethamishpat.NethamishpatApiClient(config=self.config)

        return self.nhc

    def remove_nhc(self):
        if self.nhc:
            self.nhc = None

    def init_permissions(self, key):
        dynamo = boto3factory.client('dynamodb')
        dynamo.update_item(TableName=self.master, Key=key, UpdateExpression='SET #p = if_not_exists(#p, :empty)',
                           ExpressionAttributeNames={'#p': 'permissions'},
                           ExpressionAttributeValues={':empty': {'M': {}}})

    def set_permissions(self, key, permission_name, reason):
        dynamo = boto3factory.client('dynamodb')

        self.init_permissions(key)

        value = {'M': {'ts': {'N': str(int(time.time()))}, 'reason': {'S': reason}}}

        dynamo.update_item(TableName=self.master, Key=key,
                                UpdateExpression='SET #ps.#p=:v',
                                ExpressionAttributeNames={'#ps': 'permissions', '#p': permission_name},
                                ExpressionAttributeValues={':v': value})

    def get_permission(self, key, permission):
        dynamo = boto3factory.client('dynamodb')

        r = dynamo.get_item(TableName=self.master, Key=key,
                        ProjectionExpression='#permissions.#permission',
                       ExpressionAttributeNames={'#permissions': 'permissions', '#permission': permission}
        )

        if not r['Item']:
            return None
        p = r['Item']['permissions']['M'][permission]['M']
        return p

    def is_govblocked(self, key):
        return self.get_permission(key, 'govblock') is not None

    def fetch(self, key):
        dynamo = boto3factory.client('dynamodb')
        fields = ('api', 'permissions')
        attribute_names = {f'#{attr}': attr for attr in fields}
        projection_expr_list = [f'#{attr}' for attr in fields]
        projection_expr = ', '.join(projection_expr_list)
        r = dynamo.get_item(TableName=self.master, Key=key,
                            ProjectionExpression=projection_expr,
                            ExpressionAttributeNames=attribute_names)

        return r.get('Item')

    def fetch_case_and_documents(self, key, decisions_type):
        assert decisions_type in ('decisions', 'verdicts')
        dynamo = boto3factory.client('dynamodb')
        attribute_names = {f'#api': 'api', '#case': 'case',  '#d': decisions_type}
        r = dynamo.get_item(TableName=self.master, Key=key,
                            ProjectionExpression='#api.#case, #api.#d',
                            ExpressionAttributeNames=attribute_names)

        return r.get('Item')

    def can_scrape(self, key):
        r = self.fetch(key)

        if 'Item' not in r:
            return True

        item = r['Item']
        return 'api' not in item and 'permissions' not in r


    def mark_govblock(self, case):
        case_id = case['CaseDisplayIdentifier']
        ct = case['CaseType']
        key = {'case_id': {'S': f'{ct}:{case_id}'}}
        if self.is_govblocked(key):
            logging.info('Case %s is already govblocked', case)
            return
        keys = [key]
        dynamo = boto3factory.client('dynamodb')

        r= dynamo.batch_get_item(RequestItems={self.master: {'Keys': keys}})
        if len(r['Responses'][self.master]) != 1:
            return
        item = r['Responses'][self.master][0]
        key = {'case_id': item['case_id']}
        self.set_permissions(key, 'govblock', 'unavailable')


    def get_key(self, case):
        case_number = case['CaseDisplayIdentifier']
        t = case['CaseType']
        self.logger.info('Key %s:%s', t, case_number)
        return {'case_id': {'S': f'{t}:{case_number}'}}


    def scrape_one_document(self, key, case, decision_type, index, decision):
        assert decision_type in ('verdicts', 'decisions')

        nhc = self.get_nhc()
        nhc.get_pdfs([decision])

        if decision.get('missing'):
            documents = nhc.get_documents(case, decision_type)
            decision['DocumentID'] = documents[index]['DocumentID']
            nhc.get_pdfs([decision])
            print()

        caseId = case['CaseID']

        self.upload_decisions(caseId, decision_type, [decision], index)

        dynamo = boto3factory.client('dynamodb')

        dec_dynamo = self.map_to_dynamo(decision)
        self.logger.info('setting %s[%s] to %s', decision_type, index, decision)
        r = dynamo.update_item(
            TableName=self.master,
            Key=key,
            UpdateExpression=f'set #api.#d[{index}] = :m',
            ExpressionAttributeNames={'#api': 'api', '#d': decision_type},
            ExpressionAttributeValues={':m': dec_dynamo}
        )

    def scrape_documents(self, key, case, decisions, verdicts,  decision_indices,
                         verdicts_indices, finish):

        futures = set()
        self.logger.info('Scraping documents. decisions %s, verdicts %s', decision_indices, verdicts_indices)

        with ThreadPoolExecutor(max_workers=10) as tp:
            for indices, array, d_type in [
                    (decision_indices, decisions, 'decisions'),
                    (verdicts_indices, verdicts, 'verdicts')]:
                for index in indices:
                    future = tp.submit(self.scrape_one_document,
                                key, case, d_type, index, array[index])

                    futures.add(future)


            timeout = finish - time.time()
            self.logger.info('%s futures, timeout is %s', len(futures), timeout)

            while futures and time.time() < finish:
                done, futures = wait(futures,  finish - time.time(), FIRST_COMPLETED)
                for f in done:
                    f.result()

                self.logger.info('%s done, %s not done', len(done), len(futures))
            for f in futures:
                f.cancel()


    def smart_scrape(self, case):
        start_time =  time.time()
        finish = start_time + self.timeout
        self.logger.info('Smart scrape %s', case)

        _1d = datetime.timedelta(days=1)
        now = datetime.datetime.now()
        key = self.get_key(case)
        r = self.fetch(key)

        nhc = self.get_nhc()

        if 'permissions' in r:
            permissions = r['permissions']['M']
            if 'govblock' in permissions:
                self.logger.info('govblock')
                return

        new_ts = int(time.time())
        dynamo_new_ts = {'S': str(new_ts)}
        dynamo = boto3factory.client('dynamodb')

        truncated = False

        if 'api' in r:
            ts = int(r['api']['M']['ts']['S'])
            if 'checked' in r['api']['M']:
                checked = int(r['api']['M']['checked']['S'])
            else:
                checked = 0

            if 'truncated' in r['api']['M']:
                truncated = r['api']['M']['truncated']['BOOL']

            last_time = datetime.datetime.fromtimestamp(max(ts, checked))
            ago = now - last_time
            self.logger.info('Last time %s, now %s, time passed %s', last_time, now, ago)
            if ago < _1d and not truncated:
                self.logger.info('Less than one day, skipping')
                return

            sittings = r['api']['M']['sittings']
            sittings = self.dynamo_to_list_of_maps(sittings)
            verdicts = r['api']['M']['verdicts']
            verdicts = self.dynamo_to_list_of_maps(verdicts)
            decisions = r['api']['M']['decisions']
            decisions = self.dynamo_to_list_of_maps(decisions)
            case = r['api']['M']['case']
            case = self.dynamo_to_map(case)
        else:
            sittings = []
            verdicts = []
            decisions = []
            caseDisplayIdentifier = case['CaseDisplayIdentifier']
            caseType = case['CaseType']
            case = nhc.get_case_by_case_type(caseDisplayIdentifier, caseType)
            dynamo_case_obj = self.map_to_dynamo(case)
            ts = int(time.time())
            r = dynamo.update_item(
                TableName=self.master,
                Key=key,
                UpdateExpression='set #api=:api',
                ExpressionAttributeNames={'#api': 'api'},
                ExpressionAttributeValues={':api': {'M': {'ts': {'S': str(ts)},
                                                          'case': dynamo_case_obj,
                                                          'sittings': {'L': []},
                                                          'verdicts': {'L': []},
                                                          'decisions': {'L': []}}
                                                    }}
            )

        with ThreadPoolExecutor(max_workers=3) as tp:
            future_sittings = tp.submit(nhc.get_sittings, case)
            future_verdicts = tp.submit(nhc.get_verdicts, case)
            future_decisions = tp.submit(nhc.get_decisions, case)

            fs = set()
            fs.add(future_decisions)
            fs.add(future_verdicts)
            fs.add(future_sittings)

            wait(fs, None, ALL_COMPLETED)

            new_sittings = future_sittings.result()
            new_verdicts = future_verdicts.result()
            new_decisions = future_decisions.result()

        if len(new_verdicts) < len(verdicts):
            raise Exception('Verdict removed')

        if len(new_decisions) < len(decisions):
            raise Exception('Verdict removed')

        diff = Diff()
        sittings_changed  = diff.has_changed(sittings, new_sittings, 'sittings')
        verdicts_added  = len(new_verdicts) > len(verdicts)
        decisions_added = len(new_decisions) > len(decisions)

        if self.only_one:
            if len(new_decisions) > len(decisions):
                self.logger.info('only one, cutting new decisions from %s to %s', len(new_decisions), len(decisions)+1)
                self.logger.info('only one, cutting new verdicts from %s to %s', len(new_verdicts), len(verdicts))
                new_decisions = new_decisions[:len(decisions)+1]
                new_verdicts = new_verdicts[:len(verdicts)]
                truncated = True
            elif len(new_verdicts) > len(verdicts):
                self.logger.info('only one, cutting new verdicts from %s to %s', len(new_verdicts), len(verdicts)+1)
                new_verdicts = new_verdicts[:len(verdicts)+1]
                truncated = True
            else:
                truncated = False


        old_dt = datetime.datetime.fromtimestamp(ts)
        new_dt = datetime.datetime.fromtimestamp(new_ts)
        self.logger.info('Updating ts from %s to %s [%s]', old_dt, new_dt, new_ts)

        update_expr = ['set #api.#checked=:checked, #api.#truncated=:truncated']
        update_values = {':checked': dynamo_new_ts, ':truncated': {'BOOL': truncated}}
        update_names = {'#api': 'api', '#checked': 'checked', '#truncated': 'truncated'}

        something_changed = False

        if sittings_changed:
            something_changed = True
            diff.copy_extra_data(sittings, new_sittings, 'sittings')
            dynamo_new_sittings = self.list_to_dynamo(new_sittings)
            self.logger.info('Uploading sittings')
            update_expr.append('#api.#sittings=:sittings')
            update_values[':sittings'] = dynamo_new_sittings
            update_names['#sittings'] = 'sittings'
        else:
            self.logger.info('Not updating sittings')

        decisions_indices = []
        if decisions_added:
            something_changed = True
            decisions_indices = list(range(len(decisions), len(new_decisions)))
            diff.copy_extra_data(decisions, new_decisions, 'decisions')
            dynamo_new_decisions = self.list_to_dynamo(new_decisions)
            self.logger.info('Writing decisions to dynamo')
            update_expr.append('#api.#decisions=:decisions')
            update_values[':decisions'] = dynamo_new_decisions
            update_names['#decisions'] = 'decisions'

        for dec_index, decision in enumerate(decisions):
            if decision.get('missing'):
                self.logger.info('Found missing decision in index %s', dec_index)
                decisions_indices.append(dec_index)

        verdicts_indices = []
        if verdicts_added:
            something_changed = True
            verdicts_indices = list(range(len(verdicts), len(new_verdicts)))
            diff.copy_extra_data(verdicts, new_verdicts, 'verdicts')
            dynamo_new_verdicts = self.list_to_dynamo(new_verdicts)
            self.logger.info('Writing verdicts to dynamo')
            update_expr.append('#api.#verdicts=:verdicts')
            update_values[':verdicts'] = dynamo_new_verdicts
            update_names['#verdicts'] = 'verdicts'

        for verd_index, verdict in enumerate(verdicts):
            if verdict.get('missing'):
                self.logger.info('Found missing verdict in index %s', verd_index)
                verdicts_indices.append(verd_index)

        if something_changed:
            update_expr.append('#api.#ts=:ts')
            update_values[':ts'] = dynamo_new_ts
            update_names['#ts'] = 'ts'

        update_expr = ', '.join(update_expr)

        self.logger.info('')
        self.logger.info('Dynamo Update')
        self.logger.info('Update expr: %s', update_expr)
        for k, v in update_names.items():
            self.logger.info('Name: %s=%s', k, v)
        for k, v in update_values.items():
            t = next(iter(v.keys()))
            self.logger.info('Value: %s', k)
            if t == 'L':
                self.logger.info('Length: %s', len(v['L']))
            self.logger.info(v)


        r = dynamo.update_item(
            TableName=self.master,
            Key=key,
            UpdateExpression=update_expr,
            ExpressionAttributeNames=update_names,
            ExpressionAttributeValues=update_values
        )

        status = r.get('ResponseMetadata', {}).get('HTTPStatusCode', -1)
        self.logger.info('Status %s', status)
        self.logger.info('Scraping documents')
        self.scrape_documents(key, case, new_decisions, new_verdicts, decisions_indices, verdicts_indices, finish)
        total = time.time() - start_time
        self.logger.info('Total time: %s', total)

    def close(self):
        self.get_nhc().close()
        self.remove_nhc()


if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('botocore').setLevel(logging.WARN)
    logging.getLogger('urllib3').setLevel(logging.WARN)


    o=OneCase(config={'only_one': False})

    o.smart_scrape({'CaseDisplayIdentifier': '8002-02-21', 'CaseType': 'n'})

    exit(0)
    exit(0)
    o.mark_govblock({'CaseDisplayIdentifier': '46676-06-21', 'CaseType': 'n'})

    o.mark_govblock({'CaseDisplayIdentifier': '46676-06-21', 'CaseType': 'n'})
