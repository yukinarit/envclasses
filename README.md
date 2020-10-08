```
                    | |
  ___ _ ____   _____| | __ _ ___ ___  ___  ___
 / _ \ '_ \ \ / / __| |/ _` / __/ __|/ _ \/ __|
|  __/ | | \ V / (__| | (_| \__ \__ \  __/\__ \
 \___|_| |_|\_/ \___|_|\__,_|___/___/\___||___/

```

[![image](https://img.shields.io/pypi/v/envclasses.svg)](https://pypi.org/project/envclasses/)
[![image](https://img.shields.io/pypi/pyversions/envclasses.svg)](https://pypi.org/project/envclasses/)
[![CircleCI](https://circleci.com/gh/yukinarit/envclasses.svg?style=svg)](https://circleci.com/gh/yukinarit/envclasses)

envclass is a small library which maps environment variables dataclass's fields
This is very useful in a case like you want to override the configurations read
from file.


## Installation

```bash
pip install envclasses
```


## Usage

```python
# foo.py
from typing import List, Dict
from dataclasses import dataclass, field
from envclasses import envclass, load_env

@envclass
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool
    lst: List[int] = field(default_factory=list)
    dct: Dict[str, float] = field(default_factory=dict)

foo = Foo(i=10, s='foo', f=0.1, b=False)

# Map environment variables to fields.
load_env(foo, prefix='FOO')

print(foo)
```

run

```bash
$ python foo.py
Foo(i=10, s='foo', f=0.1, b=False, lst=[], dct={})
```

Run with environment variables

```bash
$ FOO_I=20 FOO_S=foofoo FOO_F=0.2FOO_B=true FOO_DCT="{key: 100.0}" FOO_LST="[1, 2, 3]" python foo.py
Foo(i=20, s='foofoo', f=0.2, b=True, lst=[1, 2, 3], dct={'key': 100.0})
```

Notes:
- If `prefix` is not defined or set to `None`, the default prefix (`ENV_`) will be expected.
- If `prefix` is set to the empty string `''`, no prefix will be expected in the environment variables.
