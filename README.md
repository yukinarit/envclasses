```
                    | |
  ___ _ ____   _____| | __ _ ___ ___  ___  ___
 / _ \ '_ \ \ / / __| |/ _` / __/ __|/ _ \/ __|
|  __/ | | \ V / (__| | (_| \__ \__ \  __/\__ \
 \___|_| |_|\_/ \___|_|\__,_|___/___/\___||___/

```

[![CircleCI](https://circleci.com/gh/yukinarit/envclasses.svg?style=svg)](https://circleci.com/gh/yukinarit/envclasses)
[![PyPI version](https://badge.fury.io/py/envclasses.svg)](https://badge.fury.io/py/envclasses)

envclass is a meta programming library on top of dataclass.
Once envclass decorator is specified in a dataclass,
It will generate dunder function which loads values from
environment variables. This functionality is very useful
in a case like you want to override the exisiting configurations
for an application by the ones defined in environment variables.

Requirements
============

python >= 3.6.0


Installation
============

* Install from PyPI
    ```
    pip install envclasses
    ```

* Install development version from Github
    ```
    pip install git+https://github.com/yukinarit/envclasses.git
    ```

Usage
=====

* Create Hoge instance
    ```python
    from typing import List, Dict
    from dataclasses import dataclass, field
    from envclasses import envclass, load_env


    @envclass
    @dataclass
    class Hoge:
        i: int
        s: str
        f: float
        b: bool
        lst: List[int] = field(default_factory=list)
        dct: Dict[str, float] = field(default_factory=dict)


    # Create an instance.
    hoge = Hoge(i=10, s='hoge', f=0.1, b=False)

    # Load values from environment variables.
    load_env(hoge, prefix='HOGE')

    print(hoge)
    ```

* Run
    ```bash
    $ python hoge.py
    ```

    ```bash
    Hoge(i=10, s='hoge', f=0.1, b=False, lst=[], dct={})
    ```

* Override Hoge values by environment variables
    ```bash
    $ export HOGE_I=20
    $ export HOGE_S=hogehoge
    $ export HOGE_F=0.2
    $ export HOGE_B=true
    $ export HOGE_DCT="{key: 100.0}"
    $ export HOGE_LST="[1, 2, 3]"
    $ python hoge.py
    ```

    ```bash
    Hoge(i=20, s='hogehoge', f=0.2, b=True, lst=[1, 2, 3], dct={'key': 100.0})
    ```
