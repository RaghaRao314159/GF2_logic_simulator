"""
parse.py.

Parses the definition file and builds the network for the Logic Simulator.

This module contains the Parser class, which is responsible for syntactic
and semantic analysis of the circuit definition file. It checks for errors,
reports them, and builds the logic network using the provided devices,
network, monitors, and names modules.
"""


class Parser:
    """
    Parser class for the Logic Simulator project.

    The Parser analyses the definition file, checks for syntactic and
    semantic errors, and builds the logic network. It interacts with the
    scanner to receive tokens, and with devices, network, monitors, and
    names modules to construct the circuit.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """
        Initialise the Parser with references to other modules.

        Set up constants.
        """
        # Store references to other modules
        self.names = names
        self.scanner = scanner
        self.monitors = monitors
        self.devices = devices
        self.parent = None
        self.network = network

        # Current symbol from the scanner
        self.symbol = None

        # Error tracking
        self.error_count = 0
        self.error_type_list = [
            self.NO_SEMICOLON, self.NO_COLON, self.NO_ARROW, self.NO_DOT,
            self.DOT, self.NO_DEVICE_TYPE, self.NO_NUMBER, self.INVALID_NAME,
            self.CLOCK_PERIOD_ZERO, self.NO_INITIALISATION_KEYWORD,
            self.NOT_BIT, self.NO_ERROR, self.QUALIFIER_PRESENT,
            self.INVALID_RANGE, self.INVALID_CONNECTION_SC,
            self.DEVICE_ABSENT, self.INPUT_CONNECTED, self.INPUT_TO_INPUT,
            self.PORT_ABSENT, self.OUTPUT_TO_OUTPUT, self.NOT_CONNECTED,
            self.INVALID_PORT, self.INVALID_PORT_DTYPE,
            self.INVALID_PORT_XOR, self.NOT_I_PORT,
            self.PORT_OUT_RANGE, self.NOT_END, self.REPEATED_MONITOR, 
            self.REPEATED_DEVICE, self.MISSED_SEMICOLON
        ] = range(30)
        # Device types that require dot notation for ports
        self.dot_signals = {
            "IN": [self.devices.D_TYPE],
            "OUT": [
                self.devices.D_TYPE, self.devices.XOR, self.devices.AND,
                self.devices.NAND, self.devices.OR, self.devices.NOR
            ]
        }

    def parse_network(self):
        """
        Parse the circuit definition file.

        Returns True if parsing is successful (no errors), False otherwise.
        """
        self.symbol = self.scanner.get_symbol()
        while self.symbol.type != self.scanner.EOF:
            if self.symbol.id == self.scanner.DEVICES_ID:
                self.parent = 'D'
                # Start parsing device list
                self.symbol = self.scanner.get_symbol()
                self.device_list()
            elif self.symbol.id == self.scanner.CONNECT_ID:
                self.parent = 'C'
                self.symbol = self.scanner.get_symbol()
                self.connection_list()
            elif self.symbol.id == self.scanner.MONITOR_ID:
                self.parent = 'M'
                self.symbol = self.scanner.get_symbol()
                self.monitor_list()
            elif self.symbol.id == self.scanner.END_ID:
                self.symbol = self.scanner.get_symbol()
                self.end_of_file()
                break
            else:
                # Error: expected a section keyword
                self.error(self.NO_INITIALISATION_KEYWORD)
            self.parent = None
        
        if self.error_count == 0 and not self.network.check_network():
            print()
            print("Network connectivity issues found")
            print()
            self.error_count += 1

        if self.error_count > 0:
            print(f"Summary: {self.error_count} error/s found\n")
            return False
        
        return True

    def end_of_file(self):
        """Check if the current symbol is EOF, otherwise report an error."""
        if self.symbol.type != self.scanner.EOF:
            self.error(self.NOT_END)
        return

    def make_device_parser(self, device_id, device_type_id):
        """
        Create a device with its parameter.

        Handles device-specific errors.
        """
        self.symbol = self.scanner.get_symbol()
        error = None
        # Handle XOR and DTYPE devices
        if device_type_id == self.scanner.XOR_ID:
            error = self.devices.make_device(
                device_id, self.devices.XOR, device_property=self.symbol.id)
        elif device_type_id == self.scanner.DTYPE_ID:
            error = self.devices.make_device(
                device_id, self.devices.D_TYPE, device_property=self.symbol.id)
        # Check for qualifier errors
        if error == self.devices.QUALIFIER_PRESENT:
            error = self.QUALIFIER_PRESENT
            return error
        if error == self.devices.DEVICE_PRESENT:
            error = self.REPEATED_DEVICE
            return error
        elif error == self.devices.NO_ERROR:
            error = self.NO_ERROR
            return error
        # Handle AND, OR, NAND, NOR devices
        if device_type_id == self.scanner.AND_ID:
            error = self.devices.make_device(
                device_id, self.devices.AND, device_property=self.symbol.id)
        elif device_type_id == self.scanner.OR_ID:
            error = self.devices.make_device(
                device_id, self.devices.OR, device_property=self.symbol.id)
        elif device_type_id == self.scanner.NAND_ID:
            error = self.devices.make_device(
                device_id, self.devices.NAND, device_property=self.symbol.id)
        elif device_type_id == self.scanner.NOR_ID:
            error = self.devices.make_device(
                device_id, self.devices.NOR, device_property=self.symbol.id)
        # Check for missing or invalid qualifiers
        if error == self.devices.NO_QUALIFIER:
            error = self.NO_NUMBER
        elif error == self.devices.NO_ERROR:
            error = self.NO_ERROR
        elif error == self.devices.INVALID_QUALIFIER:
            error = self.INVALID_RANGE
        # Handle CLOCK device
        if device_type_id == self.scanner.CLOCK_ID:
            error = self.devices.make_device(
                device_id, self.devices.CLOCK, device_property=self.symbol.id)
            if error == self.devices.NO_QUALIFIER:
                error = self.NO_NUMBER
            elif error == self.devices.NO_ERROR:
                error = self.NO_ERROR
            elif error == self.devices.INVALID_QUALIFIER:
                error = self.CLOCK_PERIOD_ZERO
        # Handle SWITCH device
        elif device_type_id == self.scanner.SWITCH_ID:
            error = self.devices.make_device(
                device_id, self.devices.SWITCH, device_property=self.symbol.id)
            if error in [
                self.devices.NO_QUALIFIER,
                self.devices.INVALID_QUALIFIER
            ]:
                error = self.NOT_BIT
            elif error == self.devices.NO_ERROR:
                error = self.NO_ERROR
        # Default to no error if error is still None
        if error is None:
            error = self.NO_ERROR
        self.symbol = self.scanner.get_symbol()
        return error

    def device(self):
        """Parse a device with its device type."""
        if self.symbol.type == self.scanner.NAME:
            # Valid device name, get the next symbol
            device_id = self.symbol.id
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.COLON:
                self.symbol = self.scanner.get_symbol()
                if (self.symbol.type == self.scanner.KEYWORD and
                        self.symbol.id in self.scanner.device_id_list):
                    device_type_id = self.symbol.id
                    return self.make_device_parser(device_id, device_type_id)
                else:
                    return self.NO_DEVICE_TYPE
            else:
                return self.NO_COLON
        elif self.symbol.id in [
                self.scanner.DEVICES_ID, self.scanner.CONNECT_ID,
                self.scanner.MONITOR_ID, self.scanner.END_ID]:
            return self.MISSED_SEMICOLON

        else:
            return self.INVALID_NAME

    def device_list(self):
        """Parse a list of devices from the definition file."""
        # Parse the first device
        error = self.device()
        # Check for errors in the first device
        if error != self.NO_ERROR:
            self.error(error)
        # Check if there are more devices to be parsed
        if self.parent is None:
            return
        # Check for more devices
        while True:
            if self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()

                error = self.device()
                # Check for errors in the subsequent devices
                if error != self.NO_ERROR:
                    self.error(error)
                # Check if there are more devices to be parsed
                if self.parent is None:
                    return
            elif self.symbol.type == self.scanner.SEMICOLON:
                # End of device list
                self.symbol = self.scanner.get_symbol()
                break
            else:
                # Error: expected semicolon
                self.error(self.NO_SEMICOLON)
            if self.parent is None:
                return
        return

    def in_signame(self):
        """Parse a signal name and return the device and port IDs."""
        if self.symbol.type == self.scanner.NAME:
            # Valid device name, get the next symbol
            device_id = self.symbol.id
            if self.devices.get_device(device_id) is None:
                return self.DEVICE_ABSENT
            self.symbol = self.scanner.get_symbol()
            device_type_id = self.devices.get_device(device_id).device_kind
            if device_type_id not in self.dot_signals["IN"]:
                if self.symbol.type == self.scanner.DOT:
                    if device_type_id in [
                        self.devices.SWITCH,
                        self.devices.CLOCK
                    ]:
                        return self.DOT
                    else:
                        return self.INPUT_TO_INPUT
                return [device_id, None]
            if self.symbol.type == self.scanner.DOT:
                # Found a dot, get the port number
                self.symbol = self.scanner.get_symbol()
                # Found a number, this is the port number
                port_id = self.symbol.id
                if port_id not in [self.scanner.Q_ID, self.scanner.QBAR_ID]:
                    return self.INVALID_PORT
                self.symbol = self.scanner.get_symbol()
                return [device_id, port_id]
            else:
                # Error: expected a dot after the device name
                return self.NO_DOT
        elif self.symbol.id in [
                self.scanner.DEVICES_ID, self.scanner.CONNECT_ID,
                self.scanner.MONITOR_ID, self.scanner.END_ID]:
            return self.MISSED_SEMICOLON
        else:
            # Error: invalid device name
            return self.INVALID_NAME

    def out_signame(self):
        """Parse a signal name and return the device and port IDs."""
        if self.symbol.type == self.scanner.NAME:
            # Valid device name, get the next symbol
            device_id = self.symbol.id
            if self.devices.get_device(device_id) is None:
                return self.DEVICE_ABSENT
            device_type_id = self.devices.get_device(device_id).device_kind
            if device_type_id in [self.devices.SWITCH, self.devices.CLOCK]:
                return self.INVALID_CONNECTION_SC
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.DOT:
                # Found a dot, get the port number
                self.symbol = self.scanner.get_symbol()
                # Found a number, this is the port number
                port_id = self.symbol.id
                if port_id not in (
                    self.devices.get_device(device_id).inputs.keys()
                ):
                    if device_type_id == self.devices.D_TYPE:
                        if port_id in [
                            self.scanner.Q_ID, self.scanner.QBAR_ID
                        ]:
                            return self.OUTPUT_TO_OUTPUT
                        return self.INVALID_PORT_DTYPE
                    elif device_type_id == self.devices.XOR:
                        return self.INVALID_PORT_XOR
                    else:
                        name = self.names.get_name_string(
                            self.symbol.id)
                        if name[0] != 'I':
                            return self.NOT_I_PORT
                        return self.PORT_OUT_RANGE
                self.symbol = self.scanner.get_symbol()
                return [device_id, port_id]
            else:
                # Error: expected a dot after the device name
                return self.OUTPUT_TO_OUTPUT
        else:
            # Error: invalid device name
            return self.INVALID_NAME

    def connection(self):
        """Parse a single connection."""
        # Get the input device and port number
        in_signal = self.in_signame()
        if isinstance(in_signal, int):
            # error has occurred
            return in_signal
        else:
            in_device_id, in_port_id = in_signal

        # Check for arrow symbol
        if self.symbol.type != self.scanner.ARROW:
            return self.NO_ARROW

        self.symbol = self.scanner.get_symbol()

        # Get the output device and port number
        out_signal = self.out_signame()
        if isinstance(out_signal, int):
            # error has occurred
            return out_signal
        else:
            out_device_id, out_port_id = out_signal

        error_type = self.network.make_connection(
            in_device_id, in_port_id, out_device_id, out_port_id)
        if error_type == self.network.DEVICE_ABSENT:
            return self.DEVICE_ABSENT
        elif error_type == self.network.INPUT_CONNECTED:
            return self.INPUT_CONNECTED
        elif error_type == self.network.INPUT_TO_INPUT:
            return self.INPUT_TO_INPUT
        elif error_type == self.network.PORT_ABSENT:
            return self.PORT_ABSENT
        elif error_type == self.network.OUTPUT_TO_OUTPUT:
            return self.OUTPUT_TO_OUTPUT
        return self.NO_ERROR

    def connection_list(self):
        """Parse a list of connections."""
        # Parse the first connection
        error = self.connection()
        if error != self.NO_ERROR:
            # Check for errors in the first connection
            self.error(error)
        if self.parent is None:
            return
        # Check for more connections
        while True:
            if self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                error = self.connection()
                # Check for errors in the subsequent connections
                if error != self.NO_ERROR:
                    self.error(error)
                # Check if there are more connections to be made
                if self.parent is None:
                    return
            elif self.symbol.type == self.scanner.SEMICOLON:
                # End of connection list
                self.symbol = self.scanner.get_symbol()
                break
            else:
                # Error: expected semicolon
                self.error(self.NO_SEMICOLON)
            if self.parent is None:
                return
        return

    def monitor(self):
        """Parse a signal name and monitor it."""
        if self.symbol.type == self.scanner.NAME:
            # Valid device name, get the next symbol
            device_id = self.symbol.id
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.DOT:
                # Found a dot, get the port number
                self.symbol = self.scanner.get_symbol()
                # Found a number, this is the port number
                port_id = self.symbol.id
                error = self.monitors.make_monitor(device_id, port_id)
                self.symbol = self.scanner.get_symbol()
                if error == self.network.DEVICE_ABSENT:
                    error = self.DEVICE_ABSENT
                elif error == self.monitors.NOT_OUTPUT:
                    error = self.INVALID_PORT
                elif error == self.monitors.MONITOR_PRESENT:
                    error = self.REPEATED_MONITOR
                elif error == self.monitors.NO_ERROR:
                    error = self.NO_ERROR
                return error
            else:
                error = self.monitors.make_monitor(device_id, None)
                if error == self.network.DEVICE_ABSENT:
                    error = self.DEVICE_ABSENT
                elif error == self.monitors.NOT_OUTPUT:
                    error = self.INVALID_PORT
                elif error == self.monitors.MONITOR_PRESENT:
                    error = self.REPEATED_MONITOR
                elif error == self.monitors.NO_ERROR:
                    error = self.NO_ERROR
                return error
        elif self.symbol.id in [
                self.scanner.DEVICES_ID, self.scanner.CONNECT_ID,
                self.scanner.MONITOR_ID, self.scanner.END_ID]:
            return self.MISSED_SEMICOLON
        else:
            return self.INVALID_NAME

    def monitor_list(self):
        """Parse a list of signals to be monitored from the definition file."""
        # Parse the first signal to be monitored
        error = self.monitor()
        # Check for errors in the first monitored signal
        if error != self.NO_ERROR:
            self.error(error)
        if self.parent is None:
            return
        while True:
            if self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                error = self.monitor()
                # Check for errors in the monitored signal
                if error != self.NO_ERROR:
                    self.error(error)
                # Check if there are more signals to be monitored
                if self.parent is None:
                    return
            elif self.symbol.type == self.scanner.SEMICOLON:
                # End of monitor list
                self.symbol = self.scanner.get_symbol()
                break
            else:
                # Error: expected semicolon
                self.error(self.NO_SEMICOLON)

            if self.parent is None:
                return
        return

    def error(self, error_type):
        """Handle errors in the definition file."""
        if error_type == self.MISSED_SEMICOLON:
            self.parent = None
            self.error_count += 1
            print("Expected a semicolon prior to this")  # tested
            print(f"LINE {self.symbol.line_number}:")
            print(self.scanner.print_error(self.symbol))
            print()
            return
        
        self.error_count += 1
        stopping_punctuation_flag = False
        if error_type == self.NO_SEMICOLON:
            print("Expected a comma or semicolon")  # tested
            stopping_punctuation_flag = True
        elif error_type == self.NO_COLON:
            print("Expected a colon")
        elif error_type == self.NO_ARROW:
            print("Expected an arrow")
        elif error_type == self.NO_DOT:
            print("Expected a dot")
        elif error_type == self.DOT:
            print("Did not expect a dot")
        elif error_type == self.NO_DEVICE_TYPE:
            print("Expected a device type")  # tested
        elif error_type == self.NO_NUMBER:
            print("Expected a number")  # tested
        elif error_type == self.INVALID_NAME:
            print("Invalid device name")
        elif error_type == self.NO_INITIALISATION_KEYWORD:
            print("Expected DEVICES, CONNECT, MONITOR or END")  # tested
        elif error_type == self.NOT_BIT:
            print("Expected a bit (0 or 1)")  # tested
        elif error_type == self.QUALIFIER_PRESENT:
            print("Did not expect a parameter")  # tested
        elif error_type == self.INVALID_RANGE:
            print("Expected number between 1 and 16 inclusive")
        elif error_type == self.INVALID_CONNECTION_SC:
            print("Connection should not be made to SWITCH or CLOCK")
        elif error_type == self.DEVICE_ABSENT:
            print("Device not found")  # tested
        elif error_type == self.REPEATED_DEVICE:
            print("Device has already been initialised")
        elif error_type == self.INPUT_CONNECTED:
            print("Input has already been connected")
        elif error_type == self.INPUT_TO_INPUT:
            print("Input cannot be connected to another input")
        elif error_type == self.PORT_ABSENT:
            print("Port not found")
        elif error_type == self.OUTPUT_TO_OUTPUT:
            print("Output cannot be connected to another output")
        elif error_type == self.NOT_I_PORT:
            print("Port Absent, Port is not a valid gate input port")
        elif error_type == self.PORT_OUT_RANGE:
            print("Port number out of range")
        elif error_type == self.INVALID_PORT:
            print("Invalid port number")
        elif error_type == self.INVALID_PORT_DTYPE:
            print("Port Absent, Invalid port for D-type device")
        elif error_type == self.INVALID_PORT_XOR:
            print("Port Absent, Invalid port number for XOR device")
        elif error_type == self.NOT_END:
            print("Expected file to end after END keyword") 
        elif error_type == self.REPEATED_MONITOR:
            print("Signal cannot be monitored more than once")
        else:
            print("Unknown error")
        print(f"LINE {self.symbol.line_number}:")
        print(self.scanner.print_error(self.symbol))
        print()
        if self.symbol.type == self.scanner.COMMA:
            return
        if self.symbol.type == self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol()
            self.parent = None
            return
        while self.symbol.type != self.scanner.EOF:
            self.symbol = self.scanner.get_symbol()
            if self.parent and self.symbol.type == self.scanner.COMMA:
                return
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
                self.parent = None
                return
            if self.symbol.id in [
                self.scanner.DEVICES_ID, self.scanner.CONNECT_ID,
                self.scanner.MONITOR_ID, self.scanner.END_ID
            ]:
                self.parent = None
                if not stopping_punctuation_flag:
                    self.error_count += 1
                    print("Expected a semicolon prior to this")  # tested
                    print(f"LINE {self.symbol.line_number}:")
                    print(self.scanner.print_error(self.symbol))
                    print()
                return
        self.error_count += 1
        print("Expected 'END' keyword before end of file.")  # tested
        print(f"LINE {self.symbol.line_number}:")
        print(self.scanner.print_error(self.symbol))
        print()
        self.parent = None
        return
