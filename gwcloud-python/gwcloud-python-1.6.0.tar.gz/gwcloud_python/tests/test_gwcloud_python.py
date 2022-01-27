from gwcloud_python import GWCloud, FileReference, JobStatus
from gwcloud_python.utils import convert_dict_keys
import pytest


@pytest.fixture
def setup_mock_gwdc(mocker):
    def mock_gwdc(request_data):
        def mock_init(self, token, endpoint):
            pass

        def mock_request(self, query, variables=None, headers=None):
            return request_data

        mocker.patch('gwdc_python.gwdc.GWDC.__init__', mock_init)
        mocker.patch('gwdc_python.gwdc.GWDC.request', mock_request)

    return mock_gwdc


@pytest.fixture
def single_job_request(setup_mock_gwdc):
    job_data = {
        "id": 1,
        "name": "test_name",
        "description": "test description",
        "userId": 1,
        "jobStatus": {
            "name": "Completed",
            "date": "2021-12-02"
        }
    }
    setup_mock_gwdc({"bilbyJob": job_data})
    return job_data


@pytest.fixture
def multi_job_request(setup_mock_gwdc):
    def modify_query_name(query_name):
        job_data_1 = {
            "id": 1,
            "name": "test_name_1",
            "description": "test description 1",
            "userId": 1,
            "jobStatus": {
                "name": "Completed",
                "date": "2021-01-01"
            }
        }

        job_data_2 = {
            "id": 2,
            "name": "test_name_2",
            "description": "test description 2",
            "userId": 2,
            "jobStatus": {
                "name": "Completed",
                "date": "2021-02-02"
            }
        }

        job_data_3 = {
            "id": 3,
            "name": "test_name_3",
            "description": "test description 3",
            "userId": 3,
            "jobStatus": {
                "name": "Error",
                "date": "2021-03-03"
            }
        }

        setup_mock_gwdc({
            query_name: {
                "edges": [
                    {"node": job_data_1},
                    {"node": job_data_2},
                    {"node": job_data_3},
                ]
            }
        })

        return [job_data_1, job_data_2, job_data_3]

    return modify_query_name


@pytest.fixture
def job_file_request(setup_mock_gwdc):
    job_file_data_1 = {
        "path": "path/to/test.png",
        "fileSize": "1",
        "downloadToken": "test_token_1",
        "isDir": False
    }

    job_file_data_2 = {
        "path": "path/to/test.json",
        "fileSize": "10",
        "downloadToken": "test_token_2",
        "isDir": False
    }

    job_file_data_3 = {
        "path": "path/to/test",
        "fileSize": "100",
        "downloadToken": "test_token_3",
        "isDir": True
    }

    setup_mock_gwdc({
        "bilbyResultFiles": {
            "files": [
                job_file_data_1,
                job_file_data_2,
                job_file_data_3
            ],
            "isUploadedJob": False
        }
    })

    return [job_file_data_1, job_file_data_2, job_file_data_3]


@pytest.fixture
def user_jobs(multi_job_request):
    return multi_job_request('bilbyJobs')


def test_get_job_by_id(single_job_request):
    gwc = GWCloud(token='my_token')

    job = gwc.get_job_by_id('job_id')

    assert job.job_id == single_job_request["id"]
    assert job.name == single_job_request["name"]
    assert job.description == single_job_request["description"]
    assert job.status == JobStatus(
        status=single_job_request["jobStatus"]["name"],
        date=single_job_request["jobStatus"]["date"]
    )
    assert job.other['user_id'] == single_job_request["userId"]


def test_get_user_jobs(user_jobs):
    gwc = GWCloud(token='my_token')

    jobs = gwc.get_user_jobs()

    assert jobs[0].job_id == user_jobs[0]["id"]
    assert jobs[0].name == user_jobs[0]["name"]
    assert jobs[0].description == user_jobs[0]["description"]
    assert jobs[0].status == JobStatus(
        status=user_jobs[0]["jobStatus"]["name"],
        date=user_jobs[0]["jobStatus"]["date"]
    )
    assert jobs[0].other['user_id'] == user_jobs[0]["userId"]

    assert jobs[1].job_id == user_jobs[1]["id"]
    assert jobs[1].name == user_jobs[1]["name"]
    assert jobs[1].description == user_jobs[1]["description"]
    assert jobs[1].status == JobStatus(
        status=user_jobs[1]["jobStatus"]["name"],
        date=user_jobs[1]["jobStatus"]["date"]
    )
    assert jobs[1].other['user_id'] == user_jobs[1]["userId"]

    assert jobs[2].job_id == user_jobs[2]["id"]
    assert jobs[2].name == user_jobs[2]["name"]
    assert jobs[2].description == user_jobs[2]["description"]
    assert jobs[2].status == JobStatus(
        status=user_jobs[2]["jobStatus"]["name"],
        date=user_jobs[2]["jobStatus"]["date"]
    )
    assert jobs[2].other['user_id'] == user_jobs[2]["userId"]


def test_gwcloud_files_by_job_id(job_file_request):
    gwc = GWCloud(token='my_token')

    file_list, is_uploaded_job = gwc._get_files_by_job_id('arbitrary_job_id')

    for i, ref in enumerate(file_list):
        assert ref == FileReference(**convert_dict_keys(job_file_request[i]))
