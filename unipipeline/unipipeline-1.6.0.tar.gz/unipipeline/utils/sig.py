import signal
from types import FrameType
from typing import Callable, Tuple, Any, Optional, Union


class soft_interruption:  # noqa
    def __init__(self, on_interrupt_once: Callable[[], None], on_force_interruption: Optional[Callable[[], None]] = None, on_error: Optional[Callable[[Exception], None]] = None) -> None:
        self._on_interrupt_once = on_interrupt_once
        self._on_force_interruption = on_force_interruption
        self._sig_int_received = False
        self._sig_term_received = False
        self._first_sig_data: Optional[Tuple[Any, Any]] = None
        self._old_sig_int: Union[Callable[[signal.Signals, FrameType], Any], int, signal.Handlers, None] = None
        self._old_sig_term: Union[Callable[[signal.Signals, FrameType], Any], int, signal.Handlers, None] = None
        self._on_error = on_error

    def _the_end(self, force: bool = False) -> None:
        if force:
            self._on_force_interruption and self._on_force_interruption()
        if self._sig_int_received and callable(self._old_sig_int):
            assert self._first_sig_data is not None
            self._old_sig_int(*self._first_sig_data)
        elif self._sig_term_received and callable(self._old_sig_term):
            assert self._first_sig_data is not None
            self._old_sig_term(*self._first_sig_data)
        if force or self._sig_term_received or self._sig_int_received:
            exit(1)

    def _interruption_handler(self, sig: signal.Signals, frame: FrameType) -> None:
        try:
            if self._sig_term_received or self._sig_int_received:
                self._the_end(True)
                return
            self._sig_term_received = True
            self._first_sig_data = (sig, frame)
            self._on_interrupt_once()
        except Exception as e:  # noqa
            if self._on_error:
                self._on_error(e)
            else:
                print(e)  # noqa

    def _term_handler(self, sig: signal.Signals, frame: FrameType) -> None:
        try:
            if self._sig_term_received or self._sig_int_received:
                self._the_end(True)
                return
            self._sig_term_received = True
            self._first_sig_data = (sig, frame)
            self._on_interrupt_once()
        except Exception as e:  # noqa
            if self._on_error:
                self._on_error(e)
            else:
                print(e)  # noqa

    def __enter__(self) -> None:
        self._old_sig_int = signal.signal(signal.SIGINT, self._interruption_handler)
        self._old_sig_term = signal.signal(signal.SIGTERM, self._term_handler)
        return None

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._the_end(False)
