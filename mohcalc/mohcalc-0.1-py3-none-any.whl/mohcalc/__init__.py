def add_numbers(a,b):
    return a+b

def mul_numbers(a,b):
    return a*b   

def div_numbers(a,b):
    return a/b

def sub_numbers(a,b):
    return a-b

    #  https://opensource.org/licenses/MIT
    # cd calculator
    #  py -i __init__.py
    # publish> pip install setuptools wheel
    # publish> pip install twine
    # publish> pip install tqdm
    # publish> py setup.py bdist_wheel
    # https://pypi.org/account/register/
    # publish> twine upload --repository-url https://upload pypi.org/legacy/ dist/*