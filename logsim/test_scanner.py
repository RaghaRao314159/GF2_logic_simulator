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

    symbol = adder.get_symbol()
    with open(os.path.join(os.path.dirname(__file__), "test_adder.txt")) as f:
        l = [line.rstrip() for line in f]
        l = [x for x in l if x.strip()]

    print (symbol.line_number, symbol.position)
    # symbol position defined as starting at 1 not zero 
    assert l[symbol.line_number][symbol.position] == 'D'

    #print('one',l[symbol.line_number][symbol.position], 'two')
    # s=True
    # i=0
    # while s == True:
    #     print(f'{i}th time')
    #     nam = f'symbol_{i}'
    #     nam = adder.get_symbol()
    #     print(nam.line_number, nam.position, nam.current_character)
    #     i+=1





