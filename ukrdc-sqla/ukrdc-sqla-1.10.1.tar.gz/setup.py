# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ukrdc_sqla', 'ukrdc_sqla.utils']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.25,<2.0.0']

setup_kwargs = {
    'name': 'ukrdc-sqla',
    'version': '1.10.1',
    'description': 'SQLAlchemy models for the UKRDC',
    'long_description': '# UKRDC-SQLA\n\nSQLAlchemy models for the UKRDC and related databases.\n\n## Installation\n\n`pip install ukrdc-sqla`\n\n## Example Usage\n\n```python\nfrom datetime import datetime\n\nfrom ukrdc_sqla.ukrdc import LabOrder, PatientNumber, PatientRecord, ResultItem\n\ndef commit_extra_resultitem(session):\n    patient_record = PatientRecord(\n        pid="PYTEST01:LABORDERS:00000000L",\n        sendingfacility="PATIENT_RECORD_SENDING_FACILITY_1",\n        sendingextract="PV",\n        localpatientid="00000000L",\n        ukrdcid="000000001",\n        repository_update_date=datetime(2020, 3, 16),\n        repository_creation_date=datetime(2020, 3, 16),\n    )\n    patient_number = PatientNumber(\n        id=2,\n        pid="PYTEST01:LABORDERS:00000000L",\n        patientid="111111111",\n        organization="NHS",\n        numbertype="NI",\n    )\n    laborder = LabOrder(\n        id="LABORDER_TEST2_1",\n        pid="PYTEST01:LABORDERS:00000000L",\n        external_id="EXTERNAL_ID_TEST2_1",\n        order_category="ORDER_CATEGORY_TEST2_1",\n        specimen_collected_time=datetime(2020, 3, 16),\n    )\n    resultitem = ResultItem(\n        id="RESULTITEM_TEST2_1",\n        order_id="LABORDER_TEST2_1",\n        service_id_std="SERVICE_ID_STD_TEST2_1",\n        service_id="SERVICE_ID_TEST2_1",\n        service_id_description="SERVICE_ID_DESCRIPTION_TEST2_1",\n        value="VALUE_TEST2_1",\n        value_units="VALUE_UNITS_TEST2_1",\n        observation_time=datetime(2020, 3, 16),\n    )\n\n    session.add(patient_record)\n    session.add(patient_number)\n    session.add(laborder)\n    session.add(resultitem)\n\n    session.commit()\n```\n\n## Developer notes\n\n### Publish updates\n\n- Iterate the version number (`poetry version major/minor/patch`)\n- Push to GitHub repo\n- Create a GitHub release\n  - GitHub Actions will automatically publish the release to PyPI\n',
    'author': 'Joel Collins',
    'author_email': 'joel.collins@renalregistry.nhs.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
