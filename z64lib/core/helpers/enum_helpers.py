"""
Enum Helpers
=====
"""
def safe_enum(enum_cls, value: int):
    """
    Safely converts `value` to `enum_cls`

    Args:
        enum_cls (Class): The enum class.
        value (int): The value to convert.
    """
    try:
        return enum_cls(value)
    except ValueError as e:
        raise ValueError(f'Invalid value {value} for enum {enum_cls.__name__}')