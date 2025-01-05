from typing import Annotated, Optional, Type

import sqlmodel
from fastapi import Depends, FastAPI
from fastapi_pagination import Page, add_pagination
from model import Hero
from pydantic import Field
from pydantic.json_schema import SkipJsonSchema
from schema import HeroOut
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from model_controller.controller import ModelController
from model_controller.filters import FiltersBase, create_filter_model
from model_controller.processors.logging_processor import LoggingProcessor

app = FastAPI(title="Model Controller Example")
add_pagination(app)

users_controller = ModelController(Hero)
users_controller.register_processor(LoggingProcessor())
paginated_users_controller = ModelController(Hero, paginate=True)
engine = create_engine(
    "sqlite:///test.sqlite", connect_args={"check_same_thread": False}
)
sqlmodel.SQLModel.metadata.create_all(engine)
session = sqlmodel.Session(engine)

hero1 = Hero(name="Deadpond", secret_name="Dive Wilson", age=121)
hero2 = Hero(name="Whateverest", secret_name="Morty Smith", age=1)
session.add_all([hero1, hero2])

HeroFilterParams = create_filter_model(Hero)


class HeroFilterParams2(FiltersBase):
    """
    Parameters to filter Hero model.
    """

    name: str | SkipJsonSchema[None] = Field(None, description="Filter by name")
    age: Optional[int] = Field(None, description="Filter by exact age")
    age_lt: Optional[int] = Field(
        None, description="Filter by age less than this value"
    )
    age_gt: Optional[int] = Field(
        None, description="Filter by age greater than this value"
    )


# req: GET /users
@app.get("/users", response_model=list[HeroOut])
async def get_users(
    filter_params: Annotated[HeroFilterParams, Depends()],
):
    with users_controller.set_context({"user_id": 12}):
        return users_controller.get_many(session, filter_params)


@app.get("/users/{id}", response_model=HeroOut)
async def get_user(id: int):
    return users_controller.get_one(session, Hero.id == id)


@app.get("/users-paginated", response_model=Page[HeroOut])
async def get_users_paginated():
    return paginated_users_controller.get_many(session)


def get_session():
    return session


def create_controller(filter_class: Type[FiltersBase]):
    """
    Dynamically create a controller class with a __call__ method
    that has type annotations based on the provided filter_class.
    """

    class DynamicGetManyController:
        def __call__(
            self,
            db: Annotated[Session, Depends(get_session)],
            filter_params: Annotated[filter_class, Depends()],
            order: Optional[str] = None,
        ):
            return True

    return DynamicGetManyController()


@app.get("/query-checker/")
async def read_query_check(
    data: Annotated[bool, Depends(create_controller(HeroFilterParams2))],
):
    return data
