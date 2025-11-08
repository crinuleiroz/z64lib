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