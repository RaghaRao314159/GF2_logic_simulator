"""Test the devices module."""
import pytest

from names import Names

def test_lookup():
    pass

def test_query():
    # create empty names
    mynames = Names()

    # names from our full-adder circuit
    names_list = ["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"]

    # add these names into out names dictionary in mynames object
    mynames.lookup(["X1", "X2", "A1", "A2", "O1", "S1", "S2", "S3", "NO1"])

    # assert the id of every name
    for i,name in enumerate(names_list):
        print(i, name, mynames.lookup(name))
        assert mynames.query(name) == i


def test_get_name_string():
    pass


