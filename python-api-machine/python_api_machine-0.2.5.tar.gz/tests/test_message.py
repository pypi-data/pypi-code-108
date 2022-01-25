from api_machine.pubsub import RefStr


def test_valid_ref():
    ref = RefStr("service:entity:command:something")
    assert ref.service == "service"
    assert ref.entity == "entity"
    assert ref.action_type == "command"
    assert ref.action == "something"
