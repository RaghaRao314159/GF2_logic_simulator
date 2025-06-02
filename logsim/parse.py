"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        # inputs
        self.names = names
        self.scanner = scanner
        self.monitors = monitors
        self.devices = devices
        self.parent = None

        """ TODO
        self.network = network
        """

        # from parser
        self.symbol = None

        # errors
        self.error_count = 0
        self.error_type_list = [
            self.NO_COMMA, self.NO_SEMICOLON, self.NO_COLON, self.NO_ARROW, self.NO_DOT,
            self.NO_KEYWORD, self.NO_DEVICE_TYPE, self.NO_NUMBER, self.INVALID_NAME,
            self.CLOCK_PERIOD_ZERO, self.NO_INITIALISATION_KEYWORD, self.NOT_BIT,
            self.NO_ERROR, self.QUALIFIER_PRESENT, self.INVALID_RANGE] = range(11)
        
        self.dot_signals = {"IN": [self.devices.D_TYPE],
                            "OUT": [self.devices.D_TYPE, self.devices.XOR, self.devices.AND, self.devices.NAND, self.devices.OR, self.devices.NOR] }

    def parse_network(self):
        """Parse the circuit definition file."""
        # TODO
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        self.scanner.get_symbol()
        while self.symbol.type != self.scanner.EOF:
            if self.symbol.id == self.scanner.DEVICES_ID:
                self.parent = 'D'
                # Keyword 'connect' found, start parsing connections
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
                self.error(self.NO_INITIALISATION_KEYWORD)
            self.parent = None

        return True


    def end_of_file(self):
        if self.scanner.type != self.scanner.EOF:
            self.error(self.NOT_END)

        return

    def make_device_parser(self, device_id):
        self.symbol = self.scanner.get_symbol()
        error = None

        if device_id == self.scanner.XOR_ID:
            error = self.devices.make_device(device_id, self.devices.XOR, device_property=self.symbol.id)
        elif device_id == self.scanner.DTYPE_ID:
            error = self.devices.make_device(device_id, self.devices.D_TYPE, device_property=self.symbol.id)

        if error == self.devices.QUALIFIER_PRESENT:
            error = self.QUALIFIER_PRESENT
            return error
        elif error == self.devices.NO_ERROR:
            error = self.NO_ERROR
            return error

        if device_id == self.scanner.AND_ID:
            error =self.devices.make_device(device_id, self.devices.AND, device_property=self.symbol.id)
        elif device_id == self.scanner.OR_ID:
            error = self.devices.make_device(device_id, self.devices.OR, device_property=self.symbol.id)
        elif device_id == self.scanner.NAND_ID:
            error = self.devices.make_device(device_id, self.devices.NAND, device_property=self.symbol.id)
        elif device_id == self.scanner.NOR_ID:
            error = self.devices.make_device(device_id, self.devices.NOR, device_property=self.symbol.id)

        if error == self.devices.NO_QUALIFIER:
            error = self.NO_NUMBER
        elif error == self.devices.NO_ERROR:
            error = self.NO_ERROR
        elif error == self.devices.INVALID_QUALIFIER:
            error = self.INVALID_RANGE

        if device_id == self.scanner.CLOCK_ID:
            error = self.devices.make_device(device_id, self.devices.CLOCK, device_property=self.symbol.id)
            if error == self.devices.NO_QUALIFIER:
                error = self.NO_NUMBER
            elif error == self.devices.NO_ERROR:
                error = self.NO_ERROR
            elif error == self.devices.INVALID_QUALIFIER:
                error = self.CLOCK_PERIOD_ZERO
        elif device_id == self.scanner.SWITCH_ID:
            error = self.devices.make_device(device_id, self.devices.SWITCH, device_property=self.symbol.id)
            if error in [self.devices.NO_QUALIFIER, self.devices.INVALID_QUALIFIER]:
                error = self.NOT_BIT
            elif error == self.devices.NO_ERROR:
                error = self.NO_ERROR

        self.symbol = self.scanner.get_symbol()
        return error

    def device(self):
        if self.symbol.type == self.scanner.NAME:
            # Valid device name, get the next symbol
            device_id = self.symbol.id
            self.symbol = self.scanner.get_symbol()

            if self.symbol.type == self.scanner.COLON:
                self.symbol = self.scanner.get_symbol()

                if (self.symbol.type == self.scanner.KEYWORD and
                        self.symbol.id in self.scanner.device_id_list):
                    return self.make_device_parser(device_id)

                else:
                    return self.NO_DEVICE_TYPE

            else:
                return self.NO_COLON

        else:
            return self.INVALID_NAME



    def device_list(self):

        # Parse the first device
        error = self.device()

        while self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            error = self.device()
            if error !=  self.NO_ERROR:
                self.error(error)
            if self.parent == None:
                return

        if self.symbol.type == self.scanner.SEMICOLON:
            # End of connection list
            self.symbol = self.scanner.get_symbol()

        else:
            # Error: expected semicolon
            self.error(self.NO_SEMICOLON)

        return




    def in_signame(self):
        """Parse a signal name and return the device and port IDs."""
        # TODO: What happens when the output is defined with no dot?

        if self.symbol.type == self.scanner.NAME:
            # Valid device name, get the next symbol
            device_id = self.symbol.id
            self.symbol = self.scanner.get_symbol()
            device_type_id = self.get_device(device_id).device_kind

            if device_type_id not in [self.dot_signals["IN"]]:
                if self.symbol.type == self.scanner.DOT:
                    return self.DOT
                return [device_id, None]

            
            if self.symbol.type == self.scanner.DOT:

                # Found a dot, get the port number
                self.symbol = self.scanner.get_symbol()

                # Found a number, this is the port number
                port_id = self.symbol.id

                if port_id not in [self.scanner.Q_ID, self.scanner.QBAR_ID]:
                    return self.INVALID_PORT

                return [device_id, port_id]

            else:
                # Error: expected a dot after the device name
                return self.NO_DOT

        else:
            # Error: invalid device name
            return self.INVALID_NAME
        
    
    def out_signame(self):
        """Parse a signal name and return the device and port IDs."""
        # TODO: What happens when the output is defined with no dot?

        if self.symbol.type == self.scanner.NAME:
            # Valid device name, get the next symbol
            device_id = self.symbol.id
            device_type_id = self.get_device(device_id).device_kind
            if device_type_id == None:
                return self.DEVICE_ABSENT
            
            if device_type_id in [self.devices.SWITCH, self.devices.CLOCK]:
                return self.INVALID_CONNECTION_SC
            
            self.symbol = self.scanner.get_symbol()

            if self.symbol.type == self.scanner.DOT:
                # Found a dot, get the port number
                self.symbol = self.scanner.get_symbol()
                # Found a number, this is the port number
                port_id = self.symbol.id

                if port_id not in self.get_device(device_id).inputs.keys():
                    if device_type_id == self.devices.D_TYPE:        
                            return self.INVALID_PORT_DTYPE      

                    elif device_type_id == self.devices.XOR:        
                            return self.INVALID_PORT_XOR  
                     
                    else: 
                        name = self.names.get_name_string(self.symbol.id)
                        if name[0] != 'I':
                            return self.NOT_I_PORT
                        return self.PORT_OUT_RANGE
                    
                return [device_id, port_id]

            else:
                # Error: expected a dot after the device name
                return self.NO_DOT

        else:
            # Error: invalid device name
            return self.INVALID_NAME
    

    def connection(self):
        """Parse a single connection."""

        # Get the input device and port number
        in_signal = self.in_signame()
        if type(signal) == int:
            # error has occured
            self.error(signal)
            return
        else:
            [in_device_id, in_port_id] = in_signal

        # Check for arrow symbol
        if self.symbol.type == self.scanner.ARROW:
            self.symbol = self.scanner.get_symbol()
            [out_device_id, out_port_id] = self.out_signame()
        else:
            self.error(self.NO_ARROW)
            return

        """ TBC
        if self.error_count == 0:
            error_type = self.network.make_connection(in_device_id, in_port_id, out_device_id, out_port_id)
            if error_type != self.network.NO_ERROR:
                self.error(...)
        """

    def connection_list(self):
        """Parse a list of connections."""
        # Parse the first device
        error = self.connection()

        while self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            error = self.connection()
            if error !=  self.NO_ERROR:
                self.error(error)
            if self.parent == None:
                return

        if self.symbol.type == self.scanner.SEMICOLON:
            # End of connection list
            self.symbol = self.scanner.get_symbol()

        else:
            # Error: expected semicolon
            self.error(self.NO_SEMICOLON)

        return

    def error(self, error_type):
        """Handle errors in the definition file."""
        self.error_count += 1
        stopping_punctuation_flag = False
        if error_type == self.NO_COMMA:
            print("Expected a comma")
        elif error_type == self.NO_SEMICOLON:
            print("Expected a comma or semicolon")
            stopping_punctuation_flag = True
        elif error_type == self.NO_COLON:
            print("Expected a colon")
        elif error_type == self.NO_ARROW:
            print("Expected an arrow")
        elif error_type == self.NO_DOT:
            print("Expected a dot")
        elif error_type == self.DOT:
            print("Did not expect a dot")
        elif error_type == self.NO_KEYWORD:
            print("Expected a keyword")
        elif error_type == self.NO_DEVICE_TYPE:
            print("Expected a device type")
        elif error_type == self.NO_NUMBER:
            print("Expected a number")
        elif error_type == self.INVALID_NAME:
            print("Invalid device name")
        elif error_type == self.NO_INITIALISATION_KEYWORD:
            print("Expected DEVICES, CONNECT, MONITOR or END")
        elif error_type == self.NOT_BIT:
            print("Expected a bit (0 or 1)")
        elif error_type == self.QUALIFIER_PRESENT:
            print("Did not expect a parameter")
        elif error_type == self.INVALID_RANGE:
            print("Expected number between 1 and 16 inclusive")
        elif error_type == self.INVALID_CONNECTION_SC:
            print("Should not to SWITCH or CLOCK")

        while self.symbol.type != self.scanner.EOF:
            self.symbol = self.scanner.get_symbol()

            if self.parent and self.symbol.type == self.scanner.COMMA:
                return

            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
                self.parent = None
                return


            if self.symbol.id in [self.scanner.DEVICES_ID, self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID]:
                self.parent = None
                if not stopping_punctuation_flag:
                    self.error_count += 1
                    print("Expected a semicolon")
                return


        self.error_count += 1
        print("Expected 'END' keyword")
        return
                

            
