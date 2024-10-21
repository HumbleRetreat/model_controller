from typing import TypeVar

from pydantic import BaseModel

ORMModel = TypeVar("ORMModel")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
