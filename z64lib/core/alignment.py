def align_to(offset: int, align: int) -> int:
    """ Align the offset to the next multiple of `align`. """
    if align == 0:
        return offset
    return (offset + align - 1) & ~(align - 1) # (offset + align - 1) // align * align


def natural_alignment(field_type) -> int:
    """ Returns the natural alignment for a field type. """

    # Avoid circular import issues
    import inspect
    from z64lib.core.types import pointer, array, bitfield, Z64Struct

    # if isinstance(field_type, pointer):
    #     return 4

    if isinstance(field_type, array):
        return natural_alignment(field_type.field_type)

    # if isinstance(field_type, bitfield):
    #     return natural_alignment(field_type.field_type)

    if inspect.isclass(field_type) and issubclass(field_type, Z64Struct):
        return max((natural_alignment(f[1]) for f in field_type._fields_), default=1)

    return getattr(field_type, "size", 1)


def align_field(offset: int, field_type) -> int:
    """ Return the offset aligned for this field type. """
    return align_to(offset, natural_alignment(field_type))


def walk_fields(fields, callback, start_offset: int = 0) -> int:
    """
    Walks through the fields of a struct, calling `callback` for each field.

    Parameters
    ----------
    fields: list
        List of struct field definitions (_fields_).
    callback: Callable[[name, field_type, offset, extra], int]
        Function called for each field. Must return the new offset after processing.
    start_offset: int
        Starting offset.

    Returns
    ----------
    int
        Final offset after processing all fields.
    """
    offset = start_offset
    bit_cursor = 0
    last_bitfield_type = None

    for field in fields:
        match len(field):
            # Primitive, pointer, or array
            case 2:
                name, field_type = field
                offset = align_field(offset, field_type)
                offset = callback(name, field_type, offset, None)
                bit_cursor = 0
                last_bitfield_type = None

            # Bitfields
            case 3:
                name, container_or_type, subfields = field
                # Grouped bitfields
                if isinstance(subfields, list):
                    base_type = subfields[0][1]
                    offset = align_field(offset, base_type)
                    offset = callback(name, container_or_type, offset, subfields)
                    bit_cursor = 0
                    last_bitfield_type = None

                # Single Bitfield
                else:
                    base_type = container_or_type
                    if last_bitfield_type != base_type:
                        bit_cursor = 0
                        last_bitfield_type = base_type
                        offset = align_field(offset, base_type)

                    offset = callback(name, base_type, offset, subfields)
                    bit_cursor += subfields
                    if bit_cursor >= base_type.size * 8:
                        offset += base_type.size
                        bit_cursor = 0
                        last_bitfield_type = None

    return offset