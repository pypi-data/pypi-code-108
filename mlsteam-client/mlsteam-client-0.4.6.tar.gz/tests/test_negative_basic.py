import pexpect
import re
import os
import time
from os import system

from .config import API_SERVER_ADDRESS, DATA_PORT

def setup_module(module):
    child = pexpect.spawn('mlsteam login --address {} --username superuser --data-port {}'.format(API_SERVER_ADDRESS, DATA_PORT))
    child.expect ('password:')
    child.sendline ('superuser')
    child.expect(pexpect.EOF)
    out=child.before
    exp=re.findall(b"Login success", out)
    assert exp==[b'Login success']
    system("mlsteam data mb bk/cifar10")
    system("mlsteam data cp -r /workspace/cifar10/* bk/cifar10")
    system("mlsteam data ls bk/cifar10")

def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    #clean jobs if any test case failed
    job_ids=os.popen("mlsteam job list | awk '/job1/ {print $2}'").read()
    print(job_ids)
    print(job_ids.split('\n'))
    for job_id in job_ids.split('\n'):
        if job_id=='': continue
        ret=system("mlsteam job delete --job-id "+job_id)
        assert ret==0

    #clean dataset
    system("mlsteam data rb bk/cifar10")
    system("mlsteam data rb bk/wrong_dataset")

    #clean project
    proj_id=os.popen("mlsteam project list | awk '/test_negative_project/ {print $2}'").read()
    print(proj_id)
    ret=system("mlsteam project delete --id "+proj_id)

#wrong password is covered in api negative tests

# data
def test_data_cp_wrong_bucket():
    ret=system("mlsteam data cp /workspace/tests/fake_dataset/file1 bk/wrong_bucket")
    assert ret!=0

def test_data_ls_wrong_bucket():
    ret=system("mlsteam data ls bk/wrong_bucket")
    assert ret!=0

def test_data_rm_wrong_bucket():
    ret=system("mlsteam data rm bk/wrong_bucket/file1")
    assert ret!=0

def test_data_rb_wrong_bucket():
    ret=system("mlsteam data rb wrong_bucket")
    assert ret!=0

#project

def test_project_create_wrong_dataset():
    ret=system("mlsteam project create test_negative_project wrong_dataset")
    assert ret!=0

def test_project_create_same_name():
    ret=system("mlsteam project create test_negative_project cifar10")
    ret=system("mlsteam project create test_negative_project cifar10")
    assert ret!=0

def test_project_delete_wrong_id():
    ret=system("mlsteam project delete --id wrong_id")
    assert ret!=0

#job

def test_job_submit_wrong_project():
    ret=system("PROJECT=wrong project mlsteam job submit training --job-name job1 --package-path /workspace/example/cifar10_estimator")
    assert ret!=0

def test_job_submit_wrong_package():
    ret=system("PROJECT=test_negative_project project mlsteam job submit training --job-name job1 --package-path /wrong_path")
    assert ret!=0

def test_job_delete_wrong_id():
    ret=system("mlsteam job delete --job-id wrong_id")
    assert ret!=0


