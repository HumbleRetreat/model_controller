import pytest
from pydantic import BaseModel
from sqlalchemy import select

from model_controller.controller import ModelController
from model_controller.exception import ControllerException
from tests.models import ModelToTest, PolymorphicModel, SubModelA
from tests.schemas import SubModelACreateSchema


class BaseModelCreateSchema(BaseModel):
    name: str


def test_create_model(db):
    controller = ModelController(ModelToTest)
    data = BaseModelCreateSchema(name="test")

    obj = controller.create(db, data)

    assert obj.id is not None
    assert obj.name == "test"

    query = select(ModelToTest).filter_by(id=obj.id)
    obj_from_db = db.execute(query).scalar()

    assert obj_from_db.id == obj.id
    assert obj_from_db.name == obj.name


def test_create_polymorph_model(db):
    controller = ModelController(PolymorphicModel)
    data = SubModelACreateSchema(type="SubModelA", name="test", extra_field_a="test")

    obj = controller.create(db, data)

    assert isinstance(obj, SubModelA)
    assert obj.id is not None
    assert obj.name == "test"
    assert obj.extra_field_a == "test"

    query = select(SubModelA).filter_by(id=obj.id)
    obj_from_db = db.execute(query).scalar()

    assert obj_from_db.id == obj.id
    assert obj_from_db.name == obj.name


def test_fail_polymorph_cannot_resolve_actual_model(db):
    controller = ModelController(PolymorphicModel)
    data = BaseModelCreateSchema(name="test")

    with pytest.raises(ControllerException) as exc:
        controller.create(db, data)

    assert f"Cannot resolve the actual model for {PolymorphicModel.__name__}" in str(exc.value)
