"""Test the parser module."""
import pytest
import os
import sys
import io

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


@pytest.fixture
def parser_with_adder():
    """Return a parser instance with some devices already created."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    # Create a test file path
    file_path = os.path.join(os.path.dirname(__file__), "test_parser",
                             "test_adder.txt")
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return parser, names, devices, network, monitors


@pytest.fixture
def parser_with_flip_flop():
    """Return a parser instance with flip-flop circuit configuration."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    # Create a test file path for flip-flop circuit
    file_path = os.path.join(os.path.dirname(__file__), "test_parser",
                             "test_flip_flop.txt")
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return parser, names, devices, network, monitors


@pytest.fixture
def parser_with_open_comments():
    """Return a parser instance with open comments after END."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    # Create a test file path for open comments
    file_path = os.path.join(os.path.dirname(__file__), "test_parser",
                             "test_open_comment.txt")
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return parser, names, devices, network, monitors


@pytest.fixture
def parser_with_closed_comments_error():
    """Return a parser instance with closed comments
    not properly terminated."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    # Create a test file path for closed comments error
    file_path = os.path.join(os.path.dirname(__file__), "test_parser",
                             "test_closed_comment_error.txt")
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return parser, names, devices, network, monitors


@pytest.fixture
def parser_with_error_devices():
    """Return a parser instance with error test file one."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    file_path = os.path.join(os.path.dirname(__file__), "test_parser",
                             "test_print_error_devices.txt")
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return parser


@pytest.fixture
def parser_with_error_connection_syntax():
    """Return a parser instance with error test file two."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    file_path = os.path.join(os.path.dirname(__file__), "test_parser",
                             "test_print_error_connection_syntax.txt")
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return parser


@pytest.fixture
def parser_with_error_connection_semantic():
    """Return a parser instance with error test file two."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    file_path = os.path.join(os.path.dirname(__file__), "test_parser",
                             "test_print_error_connection_semantic.txt")
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return parser


@pytest.fixture
def parser_with_error_monitor():
    """Return a parser instance with error test file two."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    file_path = os.path.join(os.path.dirname(__file__), "test_parser",
                             "test_print_error_monitor.txt")
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return parser


def test_monitor_adder(parser_with_adder):
    """Test if the parser correctly handles monitor connections."""
    parser, names, devices, network, monitors = parser_with_adder

    # Parse the network which includes monitor definitions
    assert parser.parse_network()

    # Get the device IDs we expect to be monitored based on test_adder.txt
    [X2_ID, O1_ID, NO1_ID] = names.lookup(["X2", "O1", "NO1"])

    # Check that the monitors dictionary contains the expected monitors
    assert (X2_ID, None) in monitors.monitors_dictionary
    assert (O1_ID, None) in monitors.monitors_dictionary
    assert (NO1_ID, None) in monitors.monitors_dictionary

    # Check that the monitors dictionary has the correct structure
    assert monitors.monitors_dictionary[(X2_ID, None)] == []
    assert monitors.monitors_dictionary[(O1_ID, None)] == []
    assert monitors.monitors_dictionary[(NO1_ID, None)] == []

    # Verify that only these three devices are being monitored
    assert len(monitors.monitors_dictionary) == 3

    # Get the monitored signal names
    monitored_signals, _ = monitors.get_signal_names()

    # Verify the correct signals are being monitored
    assert "X2" in monitored_signals
    assert "O1" in monitored_signals
    assert "NO1" in monitored_signals
    assert len(monitored_signals) == 3


