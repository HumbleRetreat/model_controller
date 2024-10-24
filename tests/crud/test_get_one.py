from model_controller.controller import ModelController
from tests.models import ModelToTest
from tests.schemas import BaseModelCreateSchema


def test_get_one_filter_args(db):
    controller = ModelController(ModelToTest)
    data = BaseModelCreateSchema(name="test")

    obj = controller.create(db, data)

    obj_from_db = controller.get_one(db, ModelToTest.id == obj.id)

    assert obj_from_db.id == obj.id
    assert obj_from_db.name == obj.name


def test_get_one_filter_kwargs(db):
    controller = ModelController(ModelToTest)
    data = BaseModelCreateSchema(name="test")

    obj = controller.create(db, data)

    obj_from_db = controller.get_one(db, id=obj.id)

    assert obj_from_db.id == obj.id
    assert obj_from_db.name == obj.name