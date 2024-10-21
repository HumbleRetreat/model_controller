from typing import Union, List, Tuple

from model_controller.enums import OperationType
from model_controller.processor import ProcessorBase
from model_controller.types import ORMModel, CreateSchemaType, UpdateSchemaType


class ProcessorForTesting(ProcessorBase):
    def __init__(self):
        super().__init__()
        self.updates: List[Tuple[OperationType, ORMModel, Union[CreateSchemaType, UpdateSchemaType]]] = []

    def process(self, operation: OperationType, model: ORMModel, data: CreateSchemaType | UpdateSchemaType):
        self.updates.append([operation, model, data])
