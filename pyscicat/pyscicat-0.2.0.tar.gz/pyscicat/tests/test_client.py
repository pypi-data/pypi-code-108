from datetime import datetime
from pathlib import Path

import requests_mock
from ..client import (
    from_credentials,
    from_token,
    encode_thumbnail,
    get_file_mod_time,
    get_file_size,
)

from ..model import (
    Attachment,
    Datablock,
    DataFile,
    Dataset,
    Ownable,
)

local_url = "http://localhost:3000/api/v3/"


def add_mock_requests(mock_request):
    mock_request.post(
        local_url + "Users/login",
        json={"id": "a_token"},
    )
    mock_request.post(local_url + "Samples", json={"sampleId": "dataset_id"})
    mock_request.post(local_url + "RawDatasets/replaceOrCreate", json={"pid": "42"})
    mock_request.post(
        local_url + "RawDatasets/42/origdatablocks",
        json={"response": "random"},
    )
    mock_request.post(
        local_url + "RawDatasets/42/attachments",
        json={"response": "random"},
    )


def test_scicate_ingest():
    with requests_mock.Mocker() as mock_request:
        add_mock_requests(mock_request)
        scicat = from_credentials(
            base_url=local_url,
            username="Zaphod",
            password="heartofgold",
        )
        assert (
            scicat._token == "a_token"
        ), "scicat client set the token given by the server"

        ownable = Ownable(ownerGroup="magrathea", accessGroups=["deep_though"])
        thumb_path = Path(__file__).parent / "data/SciCatLogo.png"

        time = get_file_mod_time(thumb_path)
        assert time is not None
        size = get_file_size(thumb_path)
        assert size is not None

        # RawDataset
        dataset = Dataset(
            path="/foo/bar",
            size=42,
            owner="slartibartfast",
            contactEmail="slartibartfast@magrathea.org",
            creationLocation="magrathea",
            creationTime=str(datetime.now()),
            type="raw",
            instrumentId="earth",
            proposalId="deepthought",
            dataFormat="planet",
            principalInvestigator="A. Mouse",
            sourceFolder="/foo/bar",
            scientificMetadata={"a": "field"},
            sampleId="gargleblaster",
            **ownable.dict()
        )
        dataset_id = scicat.upload_raw_dataset(dataset)

        # Datablock with DataFiles
        data_file = DataFile(path="/foo/bar", size=42)
        data_block = Datablock(
            size=42,
            version=1,
            datasetId=dataset_id,
            dataFileList=[data_file],
            **ownable.dict()
        )
        scicat.upload_datablock(data_block)

        # Attachment
        attachment = Attachment(
            datasetId=dataset_id,
            thumbnail=encode_thumbnail(thumb_path),
            caption="scattering image",
            **ownable.dict()
        )
        scicat.upload_attachment(attachment)


def test_initializers():
    with requests_mock.Mocker() as mock_request:
        add_mock_requests(mock_request)

        client = from_token(local_url, "let me in!")
        assert client._token == "let me in!"
