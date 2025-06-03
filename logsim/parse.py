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
        self.network = network

        # from parser
        self.symbol = None

        # errors
        self.error_count = 0
        self.error_type_list = [
            self.NO_COMMA, self.NO_SEMICOLON, self.NO_COLON, self.NO_ARROW, self.NO_DOT,
            self.NO_KEYWORD, self.NO_DEVICE_TYPE, self.NO_NUMBER, self.INVALID_NAME,
            self.CLOCK_PERIOD_ZERO, self.NO_INITIALISATION_KEYWORD, self.NOT_BIT,
            self.NO_ERROR, self.QUALIFIER_PRESENT, self.INVALID_RANGE, self.NO_DOT, self.DOT,
            self.INVALID_CONNECTION_SC, self.DEVICE_ABSENT, self.INPUT_CONNECTED,
            self.INPUT_TO_INPUT, self.PORT_ABSENT, self.OUTPUT_TO_OUTPUT, self.NOT_CONNECTED,
            self.INVALID_PORT, self.INVALID_PORT_DTYPE, self.INVALID_PORT_XOR, self.NOT_I_PORT, self.PORT_OUT_RANGE, self.NOT_END] = range(30)
        
        self.dot_signals = {"IN": [self.devices.D_TYPE],
                            "OUT": [self.devices.D_TYPE, self.devices.XOR, self.devices.AND, self.devices.NAND, self.devices.OR, self.devices.NOR] }

    def parse_network(self):
        """Parse the circuit definition file."""
        # TODO
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        self.symbol = self.scanner.get_symbol()
        while self.symbol.type != self.scanner.EOF:
            if self.symbol.id == self.scanner.DEVICES_ID:
                self.parent = 'D'
                # Keyword 'connect' found, start parsing connections
                # print("before next symbol", self.scanner.DEVICES_ID)
                self.symbol = self.scanner.get_symbol()
                # print("before entering", self.symbol.id, self.names.get_name_string(self.symbol.id))
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

    def make_device_parser(self, device_id, device_type_id):
        self.symbol = self.scanner.get_symbol()
        error = None

        if device_type_id == self.scanner.XOR_ID:
            error = self.devices.make_device(device_id, self.devices.XOR, device_property=self.symbol.id)
        elif device_type_id == self.scanner.DTYPE_ID:
            error = self.devices.make_device(device_id, self.devices.D_TYPE, device_property=self.symbol.id)

        # print("Current Charcter", self.scanner.current_character)

        if error == self.devices.QUALIFIER_PRESENT:
            error = self.QUALIFIER_PRESENT
            return error
        elif error == self.devices.NO_ERROR:
            error = self.NO_ERROR
            return error

        if device_type_id == self.scanner.AND_ID:
            error =self.devices.make_device(device_id, self.devices.AND, device_property=self.symbol.id)
        elif device_type_id == self.scanner.OR_ID:
            error = self.devices.make_device(device_id, self.devices.OR, device_property=self.symbol.id)
        elif device_type_id == self.scanner.NAND_ID:
            error = self.devices.make_device(device_id, self.devices.NAND, device_property=self.symbol.id)
        elif device_type_id == self.scanner.NOR_ID:
            error = self.devices.make_device(device_id, self.devices.NOR, device_property=self.symbol.id)

        if error == self.devices.NO_QUALIFIER:
            error = self.NO_NUMBER
        elif error == self.devices.NO_ERROR:
            error = self.NO_ERROR
        elif error == self.devices.INVALID_QUALIFIER:
            error = self.INVALID_RANGE

        if device_type_id == self.scanner.CLOCK_ID:
            error = self.devices.make_device(device_id, self.devices.CLOCK, device_property=self.symbol.id)
            if error == self.devices.NO_QUALIFIER:
                error = self.NO_NUMBER
            elif error == self.devices.NO_ERROR:
                error = self.NO_ERROR
            elif error == self.devices.INVALID_QUALIFIER:
                error = self.CLOCK_PERIOD_ZERO
        elif device_type_id == self.scanner.SWITCH_ID:
            error = self.devices.make_device(device_id, self.devices.SWITCH, device_property=self.symbol.id)
            if error in [self.devices.NO_QUALIFIER, self.devices.INVALID_QUALIFIER]:
                error = self.NOT_BIT
            elif error == self.devices.NO_ERROR:
                error = self.NO_ERROR

        if error == None:
            error = self.NO_ERROR
        self.symbol = self.scanner.get_symbol()
    
        return error

    def device(self):
        if self.symbol.type == self.scanner.NAME:
            # Valid device name, get the next symbol
            device_id = self.symbol.id
            self.symbol = self.scanner.get_symbol()

            if self.symbol.type == self.scanner.COLON:
                # print('spotted colon correctly')
                self.symbol = self.scanner.get_symbol()

                if (self.symbol.type == self.scanner.KEYWORD and
                        self.symbol.id in self.scanner.device_id_list):
                    # print('spotted keyword correctly')
                    device_type_id = self.symbol.id
                    return self.make_device_parser(device_id, device_type_id)

                else:
                    return self.NO_DEVICE_TYPE

            else:
                return self.NO_COLON

        else:
            return self.INVALID_NAME



    def device_list(self):
        # print('before first device', self.scanner.current_character)
        # Parse the first device
        error = self.device()
        # print('after first device', self.scanner.current_character)
        while self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            error = self.device()
            # print("prior parent value", self.parent)
            if error != self.NO_ERROR:
                # print("parent value", self.parent)
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

            if self.devices.get_device(device_id) == None:
                return self.DEVICE_ABSENT

            self.symbol = self.scanner.get_symbol()
            device_type_id = self.devices.get_device(device_id).device_kind

            if device_type_id not in self.dot_signals["IN"]:
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

                self.symbol = self.scanner.get_symbol()
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
            if self.devices.get_device(device_id) == None:
                print("Device not found")
                return self.DEVICE_ABSENT

            device_type_id = self.devices.get_device(device_id).device_kind

            if device_type_id in [self.devices.SWITCH, self.devices.CLOCK]:
                print("Invalid connection to SWITCH or CLOCK")
                return self.INVALID_CONNECTION_SC
            
            self.symbol = self.scanner.get_symbol()

            if self.symbol.type == self.scanner.DOT:
                # Found a dot, get the port number
                self.symbol = self.scanner.get_symbol()
                # Found a number, this is the port number
                port_id = self.symbol.id

                if port_id not in self.devices.get_device(device_id).inputs.keys():
                    if device_type_id == self.devices.D_TYPE:
                            print("Invalid port number for D-type device")        
                            return self.INVALID_PORT_DTYPE      

                    elif device_type_id == self.devices.XOR:
                            print("Invalid port number for XOR device")        
                            return self.INVALID_PORT_XOR  
                     
                    else: 
                        name = self.names.get_name_string(self.symbol.id)
                        if name[0] != 'I':
                            print("Port is not an input port")
                            return self.NOT_I_PORT
                        print("Port number out of range")
                        return self.PORT_OUT_RANGE
                
                self.symbol = self.scanner.get_symbol()
                return [device_id, port_id]

            else:
                # Error: expected a dot after the device name
                print("Expected a dot after the device name")
                return self.NO_DOT

        else:
            # Error: invalid device name
            print("Invalid device name")
            return self.INVALID_NAME
    

    def connection(self):
        """Parse a single connection."""

        # Get the input device and port number
        in_signal = self.in_signame()
        if type(in_signal) == int:
            # error has occured
            print("error in in_signal")
            return in_signal
        else:
            [in_device_id, in_port_id] = in_signal
        
        # ISSUE IS HERE, TO DO WITH NEXT SYMBOLLLL
        # self.symbol = self.scanner.get_symbol()


        # Check for arrow symbol
        if self.symbol.type != self.scanner.ARROW:
            return self.NO_ARROW

        self.symbol = self.scanner.get_symbol()

        # Get the output device and port number
        out_signal = self.out_signame()
        if type(out_signal) == int:
            # error has occured
            print("error in out_signal")
            return out_signal
        else:
            [out_device_id, out_port_id] = out_signal

        # if self.error_count == 0:
        error_type = self.network.make_connection(in_device_id, in_port_id, out_device_id, out_port_id)
        if error_type == self.network.DEVICE_ABSENT:
            print("Device not found")
            return self.DEVICE_ABSENT
        elif error_type == self.network.INPUT_CONNECTED:
            print("Input already connected")
            return self.INPUT_CONNECTED
        elif error_type == self.network.INPUT_TO_INPUT:
            print("Input cannot be connected to another input")
            return self.INPUT_TO_INPUT
        elif error_type == self.network.PORT_ABSENT:
            print("Port not found")
            return self.PORT_ABSENT
        elif error_type == self.network.OUTPUT_TO_OUTPUT:
            print("Output cannot be connected to another output")
            return self.OUTPUT_TO_OUTPUT

        return self.NO_ERROR

    def connection_list(self):
        """Parse a list of connections."""
        # Parse the first device
        error = self.connection()
        if error !=  self.NO_ERROR:
            print("connection has error")
            self.error(error)

        if self.parent == None:
            return

        # print("Current symbol type", self.symbol.type)

        while self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            error = self.connection()
            if error !=  self.NO_ERROR:
                print("connection has error")
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
        elif error_type == self.DEVICE_ABSENT:
            print("Device not found")
        elif error_type == self.INPUT_CONNECTED:
            print("Input already connected")
        elif error_type == self.INPUT_TO_INPUT:
            print("Input cannot be connected to another input")
        elif error_type == self.PORT_ABSENT:
            print("Port not found")
        elif error_type == self.OUTPUT_TO_OUTPUT:
            print("Output cannot be connected to another output")
        elif error_type == self.NOT_I_PORT:
            print("Port is not an input port")
        elif error_type == self.PORT_OUT_RANGE:
            print("Port number out of range")
        elif error_type == self.INVALID_PORT:
            print("Invalid port number")
        elif error_type == self.INVALID_PORT_DTYPE:
            print("Invalid port number for D-type device")
        elif error_type == self.INVALID_PORT_XOR:
            print("Invalid port number for XOR device")
        elif error_type == self.NOT_END:
            print("Expected 'END' keyword")
        else:
            print("Unknown error")

        print(self.scanner.print_error(self.symbol))

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
                

            
