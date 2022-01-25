import os
import pytest
import json
from boto3 import Session


@pytest.fixture(scope="session")
def source_documents(dummy_bucket):
    session = Session(
        aws_access_key_id='foo',
        aws_secret_access_key='bar',
        region_name='us-east-1'
    )
    s3 = session.client('s3')
    # Add PDFs
    for f_key in os.listdir('tests/fixtures/pdfs'):
        if f_key == '.DS_Store':
            continue
        with open('tests/fixtures/pdfs/' + f_key, 'rb') as f:
            object_key = 'pdfs/' + f_key
            s3.upload_fileobj(f, dummy_bucket.name, object_key)

        # Add 1 hidden file for testing.
        dstore = 'foo'
        with open(dstore, 'w') as newfile:
            newfile.write('bar')
        s3.upload_file(dstore, dummy_bucket.name, 'pdfs/.DS_Store')
        os.remove(dstore)

    # Add TIFFs
    for f_key in os.listdir('tests/fixtures/tiffs'):
        if f_key == '.DS_Store':
            continue
        with open('tests/fixtures/tiffs/' + f_key, 'rb') as f:
            object_key = 'tiffs/' + f_key
            s3.upload_fileobj(f, dummy_bucket.name, object_key)

    # Add PNGs
    for f_key in os.listdir('tests/fixtures/pngs'):
        if f_key == '.DS_Store':
            continue
        with open('tests/fixtures/pngs/' + f_key, 'rb') as f:
            object_key = 'pngs/' + f_key
            s3.upload_fileobj(f, dummy_bucket.name, object_key)

    # Add HTML files
    for f_key in os.listdir('tests/fixtures/html'):
        if f_key == '.DS_Store':
            continue
        with open('tests/fixtures/html/' + f_key, 'rb') as f:
            object_key = 'html/' + f_key
            s3.upload_fileobj(f, dummy_bucket.name, object_key)
