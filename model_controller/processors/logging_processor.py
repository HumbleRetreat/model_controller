import logging

from model_controller.enums import OperationType
from model_controller.processors.base import ProcessorBase
from model_controller.types import ORMModel, MutationType


class LoggingProcessor(ProcessorBase):
    def process(self, operation: OperationType, model: ORMModel, data: MutationType,
                context: dict):
        self.logger.info(f"Operation: {operation.name}, Model: {model.__name__}, Data: {data}, Context: {context}")

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
