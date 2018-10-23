#                     | |
#   ___ _ ____   _____| | __ _ ___ ___  ___  ___
#  / _ \ '_ \ \ / / __| |/ _` / __/ __|/ _ \/ __|
# |  __/ | | \ V / (__| | (_| \__ \__ \  __/\__ \
#  \___|_| |_|\_/ \___|_|\__,_|___/___/\___||___/
#

import functools
import os
import logging
import enum
from typing import List, Tuple, Callable, Any
from dataclasses import fields, Field

__all__ = [
    '__version__',
    'FUNC_NAME',
    'LIST_BRACKET',
    'TUPLE_BRACKET',
    'DICT_BRACKET',
    'LIST_QUOTES',
    'PREFIX',
    'EnvclassError',
    'LoadEnvError',
    'envclass',
    'is_envclass',
    'load_env',
]

__version__ = '0.1.0'
""" Version of envclass. """

logger = logging.getLogger('envclasses')

FUNC_NAME = '__envclasses_load_env__'
""" Name of the generated function to be called by 'load_env'. """

LIST_BRACKET = '[]'
""" Bracket to denote string as List such as \"[1, 2, 3]\". """

TUPLE_BRACKET = '()'
""" Bracket to denote string as Tuple such as \"(1, 2, 3)\". """

DICT_BRACKET = '{}'
""" Bracket to denote string as Dict such as
\"{1:\\"one\\", 2: \\"two\\"}\". """

LIST_QUOTES = ('\'', '\"')
""" Allowed quotations. """

PREFIX = 'env'
""" Default prefix used for environment variables. """


class EnvclassError(TypeError):
    """
    Exception used in envclass.
    """


class LoadEnvError(Exception):
    """
    Exception used in load_env.
    """


class InvalidNumberOfElement(LoadEnvError):
    pass


def envclass(_cls: type) -> type:
    """
    @envclass decorator: Decorate class as envclass.
    """
    @functools.wraps(_cls)
    def wrap(cls) -> type:
        def load_env(self, _prefix: str=None) -> None:
            """
            Load attributes from environmental variables.
            """
            for f in fields(cls):
                # If no prefix specified, use the default PREFIX.
                prefix = _prefix or PREFIX
                logger.debug(f'prefix={prefix}, type={f.type}')

                if is_envclass(f.type):
                    _load_dataclass(self, f, prefix)
                elif is_list(f.type):
                    _load_list(self, f, prefix)
                elif is_tuple(f.type):
                    _load_tuple(self, f, prefix)
                elif is_enum(f.type):
                    _load_enum(self, f, prefix)
                else:
                    _load_primitive(self, f, prefix)
        setattr(cls, FUNC_NAME, load_env)
        return cls
    return wrap(_cls)


def _load_dataclass(obj, f: Field, prefix: str):
    """
    Override exisiting dataclass object by environmental variables.
    """
    inner_prefix = f'{prefix}_{f.name}'
    o = getattr(obj, f.name)
    try:
        o.__envclasses_load_env__(inner_prefix)
    except KeyError:
        pass


def _load_list(obj, f: Field, prefix: str):
    """
    Override list values by environmental variables.
    """
    typ = f.type
    element_typ = typ.__args__[0]
    name = f'{prefix.upper()}_{f.name.upper()}'
    try:
        s: str = os.environ[name].strip()
        if LIST_BRACKET[0] != s[0] or LIST_BRACKET[1] != s[-1]:
            raise EnvclassError(f'Not a valid list string: {s}')
        s = s[1:-1]
        lst = [_to_list_element(e.strip(), element_typ) for e in s.split(',')]
        setattr(obj, f.name, lst)

    except KeyError:
        pass


def _load_tuple(obj, f: Field, prefix: str):
    """
    Override tuple values by environmental variables.
    """
    typ = f.type
    name = f'{prefix.upper()}_{f.name.upper()}'
    element_types = typ.__args__
    try:
        s: str = os.environ[name].strip()
    except KeyError:
        pass

    if TUPLE_BRACKET[0] != s[0] or TUPLE_BRACKET[1] != s[-1]:
        raise EnvclassError(f'Not a valid tuple string: {s}')
    s = s[1:-1]
    lst = [e.strip() for e in s.split(',')]
    if len(lst) != len(element_types):
        raise InvalidNumberOfElement(f'expected={len(element_types)} '
                                     f'actual={len(lst)}')
    tpl = tuple(_to_list_element(e, element_typ)
                for e, element_typ in zip(lst, element_types))

    setattr(obj, f.name, tpl)


def _to_list_element(e: str, typ: type):
    if typ is str:
        if e[0] not in LIST_QUOTES or e[-1] not in LIST_QUOTES:
            raise EnvclassError(f'Not a valid string: {e}')
        return typ(e[1:-1])
    if typ is bool:
        return str_to_bool(e)
    else:
        return typ(e)


def _load_enum(obj, f: Field, prefix: str) -> None:
    enum_annotations = f.type.__dict__.get('__annotations__', {})
    name = f'{prefix.upper()}_{f.name.upper()}'
    for n, nested_type in enum_annotations.items():
        try:
            setattr(obj, f.name, f.type(nested_type(os.environ[name])))
            break

        except ValueError:
            pass


def _load_primitive(obj, f: Field, prefix: str):
    """
    Override primitive values object by environmental variables.
    """
    name = f'{prefix.upper()}_{f.name.upper()}'
    try:
        conv: Callable[[str], Any]
        if f.type is bool:
            conv = str_to_bool
        else:
            conv = f.type
        setattr(obj, f.name, conv(os.environ[name]))

    except KeyError:
        pass


def str_to_bool(s: str) -> bool:
    """
    Convert string to boolean.
    """
    if not isinstance(s, str):
        raise LoadEnvError(f'{s} is not string.')
    s = s.lower()
    if s in ('true', '1', 'yes'):
        return True
    elif s in ('false', '0', 'no'):
        return False
    else:
        raise LoadEnvError(f'\'{s}\' is a valid boolean.')


def is_enum(cls: type) -> bool:
    """
    Test if class is Enum class.
    """
    return issubclass(cls, enum.Enum)


def is_list(instance_or_class: Any) -> bool:
    """
    Test if instance or class is List.
    """
    return getattr(instance_or_class, '__origin__', None) is List


def is_tuple(instance_or_class: Any) -> bool:
    """
    Test if instance or class is Tuple.
    """
    return getattr(instance_or_class, '__origin__', None) is Tuple


def is_envclass(instance_or_class: Any):
    """
    Test if instance_or_class is envclass.
    """
    return hasattr(instance_or_class, FUNC_NAME)


def load_env(inst, prefix: str=None):
    """
    Load environmental variable and override an instance of envclass.
    """
    inst.__envclasses_load_env__(prefix)
