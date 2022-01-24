import json
import logging
import tempfile
import hashlib
import time

import requests
from PyPDF2 import PdfFileReader

class NethamishpatApiClient:

    def __init__(self, config=None):
        config = config or {}
        self.base_url = 'https://mngcs.court.gov.il/NGCS.MobilePublic.Web//AnonymousServices'
        self.data_url = f'{self.base_url}/mDataProvider.asmx'
        self._by_case = f'{self.data_url}/GetCaseSearchResultByCase'
        self._decisions = f'{self.data_url}/GetDecisionListByCaseIDForWeb'
        self._sittings = f'{self.data_url}/GetSitttingsByCase'
        self._pdf = f'{self.base_url}/Viewer/NGCSMobileViewerService.asmx/GetDocFile'
        self._get_images =f'{self.base_url}/Viewer/NGCSMobileViewerService.asmx/GetImages'

        self.session = None

        self.logger = logging.getLogger('headless.nhc')

        self.skip_documents = config.get('skip_documents', False)


    def close(self):
        self.session and self.session.close()

    def send_request(self, url, body, expected='json'):

        if self.session is None:
            self.session = requests.session()

        retries = 2
        r = {}
        success = False
        for retry in range(retries):
            try:
                before = time.time()
                try:
                    r = self.session.post(url, json=body, headers={'Content-Type': 'application/json'})
                    success = True
                finally:
                    after = round(time.time() - before, 3)
            except:
                self.logger.warning('Exception : %s on retry %s', url, retry)
                self.logger.warning('Exception: %s', json.dumps(body))
                self.logger.warning('Time %s', after, exc_info=True)
                if retry == retries-1:
                    self.logger.warning('Retries exhausted giving up and raising')
                    raise
                else:
                    time.sleep(2 ** retry)
                    continue
            if r.status_code == 500 and expected=='binary' and 'There is a problem with the resource you are look' \
                                                               'ing for, and it cannot be displayed' in r.text:
                self.logger.warning('Cannot be displayed')
                return None
            elif r.status_code != 200:
                self.logger.warning('Status code %s for %s on retry %s', r.status_code, url, retry)
                self.logger.warning(json.dumps(body))
                self.logger.warning('HEADERS:')
                for k, v in r.headers.items():
                    self.logger.warning('%s: %s', k, v)
                self.logger.warning(r.text)
            else:
                break

        if not success:
            raise Exception('Failed to invoke nh api server')
        if expected == 'json':
            total = round(time.time() - before, 3)
            self.logger.info('Download json retry %s after %s, total %s', retry, after, total)
            return r.json()
        else:
            spooled = tempfile.SpooledTemporaryFile(1024 ** 2)
            for chunk in r.iter_content(1024, 'wb'):
                spooled.write(chunk)
            total = round(time.time() - before, 3)
            self.logger.info('Download pdf retry %s after %s, total %s', retry, after, total)
            return spooled

    def get_by_case(self, number, month, year, numeratorGroup='1'):
        if type(year) == int:
            year = str(year)
        if type(year) == str and len(year) == 2:
            year = f'20{year}'
        body = {'numeratorGroup': numeratorGroup, 'caseNumber': number, 'caseYear': year, 'caseMonth': month}
        return self.send_request(self._by_case, body)

    def get_pdf(self, documentID):
        body = {'documentNumber': documentID}
        return self.send_request(self._pdf, body, expected='binary')

    def get_case_by_case_obj(self, obj):
        if 'CaseDisplayIdentifier' in obj and 'CaseID' in obj:
            display_identifier = obj['CaseDisplayIdentifier']
            case_id = obj['CaseID']
            return self.get_case_by_display_name(display_identifier, case_id)

        elif 'CaseDisplayIdentifier' in obj and 'CaseType' in obj:
            display_identifier = obj['CaseDisplayIdentifier']
            case_type = obj['CaseType']
            return self.get_case_by_case_type(display_identifier, case_type)

    def get_all_images(self, documentID):
        CH = 50
        all_images = []
        for i in range(0, 350, CH):
            r = self.get_images(documentID, i, i + CH)
            if 'd' not in r:
                return None
            images = r['d']
            all_images.extend(images)
            if len(images) < CH:
                break
        return {'d': all_images}

    def get_images(self, documentID, fromIndex, toIndex):
        body = {'documentNumber': documentID, 'fromIndex': fromIndex, 'toIndex': toIndex,
                'updateDocumentViewState': True}
        return self.send_request(self._get_images, body)

    def get_case_by_display_name(self, display_identifier, case_id):
        n, m, y = display_identifier.split('-')
        return self.get_case(n, m, y, case_id=case_id)

    def get_case_by_case_type(self, display_identifier, case_type):
        n, m, y = display_identifier.split('-')
        return self.get_case(n, m, y, case_type=case_type)



    def get_case_documents(self, case, clickedFolderIndex):
        if 'd' not in case:
            case = {'d': case}
        d = case['d']
        caseID = d['CaseID']
        courtName = d['CourtName']
        numeratorGroup = {'court': '1', 'transport': '2'}[d['type']]
        body = {'courtName': courtName,
                'numeratorGroup': numeratorGroup,
                'caseID': caseID, 'clickedFolderIndex': clickedFolderIndex}
        r = self.send_request(self._decisions, body)
        if 'd' in r:
            return r['d']

    def get_sittings(self, case):
        if 'd' not in case:
            case = {'d': case}
        d = case['d']
        caseID = d['CaseID']
        courtName = d['CourtName']
        body = {'courtName': courtName, 'caseID': caseID}
        r = self.send_request(self._sittings, body)
        if 'd' in r:
            r = r['d']
        return r

    def get_decisions(self, case):
        return self.get_case_documents(case, 1)

    def get_verdicts(self, case):
        return self.get_case_documents(case, 2)

    def get_documents(self, case, doc_type):
        if doc_type == 'verdicts':
            return self.get_verdicts(case)
        elif doc_type == 'decisions':
            return self.get_decisions(case)
        assert doc_type in ('verdicts', 'decisions')

    def get_case(self, number, month, year, case_id=None, case_type=None):
        if case_id:
            self.logger.info('Get case by case_id %s %s %s %s', number, month, year, case_id)
        elif case_type:
            self.logger.info('Get case by case_type %s %s %s %s', number, month, year, case_type)
        else:
            raise Exception('Need to provide case_id or title')

        map = {'1': 'court', '2': 'transport'}
        for numeratorGroup in '1', '2':
            case = self.get_by_case(number, month, year, numeratorGroup)
            data = case.get('d', {})
            if case_id:
                if data.get('CaseID') == int(case_id):
                    r = map[numeratorGroup]
                    self.logger.info('Result: %s', r)
                    del data['__type']
                    data['type'] = map[numeratorGroup]
                    return data
            elif case_type:
                case_type_map = {'n': '1', 't': '2'}
                if case_type_map[case_type] == numeratorGroup:
                    r = map[numeratorGroup]
                    self.logger.info('Result: %s', r)
                    del data['__type']
                    data['type'] = map[numeratorGroup]
                    return data

        self.logger.info('Not found')
        return None

    def tolaathash(self, f):
        bug_size = 65536  # lets read stuff in 64kb chunks!

        sha1algo = hashlib.sha1()
        sha1algo.update(b'tolat mishpat ugc jqQGvOUnzyufgTrEUVaj')

        while True:
            data = f.read(bug_size)
            if not data:
                break
            sha1algo.update(data)

        return sha1algo.hexdigest()

    def get_pdfs_from_images(self, decisions):
        for index, decision in enumerate(decisions):
            doc_id = decision['DocumentID']
            self.logger.info('Parsing pdf index %s docid %s', index, doc_id)
            images = self.get_all_images(doc_id)
            if images is None or 'd' not in images:
                self.logger.info('No images found %s docid %s', index, doc_id)
                decision['missing'] = True
                continue

            pages = len(images['d'])
            self.logger.info('Pages %s docid %s is %s', index, doc_id, pages)
            decision['pages'] = pages
            decision['images'] = images

    def get_pdfs(self, decisions):
        for index, decision in enumerate(decisions):
            doc_id = decision['DocumentID']
            self.logger.info('Parsing pdf index %s docid %s', index, doc_id)

            pdf = self.get_pdf(doc_id)
            if pdf is None:
                self.logger.info('Missing pdf index %s docid %s', index, doc_id)
                decision['missing'] = True
                continue

            self.logger.info('Parsing pages %s docid %s', index, doc_id)
            pdf.seek(0)
            parsed_pdf = PdfFileReader(pdf)
            pages = parsed_pdf.getNumPages()
            self.logger.info('Pages %s docid %s is %s', index, doc_id, pages)
            del parsed_pdf
            decision['pages'] = pages
            pdf.seek(0)
            self.logger.info('Parsing hash %s docid %s', index, doc_id)
            decision['tolaathash'] = self.tolaathash(pdf)
            self.logger.info('Parsed hash %s docid %s %s', index, doc_id, decision['tolaathash'])
            pdf.seek(0)
            decision['pdf'] = pdf
            decision['ts'] = int(time.time())

    def parse_by_type(self, type, case):
        self.get_case_by_case_obj(case)

    def _parse_everything(self, case):
        result = {}

        display_id = case.get('CaseDisplayIdentifier')
        self.logger.info('Parse everything %s', display_id)

        if display_id is not None and display_id.count('-') == 2:
            result['case'] = self.get_case_by_case_obj(case)
            if result['case'] is None or result['case']['CaseID'] == 0:
                return None
            case['type'] = result['case']['type']
            result['type'] = result['case']['type']
        else:
            case['type'] = 'court'
            result['type'] = 'old'

        self.logger.info('Parse sittings %s', display_id)
        result['sittings'] = self.get_sittings(result['case'])
        self.logger.info('Parse decisions %s', display_id)
        result['decisions'] = self.get_decisions(result['case'])
        self.logger.info('Parse verdicts %s', display_id)
        result['verdicts'] = self.get_verdicts(result['case'])

        if not self.skip_documents:
            for k in 'decisions', 'verdicts':
                try:
                    self.logger.info('Parsing pdfs %s %s', display_id, k)
                    self.get_pdfs(result[k])
                    #self.get_pdfs_from_images(result[k])
                except:
                    self.logger.warning('Error parsing %s', display_id, exc_info=True)
                    raise
        else:
            self.logger.info('Skipping documents')
        return result

    def parse_everything(self, case):
        retries = 1
        display_id = case.get('CaseDisplayIdentifier')

        for retry in range(retries):
            try:
                if retry > 0:
                    self.logger.info('Retrying retry %s', retry)
                r = self._parse_everything(case)
                self.logger.info('Succesfully parsed %s in retry %s', display_id, retry)
                return r
            except:
                self.session = None
                if retry == retries-1:
                    self.logger.error('Repeated exceptions. Retry is %s. Giving up', retry, exc_info=True)
                    raise
                else:
                    self.logger.warning('Exception in parse_everything, retry %s, restarting session and retrying',
                                        retry,
                                        exc_info=True)

            self.logger.warning('Retrying')





