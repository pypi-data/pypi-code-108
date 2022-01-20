from pydantic import BaseModel, constr, conlist


class BatchDeleteFilter(BaseModel):
    record_key: conlist(constr(min_length=1, strict=True), min_items=1) = None
