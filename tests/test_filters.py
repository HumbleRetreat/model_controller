import pytest
from pydantic import ValidationError
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from model_controller.filters import create_filter_model

Base = declarative_base()


# Mock SQLAlchemy models
class Hero(Base):
    __tablename__ = 'heroes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer)


@pytest.fixture
def hero_model():
    return Hero


def test_create_filter_model_for_integers(hero_model):
    """Test that the filter model includes integer filtering fields."""
    hero_filter = create_filter_model(hero_model)

    # Assert that the filter model contains the expected fields
    assert 'id' in hero_filter.model_fields
    assert 'id_lt' in hero_filter.model_fields
    assert 'id_gt' in hero_filter.model_fields

    # Test validation of correct input
    filters = hero_filter(id=1, id_lt=10, id_gt=0)
    assert filters.id == 1
    assert filters.id_lt == 10
    assert filters.id_gt == 0

    # Test invalid input should raise validation error
    with pytest.raises(ValidationError):
        hero_filter(id="not_an_integer")


def test_create_filter_model_for_strings(hero_model):
    """Test that the filter model includes string filtering fields."""
    hero_filter = create_filter_model(hero_model)

    # Assert that the filter model contains the expected fields for string
    assert 'name' in hero_filter.model_fields
    assert 'name_like' in hero_filter.model_fields

    # Test validation of correct input
    filters = hero_filter(name="John", name_like="Jo")
    assert filters.name == "John"
    assert filters.name_like == "Jo"

    # Test invalid input should raise validation error
    with pytest.raises(ValidationError):
        hero_filter(name=123)  # Invalid type for name


def test_missing_fields_in_model(hero_model):
    """Test that fields not in the model are not included in the generated filter."""
    hero_filter = create_filter_model(hero_model)

    # The hero model doesn't have a "non_existent_field", so it should not appear in the filter model
    assert 'non_existent_field' not in hero_filter.model_fields

    # Also test for correct filtering of available fields
    filters = hero_filter(id=1, name="John")
    assert filters.id == 1
    assert filters.name == "John"
