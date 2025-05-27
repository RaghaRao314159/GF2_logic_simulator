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
    my_scanner = Scanner(file_path, my_names)

    return my_scanner

@pytest.fixture
def flip_flop():
    # create class of empty names
    my_names = Names()
    # use os library to get path of file in Linux and Windows environments
    file_path = os.path.join(os.path.dirname(__file__), "test_flip_flop.txt")
    my_scanner = Scanner(file_path, my_names)

    return my_scanner

def test_lookup_adder(adder):
    # example case

    # expected output
    # convert self.FILE, while is a python file object to string using read


    # exp_string = adder.FILE.read(1)

    # print(exp_string)
    print("HELKLO WORLD")

    symbol = adder.get_symbol()
    symbol = adder.get_symbol()
    symbol = adder.get_symbol()

    print(symbol.line_number, symbol.position)

    assert 1 == 1




