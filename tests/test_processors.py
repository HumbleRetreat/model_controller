from model_controller.controller import ModelController
from model_controller.enums import OperationType
from tests.models import ModelToTest
from tests.processors import ProcessorForTesting
from tests.schemas import BaseModelCreateSchema


def test_processor_create(db, mocker):
    controller = ModelController(ModelToTest)
    processor = ProcessorForTesting()
    spy = mocker.spy(processor, "process")
    controller.register_processor(processor)

    data = BaseModelCreateSchema(name="test")
    controller.create(db, data)

    spy.assert_called_once_with(OperationType.CREATE, ModelToTest, data, {})
