import copy
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.Newswire import Newswire
from src.cs_models.resources.Subsidiary import Subsidiary
from src.cs_models.resources.CompanySEC import CompanySEC
from src.cs_models.resources.CompanyOUS import CompanyOUS
from src.cs_models.resources.File import File


class NewswireResourceTestCase(TestCase):
    def setUp(self):
        super(NewswireResourceTestCase, self).setUp()
        self.inst = Newswire()
        self.inst_file = File()
        self.inst_subsidiary = Subsidiary()
        self.inst_sec_company = CompanySEC()
        self.inst_ous_company = CompanyOUS()

        self.company_sec1 = self.inst_sec_company.create({
            'cik_str': '1382101',
            'ticker': 'STRO',
            "title": "SUTRO BIOPHARMA, INC.",
        })

        self.company_sec2 = self.inst_sec_company.create({
            "cik_str": "885590",
            "ticker": "BHC",
            "title": "Bausch Health Companies Inc."
        })

        self.company_ous1 = self.inst_ous_company.create({
            'name': 'Kolon Tissuegene',
            'ticker': None,
            'exchange': 'NSE',
        })

        self.subsidiary1 = self.inst_subsidiary.create({
            'name': 'Sutro Biopharma Inc.',
            'company_sec_id': self.company_sec1["id"],
            'company_ous_id': None,
        })

        self.subsidiary2 = self.inst_subsidiary.create({
            'name': 'Bausch Health Inc.',
            'company_sec_id': self.company_sec2["id"],
            'company_ous_id': None,
        })

        self.subsidiary3 = self.inst_subsidiary.create({
            'name': 'Kolon Tissuegene',
            'company_sec_id': None,
            'company_ous_id': self.company_ous1["id"],
        })

        self.file1 = self.inst_file.create(
            {
                "file_format": "xml",
                "s3_bucket_name": "newswires",
                "s3_key_name": "PRN/202004131700PR_NEWS_USPR_____NY76479.xml",
            }
        )

        self.file2 = self.inst_file.create(
            {
                "file_format": "xml",
                "s3_bucket_name": "newswires",
                "s3_key_name": "PRN/20200413170343R_NEWS_USPR_____NY76349.xml",
            }
        )

        self.newswire1 = self.inst.create({
            'date': '20200413T152300',
            'source': 'PR Newswire',
            'headline': 'Sutro Biopharma to Present Updated Clinical Data '
                        'for its STRO-002 Antibody-Drug Conjugate at the '
                        'AACR Virtual Annual Meeting on April 27, 2020',
            'drugs': '[STRO-002]',
            'conditions': "['Levine Cancer', 'ovarian and endometrial "
                          "cancer', 'ovarian cancer', "
                          "'Platinum-Resistant/Refractory Epithelial Ovarian Cancer', "
                          "'Cancers']",
            "subsidiary_id": self.subsidiary1["id"],
            "news_file_id": self.file1["id"]
        })

        self.newswire2 = self.inst.create({
            'date': '20200409T120300',
            'source': 'PR Newswire',
            'headline': 'Bausch Health Initiates VIRAZOLE® (Ribavirin for '
                        'Inhalation Solution, USP) Clinical Study in '
                        'Patients with COVID-19',
            'drugs': "['VIRAZOLE', 'Ribavirin']",
            'conditions': "['respiratory distress', 'COVID-19']",
            "subsidiary_id": self.subsidiary2["id"],
            "news_file_id": self.file2["id"]
        })

        self.newswire3 = self.inst.create({
            'date': '20200413T063000',
            'source': 'PR Newswire',
            'headline': 'Kolon Tissuegene Announces Plans To Resume US Phase '
                        'III Clinical Trial For TG-C',
            'drugs': "['TG-C']",
            'conditions': "['osteoarthritis', 'COVID-19']",
            "subsidiary_id": self.subsidiary3["id"],
            "news_file_id": self.file2["id"]
        })

        self.valid_data = {
            'date': '20200410T080000',
            'source': 'PR Newswire',
            'headline': 'FDA Approves First Ever Treatment for '
                        'Neurofibromatosis',
            'drugs': "['Koselugo', 'selumetinib']",
            'conditions': "['neurofibromatosis']",
            "subsidiary_id": self.subsidiary1["id"],
            "news_file_id": self.file1["id"]
        }

    @parameterized.expand([
        ('source',),
    ])
    def test_create_validation_error_missing_field(self, field_to_pop):
        base_data = copy.copy(self.valid_data)
        base_data.pop(field_to_pop)
        self.assertRaises(
            ValidationError,
            self.inst.create,
            base_data,
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        expected_data = {
            **self.valid_data,
            **{
                'date': '2020-04-10T08:00:00+00:00',
            }
        }
        second_equals_first(expected_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(3, len(resp))

    @parameterized.expand([
        ('id', 'newswire1', 'id', 1),
        ('headline', 'newswire1', 'headline', 1),
    ])
    def test_read_w_params(
        self,
        field_name,
        attr,
        attr_field,
        expected_length,
    ):
        resp = self.inst.read({})
        self.assertEqual(3, len(resp))

        resp = self.inst.read({
            field_name: getattr(self, attr)[attr_field],
        })
        self.assertEqual(expected_length, len(resp))

    @parameterized.expand([
        ('id', 999, NoResultFound),
    ])
    def test_one_raises_exception(self, field_name, field_value, exception):
        self.assertRaises(
            exception,
            self.inst.one,
            {
                field_name: field_value,
            },
        )

    @parameterized.expand([
        ('id',),
        ('headline',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.newswire1[field_name],
        })
        second_equals_first(
            self.newswire1,
            resp,
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'subsidiary_id': self.valid_data['subsidiary_id'],
            }
        )

    def test_upsert_creates_new_entry(self):
        data = copy.copy(self.valid_data)
        self.assertEqual(3, len(self.inst.read({})))
        self.inst.upsert(data)
        self.assertEqual(4, len(self.inst.read({})))

    def test_upsert_updates_existing_row(self):
        data = {
            **self.valid_data,
            **{'headline': self.newswire1['headline'],
               'subsidiary_id': self.subsidiary1['id'],
               },
        }
        resp = self.inst.upsert(data)
        expected_data = {
            **data,
            **{
                'date': '2020-04-10T08:00:00+00:00',
            }
        }
        second_equals_first(
            expected_data,
            resp,
        )
        self.assertEqual(3, len(self.inst.read({})))

    def test_upsert_with_invalid_subsidiary_id(self):
        invalid_id = 9999999
        data = {
            **self.valid_data,
            **{'headline': self.newswire1['headline'],
               'subsidiary_id': invalid_id,
               },
        }
        self.assertRaises(
            IntegrityError,
            self.inst.upsert,
            data,
        )
