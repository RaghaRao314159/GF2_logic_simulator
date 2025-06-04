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
def parser_with_devices():
    """Return a parser instance with some devices already created."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    
    # Create a test file path
    file_path = os.path.join(os.path.dirname(__file__), "test_parser", "test_adder.txt")
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
    file_path = os.path.join(os.path.dirname(__file__), "test_parser", "test_flip_flop.txt")
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    return parser, names, devices, network, monitors

@pytest.fixture
def parser_with_error_one():
    """Return a parser instance with error test file one."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    
    file_path = os.path.join(os.path.dirname(__file__), "test_parser", "test_print_error_one.txt")
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    return parser

@pytest.fixture
def parser_with_error_two():
    """Return a parser instance with error test file two."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    
    file_path = os.path.join(os.path.dirname(__file__), "test_parser", "test_print_error_two.txt")
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    return parser

def test_monitor_connections(parser_with_devices):
    """Test if the parser correctly handles monitor connections."""
    parser, names, devices, network, monitors = parser_with_devices
    
    # Parse the network which includes monitor definitions
    parser.parse_network()
    
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
    """Test if the parser correctly handles monitor connections for the flip-flop circuit."""
    parser, names, devices, network, monitors = parser_with_flip_flop
    
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

def test_parser_error_one(parser_with_error_one, capsys):
    """Test if the parser correctly handles errors in test_print_error_one.txt."""
    parser = parser_with_error_one
    
    # Parse the network which should contain errors
    assert not parser.parse_network()  # Should return False due to errors
    
    # Get the captured output
    captured = capsys.readouterr()
    output = captured.out
    
    # Check for expected error messages
    expected_errors = ["Expected DEVICES, CONNECT, MONITOR or END", # ? before DEVICES leads to invalid character error
                       "Expected a semicolon prior to this", # ? before DEVICES leads to missing semi-colon error
                        "Did not expect a parameter", # input parameter for DTYPE should not be specified
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
    
    # Check that each expected error appears in the output
    for error in expected_errors:
        assert error in output, f"Expected error message '{error}' not found in output"
    
    # Check total number of errors
    assert parser.error_count == len(expected_errors)

def test_parser_error_two(parser_with_error_two, capsys):
    """Test if the parser correctly handles errors in test_print_error_two.txt."""
    parser = parser_with_error_two
    
    # Parse the network which should contain errors
    assert not parser.parse_network()  # Should return False due to errors
    
    # Get the captured output
    captured = capsys.readouterr()
    output = captured.out
    
    # Check for expected error messages
    expected_errors = [
        "Expected a colon",  # For X1.XOR
        "Expected an arrow",  # For S1 A1.I1
        "Expected a dot",  # For X2 I2
        "Did not expect a dot",  # For S3.I1
        "Port Absent, Port is not a valid gate input port",  # For NO1.P1
        "Invalid device name",  # For 2F2
        "Port number out of range",  # For O1.I5
        "Connection should not be made to SWITCH or CLOCK",  # For O1 > S1
        "Input has already been connected",  # For S1 > NO1.I2
        "Output cannot be connected to another output"  # For NO1.I2 > O1.I1
    ]
    
    # Check that each expected error appears in the output
    for error in expected_errors:
        assert error in output, f"Expected error message '{error}' not found in output"
    
    # Check total number of errors
    assert parser.error_count == len(expected_errors)