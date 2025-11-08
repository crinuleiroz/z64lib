from enum import IntEnum


class VersionedIntEnum(IntEnum):
    def __new__(cls, value, version=2):
        # Determine the actual integer value
        if isinstance(value, int):
            int_value = value
        elif isinstance(value, tuple):
            # If tuple of tuples, take the first element of the first tuple
            if isinstance(value[0], tuple):
                int_value = value[0][0]
            else:
                int_value = value[0]
        else:
            raise TypeError(f"Unsupported value type {type(value)}")

        obj = int.__new__(cls, int_value)
        obj._value_ = value  # store original value (int, tuple, or tuple-of-tuples)
        obj.version = version
        return obj

    @classmethod
    def for_version(cls, value, version):
        for member in cls:
            # handle tuple-of-tuples
            vals = member.value
            if isinstance(vals[0], tuple) and isinstance(vals[0][0], int):
                if isinstance(vals[0], tuple) and isinstance(vals[0][0], int):
                    # tuple-of-tuples
                    for val, ver in vals:
                        if val == value and (ver == version or ver == 2):
                            return member
                else:
                    val, ver = vals
                    if val == value and (ver == version or ver == 2):
                        return member
            else:
                if vals == value:
                    return member
        raise ValueError(f"No member for value {value} and version {version}")