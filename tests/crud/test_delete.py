from model_controller.controller import ModelController
from tests.models import ModelToTest
from tests.schemas import BaseModelCreateSchema


def test_delete(db):
    controller = ModelController(ModelToTest)
    data = BaseModelCreateSchema(name="test")

    obj = controller.create(db, data)

    controller.delete(db, obj)

    obj_from_db = controller.get_one(db, ModelToTest.id == obj.id)

    assert obj_from_db is None