"""Test the devices module."""
import pytest

from names import Names


@pytest.fixture
def adder():
    # create class of empty names
    my_names = Names()

    names_list = ["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"]

    idx_list = my_names.lookup(names_list)

    return my_names, names_list, idx_list


@pytest.fixture
def flip_flop():
    # create class of empty names
    my_names = Names()

    names_list = ["D1", "D2", "N1", "C1", "S1", "S2", "S3"]

    idx_list = my_names.lookup(names_list)

    return my_names, names_list, idx_list


@pytest.fixture
def empty():
    # create class of empty names
    my_names = Names()

    return my_names


def test_lookup_adder(adder):
    # example case
    (*_, idx_list) = adder

    # expected output
    exp_idx_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    assert idx_list == exp_idx_list


def test_lookup_flip_flop(flip_flop):
    # example case
    (*_, idx_list) = flip_flop

    # expected output
    exp_idx_list = [0, 1, 2, 3, 4, 5, 6]

    assert idx_list == exp_idx_list


def test_lookup_empty(empty):
    # example case
    names_list = []

    # lookup output
    idx_list = empty.lookup(names_list)

    # expected output
    exp_idx_list = []

    assert idx_list == exp_idx_list


def test_lookup_multiple_lists(empty):
    # example case
    names_list = ["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"]

    # lookup for each case individually
    for idx, name in enumerate(names_list):
        assert [idx] == empty.lookup([name])


def test_query_adder(adder):
    # example case
    (my_names, names_list, _) = adder

    # assert the id of every name
    for idx, name in enumerate(names_list):
        assert my_names.query(name) == idx


def test_query_flip_flop(flip_flop):
    # example case
    (my_names, names_list, _) = flip_flop

    # assert the id of every name
    for idx, name in enumerate(names_list):
        assert my_names.query(name) == idx


def test_query_nonexistent(empty):
    # names from our adder circuit
    names_list = ["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"]

    # add names to names dictionary in my_names object
    empty.lookup(names_list)

    # assert the id of every name
    assert empty.query("D1") is None


def test_get_name_string_adder(adder):
    # examples case
    (my_names, names_list, _) = adder

    # assert the name of every id
    for idx, name in enumerate(names_list):
        print(idx, name, my_names.get_name_string(idx))
        assert my_names.get_name_string(idx) == name


def test_get_name_string_flip_flop(flip_flop):
    # examples case
    (my_names, names_list, _) = flip_flop

    # assert the name of every id
    for idx, name in enumerate(names_list):
        assert my_names.get_name_string(idx) == name


def test_get_name_string_nonexistent(adder):
    # examples case
    (my_names, names_list, _) = adder

    nonexistent_idx = len(names_list) + 1

    # assert the id of every name
    assert my_names.get_name_string(nonexistent_idx) is None
