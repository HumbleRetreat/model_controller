from model_controller.controller import ModelController
from tests.models import ModelToTest
from tests.schemas import BaseModelCreateSchema


def test_get_many(db):
    obj_count = 10
    controller = ModelController(ModelToTest)

    for i in range(obj_count):
        controller.create(db, BaseModelCreateSchema(name=f"test_{i}"))

    obj_from_db = controller.get_many(db)

    assert len(obj_from_db) == obj_count


def test_get_many_filter_args(db):
    obj_count = 10
    controller = ModelController(ModelToTest)

    for i in range(obj_count):
        controller.create(db, BaseModelCreateSchema(name=f"test_{i}"))

    obj_from_db = controller.get_many(db, None, ModelToTest.id <= 5)

    assert len(obj_from_db) == 5
