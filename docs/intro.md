# Introduction

## `spic`

`spic` is an ASGI based api router with minimal dependencies and strong typing.

## features

### familiar methods

```py
# ./main.py

from spic.app import Slip

app = Slip(title="my-api", version="0.1")

@app.get("/health")
async def status_handler():
    return {"status": "healthy ✨"}

app.collapse() # collapse routes

# hypercorn main:app --reload
```

### dependency injection

```py
# ./main.py

from spic.params import Header, Query

...

@app.get("/merged")
async def merged_params(x_usr_token: Header[str], query: Query[str]):
    return {
        "X-Usr-Token": x_usr_token,
        "query", query
    }


app.collapse()
```

### `dataclass` support

```py
# ./main.py
from dataclasses import dataclass
from spic.params import Header, Query

...

@dataclass
class QueryArgs:
    query: Query[str]
    x_usr_token: Header[str]

@app.get("/class_base")
async def model_params(model: QueryArgs):
    return {
        "X-Usr-Token": model.x_usr_token,
        "query", model.query
    }

```

### generic dataclass serialization ([pyserde](https://github.com/yukinarit/pyserde))

```py
# ./models.py
from serde import serde
from dataclasses import dataclass

@serde
@dataclass
class QueryArgs:
    query: Query[str]
    x_usr_token: Header[str]

# OR

# ./models.py
from spic.utils import schema

@schema
class QueryArgs:
    query: Query[str]
    x_usr_token: Header[str]

...
```

```py
# ./main.py
...
@app.get("/serializable")
async def get_model(model: QueryArgs):
    return model # json
```

### [beartype](https://github.com/beartype/beartype) validation

```py
# ./client.py
from httpx import get
...

get(
    "http://localhost:8000/class_base?query=query-str-value" # missing header
).json()
# powered by beartype

# >> {
# >>  "errors": [
# >>    {
# >>      "key": "X_Usr_Token",
# >>      "expected": "string",
# >>      "given": "None",
# >>      "sources": ["header"]
# >>    }
# >>  ]
# >> }
```
