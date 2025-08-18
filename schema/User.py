from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    email: str
    name: Optional[str] = None
    
    def dict(self):
        return {"email": self.email, "name": self.name}
