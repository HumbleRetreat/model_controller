import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tests.models import Base


@pytest.fixture(scope="function")
def db_engine():
    return create_engine("sqlite+pysqlite:///:memory:", echo=False)


@pytest.fixture(scope="function")
def tables(db_engine):
    Base.metadata.create_all(db_engine)
    yield
    Base.metadata.drop_all(db_engine)

@pytest.fixture(scope="function")
def db(db_engine, tables):
    """Returns an SQLAlchemy session, and after the test tears down everything properly."""
    connection = db_engine.connect()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    connection.close()
