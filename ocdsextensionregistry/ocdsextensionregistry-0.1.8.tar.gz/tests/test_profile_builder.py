import json
import logging
from pathlib import Path

from ocdsextensionregistry import ProfileBuilder
from tests import path

standard_codelists = [
    'awardCriteria.csv',
    'awardStatus.csv',
    'contractStatus.csv',
    'currency.csv',
    'documentType.csv',
    'extendedProcurementCategory.csv',
    'initiationType.csv',
    'itemClassificationScheme.csv',
    'method.csv',
    'milestoneStatus.csv',
    'milestoneType.csv',
    'partyRole.csv',
    'procurementCategory.csv',
    'relatedProcess.csv',
    'relatedProcessScheme.csv',
    'releaseTag.csv',
    'submissionMethod.csv',
    'tenderStatus.csv',
    'unitClassificationScheme.csv',
]

new_extension_codelists = [
    # ppp
    'metricID.csv',
    'milestoneCode.csv',
    # charges, tariffs
    'chargePaidBy.csv',
]


def test_extensions():
    builder = ProfileBuilder('1__1__4', {'charges': 'master', 'location': 'v1.1.4'})
    result = list(builder.extensions())

    assert len(result) == 2
    assert result[0].as_dict() == {
        'id': 'charges',
        'date': '',
        'version': 'master',
        'base_url': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_charges_extension/master/',
        'download_url': 'https://github.com/open-contracting-extensions/ocds_charges_extension/archive/master.zip',
    }
    assert result[1].as_dict() == {
        'id': 'location',
        'date': '2019-02-25',
        'version': 'v1.1.4',
        'base_url': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1.4/',
        'download_url': 'https://api.github.com/repos/open-contracting-extensions/ocds_location_extension/zipball/v1.1.4',  # noqa: E501
    }


def test_release_schema_patch():
    # Use the ppp extension to test null values.
    builder = ProfileBuilder('1__1__4', {
        'https://raw.githubusercontent.com/open-contracting-extensions/ocds_ppp_extension/70c5cb759d4739d1eca5db832e723afb69bbdae0/',  # noqa: E501
        'https://github.com/open-contracting-extensions/ocds_location_extension/archive/v1.1.4.zip',
    })
    result = builder.release_schema_patch()

    # Merges patches.
    assert 'Location' in result['definitions']

    # Preserves null values.
    assert result['properties']['buyer'] is None
    assert 'REPLACE_WITH_NULL' not in json.dumps(result)


def test_patched_release_schema():
    # Use the ppp extension to test null values.
    builder = ProfileBuilder('1__1__5', {
        'https://raw.githubusercontent.com/open-contracting-extensions/ocds_ppp_extension/70c5cb759d4739d1eca5db832e723afb69bbdae0/',  # noqa: E501
        'https://github.com/open-contracting-extensions/ocds_location_extension/archive/v1.1.5.zip',
    })
    result = builder.patched_release_schema()

    # Patches core.
    assert '$schema' in result
    assert 'Location' in result['definitions']

    # Removes null'ed fields.
    assert 'buyer' not in result['properties']


def test_patched_release_schema_with_extension_field():
    builder = ProfileBuilder('1__1__4', {'location': 'v1.1.4'})
    result = builder.patched_release_schema(extension_field='extension')

    definition = result['definitions']['Location']
    assert definition['extension'] == 'Location'
    assert definition['properties']['geometry']['extension'] == 'Location'
    assert definition['properties']['geometry']['properties']['type']['extension'] == 'Location'


def test_patched_release_schema_with_extension_field_and_language():
    builder = ProfileBuilder('1__1__4', ['https://extensions.open-contracting.org/en/extensions/location/master/'])
    result = builder.patched_release_schema(extension_field='extension', language='es')

    definition = result['definitions']['Location']
    assert definition['extension'] == 'Ubicación'
    assert definition['properties']['geometry']['extension'] == 'Ubicación'
    assert definition['properties']['geometry']['properties']['type']['extension'] == 'Ubicación'


def test_patched_release_schema_with_metadata_url():
    url = 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_coveredBy_extension/master/extension.json'  # noqa: E501
    builder = ProfileBuilder('1__1__4', [url])
    result = builder.patched_release_schema()

    assert '$schema' in result
    assert 'coveredBy' in result['definitions']['Tender']['properties']


