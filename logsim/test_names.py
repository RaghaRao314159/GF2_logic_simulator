"""Test the devices module."""
import pytest

from names import Names

def test_lookup_adder():
    # create class of empty names
    my_names = Names()

    # example case
    names_list = ["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"]

    # lookup output
    out = my_names.lookup(names_list)

    # expected output
    exp_out = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    assert out == exp_out

def test_lookup_flip_flop():
    # create class of empty names
    my_names = Names()

    # example case
    names_list = ["D1", "D2", "N1", "C1", "S1", "S2", "S3"]

    # lookup output
    out = my_names.lookup(names_list)

    # expected output
    exp_out = [0, 1, 2, 3, 4, 5, 6]

    assert out == exp_out

def test_lookup_empty():
    # create class of empty names
    my_names = Names()

    # example case
    names_list = []

    # lookup output
    out = my_names.lookup(names_list)

    # expected output
    exp_out = []

    assert out == exp_out

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