def test_monitor_connections_flip_flop(parser_with_flip_flop):
    """Test if the parser correctly handles monitor connections for the
    flip-flop circuit."""
    parser, names, devices, network, monitors = parser_with_flip_flop

    # Parse the network which includes monitor definitions
    assert parser.parse_network()

    # Get the device IDs we expect to be monitored based on test_flip_flop.txt
    [D1_ID, N1_ID, QBAR_ID] = names.lookup(["D1", "N1", "QBAR"])

    # Check that the monitors dictionary contains the expected monitors
    # Note: D1.QBAR is monitored, so we need to check for (D1_ID, QBAR_ID)
    assert (D1_ID, QBAR_ID) in monitors.monitors_dictionary
    assert (N1_ID, None) in monitors.monitors_dictionary

    # Check that the monitors dictionary has the correct structure
    assert monitors.monitors_dictionary[(D1_ID, QBAR_ID)] == []
    assert monitors.monitors_dictionary[(N1_ID, None)] == []

    # Verify that only these two devices are being monitored
    assert len(monitors.monitors_dictionary) == 2

    # Get the monitored signal names
    monitored_signals, _ = monitors.get_signal_names()

    # Verify the correct signals are being monitored
    assert "D1.QBAR" in monitored_signals
    assert "N1" in monitored_signals
    assert len(monitored_signals) == 2


def test_monitor_connections_open_comments(parser_with_open_comments):
    """Test if the parser correctly handles monitor connections for the
    flip-flop circuit."""
    parser, names, devices, network, monitors = parser_with_open_comments

    # Parse the network which includes monitor definitions
    parser.parse_network()

    # Get the device IDs we expect to be monitored based on test_flip_flop.txt
    [D1_ID, N1_ID, QBAR_ID] = names.lookup(["D1", "N1", "QBAR"])

    # Check that the monitors dictionary contains the expected monitors
    # Note: D1.QBAR is monitored, so we need to check for (D1_ID, QBAR_ID)
    assert (D1_ID, QBAR_ID) in monitors.monitors_dictionary
    assert (N1_ID, None) in monitors.monitors_dictionary

    # Check that the monitors dictionary has the correct structure
    assert monitors.monitors_dictionary[(D1_ID, QBAR_ID)] == []
    assert monitors.monitors_dictionary[(N1_ID, None)] == []

    # Verify that only these two devices are being monitored
    assert len(monitors.monitors_dictionary) == 2

    # Get the monitored signal names
    monitored_signals, _ = monitors.get_signal_names()

    # Verify the correct signals are being monitored
    assert "D1.QBAR" in monitored_signals
    assert "N1" in monitored_signals
    assert len(monitored_signals) == 2


def test_parser_error_devices(parser_with_error_devices, capsys):
    """Test if the parser correctly handles errors in
    test_print_error_devices.txt."""
    parser = parser_with_error_devices

    # Parse the network which should contain errors
    assert not parser.parse_network()  # Should return False due to errors

    # Get the captured output
    captured = capsys.readouterr()
    output = captured.out

    # Check for expected error messages
    expected_errors = [
        "Expected DEVICES, CONNECT, MONITOR or END",
        "Expected a semicolon prior to this",
        "Did not expect a parameter",
        "Expected a device type",
        "Expected a number",
        "Expected a bit (0 or 1)",
        "Expected a comma or semicolon",
        "Expected DEVICES, CONNECT, MONITOR or END",
        "Expected a semicolon prior to this",
        "Device not found",
        "Expected DEVICES, CONNECT, MONITOR or END",
        "Expected 'END' keyword before end of file"
    ]

    expected_lines = [
        "LINE 7:",
        "LINE 9:",
        "LINE 10:",
        "LINE 11:",
        "LINE 12:",
        "LINE 13:",
        "LINE 15:",
        "LINE 18:",
        "LINE 32:",
        "LINE 33:",
        "LINE 36:",
        "LINE 36:"
    ]

    expected_indications = [
        "? # leads to double error, invalid character and no semicolon\n^",
        "DEVICES D1:DTYPE,\n^",
        ("D2:DTYPE 3, # error as input parameter"
            + " for DTYPE should not be specified\n                 ^"),
        "N1:NAD 2, # error as NAND is spelt incorrectly\n           ^",
        "C1:CLOCK -8, # error as - is an invalid symbol\n                  ^",
        ("S1:SWITCH 2, # error as"
            + " switch only takes a bit\n                   ^"),
        "S3:SWITCH 0 ;\n        ^",
        "CONECT S1 > D1.SET, # error as connect is spelt incorrectly\n^",
        "MONITOR D1.QBAR,\n^",
        "        N1 ;\n           ^",
        "ED\n^",
        "ED\n  ^"]

    # Check that each expected error appears in the output
    for error in expected_errors:
        assert error in output

    for line in expected_lines:
        assert line in output

    for indication in expected_indications:
        assert indication in output

    # Check total number of errors
    assert parser.error_count == len(expected_errors)
    assert parser.error_count == len(expected_lines)
    assert parser.error_count == len(expected_indications)


