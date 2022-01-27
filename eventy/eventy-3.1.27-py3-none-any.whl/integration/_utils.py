# Copyright (c) Qotto, 2021

def _merge_docs(eventy_object, vendor_object) -> None:
    eventy_doc: str = getattr(eventy_object, '__doc__', '')
    vendor_doc: str = getattr(vendor_object, '__doc__', '')
    if vendor_doc:
        vendor_doc = f'\n{vendor_doc}'
    merged_doc = eventy_doc + vendor_doc
    setattr(eventy_object, '__doc__', merged_doc)
