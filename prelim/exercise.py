#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""
import sys
from mynames import MyNames


def open_file(path):
    """Open and return the file specified by path."""
    return open(path, 'r')


def get_next_character(input_file):
    """Read and return the next character in input_file."""
    return input_file.read(1)


def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""
    non_white = input_file.read(1)

    while non_white.isspace():
        # print(non_white, "is a space")
        non_white = input_file.read(1)

    return non_white


def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.
    """
    number = input_file.read(1)
    num_str = ''

    while len(number) > 0 and not number.isdigit():
        # print(non_white, "is a space")
        number = input_file.read(1)

    if not number.isdigit():
        return ''

    num_str += str(number)
    number = input_file.read(1)

    while len(number) > 0 and number.isdigit():
        num_str += str(number)
        number = input_file.read(1)

    return num_str


def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """
    name = input_file.read(1)
    name_str = ''

    while len(name) > 0 and not name.isalpha():
        # print(non_white, "is a space")
        name = input_file.read(1)

    if not name.isalnum():
        return ''

    name_str += str(name)
    name = input_file.read(1)

    while len(name) > 0 and name.isalnum():
        name_str += str(name)
        name = input_file.read(1)

    return name_str


def main():
    """Preliminary exercises for Part IIA Project GF2."""
    # Check command line arguments
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:
        print("\nNow opening file...")
        # Print the path provided and try to open the file for reading
        file = open_file(arguments[-1])

        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of
        # file
        file.seek(0, 0)
        while True:
            char = get_next_character(file)
            if not char:
                break
            print(char)

        print("\nNow skipping spaces...")
        # Print out all the characters in the file, without spaces
        file.seek(0, 0)
        while True:
            char = get_next_non_whitespace_character(file)
            if not char:
                break
            print(char)

        print("\nNow reading numbers...")
        # Print out all the numbers in the file
        file.seek(0, 0)
        while True:
            num_str = get_next_number(file)
            if len(num_str) == 0:
                break
            print(num_str)

        print("\nNow reading names...")
        # Print out all the names in the file
        file.seek(0, 0)
        name = MyNames()
        while True:
            name_str = get_next_name(file)
            if len(name_str) == 0:
                break

            name.lookup(name_str)
            print(name_str)

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        bad_name_ids = [
            name.lookup("Terrible"), name.lookup("Horrid"),
            name.lookup("Ghastly"), name.lookup("Awful")
        ]

        for n in name.get_ids():
            if n in bad_name_ids:
                continue
            print(name.get_string(n))


if __name__ == "__main__":
    main()