def test_parser_error_connection_syntax(parser_with_error_connection_syntax,
                                        capsys):
    """Test if the parser correctly handles errors in
    test_print_error_connection_syntax.txt."""
    parser = parser_with_error_connection_syntax

    # Parse the network which should contain errors
    assert not parser.parse_network()  # Should return False due to errors

    # Get the captured output
    captured = capsys.readouterr()
    output = captured.out
    # Check for expected error messages
    expected_errors = [
        "Output cannot be connected to another output",
        "Port Absent, Invalid port for D-type device"]

    expected_lines = [
        "LINE 27:",
        "LINE 28:"
    ]

    expected_indications = [
        ("D2.Q > D1.Q, # Output cannot"
         + " be connected to another output\n                  ^"),
        ("D2.Q > D1.PLATYPUS, # Port Absent,"
         + " Invalid port for D-type device\n                  ^")
    ]

    # Check that each expected error appears in the output
    for error in expected_errors:
        assert error in output

    for line in expected_lines:
        assert line in output

    for indication in expected_indications:
        assert indication in output

    # Check total number of errors
    assert parser.error_count == len(expected_errors)
    assert parser.error_count == len(expected_lines)
    assert parser.error_count == len(expected_indications)


def test_parser_error_connection_semantic(
        parser_with_error_connection_semantic, capsys):
    """Test if the parser correctly handles errors in
    test_print_error_connection_semantic.txt."""
    parser = parser_with_error_connection_semantic

    # Parse the network which should contain errors
    assert not parser.parse_network()  # Should return False due to errors

    # Get the captured output
    captured = capsys.readouterr()
    output = captured.out

    # Check for expected error messages
    expected_errors = [
        "Expected a colon",
        "Expected an arrow",
        "Device not found",
        "Device not found",
        "Output cannot be connected to another output",
        "Did not expect a dot",
        "Device not found",
        "Device not found",
        "Port Absent, Port is not a valid gate input port",
        "Invalid device name",
        "Port number out of range",
        "Connection should not be made to SWITCH or CLOCK",
        "Input has already been connected",
        "Input has already been connected",
        "Input cannot be connected to another input",
        "Expected a semicolon prior to this"]

    expected_lines = [
        "LINE 4:",
        "LINE 15:",
        "LINE 16:",
        "LINE 18:",
        "LINE 20:",
        "LINE 21:",
        "LINE 23:",
        "LINE 24:",
        "LINE 25:",
        "LINE 27:",
        "LINE 28:",
        "LINE 31:",
        "LINE 33:",
        "LINE 34:",
        "LINE 35:",
        "LINE 39:"
    ]

    expected_indications = [
        "DEVICES X1.XOR, # expected a colon error\n                  ^",
        "CONNECT S1  A1.I1, # missing arrow\n                    ^",
        "S1 > X1.I1,\n                     ^",
        "S2 > X1.I2,\n                     ^",
        "S3 > X2 I2, # missing dot\n                        ^",
        "S3.I1 > A2.I2, # did not expect dot\n                  ^",
        "X1 > X2.I1,\n                ^",
        "X1 > A2.I1,\n                ^",
        "X2 > NO1.P1, # invalid port\n                         ^",
        "2F2 > O1.I1, # invalid device name\n                ^",
        "A2 > O1.I5, # invalid range\n                        ^",
        ("O1 > S1  , # Connection should not"
            + " be made to SWITCH or CLOCK\n                     ^"),
        ("S1 > NO1.I2, # Input has already"
            + " been connected\n                           ^"),
        ("S2 > NO1.I2, # Input has already"
            + " been connected\n                           ^"),
        ("NO1.I2 > O1.I1 # Output cannot be connected"
            + " to another output\n                   ^"),
        "MONITOR X2, # this is the summed bit\n        ^"
    ]

    # Check that each expected error appears in the output
    for error in expected_errors:
        assert error in output

    for line in expected_lines:
        assert line in output

    for indication in expected_indications:
        assert indication in output

    # Check total number of errors
    assert parser.error_count == len(expected_errors)
    assert parser.error_count == len(expected_lines)
    assert parser.error_count == len(expected_indications)


