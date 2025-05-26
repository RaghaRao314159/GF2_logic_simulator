"""Test the devices module."""
import pytest

from names import Names

def test_lookup_adder():
    #create empty names
    my_names = Names()

    # example cases
    names_list = ["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"]

    # lookup output
    out = my_names.lookup(names_list)

    # expected output
    exp_out = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    assert out == exp_out

def test_lookup_flip_flop():
    #create empty names
    my_names = Names()

    # example cases
    names_list = ["D1", "D2", "N1", "C1", "S1", "S2", "S3"]

    # lookup output
    out = my_names.lookup(names_list)

    # expected output
    exp_out = [0, 1, 2, 3, 4, 5, 6]

    assert out == exp_out

def test_query():
    # create empty names
    my_names = Names()

    # names from our full-adder circuit
    names_list = ["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"]

    # add these names into out names dictionary in my_names object
    my_names.lookup(["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"])

    # assert the id of every name
    for i,name in enumerate(names_list):
        assert my_names.query(name) == i


def test_get_name_string():
    pass


