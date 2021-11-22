"""
`envclasses` is a library to map fields on dataclass object to environment variables.

Declare a class with `dataclass` and `envclass` decorators. If you are new to dataclass,
I recommend to read [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html)
first.

>>> from dataclasses import dataclass
>>>
>>> @envclass
... @dataclass
... class Foo:
...     v: int

Create an instance of `Foo`, now `foo.v` is 10.

>>> foo = Foo(v=10)

Set environment variable `FOO_V` `100`.

>>> import os
>>> os.environ['FOO_V'] = '100'

Calling `load_env` will change the value from `10` to `100` on `foo.v`.

>>> load_env(foo, prefix='foo')
>>> foo.v
100

### Supported types

* Primitives (int, float, str, bool)
* Containers (List, Tuple, Dict)

>>> from typing import List, Dict
>>> from dataclasses import dataclass, field
>>>
>>> @envclass
... @dataclass
... class Foo:
...     lst: List[int] = field(default_factory=list)
...     dct: Dict[str, float] = field(default_factory=dict)
...
>>> foo = Foo()
>>> os.environ['FOO_LST'] = '[1, 2]'
>>> os.environ['FOO_DCT'] = '{key: 100.0}'
>>> load_env(foo, prefix='FOO')
>>> foo
Foo(lst=[1, 2], dct={'key': 100.0})

* Nested envclass

>>> @envclass
... @dataclass
... class Bar:
...     v: int
>>>
>>> @envclass
... @dataclass
... class Foo:
...     bar: Bar

>>> foo = Foo(Bar(v=10))
>>> os.environ['FOO_BAR_V'] = '100'
>>> load_env(foo, prefix='foo')
>>> foo.bar.v
100

### Debugging

If you want to see how `envclasses` looks up environment variables, you may want to see the logs
produced in the module. `envclasses` uses the logger of standard `logging` module. In order to
see DEBUG logs, you can get the logger and configure the log level.

```python
import logging

logging.getLogger("envclasses").setLevel(logging.DEBUG)
```
"""
import enum
import functools
import logging
import os
from dataclasses import Field, fields
from typing import Any, Dict, List, Type, TypeVar

import yaml
from typing_inspect import get_origin

__all__ = [
    'envclass',
    'is_envclass',
    'load_env',
    'EnvclassError',
    'LoadEnvError',
]

__version__ = '0.2.4'
""" Version of envclass. """

logger = logging.getLogger('envclasses')

ENVCLASS_DUNDER_FUNC_NAME = '__envclasses_load_env__'
""" Name of the generated dunder function to be called by `load_env`. """

ENVCLASS_PREFIX = 'env'
""" Default prefix used for environment variables. """

T = TypeVar('T')

JsonValue = TypeVar('JsonValue', str, int, float, bool, Dict, List)


class EnvclassError(TypeError):
    """
    Exception used in `envclass`. This exception is only raised when there is an
    error in the class declaration.
    """


class LoadEnvError(Exception):
    """
    Exception raised in `load_env`.
    """


class InvalidNumberOfElement(LoadEnvError):
    """
    Raised if the number of element is imcompatible with
    the number of elemtn of type.
    """


def envclass(_cls: type) -> type:
    """
    `envclass` decorator generates methods to loads field values from environment variables.

    """
    @functools.wraps(_cls)
    def wrap(cls) -> type:
        def load_env(self, _prefix: str = None) -> None:
            """
            Load attributes from environment variables.
            """
            for f in fields(cls):
                # If no prefix specified, use the default PREFIX.
                prefix = _prefix if _prefix is not None else ENVCLASS_PREFIX
                prefix += '_' if prefix else ''
                logger.debug(f'prefix={prefix}, type={f.type}')

                if is_envclass(f.type):
                    _load_dataclass(self, f, prefix)
                elif is_list(f.type):
                    _load_list(self, f, prefix)
                elif is_tuple(f.type):
                    _load_tuple(self, f, prefix)
                elif is_dict(f.type):
                    _load_dict(self, f, prefix)
                elif is_enum(f.type):
                    _load_enum(self, f, prefix)
                elif is_str(f.type):
                    _load_str(self, f, prefix)
                else:
                    _load_other(self, f, prefix)

        setattr(cls, ENVCLASS_DUNDER_FUNC_NAME, load_env)
        return cls

    return wrap(_cls)


def _load_dataclass(obj, f: Field, prefix: str) -> None:
    """
    Override exisiting dataclass object by environment variables.
    """
    inner_prefix = f'{prefix}{f.name}'
    o = getattr(obj, f.name)
    try:
        o.__envclasses_load_env__(inner_prefix)
    except KeyError:
        pass