def test_patched_release_schema_with_base_url():
    url = 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_coveredBy_extension/master/'
    builder = ProfileBuilder('1__1__4', [url])
    result = builder.patched_release_schema()

    assert '$schema' in result
    assert 'coveredBy' in result['definitions']['Tender']['properties']


def test_patched_release_schema_with_download_url():
    url = 'https://github.com/open-contracting-extensions/ocds_coveredBy_extension/archive/master.zip'
    builder = ProfileBuilder('1__1__4', [url])
    result = builder.patched_release_schema()

    assert '$schema' in result
    assert 'coveredBy' in result['definitions']['Tender']['properties']


def test_patched_release_schema_with_absolute_path():
    url = Path(path('ocds_coveredBy_extension')).resolve().as_uri()
    builder = ProfileBuilder('1__1__4', [url])
    result = builder.patched_release_schema()

    assert '$schema' in result
    assert 'coveredBy' in result['definitions']['Tender']['properties']


def test_patched_release_schema_with_schema_base_url():
    schema_base_url = 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/'
    builder = ProfileBuilder('1__1__4', {}, schema_base_url=schema_base_url)
    result = builder.patched_release_schema()

    # Changes `id`.
    assert result['id'] == 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/release-schema.json'  # noqa: E501


def test_release_package_schema_with_schema_base_url():
    schema_base_url = 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/'
    builder = ProfileBuilder('1__1__4', {}, schema_base_url=schema_base_url)
    result = builder.release_package_schema()

    # Changes `id` and `$ref`.
    assert result['id'] == 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/release-package-schema.json'  # noqa: E501
    assert result['properties']['releases']['items']['$ref'] == 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/release-schema.json'  # noqa: E501


def test_release_package_schema_with_schema_base_url_and_embed():
    schema_base_url = 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/'
    builder = ProfileBuilder('1__1__4', {}, schema_base_url=schema_base_url)
    result = builder.release_package_schema(embed=True)

    # Changes `id` and `$ref`.
    assert result['id'] == 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/release-package-schema.json'  # noqa: E501
    assert result['properties']['releases']['items']['id'] == 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/release-schema.json'  # noqa: E501
    assert '$ref' not in result['properties']['releases']['items']


def test_record_package_schema_with_schema_base_url():
    schema_base_url = 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/'
    builder = ProfileBuilder('1__1__4', {}, schema_base_url=schema_base_url)
    result = builder.record_package_schema()

    # Changes `id` and `$ref`.
    assert result['id'] == 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/record-package-schema.json'  # noqa: E501
    assert result['definitions']['record']['properties']['compiledRelease']['$ref'] == 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/release-schema.json'  # noqa: E501
    assert result['definitions']['record']['properties']['releases']['oneOf'][1]['items']['$ref'] == 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/release-schema.json'  # noqa: E501


def test_record_package_schema_with_schema_base_url_and_embed():
    schema_base_url = 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/'
    builder = ProfileBuilder('1__1__4', {}, schema_base_url=schema_base_url)
    result = builder.record_package_schema(embed=True)

    # Changes `id` and `$ref`.
    assert result['id'] == 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/record-package-schema.json'  # noqa: E501
    assert result['definitions']['record']['properties']['compiledRelease']['id'] == 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/release-schema.json'  # noqa: E501
    assert result['definitions']['record']['properties']['releases']['oneOf'][1]['items']['id'] == 'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/release-schema.json'  # noqa: E501
    assert '$ref' not in result['definitions']['record']['properties']['compiledRelease']
    assert '$ref' not in result['definitions']['record']['properties']['releases']['oneOf'][1]['items']


def test_standard_codelists():
    builder = ProfileBuilder('1__1__4', {})
    result = builder.standard_codelists()

    # Collects codelists.
    assert len(result) == 19
    assert [codelist.name for codelist in result] == standard_codelists

    # Preserves content.
    assert result[0].name == 'awardCriteria.csv'
    assert len(result[0]) == 8
    assert len(result[0][0]) == 4
    assert result[0][0]['Code'] == 'priceOnly'
    assert result[0][0]['Title'] == 'Price only'
    assert result[0][0]['Description'].startswith('The award will be made to the qualified bid with the lowest ')
    assert result[0][0]['Deprecated'] == ''


