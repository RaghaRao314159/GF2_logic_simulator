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


    exp_words_numbers = [
        'DEVICES', 'X1', 'XOR', 'X2', 'XOR', 'A1', 'AND', 2, 'A2', 'AND', 2, 
        'NO1', 'NOR', 2, 'O1', 'OR', 2, 'S1', 'SWITCH', 1, 'S2', 'SWITCH', 1, 
        'S3', 'SWITCH', 0, 'CONNECT', 'S1', 'X1', 'I1', 'S1', 'A1', 'I1', 'S2', 
        'X1', 'I2', 'S2', 'A1', 'I2', 'S3', 'X2', 'I2', 'S3', 'A2', 'I2', 'X1', 
        'X2', 'I1', 'X1', 'A2', 'I1', 'X2', 'NO1', 'I1', 'A1', 'O1', 'I1', 'A2', 
        'O1', 'I2', 'O1', 'NO1', 'I2', 'MONITOR', 'X2', 'O1', 'NO1', 'END'
    ]

    with open(os.path.join(os.path.dirname(__file__), "test_adder.txt")) as f:
        # l = [line.rstrip() for line in f]
        # l = [x for x in l if x.strip()]
        l = [line for line in f]

    symbol = adder.get_symbol()
    
    words_numbers = []

    while symbol.type != 8:
        first_char = ""
        if (symbol.type in [5, 7]):
            # name or keyword
            # print(adder.names.get_name_string(symbol.id), end = " ")
            words_numbers.append(adder.names.get_name_string(symbol.id))
            first_char = adder.names.get_name_string(symbol.id)[0]


        elif symbol.type == 6:
            # number
            # print(symbol.id, end = " ")
            words_numbers.append(symbol.id)
            first_char = str(symbol.id)[0]
        
        else:
            first_char = adder.symbol_list[symbol.type]

        # assert l[symbol.line_number - 1][symbol.position - 1] ==  first_char]
        print(symbol.line_number, symbol.position, symbol.type)
        # tests that scanner works
        assert l[symbol.line_number - 1][symbol.position - 1] == first_char
        symbol = adder.get_symbol()

    # tests if names adds keywords
    assert words_numbers == exp_words_numbers


def test_lookup_flip_flop(flip_flop):
    # example case

    # expected output
    # convert self.FILE, while is a python file object to string using read


    exp_words_numbers = [
        'DEVICES', 'D1', 'DTYPE', 'D2', 'DTYPE', 'N1', 'NAND', 2, 'C1', 'CLOCK', 8,
        'S1', 'SWITCH', 0, 'S2', 'SWITCH', 1, 'S3', 'SWITCH', 0,
        'CONNECT', 'S1', 'D1', 'SET', 'S1', 'D2', 'SET',
        'S2', 'D1', 'DATA', 'S3', 'D1', 'CLEAR', 'S3', 'D2', 'CLEAR',
        'C1', 'D1', 'CLK', 'C1', 'D2', 'CLK',
        'D1', 'Q', 'D2', 'DATA', 'D2', 'Q', 'N1', 'I1', 'D2', 'QBAR', 'N1', 'I2',
        'MONITOR', 'D1', 'QBAR', 'N1',
        'END'
    ]


    symbol = flip_flop.get_symbol()
    
    words_numbers = []

    while symbol.type != 8:
        if (symbol.type in [5, 7]):
            # name or keyword
            # print(flip_flop.names.get_name_string(symbol.id), end = " ")
            words_numbers.append(flip_flop.names.get_name_string(symbol.id))

        elif symbol.type == 6:
            # number
            # print(symbol.id, end = " ")
            words_numbers.append(symbol.id)

        symbol = flip_flop.get_symbol()

    # test key words

    assert words_numbers == exp_words_numbers