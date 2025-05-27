"""Test the devices module."""
import pytest
import os
from names import Names
from scanner import Scanner, Symbol

@pytest.fixture
def adder():
    # create class of empty names
    my_names = Names()
    # use os library to get path of file in Linux and Windows environments
    file_path = os.path.join(os.path.dirname(__file__), "test_adder.txt")
    my_scanner = Scanner(file_path,my_names)

    idx_list = my_names.lookup(names_list)
    
    return my_names, names_list, idx_list

def test_lookup_adder(adder):
    # example case
    (*_, idx_list) = adder

    # expected output
    exp_idx_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    assert idx_list == exp_idx_list


