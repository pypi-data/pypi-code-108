from sqlalchemy import select, func


def test_upsert_role():
    assert str(select(func.puddl_upsert_role('unittest', 'unittest'))) == (
        'SELECT puddl_upsert_role(:puddl_upsert_role_2, :puddl_upsert_role_3) '
        'AS puddl_upsert_role_1'
    )
