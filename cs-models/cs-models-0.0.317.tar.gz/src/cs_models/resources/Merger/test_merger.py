from marshmallow import ValidationError
from freezegun import freeze_time
from test.backendtestcase import TestCase
from sqlalchemy.orm import Session
from src.cs_models.database import engine, operations
from src.cs_models.resources.Merger.models import MergerModel
from src.cs_models.resources.Merger.schemas import MergerResourceSchema
from src.cs_models.resources.File.models import FileModel
from src.cs_models.resources.File.schemas import FileResourceSchema
from src.cs_models.resources.CompanySEC.models import CompanySECModel
from src.cs_models.resources.CompanySEC.schemas import CompanySECResourceSchema
from src.cs_models.resources.CompanyOUS.models import CompanyOUSModel
from src.cs_models.resources.CompanyOUS.schemas import CompanyOUSResourceSchema


@freeze_time("2020-01-01")
class MergerResourceTestCase(TestCase):
    def setUp(self):
        super(MergerResourceTestCase, self).setUp()
        with operations.session_scope() as session:

            self.company_sec1 = operations.create(
                session=session,
                model=CompanySECModel,
                schema=CompanySECResourceSchema,
                obj={
                    'cik_str': '1750',
                    'ticker': 'ABBV',
                    'title': 'Abbvie',
                }
            )

            self.company_sec2 = operations.create(
                session=session,
                model=CompanySECModel,
                schema=CompanySECResourceSchema,
                obj={
                    'cik_str': '1760',
                    'ticker': 'MYL',
                    'title': 'Mylan N.V.',
                }
            )

            self.file1 = operations.create(
                session=session,
                model=FileModel,
                schema=FileResourceSchema,
                obj={
                    'file_format': 'html',
                    's3_bucket_name': 'dma',
                    's3_key_name': '1/dma.html',
                },
            )

            self.merger1 = operations.create(
                session=session,
                model=MergerModel,
                schema=MergerResourceSchema,
                obj={
                    "target_sec_id": self.company_sec1.id,
                    "acquirer_sec_id": self.company_sec2.id,
                    "deal_value": 1500000000,
                    "type": "Cash",
                    "announcement_date": "02/15/2020",
                    "offer_price": 10.30,
                    "market_price": 8.90,
                    "dma_file_id": self.file1.id,
                },
            )

            self.valid_data = {
                        "target_sec_id": self.company_sec1.id,
                        "acquirer_sec_id": self.company_sec2.id,
                        "deal_value": 20000000,
                        "type": "Cash",
                        "announcement_date": "01/01/2020",
                        "offer_price": 15.75,
                        "market_price": 11.43,
                        "dma_file_id": self.file1.id,
                    }

    def test_create_inside_context_manager(self):
        with operations.session_scope() as session:

            self.file2 = operations.create(
                session=session,
                model=FileModel,
                schema=FileResourceSchema,
                obj={
                    'file_format': 'html',
                    's3_bucket_name': 'dma',
                    's3_key_name': '2/dma.html',
                },
            )

            self.company_sec3 = operations.create(
                session=session,
                model=CompanySECModel,
                schema=CompanySECResourceSchema,
                obj={
                    'cik_str': '1770',
                    'ticker': 'LLY',
                    'title': 'Eli Lily',
                }
            )

            self.company_sec4 = operations.create(
                session=session,
                model=CompanySECModel,
                schema=CompanySECResourceSchema,
                obj={
                    'cik_str': '1780',
                    'ticker': 'JNJ',
                    'title': 'Johnson & Johnson',
                }
            )

            instance = operations.create(
                session=session,
                model=MergerModel,
                schema=MergerResourceSchema,
                obj={
                    "target_sec_id": self.company_sec3.id,
                    "acquirer_sec_id": self.company_sec4.id,
                    "deal_value": 148575940,
                    "type": "Cash",
                    "announcement_date": "05/31/2020",
                    "offer_price": 155.50,
                    "market_price": 138.90,
                    "dma_file_id": self.file2.id,
                },
            )
            self.assertEqual(
                MergerResourceSchema().dump(instance).data,
                {
                    "id": 2,
                    "target_sec_id": 3,
                    "target_ous_id": None,
                    "acquirer_sec_id": 4,
                    "acquirer_ous_id": None,
                    "deal_value": 148575940,
                    "announcement_date": '2020-05-31T00:00:00+00:00',
                    "type": "Cash",
                    "offer_price": 155.50,
                    "market_price": 138.90,
                    "dma_file_id": 2,
                    "updated_at": '2020-01-01T00:00:00+00:00',
                },
            )

    def test_create(self):
        session = Session(bind=engine)
        try:
            self.file3 = operations.create(
                session=session,
                model=FileModel,
                schema=FileResourceSchema,
                obj={
                    'file_format': 'html',
                    's3_bucket_name': 'dma',
                    's3_key_name': '3/dma.html',
                },
            )

            self.company_sec5 = operations.create(
                session=session,
                model=CompanySECModel,
                schema=CompanySECResourceSchema,
                obj={
                    'cik_str': '1790',
                    'ticker': 'PTLA',
                    'title': 'Portola Pharma',
                }
            )

            self.company_sec6 = operations.create(
                session=session,
                model=CompanySECModel,
                schema=CompanySECResourceSchema,
                obj={
                    'cik_str': '1800',
                    'ticker': 'NVS',
                    'title': 'Novartis',
                }
            )
            instance = operations.create(
                session=session,
                model=MergerModel,
                schema=MergerResourceSchema,
                obj={
                    "target_sec_id": self.company_sec5.id,
                    "acquirer_sec_id": self.company_sec6.id,
                    "deal_value": 2000000,
                    "type": "Cash",
                    "announcement_date": "02/01/2020",
                    "offer_price": 120,
                    "market_price": 105,
                    "dma_file_id": self.file3.id,
                },
            )
            self.assertEqual(
                MergerResourceSchema().dump(instance).data,
                {
                    "id": 2,
                    "target_sec_id": 3,
                    "target_ous_id": None,
                    "acquirer_sec_id": 4,
                    "acquirer_ous_id": None,
                    "deal_value": 2000000,
                    "type": "Cash",
                    "announcement_date": "2020-02-01T00:00:00+00:00",
                    "offer_price": 120.0,
                    "market_price": 105.0,
                    "dma_file_id": 2,
                    "updated_at": '2020-01-01T00:00:00+00:00',
                },
            )

            # This commit is not really needed since
            # we commit in `create` but is done for consistency.
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def test_create_validation_error(self):
        session = Session(bind=engine)
        self.file3 = operations.create(
            session=session,
            model=FileModel,
            schema=FileResourceSchema,
            obj={
                'file_format': 'html',
                's3_bucket_name': 'dma',
                's3_key_name': '3/dma.html',
            },
        )

        self.company_sec5 = operations.create(
            session=session,
            model=CompanySECModel,
            schema=CompanySECResourceSchema,
            obj={
                'cik_str': '1790',
                'ticker': 'PTLA',
                'title': 'Portola Pharma',
            }
        )

        self.company_sec6 = operations.create(
            session=session,
            model=CompanySECModel,
            schema=CompanySECResourceSchema,
            obj={
                'cik_str': '1800',
                'ticker': 'NVS',
                'title': 'Novartis',
            }
        )
        self.assertRaises(
            ValidationError,
            operations.create,
            session,
            MergerModel,
            MergerResourceSchema,
            {
                "target_sec_id": self.company_sec5.id,
                "acquirer_sec_id": self.company_sec6.id,
                "deal_value": 2000000,
                "type": "Cash",
                "offer_price": 120,
                "market_price": 105,
                "dma_file_id": self.file3.id,
            },
        )

    def test_update_or_create(self):
        with operations.session_scope() as session:
            self.file3 = operations.create(
                session=session,
                model=FileModel,
                schema=FileResourceSchema,
                obj={
                    'file_format': 'html',
                    's3_bucket_name': 'dma',
                    's3_key_name': '3/dma.html',
                },
            )

            self.company_sec5 = operations.create(
                session=session,
                model=CompanySECModel,
                schema=CompanySECResourceSchema,
                obj={
                    'cik_str': '1790',
                    'ticker': 'PTLA',
                    'title': 'Portola Pharma',
                }
            )

            self.company_sec6 = operations.create(
                session=session,
                model=CompanySECModel,
                schema=CompanySECResourceSchema,
                obj={
                    'cik_str': '1800',
                    'ticker': 'NVS',
                    'title': 'Novartis',
                }
            )
            instance, created = operations.update_or_create(
                session=session,
                model=MergerModel,
                schema=MergerResourceSchema,
                query_fields=["target_sec_id", "target_ous_id",
                              "acquirer_sec_id", "acquirer_ous_id",
                              "announcement_date"],
                obj={
                    "target_sec_id": self.company_sec5.id,
                    "acquirer_sec_id": self.company_sec6.id,
                    "deal_value": 2000000,
                    "type": "Cash",
                    "announcement_date": "02/14/2020",
                    "offer_price": 120,
                    "market_price": 105,
                    "dma_file_id": self.file3.id,
                },
            )
            self.assertEqual(
                MergerResourceSchema().dump(instance).data,
                {
                    "id": 2,
                    "target_sec_id": 3,
                    "target_ous_id": None,
                    "acquirer_sec_id": 4,
                    "acquirer_ous_id": None,
                    "deal_value": 2000000,
                    "type": "Cash",
                    "announcement_date": "2020-02-14T00:00:00+00:00",
                    "offer_price": 120.0,
                    "market_price": 105.0,
                    "dma_file_id": 2,
                    "updated_at": '2020-01-01T00:00:00+00:00',
                },
            )
            self.assertTrue(created)

            instance, created = operations.update_or_create(
                session=session,
                model=MergerModel,
                schema=MergerResourceSchema,
                query_fields=["target_sec_id", "target_ous_id",
                              "acquirer_sec_id", "acquirer_ous_id",
                              "announcement_date"],
                obj={
                    "target_sec_id": self.company_sec5.id,
                    "acquirer_sec_id": self.company_sec6.id,
                    "deal_value": 3000000,
                    "type": "Cash",
                    "annoucement_date": "02/14/2020",
                    "offer_price": 120,
                    "market_price": 105,
                    "dma_file_id": self.file3.id,
                },
            )
            self.assertEqual(
                MergerResourceSchema().dump(instance).data,
                {
                    "id": 2,
                    "target_sec_id": 3,
                    "target_ous_id": None,
                    "acquirer_sec_id": 4,
                    "acquirer_ous_id": None,
                    "deal_value": 3000000,
                    "type": "Cash",
                    "announcement_date": "2020-02-14T00:00:00+00:00",
                    "offer_price": 120.0,
                    "market_price": 105.0,
                    "dma_file_id": 2,
                    "updated_at": '2020-01-01T00:00:00+00:00',
                }
                ,
            )
            self.assertFalse(created)
