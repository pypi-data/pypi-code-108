from flask import Blueprint
from dmutils.user import User
from flask_login import login_user

login_for_tests = Blueprint('login_for_tests', __name__)


# Simplified example responses from the API
USERS = {
    '123': {
        'id': 123,
        'name': 'Name',
        'emailAddress': 'email@email.com',
        'role': 'supplier',
        'supplier': {
            'name': 'Supplier Name',
            'supplierId': 1234,
            'organisationSize': 'small',
        },
        'userResearchOptedIn': True,
    },
    '234': {
        'id': 234,
        'name': 'Buyer',
        'emailAddress': 'buyer@email.com',
        'role': 'buyer',
        'userResearchOptedIn': True,
    },
}


@login_for_tests.route('/auto-supplier-login')
def auto_supplier_login():
    user_json = {"users": USERS['123']}
    user = User.from_json(user_json)
    login_user(user)
    return "OK"


@login_for_tests.route('/auto-buyer-login')
def auto_buyer_login():
    user_json = {"users": USERS['234']}
    user = User.from_json(user_json)
    login_user(user)
    return "OK"
