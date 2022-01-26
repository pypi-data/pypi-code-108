from typing import Optional

from pydantic import UUID4, BaseModel


class TaktileUser(BaseModel):
    id: UUID4
    email: Optional[str] = None
    is_active: bool
    is_superuser: bool
    username: str
    full_name: Optional[str] = None
    source_id: Optional[UUID4] = None