def test_extension_codelists(caplog):
    caplog.set_level(logging.INFO, logger='ocdsextensionregistry')

    # Note: We can't yet test, using real data, whether an error is raised if a codelist replacement either doesn't
    # contain added codes, or contains removed codes. If we were to use test data, we could create a test registry
    # and test extensions, or mock HTTP requests…. For now, additions were tested manually. We also can't yet test
    # whether an error is raised if two codelist replacements differ.

    # charges and tariffs both have chargePaidBy.csv, but the content is identical, so should not error. ppp has
    # documentType.csv and tariffs has +documentType.csv, but documentType.csv contains the codes added by
    # +documentType.csv, so should not error. ppp and enquiries both have +partyRole.csv.
    builder = ProfileBuilder('1__1__4', {
        'https://raw.githubusercontent.com/open-contracting-extensions/ocds_ppp_extension/70c5cb759d4739d1eca5db832e723afb69bbdae0/',  # noqa: E501
        'https://github.com/open-contracting-extensions/ocds_enquiry_extension/archive/v1.1.4.zip',
        'https://github.com/open-contracting-extensions/ocds_charges_extension/archive/master.zip',
        'https://github.com/open-contracting-extensions/ocds_tariffs_extension/archive/1.1.zip',
    })
    result = sorted(builder.extension_codelists())
    plus_party_role = next(codelist for codelist in result if codelist.name == '+partyRole.csv')

    # Collects codelists.
    assert len(result) == 9
    assert [codelist.name for codelist in result] == sorted([
        '+milestoneType.csv',
        '+partyRole.csv',
        '+releaseTag.csv',
        '-partyRole.csv',
        'documentType.csv',
        'initiationType.csv',
    ] + new_extension_codelists)

    # Preserves content.
    assert result[0].name == '+milestoneType.csv'
    assert len(result[0]) == 2
    assert len(result[0][0]) == 4
    assert result[0][0]['Code'] == 'procurement'
    assert result[0][0]['Title'] == 'Procurement'
    assert result[0][0]['Description'].startswith('Events taking place during the procurement which are not ')
    assert result[0][0]['Source'] == ''

    # Combines codelist additions and removals.
    assert len(plus_party_role) == 13
    assert sorted(plus_party_role)[-1]['Code'] == 'socialWitness'

    # Logs ignored codelists.
    assert len(caplog.records) == 1
    assert caplog.records[-1].levelname == 'INFO'
    assert caplog.records[-1].message == 'documentType.csv has the codes added by +documentType.csv - ignoring +documentType.csv'  # noqa: E501


def test_patched_codelists(caplog):
    caplog.set_level(logging.INFO, logger='ocdsextensionregistry')

    builder = ProfileBuilder('1__1__4', [
        'https://raw.githubusercontent.com/open-contracting-extensions/ocds_ppp_extension/70c5cb759d4739d1eca5db832e723afb69bbdae0/',  # noqa: E501
        'https://github.com/open-contracting-extensions/ocds_charges_extension/archive/master.zip',
        'https://github.com/open-contracting-extensions/ocds_tariffs_extension/archive/1.1.zip',
    ])
    result = builder.patched_codelists()
    party_role = next(codelist for codelist in result if codelist.name == 'partyRole.csv')
    initiation_type = next(codelist for codelist in result if codelist.name == 'initiationType.csv')

    # Collects codelists.
    assert len(result) == 22
    assert [codelist.name for codelist in result] == standard_codelists + new_extension_codelists

    # Preserves content.
    assert result[0].name == 'awardCriteria.csv'
    assert len(result[0]) == 8
    assert len(result[0][0]) == 4
    assert result[0][0]['Code'] == 'priceOnly'
    assert result[0][0]['Title'] == 'Price only'
    assert result[0][0]['Description'].startswith('The award will be made to the qualified bid with the lowest ')
    assert result[0][0]['Deprecated'] == ''

    # Adds codes.
    assert any(row['Code'] == 'publicAuthority' for row in party_role)

    # Removes codes.
    assert not any(row['Code'] == 'buyer' for row in party_role)

    # Replaces list.
    assert all(row['Code'] == 'ppp' for row in initiation_type)

    # Logs ignored codelists.
    assert len(caplog.records) == 1
    assert caplog.records[-1].levelname == 'INFO'
    assert caplog.records[-1].message == 'documentType.csv has the codes added by +documentType.csv - ignoring +documentType.csv'  # noqa: E501


def test_get_standard_file_contents():
    builder = ProfileBuilder('1__1__4', {})
    data = builder.get_standard_file_contents('release-schema.json')
    # Repeat requests should return the same result.
    data = builder.get_standard_file_contents('release-schema.json')

    assert json.loads(data)
