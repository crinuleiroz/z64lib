"""
z64lib.core.helpers.bit_helpers
=====
"""
def mask_lsb(bits: int) -> int:
    """
    .. code-block:: c

        (1 << bits) - 1
    """
    return (1 << bits) - 1


def mask_msb(bits: int) -> int:
    """
    .. code-block:: c

        1 << (bits - 1)
    """
    return 1 << (bits - 1)


def left_shift(value: int, bits: int) -> int:
    """
    .. code-block:: c

        value << bits
    """
    return value << bits


def right_shift(value: int, bits: int) -> int:
    """
    .. code-block:: c

        value >> bits
    """
    return value >> bits


def shift_value(value: int, bits: int, direction: str = None):
    """"""
    if direction is None:
        raise ValueError()
    if direction.lower() not in ('left', 'right'):
        raise ValueError()

    if direction.lower() == 'left':
        return value << bits
    if direction.lower() == 'right':
        return value >> bits


def mask_value(value: int, bits: int, side: str = None):
    """"""
    if side is None:
        raise ValueError()
    if side.lower() not in ('high', 'low'):
        raise ValueError()

    if side.lower() == 'high':
        return value & (1 << (bits - 1))
    if side.lower() == 'low':
        return value & ((1 << bits) - 1)


def extract_bits(value: int, offset: int, width: int, total_bits: int = None, signed: bool = False, endian: str = 'big') -> int:
    """"""
    if total_bits is None:
        total_bits = max(value.bit_length(), width + offset)

    if endian.lower() == 'big':
        shift = total_bits - offset - width
    elif endian.lower() == 'little':
        shift = offset
    else:
        raise ValueError("endian must be 'big' or 'little'")

    raw = right_shift(value, shift) & mask_lsb(width)

    if signed and (raw & mask_msb(width)):
        raw -= left_shift(1, width)

    return raw


def insert_bits(old: int, new: int, offset: int, width: int, total_bits: int = None, signed: bool = False, endian: str = 'big') -> int:
    """"""
    if total_bits is None:
        total_bits = max(old.bit_length(), width + offset)

    max_val = mask_lsb(width)
    if signed:
        if new < 0:
            new += left_shift(1, width)
        if new > max_val:
            raise ValueError(f"Value {new} does not fit in {width}-bit signed field")
    else:
        if new < 0 or new > max_val:
            raise ValueError(f"Value {new} does not fit in {width}-bit unsigned field")

    if endian.lower() == 'big':
        shift = total_bits - offset - width
    elif endian.lower() == 'little':
        shift = offset
    else:
        raise ValueError("endian must be 'big' or 'little'")

    mask = left_shift(max_val, shift)

    return (old & ~mask) | (left_shift(new, shift) & mask)


def sign_extend(value: int, n_bits: int) -> int:
    """"""
    sign = mask_msb(n_bits)
    return (value & (sign - 1)) - (value & sign)


__all__ = [
    'mask_lsb',
    'mask_msb',
    'left_shift',
    'right_shift',
    'shift_value',
    'mask_value',
    'extract_bits',
    'insert_bits',
]