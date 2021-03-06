# AUTOGENERATED! DO NOT EDIT! File to edit: notebooks/97_Helpers.ipynb (unless otherwise specified).

__all__ = ['ensure', 'ensure_equal', 'ensure_exists']

# Cell

from pathlib import Path

# Cell

def ensure(p, msg: str=None):
    """ Ensures that p value is True
    """
    if not p:
        raise ValueError(msg)

def ensure_equal(x, y, msg: str=None):
    """ Ensures that two objects are equal
    """

    if msg is None:
        msg = f"{x} != {y}"
    ensure(x == y, msg)

def ensure_exists(f: Path, msg: str=None):
    """ Ensures that path exists
    """

    if msg is None:
        msg = f"{f} does not exist"
    ensure(f.exists(), msg)