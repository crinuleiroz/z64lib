def walk_fields(fields, callback, start_offset: int = 0) -> int:
    """
    Walks through the fields of a struct, calling `callback` for each field.

    Parameters
    ----------
    fields: list
        List of struct field definitions (_fields_).
    callback: Callable[[name, data_type, offset, extra], int]
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
            # Primitive, pointer, array, or union
            case 2:
                name, data_type = field
                offset = data_type.align_field(offset, data_type)
                offset = callback(name, data_type, offset, None)
                bit_cursor = 0
                last_bitfield_type = None

            # Bitfields
            case 3:
                name, container_or_type, subfields = field

                # Grouped bitfields
                if isinstance(subfields, list):
                    base_type = subfields[0][1]
                    offset = base_type.align_field(offset, base_type)
                    offset = callback(name, container_or_type, offset, subfields)
                    bit_cursor = 0
                    last_bitfield_type = None

                # Single Bitfield
                else:
                    base_type = container_or_type
                    if last_bitfield_type != base_type:
                        bit_cursor = 0
                        last_bitfield_type = base_type
                        offset = base_type.align_field(offset, base_type)

                    offset = callback(name, base_type, offset, subfields)
                    bit_cursor += subfields

                    if bit_cursor >= base_type.size() * 8:
                        offset += base_type.size()
                        bit_cursor = 0
                        last_bitfield_type = None

    return offset