import requests                                                                          
import pexpect                                                                           
import pytest                                                                            
import json                                                                              
import os                                                                                
import re                                                                                
import time                                                                              

from os import system                                                                    

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
    system("mlsteam data rb bk/cifar10")

    url = '{}/{}'.format(base_url, 'projects')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    dic=response.json()

    for proj in dic:
        if proj['name'] == 'test_api_project_negative':
            url = '{}/{}/{}'.format(base_url, 'projects', proj['id'])
            data = None
            response = requests.delete(url, timeout=tout, headers=headers)
            print((response.text))
            assert response.status_code == 200
                                                                                         
                                                                                         
"""                                                                                      
 user account related test cases                                                         
"""  
def test_wrong_password():
    child = pexpect.spawn('mlsteam login --address {} --username superuser'.format(API_SERVER_ADDRESS))  
    child.expect ('password:')                                                           
    child.sendline ('wrong_password')                                                         
    child.expect(pexpect.EOF)                                                            
    out=child.before                                                                     
    exp=re.findall(b"Login success", out)                                                
    assert exp != [b'Login success']  

"""
 project related test cases
"""
def test_project_create_no_dataset():
    url = '{}/{}'.format(base_url, 'projects')
    response = requests.post(url, timeout=tout, headers=headers, data={ 'name':'test_api_project_negative', 'dataset':'wrong_dataset' }) #TODO pass is_member_only
    print((response.text))
    assert response.status_code != 200


def test_project_create_exists():
    url = '{}/{}'.format(base_url, 'projects')
    response = requests.post(url, timeout=tout, headers=headers, data={ 'name':'test_api_project_negative', 'dataset':'cifar10' }) #TODO pass is_member_only
    response = requests.post(url, timeout=tout, headers=headers, data={ 'name':'test_api_project_negative', 'dataset':'cifar10' }) #TODO pass is_member_only
    print((response.text))
    assert response.status_code != 200

def test_project_member_add_wrong_name():
    url = '{}/{}'.format(base_url, 'projects')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    dic=response.json()

    for proj in dic:
        if proj['name'] == 'test_api_project_negative':
            url = '{}/{}/{}/{}'.format(base_url, 'projects', proj['id'], 'members')
            data = None
            response = requests.post(url, timeout=tout, headers=headers, data={'username':'wrong_username'})
            print((response.text))
            assert response.status_code != 200

def test_project_member_remove_owner():
    url = '{}/{}'.format(base_url, 'projects')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    dic=response.json()

    for proj in dic:
        if proj['name'] == 'test_api_project_negative':
            url = '{}/{}/{}/{}/{}'.format(base_url, 'projects', proj['id'], 'members', 'superuser')
            data = None
            response = requests.delete(url, timeout=tout, headers=headers)
            print((response.text))
            assert response.status_code != 200


"""
work related test cases
"""
def test_work_create_wrong_project():
    url = '{}/{}'.format(base_url, 'works')
    data = {'container':'myelintek/python-gpu:v5', 'num_gpu':'1', 'dataset':'cifar10', 'project':'wrong_project', 'port_list':'8888', 'user_args':"jupyter-notebook --ip 0.0.0.0 --allow-root --NotebookApp.token='JOB_ID'"}
    response = requests.post(url, timeout=tout, headers=headers, data=data)
    print((response.text))
    assert response.status_code != 200

def test_work_create_wrong_dataset():
    url = '{}/{}'.format(base_url, 'works')
    data = {'container':'myelintek/python-gpu:v5', 'num_gpu':'1', 'dataset':'wrong_dataset', 'project':'test_api_project_negative', 'port_list':'8888', 'user_args':"jupyter-notebook --ip 0.0.0.0 --allow-root --NotebookApp.token='JOB_ID'"}
    response = requests.post(url, timeout=tout, headers=headers, data=data)
    print((response.text))
    assert response.status_code != 200

def test_work_create_wrong_container():
    url = '{}/{}'.format(base_url, 'works')
    data = {'container':'wrong_container', 'num_gpu':'1', 'dataset':'cifar10', 'project':'test_api_project_negative', 'port_list':'8888', 'user_args':"jupyter-notebook --ip 0.0.0.0 --allow-root --NotebookApp.token='JOB_ID'"}
    response = requests.post(url, timeout=tout, headers=headers, data=data)
    print((response.text))
    assert response.status_code != 200
