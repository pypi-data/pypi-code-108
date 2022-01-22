import json
import os
import re
import time
from os import system

import requests
import pexpect
import pytest

from .config import API_BASE_URL, API_SERVER_ADDRESS, DATA_PORT

headers={}
base_url=API_BASE_URL
tout=100


def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    child = pexpect.spawn('mlsteam login --address {} --username superuser --data-port {}'.format(API_SERVER_ADDRESS, DATA_PORT))
    child.expect ('password:')
    child.sendline ('superuser')
    child.expect(pexpect.EOF)
    out=child.before
    exp=re.findall(b"Login success", out)
    assert exp==[b'Login success']
    config_path = os.path.join(os.getenv('HOME'), '.mlsteam', 'cred')
    with open(config_path, 'r') as cred:
        data = json.load(cred)
    headers.update({'Authorization': 'Bearer {}'.format(data['access_token'])})

    system("mlsteam data mb bk/cifar10")
    system("mlsteam data cp -r /workspace/cifar10/* bk/cifar10")
    system("mlsteam data ls bk/cifar10")
    

def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
#    pytest.skip()
    system("mlsteam data rb bk/cifar10") 


"""
 user account related test cases
"""
def test_user_list():
    url = '{}/{}'.format(base_url, 'users')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    print((response.text))
    assert response.status_code == 200


def test_user_add():
    pytest.skip()

def test_user_inactive():
    pytest.skip()

def test_user_remove():
    pytest.skip()


"""
 project related test cases
"""

def test_project_create_private():
    url = '{}/{}'.format(base_url, 'projects')
    #data1 = json.dumps({ 'name':'test_api_project', 'dataset':'cifar10', 'is_member_only':True })
    #response = requests.post(url, timeout=tout, headers=headers, data=data1) #TODO pass is_member_only
    response = requests.post(url, timeout=tout, headers=headers, data={ 'name':'test_api_project', 'dataset':'cifar10' }) #TODO pass is_member_only
    print((response.text))
    assert response.status_code == 200


def test_project_create_public():
    url = '{}/{}'.format(base_url, 'projects')
    data = None
    response = requests.post(url, timeout=tout, headers=headers, data={'name':'test_api_project_public', 'dataset':'cifar10'}) #TODO pass is_member_only
    print((response.text))
    assert response.status_code == 200


def test_project_list():
    url = '{}/{}'.format(base_url, 'projects')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    dic=response.json()
    print(dic)
    assert response.status_code == 200



def test_project_info():
    url = '{}/{}'.format(base_url, 'projects')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    dic=response.json()

    for proj in dic:
        if proj['name'] == 'test_api_project_public' or  proj['name'] == 'test_api_project':
            url = '{}/{}/{}'.format(base_url, 'projects', proj['id'])
            data = None
            response = requests.get(url, timeout=tout, headers=headers)
            print((response.text))
            assert response.status_code == 200



def test_project_member_list():
    url = '{}/{}'.format(base_url, 'projects')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    dic=response.json()

    for proj in dic:
        if proj['name'] == 'test_api_project_public' or  proj['name'] == 'test_api_project':
            url = '{}/{}/{}/{}'.format(base_url, 'projects', proj['id'], 'members')
            data = None
            response = requests.get(url, timeout=tout, headers=headers)
            print((response.text))
            assert response.status_code == 200



def test_project_member_add():
    url = '{}/{}'.format(base_url, 'projects')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    dic=response.json()

    for proj in dic:
        if proj['name'] == 'test_api_project_public' or  proj['name'] == 'test_api_project':
            url = '{}/{}/{}/{}'.format(base_url, 'projects', proj['id'], 'members')
            data = None
            response = requests.post(url, timeout=tout, headers=headers, data={'username':'test1'})
            print((response.text))
            assert response.status_code == 200


def test_project_member_remove():
    url = '{}/{}'.format(base_url, 'projects')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    dic=response.json()

    for proj in dic:
        if proj['name'] == 'test_api_project_public' or  proj['name'] == 'test_api_project':
            url = '{}/{}/{}/{}/{}'.format(base_url, 'projects', proj['id'], 'members', 'test1')
            data = None
            response = requests.delete(url, timeout=tout, headers=headers)
            print((response.text))
            assert response.status_code == 200

"""
work related test cases
"""
def test_work_create():
    url = '{}/{}'.format(base_url, 'works')
    data = {'container':'myelintek/python-gpu:v5', 'num_gpu':'1', 'dataset':'cifar10', 'project':'test_api_project_public', 'port_list':'8888', 'user_args':"jupyter-notebook --ip 0.0.0.0 --allow-root --NotebookApp.token='JOB_ID'"} 
    response = requests.post(url, timeout=tout, headers=headers, data=data) 
    print((response.text))


def test_work_list():
    url = '{}/{}'.format(base_url, 'works')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    print((response.text))

def test_work_info():
    url = '{}/{}'.format(base_url, 'works')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    dic=response.json()

    for work in dic:
        if work['project'] == 'test_api_project_public' or  work['project'] == 'test_api_project':
            url = '{}/{}/{}'.format(base_url, 'works', work['id'])
            data = None
            response = requests.get(url, timeout=tout, headers=headers)
            print((response.text))
            assert response.status_code == 200


"""
Cleanup
"""
def test_work_delete():
    url = '{}/{}'.format(base_url, 'works')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    dic=response.json()

    for work in dic:
        if work['project']['name'] == 'test_api_project_public' or  work['project']['name'] == 'test_api_project':
            time.sleep(10)
            url = '{}/{}/{}'.format(base_url, 'works', work['id'])
            print((work['id']))
            data = None
            response = requests.delete(url, timeout=tout, headers=headers)
            print((response.text))
            assert response.status_code == 200
            time.sleep(30)
            response = requests.get(url, timeout=tout, headers=headers)
            assert response.text == '{}\n'


def test_project_delete():
    url = '{}/{}'.format(base_url, 'projects')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    dic=response.json()

    for proj in dic:
        if proj['name'] == 'test_api_project_public' or  proj['name'] == 'test_api_project':
            url = '{}/{}/{}'.format(base_url, 'projects', proj['id'])
            data = None
            response = requests.delete(url, timeout=tout, headers=headers)
            print((response.text))
            assert response.status_code == 200
