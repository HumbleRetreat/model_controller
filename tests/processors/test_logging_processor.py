from unittest.mock import patch

import pytest

from model_controller.enums import OperationType
from model_controller.processors.logging_processor import LoggingProcessor


# Define a mock ORM model
class MockModel:
    __name__ = "MockModel"


@pytest.fixture
def processor():
    """Fixture to create an instance of the LoggingProcessor."""
    return LoggingProcessor()


def test_logging_processor_create_operation(processor):
    """Test that the LoggingProcessor logs the correct message for a CREATE operation."""
    with patch.object(processor.logger, 'info') as mock_logger:
        # Mock data and context
        mock_data = {"field": "value"}
        mock_context = {"user_id": 123}

        # Call the process method with OperationType.CREATE
        processor.process(OperationType.CREATE, MockModel, mock_data, mock_context)

        # Check if the print statement was called with the correct output
        mock_logger.assert_called_once_with(
            "Operation: CREATE, Model: MockModel, Data: {'field': 'value'}, Context: {'user_id': 123}"
        )


def test_logging_processor_update_operation(processor):
    """Test that the LoggingProcessor logs the correct message for an UPDATE operation."""
    with patch.object(processor.logger, 'info') as mock_logger:
        # Mock data and context
        mock_data = {"field": "updated_value"}
        mock_context = {"user_id": 456}

        # Call the process method with OperationType.UPDATE
        processor.process(OperationType.UPDATE, MockModel, mock_data, mock_context)

        # Check if the print statement was called with the correct output
        mock_logger.assert_called_once_with(
            "Operation: UPDATE, Model: MockModel, Data: {'field': 'updated_value'}, Context: {'user_id': 456}"
        )


def test_logging_processor_delete_operation(processor):
    """Test that the LoggingProcessor logs the correct message for a DELETE operation."""
    with patch.object(processor.logger, 'info') as mock_logger:
        # Mock data and context
        mock_data = {"field": "deleted_value"}
        mock_context = {"user_id": 789}

        # Call the process method with OperationType.DELETE
        processor.process(OperationType.DELETE, MockModel, mock_data, mock_context)

        # Check if the print statement was called with the correct output
        mock_logger.assert_called_once_with(
            "Operation: DELETE, Model: MockModel, Data: {'field': 'deleted_value'}, Context: {'user_id': 789}"
        )


def test_logging_processor_logs_message_with_logger(processor):
    """Test that the LoggingProcessor logs the message using the logger instead of print."""
    with patch.object(processor.logger, 'info') as mock_logger:
        # Mock data and context
        mock_data = {"field": "test_value"}
        mock_context = {"user_id": 111}

        # Call the process method
        processor.process(OperationType.CREATE, MockModel, mock_data, mock_context)

        # Check that logger.info was called with the correct message (adjust this to logger's method and usage)
        mock_logger.assert_called_once_with(
            "Operation: CREATE, Model: MockModel, Data: {'field': 'test_value'}, Context: {'user_id': 111}"
        )
