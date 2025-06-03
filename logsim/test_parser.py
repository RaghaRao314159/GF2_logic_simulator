"""Test the parser module."""
import pytest
import os

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

def test_parser_adder():
    path = os.path.join(os.path.dirname(__file__), "test_files", "test_scanner.txt")
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)