def test_parser_error_monitor(parser_with_error_monitor, capsys):
    """Test if the parser correctly handles errors in
    test_print_error_monitor_syntax.txt."""
    parser = parser_with_error_monitor

    # Parse the network which should contain errors
    assert not parser.parse_network()  # Should return False due to errors

    # Get the captured output
    captured = capsys.readouterr()
    output = captured.out

    # Check for expected error messages
    expected_errors = [
        "Expected number between 1 and 16 inclusive",
        "Input cannot be connected to another input",
        "Port Absent, Invalid port number for XOR device",
        "Device not found",
        "Port Absent, Port is not a valid gate input port",
        "Device not found",
        "Output cannot be connected to another output",
        "Signal cannot be monitored more than once"]

    expected_lines = [
        "LINE 6:",
        "LINE 16:",
        "LINE 17:",
        "LINE 18:",
        "LINE 20:",
        "LINE 25:",
        "LINE 29:",
        "LINE 36:"
    ]

    expected_indications = [
        "A1:AND 17,\n                         ^",
        "X1.I1 > A1.I1,\n                  ^",
        "S2 > X1.Q,\n                        ^",
        "S2 > A1.I1,\n                     ^",
        ("S3 > A2.P, # port absent,"
         + " invalid for gates\n                        ^"),
        ("A1 > X2.PP # Port Absent,"
         + " Invalid port number for XOR device\n                ^"),
        ("A2 > O1, # Output cannot"
         + " be connected to another output\n                       ^"),
        "O1, # Signal cannot be monitored twice\n                  ^"
    ]

    # Check that each expected error appears in the output
    for error in expected_errors:
        assert error in output

    for line in expected_lines:
        assert line in output

    for indication in expected_indications:
        assert indication in output


def test_parser_closed_comment_error(parser_with_closed_comments_error,
                                     capsys):
    """Test if the parser correctly handles errors in
    test_closed_comment_error.txt."""
    parser, *_ = parser_with_closed_comments_error

    # Parse the network which should contain errors
    assert not parser.parse_network()  # Should return False due to errors

    # Get the captured output
    captured = capsys.readouterr()
    output = captured.out

    expected_errors = [
        "Device not found"] * 10

    expected_lines = [
        "LINE 16:",
        "LINE 17:",
        "LINE 18:",
        "LINE 19:",
        "LINE 20:",
        "LINE 22:",
        "LINE 23:",
        "LINE 25:",
        "LINE 26:",
        "LINE 27:"
    ]

    expected_indications = [
        "CONNECT S1 > D1.SET,\n        ^",
        "        S1 > D2.SET,\n        ^",
        "        S2 > D1.DATA,\n        ^",
        "        S3 > D1.CLEAR,\n        ^",
        "        S3 > D2.CLEAR,\n        ^",
        "        C1 > D1.CLK,\n        ^",
        "        C1 > D2.CLK,\n        ^",
        "        D1.Q > D2.DATA,\n        ^",
        "        D2.Q > N1.I1,\n        ^",
        "        D2.QBAR > N1.I2 ;\n        ^"
    ]

    # Check that each expected error appears in the output
    for error in expected_errors:
        assert error in output

    for line in expected_lines:
        assert line in output

    for indication in expected_indications:
        assert indication in output

    # Check total number of errors
    assert parser.error_count == len(expected_errors)
    assert parser.error_count == len(expected_lines)
    assert parser.error_count == len(expected_indications)
