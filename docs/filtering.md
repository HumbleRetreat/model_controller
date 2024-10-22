# Filtering

Model Controller provides a flexible way to filter query results using Pydantic models.
You can define custom filter classes or automatically generate them based on the fields of an SQLAlchemy model.

## Automatic Filter Class Generation

In some cases, manually defining filter classes can become tedious, especially for models with many fields.
You can automate this process by dynamically generating filter classes based on the fields of an SQLAlchemy or SQLModel
model.

This method uses reflection to inspect the model's fields and generate filter options for each.

### SQLAlchemy Example

```python
from typing import Optional

from sqlalchemy import declarative_base, mapped_column, Integer

from model_controller.filters import create_filter_model

Base = declarative_base()


class Hero(Base):
    __tablename__ = "heroes"

    id: int = mapped_column(Integer, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None


HeroFilterParams = create_filter_model(Hero)
```

### SQLModel Example

```python
from typing import Optional

from sqlmodel import SQLModel, Field

from model_controller.filters import create_filter_model


class Hero(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None


HeroFilterParams = create_filter_model(Hero)
```

## Manual Filter Class

You can manually create a custom filter class by extending a base FiltersBase class using Pydantic. In this example, the
filter class is specific to the Hero model and
supports filtering by name and age. Additional comparison operators such as lt (less than) and gt (greater than) are
also supported.

```python
from typing import Optional

from pydantic import Field

from model_controller.filters import FiltersBase


class HeroFilterParams(FiltersBase):
    """
    Filters for querying Hero models.
    """
    name: Optional[str] = Field(None, description="Filter by name")
    age: Optional[int] = Field(None, description="Filter by exact age")
    age_lt: Optional[int] = Field(None, description="Filter by age less than this value")
    age_gt: Optional[int] = Field(None, description="Filter by age greater than this value")
```

## Using Filters in FastAPI Endpoints

Use the custom filter class in the FastAPI endpoint: The filter parameters will be automatically validated by FastAPI,
and you can apply these filters in your SQLAlchemy query.

```python
from fastapi import Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from database import session
from models import Hero
from controllers import ModelController
from schemas import HeroOut

users_controller = ModelController(Hero)


@app.get("/users", response_model=List[HeroOut])
async def get_users(
        filter_params: Annotated[HeroFilterParams, Depends()],
        db: Session = Depends(session)
):
    return users_controller.get_many(db, filter_params)
```

## Example API Requests

Regardless of the method used to create the filter class, the API requests are the same.

```bash
GET /users?name_like=Jo&age_lt=50
```

Response:

```json
[
  {
    "id": 2,
    "name": "Joan",
    "secret_name": "Wonder Woman",
    "age": 45
  }
]
```
