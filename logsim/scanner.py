"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None
        self.line_number = 1
        self.position = 1


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        self.names = names

        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.COLON, self.ARROW, self.DOT,
            self.KEYWORD, self.NUMBER, self.NAME, self.EOF] = range(9)
        
        self.symbol_list  = [',', ';', ':', '>', '.']

        self.keywords_list = ["DEVICES", "CONNECT", "MONITOR", "END", "CLOCK", "SWITCH", "AND", "NAND", "OR", "NOR",
                              "XOR", "DTYPE", "DATA", "CLK", "SET", "CLEAR", "Q", "QBAR", "I1", "I2", "I3", "I4", "I5",
                              "I6", "I7", "I8", "I9", "I10", "I11", "I12", "I13", "I14", "I15", "I16"]

        [self.DEVICES_ID, self.CONNECT_ID, self.MONITOR_ID,
            self.END_ID, self.CLOCK_ID, self.SWITCH_ID, self.AND_ID,
            self.NAND_ID, self.OR_ID, self.NOR_ID, self.XOR_ID,
            self.DTYPE_ID, self.DATA_ID, self.CLK_ID, self.SET_ID,
            self.CLEAR_ID, self.Q_ID, self.QBAR_ID, self.I1_ID,
            self.I2_ID, self.I3_ID, self.I4_ID, self.I5_ID,
            self.I6_ID, self.I7_ID, self.I8_ID, self.I9_ID,
            self.I10_ID, self.I11_ID, self.I12_ID, self.I13_ID,
            self.I14_ID, self.I15_ID, self.I16_ID] = self.names.lookup(self.keywords_list)

        self.position = 0
        self.line_number = 1

        self.FILE = open(path, 'r')

        self.current_character = "" 
        self.advance()

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""

        symbol = Symbol()

        self.skip_spaces()  # current character now not whitespace

        while self.current_character in ["@", "#", "\n"]:
            if self.current_character == "@":
                self.advance()
                while self.current_character != "@":
                    if self.current_character == "\n":
                        self.line_number += 1
                        self.position = 0
                    self.advance()
                self.advance()
            
            elif self.current_character == "#":
                while self.current_character != "\n":
                    self.advance()
            
            elif self.current_character == "\n": # new line
                self.line_number += 1
                self.position = 0
                self.advance()

            self.skip_spaces() 

        symbol.position = self.position
        symbol.line_number = self.line_number

        if self.current_character.isalpha():  # name
            name_string = self.get_name()

            if name_string in self.keywords_list: # name is a keyword
                symbol.type = self.KEYWORD

            else:
                symbol.type = self.NAME # name is a user-defined name
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit():  # number
            symbol.id = self.get_number()
            symbol.type = self.NUMBER

        elif self.current_character == ";": # end of executable
            symbol.type = self.SEMICOLON
            self.advance()

        elif self.current_character == ">":  # signal>signal
            symbol.type = self.ARROW
            self.advance()

        elif self.current_character == ",": # used for listing
            symbol.type = self.COMMA
            self.advance()

        elif self.current_character == ":": # decive type
            symbol.type = self.COLON
            self.advance()
        
        elif self.current_character == ".": # decive type
            symbol.type = self.DOT
            self.advance()

        elif self.current_character == "":  # end of file
            symbol.type = self.EOF
            self.FILE.close()

        else:  # not a valid character
            self.advance()
        
        return symbol

    def get_name(self):
        """Seek the next name string in input_file.
        Return the name string (or None) and the next non-alphanumeric character.
        """
        name_str = ''

        while len(self.current_character) > 0 and self.current_character.isalnum():
            name_str += self.current_character
            self.advance()

        return name_str

    def get_number(self):
        """Seek the next number in input_file.

        Return the number (or None) and the next non-numeric character.
        """
        num_str = ''

        while self.current_character.isdigit():
            num_str += self.current_character
            self.advance()

        return int(num_str)
    
    def advance(self):
        """Move to next character."""
        # sets the current character and moves on to next character
        self.position += 1
        self.current_character = self.FILE.read(1)

    def skip_spaces(self):
        """Skip whitespace characters."""
        # skip whise cpaces and tabs until non white space or tab
        while self.current_character in [" ", "\t"]:
            print("here is a space")
            self.advance()
            # tab is 4 spaces, 1 pos is added in advance, 3 more added here
            if self.current_character == "\t":
                self.position += 3
    
    def print_error(self, symbol):
        "Print an error message with the symbol's line number and position."
        # dictionary of lines
        lines = self.FILE.readlines()
        if 1 <= symbol.line_number <= len(lines):
            print(lines[symbol.line_number - 1])  # line_number is 1-based
            print(" " * (symbol.position - 1), "^") # caret
        else:
            print("Line number out of range.")
        
          