from typing import Any, Callable, Iterable
from inspect import signature, Signature, Parameter

Callback = Callable[[str, Any], None]


def _check_callback(callback: Callback, fargs: Iterable[str]) -> bool:
    cb_parameters = list(signature(callback).parameters.keys())
    if set(fargs).difference(cb_parameters):
        raise RuntimeError(f'Callback {callback} miss match in parameters: expected {fargs} -'
                           f' difference {set(fargs).difference(cb_parameters)}')
    for i, (s, t) in enumerate(zip(cb_parameters, fargs)):
        if s != t:
            raise RuntimeError(f'Callback {callback} miss match in parameter at position {i}: expected {t} - got {s}')
    return True


class AttributeCallbackManager:
    """
    This object gives possibility to add on_change callbacks on all class attributes.
    Whenever the attributes is changed, the registered callbacks are called.

    The callbcak signature is as follows:

    callback(obj: Any, attr: str, value: Any)

    where:
     * obj: is the class instance which attribute was changed
     * attr: name of the attribute
     * value: the new value of the attribute
    """
    def __init__(self) -> None:
        self._callbacks = {}
        self._obj_callbacks = {}

    def on_change(self, *, obj: Any, attr: str, callback: Callback) -> None:
        """Add a callback on this object to trigger when ``attr`` changes."""
        if not hasattr(self, attr):
            raise ValueError(f"Error: on_change({attr}, {callback}), {self} has no attr: {attr}")

        _callbacks = self._callbacks.setdefault(attr, [])
        if callback in _callbacks:
            return

        _check_callback(callback, ('obj', 'attr', 'old_value', 'new_value'))
        _callbacks.append(callback)

        # update all obj registered callbacks
        _obj_callbacks = self._obj_callbacks.setdefault(obj, {})
        _obj_callbacks.update({attr: _callbacks})

    # def remove_on_change(self, obj, attr, *callbacks):
    #     """Remove a callback from this object"""
    #
    #     if len(callbacks) == 0:
    #         raise ValueError(
    #             "remove_on_change takes an attribute name and one or more callbacks, got only one parameter")
    #     _callbacks = self._callbacks.setdefault(attr, [])
    #     for callback in callbacks:
    #         _callbacks.remove(callback)
    #     _obj_callbacks = self._obj_callbacks.setdefault(obj, {})
    #     _obj_callbacks.update({attr: _callbacks})

    def remove_all_callbacks(self, obj: Any) -> None:
        """This function removes all callbacks for which are registred for obj"""
        if obj in self._obj_callbacks:
            cb_dict = self._obj_callbacks.pop(obj)
            for attr, callbacks in cb_dict.items():
                for cb in callbacks:
                    self._callbacks[attr].remove(cb)

    def __setattr__(self, key, new_value):
        """
        Set the attribute and change the callback
        """
        if hasattr(self, key):
            old_value = self.__getattribute__(key)
            if old_value == new_value:
                return
        else:
            old_value = None
        # set value
        super().__setattr__(key, new_value)
        # call callbacks
        if hasattr(self, '_callbacks') and key in self._callbacks:
            for callback in self._callbacks[key]:
                callback(self, key, old_value, new_value)
