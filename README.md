# `slip`

[![PyPI - Version](https://img.shields.io/pypi/v/spic.svg)](https://pypi.org/project/spic)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/spic.svg)](https://pypi.org/project/spic)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Code Coverage](https://img.shields.io/codecov/c/github/joshua-auchincloss/slip?style=flat-square)](https://github.com/joshua-auchincloss/spic)

---
# `slip`


**Table of Contents**

- [Intro](#intro)
- [Features](#features)

  - [familiar methods](#familiar-methods)
  - [dependency injection](#dependency-injection)
  - [dataclasses first](#dataclass-support)
  - [dataclass serialization](#generic-dataclass-serialization-pyserde)
  - [beartype validation](#beartype-validation)
  - [performance](#performance)

- [Installation](#installation)
- [Rationale](#rationale)
- [License](#license)


## Intro

`slip` is an ASGI based api router with minimal dependencies and strong typing.

## Rationale

- popular libraries have dependencies which are moving commercial
- no popular libraries for core `python` dataclass structures

## Features

### familiar methods

```py
# ./main.py

from slip.app import Slip

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

from slip.params import Header, Query

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
from slip.params import Header, Query

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
from slip.utils import schema

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

### performance

We currently test 3 primary use cases:

- request param args -> function kwargs (no metaclass & valid)
  - 1.953ms overhead deserialization + reserialization (1000 ops)
- request param args -> metaclass kwargs (dataclass)
  - 2.718ms overhead deserialization + reserialization (1000 ops)
- invalid request param -> metaclass kwargs (raises errors & generates exception subclass)
  - 2.865ms overhead deserialization + reserialization (1000 ops)

## Installation

```console
pip install spic[core]
```

## License

`slip` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
