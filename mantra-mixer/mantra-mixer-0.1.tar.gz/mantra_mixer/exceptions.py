class NoUnoccupiedTrack(Exception):
    """Raised when there are no unoccupied tracks to be found."""


class UnsupportedFormat(Exception):
    """Raised when the file format provided is unfortunately unsupported."""
