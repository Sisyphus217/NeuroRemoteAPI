from pydantic import BaseModel
from uuid import uuid4

class Task(BaseModel):
    uid: str = str(uuid4())
    path: str