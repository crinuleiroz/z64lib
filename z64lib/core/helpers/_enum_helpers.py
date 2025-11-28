"""
Enum Helpers
=====
"""
def safe_enum(enum_cls, value: int):
    """
    Safely converts the given value to its respective enum member in the given enum class.

    Parameters
    ----------
    enum_cls: Class
        The enum class.
    value: int
        Integer value to convert to an enum member.

    Returns
    ----------
    enum_cls(value)
        Returns the respective enum class member.

    Raises
    ----------
    ValueError
        Invalid enum member for the given enum class.
    """
    try:
        return enum_cls(value)
    except ValueError as e:
        raise ValueError(f"Invalid value {value} for enum {enum_cls.__name__}")