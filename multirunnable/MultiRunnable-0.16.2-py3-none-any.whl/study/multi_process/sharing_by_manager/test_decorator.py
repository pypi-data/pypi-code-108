from typing import TypeVar, Generic
from g_manager import GManager, GlobalManager, get_current_manager, get_manager_attr, assign_to_manager


T = TypeVar("T")


def sharing_process_new(_class):
    assign_to_manager(_class)
    return _class


def sharing_process_x(_class):

    def _(*args, **kwargs):
        # # # # Ver 1.
        # _current_manager = get_current_manager()
        # if _current_manager is None:
        #     raise ValueError("The _SharingManager object not be initialed yet.")
        #
        # _cls_name = _class.__name__
        # print(f"[CHECK] dir: {dir(_current_manager)}")
        # print(f"[CHECK] vars: {vars(_current_manager)}")
        # if hasattr(_current_manager, _cls_name) is False:
        #     raise AttributeError("Target attribute does not exist.")
        #
        # _cls = getattr(_current_manager, _cls_name)

        # # # # Ver 2.
        _cls_name = _class.__name__
        _cls = get_manager_attr(_cls_name)

        print(f"[DEBUG] _cls: {_cls}")
        print(f"[DEBUG] args: {args}")
        print(f"[DEBUG] kwargs: {kwargs}")
        return _cls(*args, **kwargs)

    assign_to_manager(_class)
    return _
