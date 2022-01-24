from django.dispatch import Signal


__all__ = 'upload_complete',


upload_complete: Signal = Signal()
"""
Arguments:
    - instance (Upload) - Upload instance
    - file - Uploaded file
"""
