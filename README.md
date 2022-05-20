# `envclasses`

[![image](https://img.shields.io/pypi/v/envclasses.svg)](https://pypi.org/project/envclasses/)
[![image](https://img.shields.io/pypi/pyversions/envclasses.svg)](https://pypi.org/project/envclasses/)
![Test](https://github.com/yukinarit/envclasses/workflows/Test/badge.svg)

*`envclasses` is a library to map fields on dataclass object to environment variables.*

## Installation

```bash
pip install envclasses
```

## Usage

Declare a class with `dataclass` and `envclass` decorators.

```python
from envclasses import envclass, load_env
from dataclasses import dataclass

@envclass
@dataclass
class Foo:
    v: int

foo = Foo(v=10)
load_env(foo, prefix='foo')
print(foo)
```

Run the script

```
$ python foo.py
Foo(v=10)
```

Run with environment variable

```
$ FOO_V=100 python foo.py
Foo(v=100)
```