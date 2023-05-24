# TLDR

## Create an app

```py
# ./main.py

from spic import Spic
from spic.enums import LogLevel

from mypkg.__about__ import __version__

app = Spic(
    title="my-api",
    version=__version__,
    log_level=LogLevel.follow # default
)

...

```

## Add routes

```py
# ./main.py

# added imports
from spic.params import Header, Query
...


@app.get("/search")
async def search(query: Query[str]) -> dict:
    return {"search params": query}

```

## Use `dataclass`, or core types

```py
# ./models.py
from serde import serde
from dataclasses import dataclass
from spic.params import Header, Query

@serde
@dataclass
class MyModel:
    query_1: Query[str] # can be ?query_1=value or ?query-1=value
    x_token_sess: Header[str] # resolves to X-Token-Sess
```

### this is equivalent to

```py
# ./models.py
from spic.utils import schema

@schema
class MyModel:
    query_1: Query[str]
    x_token_sess: Header[str]

```

## Define routers

```py
# ./routers/route_a.py
from spic.routing import Router
from ..models import MyModel

router = Router(prefix="/sub-route")

@router.get("/compound-params")
async def with_compound(params: MyModel) -> MyModel:
    return params # json

```

### models are equal to & valid as function calls

```py
# ./routers/route_a.py
from spic.params import Header, Query

@router.get("/compound-params")
async def with_compound(
    query_1: Query[str], x_token_sess: Header[str]
):
    return {
        'query_1' : query_1,
        'x_token_sess' : x_token_sess,
    } # json
```

## Add routers

```py
# ./main.py
from .routing.route_a import router as route_a

...
app.include_router(route_a.router)
...
```

## Build Routes to Paths

```py
# ./main.py

app.collapse()
```

## Serve

```bash
hypercorn app:main --reload
```
