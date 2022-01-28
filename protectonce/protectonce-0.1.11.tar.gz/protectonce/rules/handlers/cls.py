import threading
_thread_local_store = threading.local()


def store_property(data):
    # FIXME: Implement a real cls instead of thread local
    cls_context = getattr(_thread_local_store, 'po_cls_context', {})
    cls_context[data['config']['property']] = data['result']
    _thread_local_store.po_cls_context = cls_context


def get_property(data):
    cls_context = getattr(_thread_local_store, 'po_cls_context', {})
    return cls_context.get(data['config']['property'], '')
