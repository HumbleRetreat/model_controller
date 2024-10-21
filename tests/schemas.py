from pydantic import BaseModel


class BaseModelCreateSchema(BaseModel):
    name: str


class BaseModelUpdateSchema(BaseModel):
    name: str


class SubModelACreateSchema(BaseModel):
    type: str = "SubModelA"
    name: str
    extra_field_a: str


class SubModelBCreateSchema(BaseModel):
    type: str = "SubModelB"
    name: str
    extra_field_b: str