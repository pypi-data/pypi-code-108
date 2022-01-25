from pydantic import BaseModel


class RBACPolicy(BaseModel):
    assignee_type: str
    scope: str
    role: str
    assignee: str
