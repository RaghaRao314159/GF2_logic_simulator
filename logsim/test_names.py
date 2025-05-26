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

def test_lookup_adder(adder):
    # example case
    (*_, idx_list) = adder

    # expected output
    exp_idx_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    assert idx_list == exp_idx_list

def test_lookup_flip_flop(adder):
    # create class of empty names
    my_names = Names()

    # example case
    names_list = ["D1", "D2", "N1", "C1", "S1", "S2", "S3"]

    # lookup output
    idx_list = my_names.lookup(names_list)

    # expected output
    exp_idx_list = [0, 1, 2, 3, 4, 5, 6]

    assert idx_list == exp_idx_list

def test_lookup_empty():
    # create class of empty names
    my_names = Names()

    # example case
    names_list = []

    # lookup output
    idx_list = my_names.lookup(names_list)

    # expected output
    exp_idx_list = []

    assert idx_list == exp_idx_list

def test_lookup_multiple_lists():
    # create class of empty names
    my_names = Names()

    # example case
    names_list = ["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"]

    # lookup for each case individually
    for idx, name in enumerate(names_list):
        assert [idx] == my_names.lookup([name])

def test_query_adder():
    # create class of empty names
    my_names = Names()

    # names from full-adder circuit example
    names_list = ["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"]

    # add names to names dictionary in my_names object
    my_names.lookup(names_list)

    # assert the id of every name
    for idx, name in enumerate(names_list):
        assert my_names.query(name) == idx

def test_query_flip_flop():
    # create class of empty names
    my_names = Names()

    # names from our d-type flip flop example
    names_list = ["D1", "D2", "N1", "C1", "S1", "S2", "S3"]

    # add names to names dictionary in my_names object
    my_names.lookup(names_list)

    # assert the id of every name
    for idx, name in enumerate(names_list):
        assert my_names.query(name) == idx

def test_query_nonexistent():
    # create class of empty names
    my_names = Names()

    # names from our adder circuit
    names_list = ["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"]

    # add names to names dictionary in my_names object
    my_names.lookup(names_list)

    # assert the id of every name
    assert my_names.query("D1") == None

def test_get_name_string_adder():
    # create class of empty names
    my_names = Names()

    # names from adder circuit example 
    names_list = ["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"]

    # add names to names dictionary in my_names object
    my_names.lookup(names_list)

    # assert the name of every id
    for idx, name in enumerate(names_list):
        print(idx, name, my_names.get_name_string(idx))
        assert my_names.get_name_string(idx) == name

def test_get_name_string_flip_flop():
    # create class of empty names
    my_names = Names()

    # names from d-type flip flop circuit example 
    names_list = ["D1", "D2", "N1", "C1", "S1", "S2", "S3"]

    # add names to names dictionary in my_names object
    my_names.lookup(names_list)

    # assert the name of every id
    for idx, name in enumerate(names_list):
        assert my_names.get_name_string(idx) == name

def test_get_name_string_nonexistent():
    # create class of empty names
    my_names = Names()

    # names from our adder circuit
    names_list = ["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"]

    # add names to dictionary of names in my_names object
    my_names.lookup(names_list)

    nonexistent_idx = len(names_list) + 1

    # assert the id of every name
    assert my_names.get_name_string(nonexistent_idx) == None


