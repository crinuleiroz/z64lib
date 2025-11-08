from enum import IntEnum


class NamedIntEnum(IntEnum):
    """ Enum where members are also (and must be) ints, but print as their names. """
    def __str__(self):
        return self.name

    def describe(self):
        """ Return a (name, value) tuple for convenience. """
        return f"(name={self.name}, value={self.value})"