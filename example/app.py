from typing import Annotated, Optional

import sqlmodel
from fastapi import FastAPI, Depends
from fastapi_pagination import Page, add_pagination
from pydantic import Field
from pydantic.json_schema import SkipJsonSchema
from sqlalchemy import create_engine

from model import Hero
from model_controller.controller import ModelController
from model_controller.filters import create_filter_model, FiltersBase
from model_controller.processors.logging_processor import LoggingProcessor
from schema import HeroOut

app = FastAPI(title="Model Controller Example")
add_pagination(app)

users_controller = ModelController(Hero)
users_controller.register_processor(LoggingProcessor())
paginated_users_controller = ModelController(Hero, paginate=True)
engine = create_engine("sqlite:///:memory:")
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
    age_lt: Optional[int] = Field(None, description="Filter by age less than this value")
    age_gt: Optional[int] = Field(None, description="Filter by age greater than this value")


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
