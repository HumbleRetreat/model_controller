from model_controller.enums import OperationType
from model_controller.types import ORMModel, CreateSchemaType, UpdateSchemaType


class ProcessorBase:
    def __init__(self):
        pass

    def process(self, operation: OperationType, model: ORMModel, data: CreateSchemaType | UpdateSchemaType,
                context: dict):
        raise NotImplementedError
