from model_controller.controller import ModelController
from tests.models import ModelToTest
from tests.schemas import BaseModelCreateSchema, BaseModelUpdateSchema


def test_update(db):
    controller = ModelController(ModelToTest)
    data = BaseModelCreateSchema(name="test")

    obj = controller.create(db, data)

    update_data = BaseModelUpdateSchema(name="test_updated")

    new_obj = controller.update_object(db, obj, update_data)

    assert new_obj.id == obj.id
    assert new_obj.name == "test_updated"
