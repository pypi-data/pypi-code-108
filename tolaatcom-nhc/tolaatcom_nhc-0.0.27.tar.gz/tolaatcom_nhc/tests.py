import unittest
from tolaatcom_nhc import nethamishpat
from tolaatcom_nhc import pdf_generator
from tolaatcom_nhc import one_case
import logging

logging.basicConfig(level=logging.DEBUG)
logging.root.setLevel(level=logging.WARN)
logging.getLogger('pdfgenerator').setLevel(level=logging.DEBUG)


class SimpleTestCase(unittest.TestCase):

    def setUp(self):
        logging.info('set up')

    def test_metadata(self):
        api = nethamishpat.NethamishpatApiClient()
        r = api.parse_everything({'CaseType': 'n', 'CaseDisplayIdentifier': '52512-02-18'})
        self.assertEqual(r['case']['CourtName'].strip(), 'מחוזי מרכז')
        self.assertEqual(r['case']['CaseID'], 75263135)
        self.assertEqual(2, len(r['sittings']))
        self.assertEqual(5, len(r['decisions']))
        self.assertEqual(0, len(r['verdicts']))

    def test_metadata2(self):
        api = nethamishpat.NethamishpatApiClient()
        r = api.parse_everything({'CaseType': 'n', 'CaseDisplayIdentifier': '52512-02-18'})
        from os.path import expanduser
        with open(expanduser('~/a.pdf'), 'wb') as f:
            f.write(r['decisions'][4]['pdf'].read())
        print('done')

    def test_does_not_exist(self):
        api = nethamishpat.NethamishpatApiClient()
        r = api.parse_everything({'CaseType': 'n', 'CaseDisplayIdentifier': '26078-04-17'})
        self.assertIsNone(r)


    def test_pdf_getn(self):
        pdfg = pdf_generator.PdfGenerator()
        d, last_m = pdfg.build_document('77636097', 'decisions', 4)
        from os.path import expanduser, join
        out = join(expanduser('~'), 'temp.pdf')
        open(out, 'wb').write(d.read())
        print(out)

    def test_scrap(self):
        oc = one_case.OneCase()
        p = {'CaseDisplayIdentifier': '27040-08-20', 'CaseType': 'n'}
        oc.handle(p)

    def test_f1(self):
        p = r'C:\Users\andy\Desktop\New folder (3)\a.csv'
        f = open(p, 'r', encoding='utf-8')
        s = set()
        for line in f:
            line = line.strip()
            if '/' not in line:
                continue
            parts = line.split('/')
            s.add(parts[4])
        f.close()

        print(s)
        print(len(s))

        def p(case):
            print(f'Handling {case}')
            try:
                oc = one_case.OneCase()
                oc.handle({'CaseDisplayIdentifier': case, 'CaseType': 'n'})
                oc.handle({'CaseDisplayIdentifier': case, 'CaseType': 't'})
                oc.close()
            except:
                logging.warning('Bad', exc_info=True)
            print(f'Finished {case}')

        from concurrent.futures.thread import ThreadPoolExecutor
        from concurrent.futures import wait, ALL_COMPLETED
        import logging
        logging.basicConfig()

        futures = set()
        with ThreadPoolExecutor(max_workers=20) as tp:
            for c in s:
                future = tp.submit(p, c)
                futures.add(future)

            print(f'Waiting for {len(futures)}')

            done, not_done = wait(futures, None, ALL_COMPLETED)
            assert len(not_done) == 0
            for x in done:
                r = x.result()