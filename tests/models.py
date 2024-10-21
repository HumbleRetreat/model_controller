from typing import Optional

from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base, Mapped

Base = declarative_base()


class ModelToTest(Base):
    __tablename__ = "test_model"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str]


class PolymorphicModel(Base):
    __tablename__ = "polymorphic_model"
    __mapper_args__ = {
        "with_polymorphic": "*",
        "polymorphic_on": "type",
    }

    type: Mapped[str]
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str]


class SubModelA(PolymorphicModel):
    __mapper_args__ = {
        "polymorphic_identity": "SubModelA",
    }

    extra_field_a: Mapped[Optional[str]]


class SubModelB(PolymorphicModel):
    __mapper_args__ = {
        "polymorphic_identity": "SubModelB",
    }

    extra_field_b: Mapped[Optional[str]]