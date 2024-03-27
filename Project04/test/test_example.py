def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 1


def test_is_instance_():
    assert isinstance('This is a string', str)
    assert not isinstance('This is a string', int)

def test_boolean():
    validated = True
    assert validated is True
    assert ('hello' == 'world') is False

def test_type():
    assert type(1) == int
    assert type(1.0) == float
    assert type('hello') != int
    assert type(True) == bool
    assert type(None) == type(None)

def test_greater_and_less_than():
    assert 7 > 4
    assert 4 < 10

def test_list():
    num_list = [1, 2, 3, 4, 5]
    assert num_list[0] == 1