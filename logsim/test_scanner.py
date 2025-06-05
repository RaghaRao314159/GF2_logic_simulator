"""Test the scanner module."""
import pytest
import os
from names import Names
from scanner import Scanner, Symbol


@pytest.fixture
def adder():
    # create class of empty names
    my_names = Names()
    # use os library to get path of file in Linux and Windows environments
    file_path = os.path.join(
        os.path.dirname(__file__), "test_scanner", "test_adder.txt"
    )
    my_scanner = Scanner(file_path, my_names)

    # expected keywords to be detected
    exp_words_numbers = [
        'DEVICES', 'X1', 'XOR', 'X2', 'XOR', 'A1', 'AND', 2, 'A2', 'AND', 2,
        'NO1', 'NOR', 2, 'O1', 'OR', 2, 'S1', 'SWITCH', 1, 'S2', 'SWITCH', 1,
        'S3', 'SWITCH', 0, 'CONNECT', 'S1', 'X1', 'I1', 'S1', 'A1', 'I1',
        'S2', 'X1', 'I2', 'S2', 'A1', 'I2', 'S3', 'X2', 'I2', 'S3', 'A2',
        'I2', 'X1', 'X2', 'I1', 'X1', 'A2', 'I1', 'X2', 'NO1', 'I1', 'A1',
        'O1', 'I1', 'A2', 'O1', 'I2', 'O1', 'NO1', 'I2', 'MONITOR', 'X2',
        'O1', 'NO1', 'END'
    ]

    return my_scanner, file_path, exp_words_numbers


@pytest.fixture
def flip_flop():
    # create class of empty names
    my_names = Names()
    # use os library to get path of file in Linux and Windows environments
    file_path = os.path.join(
        os.path.dirname(__file__), "test_scanner", "test_flip_flop.txt"
    )
    my_scanner = Scanner(file_path, my_names)

    # expected keywords to be detected
    exp_words_numbers = [
        'DEVICES', 'D1', 'DTYPE', 'D2', 'DTYPE', 'N1', 'NAND', 2, 'C1',
        'CLOCK', 8, 'S1', 'SWITCH', 0, 'S2', 'SWITCH', 1, 'S3', 'SWITCH', 0,
        'CONNECT', 'S1', 'D1', 'SET', 'S1', 'D2', 'SET', 'S2', 'D1', 'DATA',
        'S3', 'D1', 'CLEAR', 'S3', 'D2', 'CLEAR', 'C1', 'D1', 'CLK', 'C1',
        'D2', 'CLK', 'D1', 'Q', 'D2', 'DATA', 'D2', 'Q', 'N1', 'I1', 'D2',
        'QBAR', 'N1', 'I2', 'MONITOR', 'D1', 'QBAR', 'N1', 'END'
    ]

    return my_scanner, file_path, exp_words_numbers


@pytest.fixture
def none_type():
    # create class of empty names
    my_names = Names()
    # use os library to get path of file in Linux and Windows environments
    file_path = os.path.join(
        os.path.dirname(__file__), "test_scanner", "test_none_type.txt"
    )
    my_scanner = Scanner(file_path, my_names)

    # expected keywords to be detected
    exp_words_numbers = [
        'DEVICES', 'D1', 'DTYPE', 'D2', 'DTYPE', 'N1', 'NAND', 2, 'C1',
        'CLOCK', 8, 'S1', 'SWITCH', 0, 'S2', 'SWITCH', 1, 'S3', 'SWITCH', 0,
        'CONNECT', 'S1', 'D1', 'SET', 'S1', 'D2', 'SET', 'S2', 'D1', 'DATA',
        'S3', 'D1', 'CLEAR', 'S3', 'D2', 'CLEAR', 'C1', 'D1', 'CLK', 'C1',
        'D2', 'CLK', 'D1', 'Q', 'D2', 'DATA', 'D2', 'Q', 'N1', 'I1', 'D2',
        'QBAR', 'N1', 'I2', 'MONITOR', 'D1', 'QBAR', 'N1', 'END'
    ]

    return my_scanner, file_path, exp_words_numbers


