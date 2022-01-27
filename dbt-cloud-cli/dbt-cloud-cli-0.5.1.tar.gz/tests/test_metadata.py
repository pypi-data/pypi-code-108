from dbt_cloud.command import DbtCloudMetadataQueryCommand


def test_foo():
    DbtCloudMetadataQueryCommand.click_options(lambda x: x)
