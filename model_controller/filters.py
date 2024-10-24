from typing import Type, Dict, Tuple, Optional

from pydantic import BaseModel, Field, create_model
from pydantic.json_schema import SkipJsonSchema
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeMeta

string_classes = [String, ]
try:
    from sqlmodel import AutoString

    string_classes.append(AutoString)
except ImportError:
    pass  # sqlmodel is not installed


class FiltersBase(BaseModel):
    pass


def create_filter_model(model: Type[DeclarativeMeta]) -> Type[FiltersBase]:
    """
    Dynamically creates a Pydantic filter model based on the fields of an SQLAlchemy model.

    Parameters:
        model (Type[DeclarativeMeta]): The SQLAlchemy model to introspect.

    Returns:
        Type[BaseModel]: A dynamically generated Pydantic model for filtering.
    """
    model_fields: Dict[str, Tuple[Optional[Type], Optional[Type]]] = {}

    # Iterate over the model's columns to extract fields
    for column in model.__table__.columns:
        column_type = type(column.type)

        # Dynamically add fields to the model filter
        if isinstance(column.type, Integer):
            # For integer fields (e.g., age), support filtering with lt, gt, eq
            model_fields[column.name] = (
                int | SkipJsonSchema[None], Field(None, description=f"Filter by {column.name}"))
            model_fields[f"{column.name}_lt"] = (
                int | SkipJsonSchema[None], Field(None, description=f"Less than {column.name}"))
            model_fields[f"{column.name}_gt"] = (
                int | SkipJsonSchema[None], Field(None, description=f"Greater than {column.name}"))

        elif isinstance(column.type, tuple(string_classes)):
            # For string fields (e.g., name), support exact match or partial match
            model_fields[column.name] = (
            str | SkipJsonSchema[None], Field(None, description=f"Filter by {column.name}"))
            model_fields[f"{column.name}_like"] = (
                str | SkipJsonSchema[None], Field(None, description=f"Partial match for {column.name}"))

    # Create a Pydantic model dynamically
    return create_model(f'{model.__name__}Filter', **model_fields, __base__=FiltersBase)
