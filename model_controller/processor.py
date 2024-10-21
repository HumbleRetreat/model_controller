from model_controller.enums import OperationType
from model_controller.types import CreateSchemaType, UpdateSchemaType, ORMModel


class ProcessorBase:
    def __init__(self):
        pass

    def process(self, operation: OperationType, model: ORMModel, data: CreateSchemaType | UpdateSchemaType):
        raise NotImplementedError
