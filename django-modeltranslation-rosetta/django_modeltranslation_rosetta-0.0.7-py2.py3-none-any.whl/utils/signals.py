from django.db.models.signals import post_delete, post_save


class DisconnectSignal(object):
    def __init__(self, handlers=None, signals=None):
        if not signals:
            signals = [post_save, post_delete]
        self._signals = signals
        self._handlers = handlers
        self._signals_receivers_map = {}

    def disconnect_signals(self):
        for signal in self._signals:
            new_receivers = []
            backup_receivers = list(signal.receivers)
            for i, receiver in enumerate(list(signal.receivers)):
                if not self._handlers:
                    continue
                _ref_f = receiver[-1]
                if type(_ref_f).__name__ == "weakref":
                    _ref_f = _ref_f()
                if _ref_f not in self._handlers:
                    new_receivers.append(receiver)
            self._signals_receivers_map[signal] = backup_receivers
            signal.receivers = new_receivers

    def restore_signals(self):
        for signal, receivers in self._signals_receivers_map.items():
            signal.receivers = receivers

    def __enter__(self):
        self.disconnect_signals()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.restore_signals()
