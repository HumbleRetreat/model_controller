# Pagination

Model Controller supports pagination using `fastapi_pagination`. Pagination is disabled by default, but you can enable
it by setting the `paginate` parameter to `True` when creating a new `ModelController` instance.

```python
from fastapi import FastAPI

from model_controller.controller import ModelController

app = FastAPI()

users_controller = ModelController(User, paginate=True)


@app.get("/users")
def get_users():
    return users_controller.get_all()
```