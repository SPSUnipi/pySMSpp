import copy

import numpy as np

from pysmspp import Attribute, Dimension, Variable
from pysmspp.components import Dict


def test_attribute():
    a = Attribute("a", np.zeros(2))
    shallow, deep = copy.copy(a), copy.deepcopy(a)
    a.value[0] = 1.0
    assert shallow is not a and shallow.value[0] == 1.0
    assert deep.name == "a" and deep.value[0] == 0.0


def test_dimension():
    d = Dimension("T", 24)
    shallow, deep = copy.copy(d), copy.deepcopy(d)
    assert shallow is not d and deep is not d
    assert shallow == d and deep == d


def test_variable():
    v = Variable("x", "f8", ("T",), np.zeros(3))
    shallow, deep = copy.copy(v), copy.deepcopy(v)
    v.data[0] = 1.0
    assert shallow is not v and shallow.data is v.data
    assert (deep.name, deep.var_type, deep.dimensions) == ("x", "f8", ("T",))
    assert deep.data[0] == 0.0


def test_dict():
    d = Dict(x=Variable("x", "f8", ("T",), np.zeros(3)), a=Attribute("a", 1))
    shallow, deep = copy.copy(d), copy.deepcopy(d)
    assert type(shallow) is Dict and type(deep) is Dict
    assert shallow["x"] is d["x"] and deep["x"] is not d["x"]
    d["x"].data[0] = 1.0
    assert deep["x"].data[0] == 0.0 and deep["a"] == 1
