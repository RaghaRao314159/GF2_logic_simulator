"""Implements a name table for lexical analysis.

Classes
-------
MyNames - implements a name table for lexical analysis.
"""


class MyNames:

    """Implements a name table for lexical analysis.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    lookup(self, name_string): Returns the corresponding name ID for the
                 given name string. Adds the name if not already present.

    get_string(self, name_id): Returns the corresponding name string for the
                 given name ID. Returns None if the ID is not a valid index.
    """

    def __init__(self):
        """Initialise the names list."""
        self.id_names = {}
        self.names_id = {}
        self.numitems = 0

    def lookup(self, name_string):
        """Return the corresponding name ID for the given name_string.

        If the name string is not present in the names list, add it.
        """
        if self.names_id.get(name_string, -1) == -1:
            self.names_id[name_string] = self.numitems
            self.id_names[self.numitems] = name_string
            self.numitems += 1
        return self.names_id[name_string]
        

    def get_string(self, name_id):
        """Return the corresponding name string for the given name_id.

        If the name ID is not a valid index into the names list, return None.
        """
        if self.id_names.get(name_id, -1) == -1:
            return None
        return self.id_names[name_id]
        
    def get_ids(self):
        return self.id_names
