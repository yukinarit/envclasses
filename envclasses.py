#                     | |
#   ___ _ ____   _____| | __ _ ___ ___  ___  ___
#  / _ \ '_ \ \ / / __| |/ _` / __/ __|/ _ \/ __|
# |  __/ | | \ V / (__| | (_| \__ \__ \  __/\__ \
#  \___|_| |_|\_/ \___|_|\__,_|___/___/\___||___/
#

import os
import logging
from typing import List, Callable, Any
from dataclasses import fields, Field

__version__ = '0.1.0'

logger = logging.getLogger('envclasses')

FUNC_NAME = '__envclasses_load_env__'

LIST_BRACKET = '[]'

DICT_BRACKET = '{}'

LIST_QUOTES = ('\'', '\"')


class EnvclassError(Exception):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class ConvError(EnvclassError):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


def envclass(_cls=None, prefix: str='env') -> type:
    """
    @envclass decorator: Decorate class as envclass.
    """
    def wrap(cls) -> type:
        def load_env(self, _prefix: str=None) -> None:
            """
            Load attributes from environmental variables.
            """
            nonlocal prefix
            for f in fields(cls):
                # Prioritize prefix from load_env function than
                # the one from envclass decorator.
                prefix = _prefix or prefix
                logger.debug(f'prefix={prefix}, type={f.type}')

                if is_envclass(f.type):
                    _load_dataclass(self, f, prefix)
                elif getattr(f.type, '__origin__', None) is List:
                    _load_list(self, f, prefix)
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
    Override list values object by environmental variables.
    """
    typ = f.type
    inner_typ = typ.__args__[0]
    name = f'{prefix.upper()}_{f.name.upper()}'
    try:
        s: str = os.environ[name].strip()
        if LIST_BRACKET[0] != s[0] or LIST_BRACKET[1] != s[-1]:
            raise EnvclassError('Not a valid list string: {s}')
        s = s[1:-1]
        lst = [_to_list_element(e.strip(), inner_typ) for e in s.split(',')]
        setattr(obj, f.name, lst)

    except KeyError:
        pass


def _to_list_element(e: str, typ: type):
    if typ is str:
        if e[0] not in LIST_QUOTES or e[-1] not in LIST_QUOTES:
            raise EnvclassError(f'Not a valid string: {e}')
        return typ(e[1:-1])
    if typ is bool:
        return _str_to_bool(e)
    else:
        return typ(e)


def _load_primitive(obj, f: Field, prefix: str):
    """
    Override primitive values object by environmental variables.
    """
    name = f'{prefix.upper()}_{f.name.upper()}'
    try:
        conv: Callable[[str], Any]
        if f.type is bool:
            conv = _str_to_bool
        else:
            conv = f.type
        setattr(obj, f.name, conv(os.environ[name]))

    except KeyError:
        pass


def _str_to_bool(s: str) -> bool:
    """
    Convert string to boolean.
    """
    if not isinstance(s, str):
        raise ConvError(f'{s} is not string.')
    s = s.lower()
    if s in ('true', '1', 'yes'):
        return True
    elif s in ('false', '0', 'no'):
        return False
    else:
        raise ConvError(f'\'{s}\' is a valid boolean.')


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
