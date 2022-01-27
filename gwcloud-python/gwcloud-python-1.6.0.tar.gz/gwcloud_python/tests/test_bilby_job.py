from gwcloud_python import BilbyJob, GWCloud, FileReference, FileReferenceList
import pytest
from gwcloud_python.utils import file_filters


@pytest.fixture
def png_data_result():
    return FileReferenceList([
        FileReference(path='data/dir/test1.png', file_size='1', download_token='test_download_token_1'),
        FileReference(path='data/dir/test2.png', file_size='1', download_token='test_download_token_2'),
        FileReference(path='result/dir/test1.png', file_size='1', download_token='test_download_token_3'),
        FileReference(path='result/dir/test2.png', file_size='1', download_token='test_download_token_4'),
    ])


@pytest.fixture
def png_extra():
    return FileReferenceList([
        FileReference(path='test1.png', file_size='1', download_token='test_download_token_5'),
        FileReference(path='test2.png', file_size='1', download_token='test_download_token_6'),
        FileReference(path='arbitrary/dir/test1.png', file_size='1', download_token='test_download_token_7'),
        FileReference(path='arbitrary/dir/test2.png', file_size='1', download_token='test_download_token_8'),
    ])


@pytest.fixture
def corner():
    return FileReferenceList([
        FileReference(path='test1_corner.png', file_size='1', download_token='test_download_token_9'),
        FileReference(path='test2_corner.png', file_size='1', download_token='test_download_token_10'),
    ])


@pytest.fixture
def config():
    return FileReferenceList([
        FileReference(path='a_config_complete.ini', file_size='1', download_token='test_download_token_11'),
    ])


@pytest.fixture
def json():
    return FileReferenceList([
        FileReference(path='result/dir/a_merge_result.json', file_size='1', download_token='test_download_token_12'),
    ])


@pytest.fixture
def index():
    return FileReferenceList([
        FileReference(path='index.html', file_size='1', download_token='test_download_token_13'),
    ])


@pytest.fixture
def png(png_data_result, png_extra, corner):
    return png_data_result + png_extra + corner


@pytest.fixture
def default(png_data_result, config, json, index):
    return png_data_result + config + json + index


@pytest.fixture
def full(png, config, json, index):
    return png + config + json + index


@pytest.fixture
def setup_mock_gwcloud(mocker, full):
    def mock_init(self, token, endpoint='test.endpoint.com'):
        pass

    def mock_get_files_by_job_id(self, job_id):
        return full, {'bilbyResultFiles': {'isUploadedJob': False}}

    mocker.patch('gwcloud_python.gwcloud.GWCloud.__init__', mock_init)
    mocker.patch('gwcloud_python.gwcloud.GWCloud._get_files_by_job_id', mock_get_files_by_job_id)

    return GWCloud(token='test_token')


@pytest.fixture
def bilby_job(setup_mock_gwcloud):
    return BilbyJob(
        client=setup_mock_gwcloud,
        job_id='test_id',
        name='TestName',
        description='Test description',
        job_status={
            'name': 'Completed',
            'date': '2021-12-02'
        }
    )


def test_bilby_job_full_file_list(bilby_job, full):
    assert bilby_job.get_full_file_list() == full


def test_bilby_job_file_filters(bilby_job, default, png, corner, config):
    assert file_filters.sort_file_list(bilby_job.get_default_file_list()) == file_filters.sort_file_list(default)
    assert file_filters.sort_file_list(bilby_job.get_png_file_list()) == file_filters.sort_file_list(png)
    assert file_filters.sort_file_list(bilby_job.get_corner_plot_file_list()) == file_filters.sort_file_list(corner)
    assert file_filters.sort_file_list(bilby_job.get_config_file_list()) == file_filters.sort_file_list(config)


def test_register_file_list_filter(bilby_job, index):
    def get_html_file(file_list):
        return [f for f in file_list if f.path.suffix == '.html']

    assert getattr(bilby_job, 'get_index_file_list', None) is None
    assert getattr(bilby_job, 'get_index_files', None) is None
    assert getattr(bilby_job, 'save_index_files', None) is None

    BilbyJob.register_file_list_filter('index', get_html_file)

    assert getattr(bilby_job, 'get_index_file_list', None) is not None
    assert getattr(bilby_job, 'get_index_files', None) is not None
    assert getattr(bilby_job, 'save_index_files', None) is not None

    assert bilby_job.get_index_file_list() == index
