import inspect


def align_to(offset: int, align: int) -> int:
    """ Align the offset to the next multiple of `align`. """
    if align == 0:
        return offset
    return (offset + align - 1) & ~(align - 1) # (offset + align - 1) // align * align


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