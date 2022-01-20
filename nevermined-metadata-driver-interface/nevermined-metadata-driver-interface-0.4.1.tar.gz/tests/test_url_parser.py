from metadata_driver_interface.driver_interface import DriverInterface


def test_parse_url_azure():
    assert DriverInterface.parse_url(
        'https://testocnfiles.blob.core.windows.net/testfiles/testzkp.pdf') == 'azure'


def test_parse_url_aws():
    assert DriverInterface.parse_url('s3://my_bucket') == 'aws'


def test_parse_url_on_premise():
    assert DriverInterface.parse_url('http://www.example.com') == 'onprem'


def test_parse_url_ipfs():
    assert DriverInterface.parse_url('ipfs://ZmOfotxMWnLTXKKW0GPV9NgtEugghgD8HgzSF4gSrp7mL9') == 'ipfs'
