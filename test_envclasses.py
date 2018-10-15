import enum
import os
from typing import List, Tuple

from dataclasses import dataclass, field
from envclasses import envclass, load_env


def test_envclass_primitive():
    @envclass
    @dataclass
    class Hoge:
        i: int
        s: str
        f: float
        b: bool

    h = Hoge(i=10, s='hoge', f=100.0, b=True)
    hid = id(h)
    assert h.i == 10
    assert h.s == 'hoge'
    assert h.f == 100.0
    assert h.b is True
    os.environ['ENV_I'] = '20'
    os.environ['ENV_S'] = 'hogehoge'
    os.environ['ENV_F'] = '200.0'
    os.environ['ENV_B'] = 'False'
    load_env(h)
    assert h.i == 20
    assert h.s == 'hogehoge'
    assert h.f == 200.0
    assert h.b is False
    assert isinstance(h, Hoge)
    assert hid == id(h)


def test_envclass_enum():
    class SEnum(enum.Enum):
        s1: str = 'hoge1'
        s2: str = 'hoge2'

    class IEnum(enum.IntEnum):
        i1: int = 1
        i2: int = 2

    @envclass
    @dataclass
    class Hoge:
        s: SEnum = SEnum.s1
        # i: IEnum = IEnum.i1

    h = Hoge()
    assert h.s == SEnum.s1
    os.environ['ENV_S'] = 'hoge2'
    # os.environ['ENV_I'] = '2'
    load_env(h)
    assert h.s == SEnum.s2
    # assert h.i == IEnum.i2


def test_envclass_list():
    @envclass
    @dataclass
    class Hoge:
        lst_int: List[int] = field(default_factory=list)
        lst_float: List[float] = field(default_factory=list)
        lst_str: List[str] = field(default_factory=list)
        lst_bool: List[bool] = field(default_factory=list)

    h = Hoge()
    assert h.lst_int == []
    assert h.lst_float == []
    assert h.lst_str == []
    assert h.lst_bool == []
    os.environ['ENV_LST_INT'] = '[1, 2, 3 ]'
    os.environ['ENV_LST_FLOAT'] = '[ 1.2,  2.3 , 3.456 ]'
    os.environ['ENV_LST_STR'] = '["hoge", "fuga", "foo"]'
    os.environ['ENV_LST_BOOL'] = ('[TRUE, FALSE, true, false,'
                                  ' True, False, 1, 0]')
    load_env(h)
    assert h.lst_int == [1, 2, 3]
    assert h.lst_float == [1.2, 2.3, 3.456]
    assert h.lst_str == ["hoge", "fuga", "foo"]
    assert h.lst_bool == [True, False, True, False, True, False, True, False]


def test_envclass_tuple():
    @envclass
    @dataclass
    class Hoge:
        tuple_int: Tuple[int] = field(default_factory=tuple)

    # h = Hoge()
    # assert h.tuple_int == []
    # os.environ['ENV_LST_INT'] = '[1, 2, 3 ]'
    # load_env(h)
    # assert h.tuple_int == [1, 2, 3]


def test_envclass_inner():
    @envclass
    @dataclass
    class Fuga:
        i: int
        s: str

    @envclass
    @dataclass
    class Hoge:
        i: int
        s: str
        fuga: Fuga

    h = Hoge(i=10, s='hoge', fuga=Fuga(i=100, s='fuga'))
    assert h.i == 10
    assert h.s == 'hoge'
    assert h.fuga.i == 100
    assert h.fuga.s == 'fuga'
    os.environ['ENV_I'] = '20'
    os.environ['ENV_S'] = 'hogehoge'
    os.environ['ENV_FUGA_I'] = '200'
    os.environ['ENV_FUGA_S'] = 'fugafuga'
    load_env(h)
    assert h.i == 20
    assert h.s == 'hogehoge'
    assert h.fuga.i == 200
    assert h.fuga.s == 'fugafuga'
