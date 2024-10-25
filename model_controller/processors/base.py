from typing import Optional, Any

from model_controller.enums import OperationType
from model_controller.types import ORMModel, MutationType


class ProcessorBase:
    def __init__(self):
        pass

    def process(self, operation: OperationType, model: ORMModel, data: Optional[MutationType],
                context: dict[Any, Any]):
        raise NotImplementedError
