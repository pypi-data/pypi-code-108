"""
Checking functionality
"""


def fake_phone(value: str) -> bool:
    """ Check a phone for a test format """

    if value is None:
        return False

    value = str(value)

    return any(
        fake in value
        for fake in (
            '0000', '1111', '2222', '3333', '4444', '5555', '6666', '7777',
            '8888', '9999', '1234', '2345', '3456', '4567', '5678', '6789',
            '9876', '8765', '7654', '6543', '5432', '4321',
        )
    )

def fake_login(value: str) -> bool:
    """ Check a login / name / mail for a test format """

    if value is None:
        return False

    value = value.lower()

    return any(
        fake in value
        for fake in (
            'test', 'тест', 'check',
            'asd', 'qwe', 'rty', 'sdf', 'sfg', 'sfd', 'hgf', 'gfd',
            'qaz', 'wsx', 'edc', 'rfv',
            '111', '123',
            'ыва', 'фыв', 'йцу', 'орп',
        )
    )