@pytest.fixture
def error_CONECT():
    # create class of empty names
    my_names = Names()
    # use os library to get path of file in Linux and Windows environments
    file_path = os.path.join(
        os.path.dirname(__file__), "test_scanner", "test_print_error.txt"
    )
    my_scanner = Scanner(file_path, my_names)

    # expected keywords to be detected
    exp_words_numbers = [
        'DEVICES', 'D1', 'DTYPE', 'D2', 'DTYPE', 'N1', 'NAND', 2, 'C1',
        'CLOCK', 8, 'S1', 'SWITCH', 0, 'S2', 'SWITCH', 1, 'S3', 'SWITCH', 0,
        'CONECT', 'S1', 'D1', 'SET', 'S1', 'D2', 'SET', 'S2', 'D1', 'DATA',
        'S3', 'D1', 'CLEAR', 'S3', 'D2', 'CLEAR', 'C1', 'D1', 'CLK', 'C1',
        'D2', 'CLK', 'D1', 'Q', 'D2', 'DATA', 'D2', 'Q', 'N1', 'I1', 'D2',
        'QBAR', 'N1', 'I2', 'MONITOR', 'D1', 'QBAR', 'N1', 'END'
    ]

    return my_scanner, file_path, exp_words_numbers


@pytest.fixture
def error_closed_comment():
    # create class of empty names
    my_names = Names()
    # use os library to get path of file in Linux and Windows environments
    file_path = os.path.join(
        os.path.dirname(__file__),
        "test_scanner",
        "test_closed_comment_error.txt"
    )
    my_scanner = Scanner(file_path, my_names)

    # expected keywords to be detected
    exp_words_numbers = [
        'CONNECT', 'S1', 'D1', 'SET', 'S1', 'D2', 'SET', 'S2', 'D1', 'DATA',
        'S3', 'D1', 'CLEAR', 'S3', 'D2', 'CLEAR', 'C1', 'D1', 'CLK', 'C1',
        'D2', 'CLK', 'D1', 'Q', 'D2', 'DATA', 'D2', 'Q', 'N1', 'I1', 'D2',
        'QBAR', 'N1', 'I2'
    ]

    return my_scanner, file_path, exp_words_numbers


@pytest.fixture
def error_open_comment():
    # create class of empty names
    my_names = Names()
    # use os library to get path of file in Linux and Windows environments
    file_path = os.path.join(
        os.path.dirname(__file__), "test_scanner", "test_open_comment.txt"
    )
    my_scanner = Scanner(file_path, my_names)

    # expected keywords to be detected
    exp_words_numbers = [
        'DEVICES', 'D1', 'DTYPE', 'D2', 'DTYPE', 'N1', 'NAND', 2, 'C1',
        'CLOCK', 8, 'S1', 'SWITCH', 0, 'S2', 'SWITCH', 1, 'S3', 'SWITCH', 0,
        'CONNECT', 'S1', 'D1', 'SET', 'S1', 'D2', 'SET', 'S2', 'D1', 'DATA',
        'S3', 'D1', 'CLEAR', 'S3', 'D2', 'CLEAR', 'C1', 'D1', 'CLK', 'C1',
        'D2', 'CLK', 'D1', 'Q', 'D2', 'DATA', 'D2', 'Q', 'N1', 'I1', 'D2',
        'QBAR', 'N1', 'I2', 'MONITOR', 'D1', 'QBAR', 'N1', 'END'
    ]

    return my_scanner, file_path, exp_words_numbers


def test_scanner_adder(adder):
    # example case where adder is tested
    adder, file_path, exp_words_numbers = adder

    with open(file_path) as f:
        lines = [line for line in f]

    symbol = adder.get_symbol()
    words_numbers = []

    while symbol.type != 8:
        first_char = ""
        print(symbol.line_number, symbol.position, symbol.type)
        if symbol.type in [5, 7]:
            # name or keyword
            words_numbers.append(adder.names.get_name_string(symbol.id))
            first_char = adder.names.get_name_string(symbol.id)[0]
            print("words_numbers", words_numbers)
        elif symbol.type == 6:
            # number
            words_numbers.append(symbol.id)
            first_char = str(symbol.id)[0]
        else:
            first_char = adder.symbol_list[symbol.type]
        # tests that scanner works
        assert lines[symbol.line_number - 1][symbol.position - 1] == first_char
        symbol = adder.get_symbol()
    # tests if names object has correctly added keywords
    assert words_numbers == exp_words_numbers


def test_scanner_flip_flop(flip_flop):
    # example case where flip flop is tested
    flip_flop, file_path, exp_words_numbers = flip_flop

    with open(file_path) as f:
        lines = [line for line in f]

    symbol = flip_flop.get_symbol()
    words_numbers = []

    while symbol.type != 8:
        if symbol.type in [5, 7]:
            # name or keyword
            words_numbers.append(flip_flop.names.get_name_string(symbol.id))
            first_char = flip_flop.names.get_name_string(symbol.id)[0]
            print("words_numbers", words_numbers)
        elif symbol.type == 6:
            # number
            words_numbers.append(symbol.id)
            first_char = str(symbol.id)[0]
        else:
            first_char = flip_flop.symbol_list[symbol.type]
        # tests that scanner works
        assert lines[symbol.line_number - 1][symbol.position - 1] == first_char
        symbol = flip_flop.get_symbol()
    # tests if names object has correctly added keywords
    assert words_numbers == exp_words_numbers


