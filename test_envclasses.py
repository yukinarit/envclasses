import enum
import os
from pathlib import Path
from typing import List, Tuple, Dict, Optional

from dataclasses import dataclass, fields, field
from envclasses import envclass, load_env, is_enum, is_dict, InvalidNumberOfElement

basedir = Path(__file__).parent


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
        i: IEnum = IEnum.i1

    h = Hoge()
    assert h.s == SEnum.s1
    os.environ['ENV_S'] = 'hoge2'
    os.environ['ENV_I'] = '2'
    load_env(h)
    assert h.s == SEnum.s2
    assert h.i == IEnum.i2


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
    os.environ['ENV_LST_STR'] = '[hoge, fuga, foo]'
    os.environ['ENV_LST_BOOL'] = ('[TRUE, FALSE, true, false,'
                                  ' True, False, 1, 0]')
    load_env(h)
    assert h.lst_int == [1, 2, 3]
    assert h.lst_float == [1.2, 2.3, 3.456]
    assert h.lst_str == ["hoge", "fuga", "foo"]
    assert h.lst_bool == [True, False, True, False, True, False, True, False]


def test_envclass_dict():
    @envclass
    @dataclass
    class Hoge:
        dct_int: Dict[int, int] = field(default_factory=dict)
        dct_str_float: Dict[str, float] = field(default_factory=dict)
        dct_in_dct: Dict[str, Dict[int, int]] = field(default_factory=dict)
        lst_in_dct: Dict[str, List[int]] = field(default_factory=dict)

    h = Hoge()
    assert h.dct_int == {}
    assert h.dct_str_float == {}
    assert h.dct_in_dct == {}
    assert h.lst_in_dct == {}
    assert is_dict(fields(Hoge)[0].type)
    os.environ['ENV_DCT_INT'] = '{1: 2}'
    os.environ['ENV_DCT_STR_FLOAT'] = "{hoge: 2}"
    os.environ['ENV_DCT_IN_DCT'] = "{hoge: {1: 2}}"
    os.environ['ENV_LST_IN_DCT'] = "{hoge: [1, 2]}"
    load_env(h)
    assert h.dct_int == {1: 2}
    assert h.dct_str_float == {'hoge': 2.0}
    assert h.lst_in_dct == {'hoge': [1, 2]}


def test_envclass_tuple():
    @envclass
    @dataclass
    class Hoge:
        tuple_one: Tuple[str] = ('hoge')
        tuple_two: Tuple[int, float] = (0, 0.0)

    h = Hoge()
    os.environ['ENV_TUPLE_ONE'] = '[fuga]'
    os.environ['ENV_TUPLE_TWO'] = '[1, 2]'
    load_env(h)
    assert h.tuple_one == ('fuga',)
    assert h.tuple_two == (1, 2.0)

    try:
        os.environ['ENV_TUPLE_TWO'] = '[1]'
        load_env(h)
    except InvalidNumberOfElement:
        assert h.tuple_two == (1, 2.0)


def test_envclass_nested():
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


def test_envclass_pathlib():
    @envclass
    @dataclass
    class Hoge:
        p: Path = field(default_factory=Path)

    h = Hoge(p=Path('.'))
    assert h.p == Path('.')
    os.environ['ENV_P'] = './hoge'
    load_env(h)
    assert h.p == Path('./hoge')


def test_load_env_with_prefix():
    @envclass
    @dataclass
    class Hoge:
        i: int

    h = Hoge(i=10)
    assert h.i == 10
    os.environ['HOGE_I'] = '20'
    load_env(h, prefix='hoge')
    assert h.i == 20


def test_load_env_with_empty_prefix():
    @envclass
    @dataclass
    class Hoge:
        i: int

    h = Hoge(i=10)
    assert h.i == 10
    os.environ['I'] = '30'
    load_env(h, prefix='')
    assert h.i == 30


def test_load_env_with_underscore_prefix():
    @envclass
    @dataclass
    class Hoge:
        i: int

    h = Hoge(i=10)
    assert h.i == 10
    os.environ['A_I'] = '30'
    os.environ['AB_I'] = '40'
    load_env(h, prefix='A')
    assert h.i == 30
    load_env(h, prefix='AB_')
    assert h.i == 40


def test_str():
    @envclass
    @dataclass
    class Hoge:
        date: str
        text: str
        foo: Optional[List[str]] = None

    h = Hoge(date='2021', text='a\nb')
    assert h.date == '2021'
    assert h.text == 'a\nb'
    assert h.foo is None
    os.environ['DATE'] = '2022-01-01T22:00:00Z'
    os.environ['TEXT'] = 'c\nd'
    os.environ['FOO'] = '["bar2"]'
    load_env(h, prefix='')
    assert h.date == '2022-01-01T22:00:00Z'
    assert h.text == 'c\nd'
    assert h.foo == ['bar2']


def test_is_enum():
    class SEnum(enum.Enum):
        s = 's'
    assert is_enum(SEnum)

    class IEnum(enum.IntEnum):
        i = 10
    assert is_enum(IEnum)

    @dataclass
    class Hoge:
        s: SEnum = SEnum.s
        i: IEnum = IEnum.i

    assert is_enum(IEnum)
    assert is_enum(SEnum)
    assert is_enum(fields(Hoge)[0].type)
    assert is_enum(fields(Hoge)[1].type)
    assert fields(Hoge)[0].type is SEnum
    assert fields(Hoge)[1].type is IEnum


def test_optional():
    class SEnum(enum.Enum):
        s = 's'

    @envclass
    @dataclass
    class Fuga:
        i: Optional[int] = None
        s: Optional[str] = None

    @envclass
    @dataclass
    class Hoge:
        a: Optional[str] = None
        i: Optional[int] = None
        lst_float: Optional[List[float]] = None
        dct_str_float: Optional[Dict[str, float]] = None
        tuple_two: Optional[Tuple[int, float]] = None
        s: Optional[SEnum] = None
        p: Optional[Path] = None
        fuga: Optional[Fuga] = None

    h = Hoge()
    assert all(getattr(h, field.name) is None for field in fields(h))
    os.environ.update({
        "A": "A",
        "I": "10",
        "LST_FLOAT": "[3.14, 1.618, 42]",
        "DCT_STR_FLOAT": "{van51: 42.0}",
        "TUPLE_TWO": "[1, 2]",
        "S": "s",
        "P": "/dev/null",
        "FUGA_I": "200",
        "FUGA_S": "fugafuga"

    })
    load_env(h, prefix="")
    assert h.a == "A"
    assert h.i == 10
    assert h.lst_float == [3.14, 1.618, 42.0]
    assert h.dct_str_float == {"van51": 42.0}
    assert h.tuple_two == (1, 2)
    assert h.s == SEnum.s
    assert h.p == Path("/dev/null")
    assert h.fuga.i == 200
    assert h.fuga.s == "fugafuga"
