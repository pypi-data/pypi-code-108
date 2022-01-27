from datetime import datetime as dt
from .base import BaseAPIModelStub
from .lot import as_a_service_lots, cloud_lots, dos_lots


class FrameworkStub(BaseAPIModelStub):
    resource_name = 'frameworks'
    variations = {}
    framework_agreement_details = {
        "contractNoticeNumber": "2018/S 074-164715",
        "countersignerName": "Zachary X. Signer",
        "countersignerRole": "Category Director",
        "frameworkAgreementVersion": "RM1557.10",
        "frameworkExtensionLength": "12 months",
        "frameworkRefDate": "18-06-2018",
        "frameworkURL": "https://www.gov.uk/government/publications/g-cloud-13-framework-agreement",
        "lotDescriptions": {
            "cloud-hosting": "Lot 1: Cloud hosting",
            "cloud-software": "Lot 2: Cloud software",
            "cloud-support": "Lot 3: Cloud support",
            "cloud-professional": "Lot 4: Cloud professional"
        },
        "lotOrder": [
            "cloud-hosting",
            "cloud-software",
            "cloud-support",
            "cloud-professional"
        ],
        "pageTotal": 44,
        "signaturePageNumber": 3,
        "variations": {}
    }
    default_data = {
        "id": 1,
        "name": "G-Cloud 13",
        "slug": "g-cloud-13",
        "framework": "g-cloud",
        "family": "g-cloud",
        "status": "open",
        "clarificationQuestionsOpen": True,
        "allowDeclarationReuse": True,
        "frameworkAgreementDetails": {},
        "countersignerName": "Zachary X. Signer",
        "frameworkAgreementVersion": "RM1557x",
        "variations": {},
        'clarificationsCloseAtUTC': "2000-01-01T00:00:00.000000Z",
        'clarificationsPublishAtUTC': "2000-01-02T00:00:00.000000Z",
        'applicationsCloseAtUTC': "2000-01-03T00:00:00.000000Z",
        'intentionToAwardAtUTC': "2000-01-04T00:00:00.000000Z",
        'frameworkLiveAtUTC': "2000-01-05T00:00:00.000000Z",
        'frameworkExpiresAtUTC': "2000-01-06T00:00:00.000000Z",
        'isESignatureSupported': False
    }
    optional_keys = [
        ('family', 'framework_family'),
        ('hasDirectAward', 'has_direct_award'),
        ('hasFurtherCompetition', 'has_further_competition'),
        ('clarificationQuestionsOpen', 'clarification_questions_open'),
        ('allowDeclarationReuse', 'allow_declaration_reuse')
    ]
    datestamp_keys = [
        ('clarificationsCloseAtUTC', 'clarifications_close_at'),
        ('clarificationsPublishAtUTC', 'clarifications_publish_at'),
        ('applicationsCloseAtUTC', 'applications_close_at'),
        ('intentionToAwardAtUTC', 'intention_to_award_at'),
        ('frameworkLiveAtUTC', 'framework_live_at'),
        ('frameworkExpiresAtUTC', 'framework_expires_at'),
    ]

    def derive_framework_details_from_slug(self, **kwargs):
        slug = kwargs.get('slug', 'g-cloud-13')
        name = kwargs.get('name')
        lots = kwargs.get('lots', [])

        if slug.startswith('g-cloud'):
            family = kwargs.get('framework_family') or kwargs.get('family') or 'g-cloud'
            name = name or 'G-Cloud {}'.format(slug.split('-')[-1])
            has_direct_award = kwargs.get('has_direct_award', True)
            has_further_competition = kwargs.get('has_further_competition', False)
            framework_iteration = int(slug.split('-')[-1])
            if not lots:
                lots = as_a_service_lots() if framework_iteration <= 8 else cloud_lots()

        elif slug.startswith('digital-outcomes-and-specialists'):
            family = kwargs.get('framework_family') or kwargs.get('family', 'digital-outcomes-and-specialists')
            name = name or slug.replace("-", " ").title().replace('And', 'and')
            has_direct_award = kwargs.get('has_direct_award', False)
            has_further_competition = kwargs.get('has_further_competition', True)
            if not lots:
                lots = dos_lots()

        else:
            family = kwargs.get('framework_family') or kwargs.get('family', slug)
            name = name or slug.replace("-", " ").title()
            has_direct_award = kwargs.get('has_direct_award', True)
            has_further_competition = kwargs.get('has_further_competition', True)

        return {
            "name": name,
            "family": family,
            "hasDirectAward": has_direct_award,
            "hasFurtherCompetition": has_further_competition,
            "lots": lots
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Overwrite framework details and lots if slug supplied
        self.response_data.update(**self.derive_framework_details_from_slug(**kwargs))

        # Backwards compatibility for deprecated 'framework' key
        self.response_data['framework'] = self.response_data['family']

        # Allow framework_agreement_version kwarg with null value
        if 'framework_agreement_version' in kwargs:
            if kwargs.get('framework_agreement_version') is not None:
                self.response_data['frameworkAgreementVersion'] = kwargs.pop('framework_agreement_version')
                self.response_data['frameworkAgreementDetails']['frameworkAgreementVersion'] = \
                    self.response_data['frameworkAgreementVersion']
            else:
                # G7 frameworks and earlier have null versions
                self.response_data['frameworkAgreementVersion'] = None
                self.response_data['frameworkAgreementDetails']['frameworkAgreementVersion'] = None

        # Convert any datetime kwargs to datestamps
        for key, snakecase_kwarg in self.datestamp_keys:
            if kwargs.get(snakecase_kwarg) is not None:
                if isinstance(kwargs.get(snakecase_kwarg), dt):
                    self.response_data[key] = kwargs.get(snakecase_kwarg).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                else:
                    self.response_data[key] = kwargs.get(snakecase_kwarg)
                del self.response_data[snakecase_kwarg]

        # Copy variations to nested framework agreement details
        self.response_data['frameworkAgreementDetails']['variations'] = self.response_data['variations']

        # Copy lots to nested framework agreement details
        if 'lots' in kwargs:
            self.response_data['frameworkAgreementDetails']['lotOrder'] = [
                lot['slug'] for lot in self.response_data['lots']
            ]
            self.response_data['frameworkAgreementDetails']['lotDescriptions'] = {
                lot['slug']: f"Lot {i+1}: {lot['name']}"
                for i, lot in enumerate(self.response_data['lots'])
            }
