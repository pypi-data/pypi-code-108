from .base import BaseAPIModelStub


class LotStub(BaseAPIModelStub):
    default_data = {
        "id": 1,
        "slug": "some-lot",
        "name": "Some lot",
        "allowsBrief": False,
        "oneServiceLimit": False,
        "unitSingular": 'service',
        "unitPlural": 'services',
    }

    optional_keys = [
        ("allowsBrief", "allows_brief"),
        ("oneServiceLimit", "one_service_limit"),
        ("unitSingular", "unit_singular"),
        ("unitPlural", "unit_plural"),
        ("id", "lot_id")
    ]


def dos_lots():
    return [
        LotStub(
            lot_id=5, slug='digital-outcomes', name='Digital outcomes', allows_brief=True, one_service_limit=True
        ).response(),
        LotStub(
            lot_id=6, slug='digital-specialists', name='Digital specialists', allows_brief=True, one_service_limit=True
        ).response(),
        LotStub(
            lot_id=7, slug='user-research-studios', name='User research studios', unit_singular='lab',
            unit_plural='labs'
        ).response(),
        LotStub(
            lot_id=8, slug='user-research-participants', name='User research participants', allows_brief=True,
            one_service_limit=True
        ).response()
    ]


def as_a_service_lots():
    return [
        LotStub(lot_id=1, slug='saas', name='Software as a Service').response(),
        LotStub(lot_id=2, slug='paas', name='Platform as a Service').response(),
        LotStub(lot_id=3, slug='iaas', name='Infrastructure as a Service').response(),
        LotStub(lot_id=4, slug='scs', name='Specialist Cloud Services').response()
    ]


def cloud_lots():
    return [
        LotStub(lot_id=9, slug='cloud-hosting', name='Cloud hosting').response(),
        LotStub(lot_id=10, slug='cloud-software', name='Cloud software').response(),
        LotStub(lot_id=11, slug='cloud-support', name='Cloud support').response()
    ]
