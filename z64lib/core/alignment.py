import inspect


def align_to(value: int, alignment: int) -> int:
    """
    Align the given value to the next multiple of `alignment`.

    Parameters
    ----------
    value: int
        The memory address to align.
    alignment: int
        The alignment boundary (must be a power of two for bitwise correctness).

    Returns
    ----------
    int
        The smallest multiple of `alignment` that is greater than or equal to `value`.

    Notes
    ----------
    The implementation uses `(alignment - 1)` to efficiently round up to the next
    alignment boundary. For example:

    >>> align_to(0x23, 0x10)

    This aligns an address of 0x23 (35) to the next 16-byte (0x10) boundary.
    """
    if alignment == 0:
        return value
    return (value + (alignment - 1)) & ~(alignment - 1)


def natural_alignment(field_type) -> int:
    """ Returns the natural alignment for a field type. """

    if hasattr(field_type, 'field_type'):
        return natural_alignment(field_type.field_type)

    if inspect.isclass(field_type) and hasattr(field_type, '_fields_'):
        return max((natural_alignment(f[1]) for f in field_type._fields_), default=1)

    return getattr(field_type, "size", 1)


def align_field(offset: int, field_type) -> int:
    """ Return the offset aligned for this field type. """
    return align_to(offset, natural_alignment(field_type))