"""
Class Helpers
=====
"""
def make_property(raw_attr_name: str, transform):
    """
    Creates a clas property with the given class name.

    Parameters
    ----------
    raw_attr_name: str
        The name for the property.
    transform: Any
        The type of the property.

    Returns
    ----------
    property
        Returns the created class property.
    """
    def getter(self):
        return transform(getattr(self, f"_{raw_attr_name}_raw"))

    def setter(self, value):
        setattr(self, f'_{raw_attr_name}_raw', value)

    return property(getter, setter)