def test_scanner_none_type(none_type):
    # example case where unknown symbols are introduced in file
    none_type, file_path, exp_words_numbers = none_type

    with open(file_path) as f:
        lines = [line for line in f]

    symbol = none_type.get_symbol()
    words_numbers = []

    while symbol.type != 8:
        if symbol.type in [5, 7]:
            # name or keyword
            words_numbers.append(none_type.names.get_name_string(symbol.id))
            first_char = none_type.names.get_name_string(symbol.id)[0]
        elif symbol.type == 6:
            # number
            words_numbers.append(symbol.id)
            first_char = str(symbol.id)[0]
        elif symbol.type is None:
            assert lines[symbol.line_number - 1][symbol.position - 1] == "["
            symbol = none_type.get_symbol()
            continue
        else:
            first_char = none_type.symbol_list[symbol.type]
        # tests that scanner works
        print("first_char", first_char)
        assert lines[symbol.line_number - 1][symbol.position - 1] == first_char
        symbol = none_type.get_symbol()
    # tests if names object has correctly added keywords
    assert words_numbers == exp_words_numbers


def test_scanner_print_error(error_CONECT):
    # example case where CONECT is not a keyword, but a name
    print_error, file_path, exp_words_numbers = error_CONECT

    print(file_path)
    with open(file_path) as f:
        lines = [line for line in f]

    symbol = print_error.get_symbol()
    words_numbers = []

    while symbol.type != 8:
        if symbol.type in [5, 7]:
            # name or keyword
            name = print_error.names.get_name_string(symbol.id)
            words_numbers.append(name)
            first_char = name[0]
            if name == "CONECT":
                exp_error_message = "CONECT S1 > D1.SET,\n^"
                error_message = print_error.print_error(symbol)
                assert exp_error_message == error_message
        elif symbol.type == 6:
            # number
            words_numbers.append(symbol.id)
            first_char = str(symbol.id)[0]
        elif symbol.type is None:
            symbol = print_error.get_symbol()
            continue
        else:
            first_char = print_error.symbol_list[symbol.type]
        # tests that scanner works
        assert lines[symbol.line_number - 1][symbol.position - 1] == first_char
        symbol = print_error.get_symbol()
    # tests if names object has correctly added keywords
    assert words_numbers == exp_words_numbers


def test_closed_comment_error(error_closed_comment):
    # example case where multi-line comment before CONNECT is never closed
    # consecutive opening comment symbol ignored since closing symbol required
    # after comment has been opened

    # convert self.FILE, while is a python file object to string using read
    my_error, file_path, exp_words_numbers = error_closed_comment

    with open(file_path) as f:
        lines = [line for line in f]

    symbol = my_error.get_symbol()
    words_numbers = []

    while symbol.type != 8:
        if symbol.type in [5, 7]:
            # name or keyword
            words_numbers.append(my_error.names.get_name_string(symbol.id))
            first_char = my_error.names.get_name_string(symbol.id)[0]
            print("words_numbers", words_numbers)
        elif symbol.type == 6:
            # number
            words_numbers.append(symbol.id)
            first_char = str(symbol.id)[0]
        else:
            first_char = my_error.symbol_list[symbol.type]
        # tests that scanner works
        assert lines[symbol.line_number - 1][symbol.position - 1] == first_char
        symbol = my_error.get_symbol()
    # tests if names object has correctly added keywords
    assert words_numbers == exp_words_numbers


def test_open_comment_error(error_open_comment):
    # example case where open comment is open
    # Code should rightfully just end

    my_error, file_path, exp_words_numbers = error_open_comment

    with open(file_path) as f:
        lines = [line for line in f]

    symbol = my_error.get_symbol()
    words_numbers = []

    while symbol.type != 8:
        if symbol.type in [5, 7]:
            # name or keyword
            words_numbers.append(my_error.names.get_name_string(symbol.id))
            first_char = my_error.names.get_name_string(symbol.id)[0]
            print("words_numbers", words_numbers)
        elif symbol.type == 6:
            # number
            words_numbers.append(symbol.id)
            first_char = str(symbol.id)[0]
        else:
            first_char = my_error.symbol_list[symbol.type]
        # tests that scanner works
        assert lines[symbol.line_number - 1][symbol.position - 1] == first_char
        symbol = my_error.get_symbol()
    # tests if names object has correctly added keywords
    assert words_numbers == exp_words_numbers
