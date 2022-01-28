from re import S
from unittest import mock
import pytest
from trebble.treblle import middleware

def test_masking():
    to_mask = {
        'card_number': '8'
    }
    trablle_class = middleware.TreblleMiddleware(mock.Mock())
    
    masked_json = trablle_class.go_through_json(to_mask)
    assert {'card_number': '*'} == masked_json

def test_long_json():
    trablle_class = middleware.TreblleMiddleware(mock.Mock())
    json_to_mask = {
    "secret": "g",
    "client_id": 1,
    "job_name": "dylan's job",
    "job_description": "Hi",
    "price": 50,
    "created_date": "2021-08-14T13:19:13+02:00",
    "excepted_date": "2021-08-31T13:19:23+02:00",
    "test": {
        "hello": "dylan",
        "secret": "dylan is awesome",
        "test": [
            {
                "secret": "5"
            },
            {
                "secret": "2"
            }
        ],
        "DylansTest": {
            "secret": [
                "3",
                "6"
            ],
            "test": {
                "test": [
                    {
                        "secret": "u"
                    }
                ]
            }
        }
    }
    }
    masked_json = trablle_class.go_through_json(json_to_mask)
    assert masked_json == {'secret': '*', 'client_id': 1, 'job_name': "dylan's job", 'job_description': 'Hi', 'price': 50, 
    'created_date': '2021-08-14T13:19:13+02:00', 'excepted_date': '2021-08-31T13:19:23+02:00', 
    'test': {'hello': 'dylan', 'secret': '****************', 'test': [{'secret': '*'}, {'secret': '*'}], 
    'DylansTest': {'secret': ['**', '**'], 'test': {'test': [{'secret': '*'}]}}}}
