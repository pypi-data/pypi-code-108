from typing import Dict, Any


_NamedInstance: Dict[str, Any] = {}


def get_instances() -> Dict[str, Any]:
    print(f"[DEBUG] _g.get_instances: {_NamedInstance}")
    return _NamedInstance


def get_instances_by_key(name: str) -> Dict[str, Any]:
    print(f"[DEBUG] _g.get_instances_by_key name: {name}")
    print(f"[DEBUG] _g.get_instances_by_key: {_NamedInstance}")
    return _NamedInstance[name]


def set_instances(instances: Dict[str, Any]) -> None:
    global _NamedInstance
    _NamedInstance.update(instances)
    print(f"[DEBUG] _g.set_instances: {_NamedInstance}")

