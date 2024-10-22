from pydantic import BaseModel, Field


class HeroOut(BaseModel):
    id: int
    name: str
    secret_name: str
    age: int
