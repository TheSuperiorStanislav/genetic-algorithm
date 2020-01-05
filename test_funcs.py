import math


def test_func_1(*args):
    value = 0
    for x in args:
        value += math.pow(x, 2)
    return value


def test_func_2(x1, x2):
    return 100 * (x1 ** 2 - x2 ** 2) ** 2 + (1 - x1) ** 2


def test_func_6(*args):
    value = 0
    for x in args:
        value += -x * math.sin(math.sqrt(math.fabs(x)))
    return value