if __name__=='__main__':

    import logconfig
    nhc = NethamishpatApiClient()
    c = {'CaseID': 74600197, 'CourtName':'בית משפט השלום בתל אביב - יפו',
                            'type': 'court'}
    nhc.get_sittings(c)
    nhc.get_case_documents(c, 1)
    exit(0)
    x = {"CaseTypeShortName": "\u05ea\u05d0\"\u05de", "CaseDisplayIdentifier": "5509-11-14", "CaseName": "\u05e9.\u05e9\u05dc\u05de\u05d4 \u05d7\u05d1\u05e8\u05d4 \u05dc\u05d1\u05d9\u05d8\u05d5\u05d7 \u05d1\u05e2\"\u05de 513879189 \u05e0' \u05d5\u05d5\u05d0\u05e7\u05d9\u05dd \u05d5\u05d0\u05d7'", "CaseInterestName": "\u05e0\u05d6\u05e7\u05d9 \u05e8\u05db\u05d5\u05e9 \u2013 \u05e8\u05db\u05d1", "CourtName": "\u05e9\u05dc\u05d5\u05dd \u05ea\u05dc \u05d0\u05d1\u05d9\u05d1 - \u05d9\u05e4\u05d5", "CaseStatusName": "\u05e1\u05d2\u05d5\u05e8", "CaselinkID": None, "CaseID": 72262476, "open_date": "2010-01-01", "ts": "1586726566"}

    e = nhc.parse_everything(x)
    exit(0)