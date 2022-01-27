import pytest
from kosmos import KosmosClient, KosmosEvent, KosmosDevice, KosmosScope, KosmosLocation, \
    KosmosNotFoundError, KosmosError, KosmosConflictError

import random, string


def getRandomString(len: int = 16) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=len))


def getKosmosAsUser():
    return KosmosClient("http://localhost:18080", "user", "pass")


def test_set():
    uuid = "virt_lamp_1"
    key = "on"
    kosmos = getKosmosAsUser()
    kosmos.set(uuid, {key: False})
    assert kosmos.get_device(uuid).state[key] == False
    kosmos.set(uuid, {key: True})
    assert kosmos.get_device(uuid).state[key] == True
    with pytest.raises(KosmosConflictError):
        kosmos.set(uuid, {"no": False})
    with pytest.raises(KosmosConflictError):
        kosmos.set(uuid, {"on": 42})


def test_set_attribute():
    uuid = "virt_lamp_1"
    key = "on"
    kosmos = getKosmosAsUser()
    kosmos.set_attribute(uuid, key, False)
    assert kosmos.get_device(uuid).state[key] is False
    kosmos.set_attribute(uuid, key, True)
    assert kosmos.get_device(uuid).state[key] is True
    with pytest.raises(KosmosConflictError):
        kosmos.set_attribute(uuid, "no", False)
    with pytest.raises(KosmosConflictError):
        kosmos.set_attribute(uuid, "on", 42)


def test_device():
    kosmos = getKosmosAsUser()
    uuid = f"test_lamp_{getRandomString(16)}"
    try:
        kosmos.get_device(uuid)
        kosmos.delete_device(uuid)

    except KosmosNotFoundError:
        pass
    with pytest.raises(KosmosNotFoundError):
        kosmos.get_device(uuid)
    with pytest.raises(KosmosConflictError):
        kosmos.add_device(uuid=uuid, state={"on": False, "hue": 120, "saturation": 60, "dimmingLevel": 128},
                          schema="https://kosmos-lab.de/schema/HSVLamp.json"
                          )
    kosmos.add_device(uuid=uuid, state={"on": False, "hue": 120, "saturation": 60, "dimmingLevel": 50},
                      schema="https://kosmos-lab.de/schema/HSVLamp.json"
                      )
    d = kosmos.get_device(uuid)
    assert d.uuid == uuid
    assert d.state["dimmingLevel"] == 50
    assert d.state["saturation"] == 60
    assert d.state["hue"] == 120
    assert d.state["on"] is False
    kosmos.set_attribute(d, "on", True)
    d = kosmos.get_device(uuid)
    assert d.state["on"] is True
    kosmos.set_attribute(d, "dimmingLevel", 100)
    d = kosmos.get_device(uuid)
    assert d.state["dimmingLevel"] == 100
    # with pytest.raises(KosmosConflictError):
    kosmos.set_attribute(d, "dimmingLevel", 101)
    d = kosmos.get_device(uuid)
    assert d.state["dimmingLevel"] == 100
    kosmos.delete_device(uuid)
    with pytest.raises(KosmosNotFoundError):
        kosmos.get_device(uuid)


def test_list_schemas():
    kosmos = getKosmosAsUser()
    list = kosmos.list_schemas()
    if len(list) < 5:
        assert False


def test_add_schema():
    schemaid = f"https://kosmos-lab.de/schema/{getRandomString(16)}.json"
    kosmos = getKosmosAsUser()
    try:
        kosmos.get_schema(schemaid)
        kosmos.delete_schema(schemaid)
        with pytest.raises(KosmosNotFoundError):
            kosmos.get_schema(schemaid)
    except KosmosNotFoundError:
        # expected
        pass

    kosmos.add_schema({
        "failures": [

        ],
        "$schema": "http://json-schema.org/draft-07/schema#",
        "examples": [

        ],
        "additionalProperties": True,
        "title": "NoSchema",
        "type": "object",
        "properties": {
        },
        "$id": schemaid
    })

    kosmos.get_schema(schemaid)
    with pytest.raises(KosmosConflictError):
        kosmos.add_schema({
            "failures": [

            ],
            "$schema": "http://json-schema.org/draft-07/schema#",
            "examples": [

            ],
            "additionalProperties": True,
            "title": "NoSchema",
            "type": "object",
            "properties": {
            },
            "$id": schemaid
        })
    kosmos.delete_schema(schemaid)
    with pytest.raises(KosmosNotFoundError):
        print(kosmos.get_schema(schemaid))


def test_scope():
    kosmos = getKosmosAsUser()
    sname = f"pytest_scope_{getRandomString(16)}"
    scope = KosmosScope(name=sname, id=0, admins=[], users=[], adminGroups=[], userGroups=[])

    scope.name = sname
    s = kosmos.add_scope(scope)
    assert s.name == sname
    assert s.id != 0
    s = kosmos.get_scope(sname)
    assert s.name == sname
    found = False
    for admin in s.admins:
        if admin.name == "user":
            found = True
            break
    assert found



    kosmos.delete_scope(scope)
    with pytest.raises(KosmosNotFoundError):
        print(kosmos.get_scope(sname))

    pass


def test_location():
    kosmos = getKosmosAsUser()
    uuid = f"test_lamp_{getRandomString(16)}"
    try:
        kosmos.get_device(uuid)
        kosmos.delete_device(uuid)

    except KosmosNotFoundError:
        pass
    with pytest.raises(KosmosNotFoundError):
        kosmos.get_device(uuid)

    with pytest.raises(KosmosNotFoundError):
        kosmos.get_location(uuid)
    kosmos.add_device(uuid=uuid, state={"on": False, "hue": 120, "saturation": 60, "dimmingLevel": 50},
                      schema="https://kosmos-lab.de/schema/HSVLamp.json"
                      )
    assert kosmos.get_location(uuid) == KosmosLocation()

    l1 = KosmosLocation(x=10, y=11, z=22)
    kosmos.set_location(uuid, l1)
    assert kosmos.get_location(uuid) == l1
    l2 = KosmosLocation(h=10, w=19)
    kosmos.set_location(uuid, l2)
    l1.h = 10
    l1.w = 19

    assert kosmos.get_location(uuid) == l1