def _load_list(obj, f: Field, prefix: str) -> None:
    """
    Override list values by environment variables.
    """
    typ = f.type
    element_type = typ.__args__[0]
    name = f'{prefix.upper()}{f.name.upper()}'
    try:
        s: str = os.environ[name].strip()
    except KeyError:
        return

    yml = yaml.safe_load(s)
    lst = [element_type(e) for e in yml]
    setattr(obj, f.name, lst)


def _load_tuple(obj, f: Field, prefix: str) -> None:
    """
    Override tuple values by environment variables.
    """
    typ = f.type
    name = f'{prefix.upper()}{f.name.upper()}'
    element_types = typ.__args__
    try:
        s: str = os.environ[name].strip()
    except KeyError:
        return

    lst = yaml.safe_load(s)
    if len(lst) != len(element_types):
        raise InvalidNumberOfElement(f'expected={len(element_types)} ' f'actual={len(lst)}')
    tpl = tuple(element_type(e) for e, element_type in zip(lst, element_types))
    setattr(obj, f.name, tpl)


def _load_dict(obj, f: Field, prefix: str) -> None:
    """
    Override dict values by environment variables.
    """
    typ = f.type
    name = f'{prefix.upper()}{f.name.upper()}'
    key_type = typ.__args__[0]
    value_type = typ.__args__[1]
    try:
        s = os.environ[name].strip()
    except KeyError:
        return

    dct = {_to_value(k, key_type): _to_value(v, value_type) for k, v in yaml.safe_load(s).items()}
    setattr(obj, f.name, dct)


def _to_value(v: JsonValue, typ: Type) -> Any:
    if isinstance(v, (List, Dict)):
        return v
    else:
        return typ(v)


def _load_enum(obj, f: Field, prefix: str) -> None:
    enum_annotations = f.type.__dict__.get('__annotations__', {})
    name = f'{prefix.upper()}{f.name.upper()}'
    for n, nested_type in enum_annotations.items():
        try:
            setattr(obj, f.name, f.type(nested_type(os.environ[name])))
            return
        except (KeyError, ValueError):
            continue


def _load_str(obj, f: Field, prefix: str) -> None:
    """
    Override str values by environment variables.
    """
    name = f'{prefix.upper()}{f.name.upper()}'
    try:
        value = os.environ[name]
        setattr(obj, f.name, _to_value(value, f.type))
    except KeyError:
        pass


def _load_other(obj, f: Field, prefix: str) -> None:
    """
    Override values by environment variables.
    """
    name = f'{prefix.upper()}{f.name.upper()}'
    try:
        yml = yaml.safe_load(os.environ[name])
        setattr(obj, f.name, _to_value(yml, f.type))
    except KeyError:
        pass


def is_enum(typ: Type) -> bool:
    """
    Test if class is Enum class.
    """
    try:
        return issubclass(typ, enum.Enum)
    except TypeError:
        return isinstance(typ, enum.Enum)


def is_list(typ: Type) -> bool:
    """
    Test if the type is `typing.List`.
    """
    try:
        return issubclass(get_origin(typ), list)
    except TypeError:
        return isinstance(typ, list)


def is_tuple(typ: Type) -> bool:
    """
    Test if the type is `typing.Tuple`.
    """
    try:
        return issubclass(get_origin(typ), tuple)
    except TypeError:
        return isinstance(typ, tuple)


def is_dict(typ: Type) -> bool:
    """
    Test if the type is `typing.Dict`.
    """
    try:
        return issubclass(get_origin(typ), dict)
    except TypeError:
        return isinstance(typ, dict)


def is_str(typ: Type) -> bool:
    """
    Test if the type is `str`.
    """
    return issubclass(typ, str)


def is_envclass(instance_or_class: Any) -> bool:
    """
    Test if instance_or_class is envclass.

    >>> from dataclasses import dataclass
    >>>
    >>> @envclass
    ... @dataclass
    ... class Foo:
    ...     pass
    >>> is_envclass(Foo)
    True
    """
    return hasattr(instance_or_class, ENVCLASS_DUNDER_FUNC_NAME)


def load_env(inst, prefix: str = None) -> None:
    """
    Load field values from environment variables.

    `inst` is an instance of envclass. If `inst` is not an envclass,
    `LoadEnvError` exception is raised.

    `prefix` specifies the prefix of environment variables that envclass looks up.
    for example `prefix="foo"`, envclass will load value from environment variable
    `FOO_<FIELD_NAME>` and update the field value on the instance. If `prefix` is
    omitted, the default prefix `env` is used.

    >>> from dataclasses import dataclass
    >>>
    >>> @envclass
    ... @dataclass
    ... class Foo:
    ...     v: int
    >>> foo = Foo(v=10)
    >>> os.environ['ENV_V'] = '100'
    >>> load_env(foo)
    >>> foo.v
    100

    If an empty string is set in `prefix`, no prefix will be expected.

    >>> os.environ['V'] = '100'
    >>> load_env(foo, '')
    >>> foo.v
    100
    """
    inst.__envclasses_load_env__(prefix)
