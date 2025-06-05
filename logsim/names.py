"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""


class Names:
    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    unique_error_codes(self, num_error_codes): Returns a list of unique integer
                                               error codes.

    query(self, name_string): Returns the corresponding name ID for the
                        name string. Returns None if the string is not present.

    lookup(self, name_string_list): Returns a list of name IDs for each
                        name string. Adds a name if not already present.

    get_name_string(self, name_id): Returns the corresponding name string for
                        the name ID. Returns None if the ID is not present.
    """

    def __init__(self):
        """Initialise names list."""
        self.error_code_count = 0  # how many error codes have been declared

        # hash map where IDs are keys and name strings are values
        self.id_names = {}

        # hash map where name strings are keys and IDs are values
        self.names_id = {}

        # number of names stored
        self.num_items = 0

    def unique_error_codes(self, num_error_codes):
        """Return a list of unique integer error codes."""
        if not isinstance(num_error_codes, int):
            raise TypeError("Expected num_error_codes to be an integer.")
        self.error_code_count += num_error_codes
        return range(self.error_code_count - num_error_codes,
                     self.error_code_count)

    def query(self, name_string):
        """Return the corresponding name ID for name_string.

        If the name string is not present in the names list, return None.
        """
        # checks if name_string is in names dictionary
        # names_string doesn't exist so returns None
        # found the device so returns the ID
        return self.names_id.get(name_string, None)

    def lookup(self, name_string_list):
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.
        """
        # create list for name ids
        names_id_list = []

        # loop for names in names list
        for name_string in name_string_list:
            name_id = self.query(name_string)

            # check if name has an id
            if name_id is None:
                name_id = self.num_items
                self.id_names[self.num_items] = name_string
                self.names_id[name_string] = self.num_items
                self.num_items += 1

            # add name id to list
            names_id_list.append(name_id)

        return names_id_list

    def get_name_string(self, name_id):
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.
        """
        # checks if name_id is in id dictionary
        # names_id doesn't exist so returns None
        # found the device so returns the ID
        return self.id_names.get(name_id, None)
