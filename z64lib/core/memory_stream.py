from z64lib.ultratypes import *


class MemoryStream:
    def __init__(self, buffer: bytearray, *, auto_expand: bool = False):
        self.buffer: bytearray = buffer
        self.pos: int = 0
        self.auto_expand: bool = auto_expand
        self._marks = []

    #region Helpers
    def _ensure_range(self, offset: int, size: int):
        end = offset + size
        if end > len(self.buffer):
            if not self.auto_expand:
                raise ValueError(f"Out of range {offset:#x} - {end:#x}")
            self.buffer.extend(b'\x00' * (end - len(self.buffer)))

    def align(self, alignment: int):
        self.pos = (self.pos + alignment - 1) & ~(alignment - 1)

    def truncate(self, amount: int, side: str = 'end'):
        """
        Remove the specified amount of bytes from the specified side of the buffer.
        If the buffer is not set to auto-expand, the buffer will be cleared if amount is
        greater than the length of the buffer.
        """
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        if amount > len(self.buffer):
            if self.auto_expand:
                self.buffer.extend(b'\x00' * (amount - len(self.buffer)))
            else:
                self.buffer.clear()
                self.pos = 0
                return

        if side == 'start':
            del self.buffer[:amount]
        if side == 'end':
            del self.buffer[-amount:]
        else:
            raise ValueError("Side must be either 'start' or 'end'")

        self.pos = min(self.pos, len(self.buffer))
    #endregion

    #region Cursor
    def seek(self, pos: int):
        """ Moves the position of the cursor in the buffer to the specified offset. """
        self.pos = pos

    def tell(self) -> int:
        """ Returns the current position of the cursor in the buffer. """
        return self.pos

    def forward(self, amount: int):
        """ Moves the position of the cursor in the buffer forward. """
        self.pos += amount
    skip = forward

    def backward(self, amount: int):
        """ Moves the position of the cursor in the buffer backward. """
        self.pos -= amount
    rewind = backward

    def mark(self):
        """ Save the current cursor position to a stack. """
        self._marks.append(self.pos)

    def reset(self):
        """ Reset cursor to the last marked position. """
        if self._marks:
            self.pos = self._marks.pop()

    def peek(self, size: int) -> bytes:
        """ Returns a slice of the buffer at the current cursor without advancing it. """
        self._ensure_range(self.pos, size)
        return self.buffer[self.pos:self.pos + size]
    #endregion

    #region Read
    @overload
    def read(self, offset: int, T: bytes, *, size: int) -> bytes: ...
    @overload
    def read(self, offset: int, T: primitive) -> primitive: ...
    @overload
    def read(self, offset: int, T: bitfield) -> bitfield: ...
    @overload
    def read(self, offset: int, T: union) -> union: ...
    @overload
    def read(self, offset: int, T: array) -> array: ...
    @overload
    def read(self, offset: int, T: structure) -> structure: ...
    @overload
    def read(self, offset: int, T: pointer) -> pointer: ...
    # Implementation
    def read(self, offset: int, T, *, size=None):
        if T is bytes:
            return self.read_bytes(offset, size)
        elif issubclass(T, DataType):
            # For is_dyna() arrays and structs, read
            # past static memory using read_bytes().
            return self.read_object(offset, T)
        else:
            raise TypeError(f"Cannot read object of type {type(T)}")

    @overload
    def read_at_pos(self, T: bytes, *, size: int) -> bytes: ...
    @overload
    def read_at_pos(self, T: primitive) -> primitive: ...
    @overload
    def read_at_pos(self, T: bitfield) -> bitfield: ...
    @overload
    def read_at_pos(self, T: union) -> union: ...
    @overload
    def read_at_pos(self, T: array) -> array: ...
    @overload
    def read_at_pos(self, T: structure) -> structure: ...
    @overload
    def read_at_pos(self, T: pointer) -> pointer: ...
    # Implementation
    def read_at_pos(self, T, *, size=None):
        """"""
        if T is bytes:
            r = self.read_bytes(self.pos, size)
            self.pos += size
        elif issubclass(T, DataType):
            r = self.read_object(self.pos, T)
            # For is_dyna() arrays and structs, read
            # past static memory using read_bytes().
            # T.size_of() only returns static memory
            # size as dyna is runtime dependent.
            self.pos += T.size_of()
        else:
            raise TypeError(f"Cannot read object of type {type(T)}")

        return r

    # Raw Bytes
    def read_bytes(self, offset: int, size: int) -> bytes:
        """"""
        self._ensure_range(offset, size)
        return self.buffer[offset:offset + size]

    def read_object(self, offset: int, T: primitive | bitfield | union | array | structure) -> DataType:
        """"""
        if not issubclass(T, DataType):
            raise TypeError(f"Expected primitive, bitfield, union, array, or structure, got {type(T).__name__}")
        return T.from_bytes(self.buffer, offset)
    #endregion

    #region Write
    @overload
    def write(self, offset: int, raw: bytes | bytearray) -> None: ...
    @overload
    def write(self, offset: int, obj: primitive) -> None: ...
    @overload
    def write(self, offset: int, obj: bitfield) -> None: ...
    @overload
    def write(self, offset: int, obj: union) -> None: ...
    @overload
    def write(self, offset: int, obj: array) -> None: ...
    @overload
    def write(self, offset: int, obj: structure) -> None: ...
    @overload
    def write(self, offset: int, obj: pointer, target_obj: DataType = None) -> None: ...
    # Implementation
    def write(self, offset: int, obj, *, target_obj=None) -> None:
        """"""
        if isinstance(obj, (bytes, bytearray)):
            self.write_bytes(offset, obj)
        if isinstance(obj, DataType):
            if obj.is_pointer():
                self.write_pointer(offset, obj, target_obj=target_obj)
            else:
                # For is_dyna() arrays and structs, write
                # past static memory using write_bytes().
                self.write_object(offset, obj)
        else:
            raise TypeError(f"Cannot write object of type {type(obj)}")

    @overload
    def write_at_pos(self, raw: bytes | bytearray) -> None: ...
    @overload
    def write_at_pos(self, obj: primitive) -> None: ...
    @overload
    def write_at_pos(self, obj: bitfield) -> None: ...
    @overload
    def write_at_pos(self, obj: union) -> None: ...
    @overload
    def write_at_pos(self, obj: array) -> None: ...
    @overload
    def write_at_pos(self, obj: structure) -> None: ...
    @overload
    def write_at_pos(self, obj: pointer, target_obj: DataType = None) -> None: ...
    # Implementation
    def write_at_pos(self, obj, *, target_obj=None) -> None:
        """"""
        if isinstance(obj, (bytes, bytearray)):
            d = self.write_bytes(self.pos, obj)
        elif isinstance(obj, DataType):
            if obj.is_pointer():
                d = self.write_pointer(self.pos, obj, target_obj=target_obj)
            else:
                # For is_dyna() arrays and structs, write
                # past static memory using write_bytes().
                d = self.write_object(self.pos, obj)
        else:
            raise TypeError(f"Cannot write object of type {type(obj)}")

        self.pos += d

    def write_to_buffer(self, offset: int, b: bytes) -> None:
        """"""
        length = len(b)
        self._ensure_range(offset, length)
        self.buffer[offset:offset + length] = b

    # Raw Bytes
    def write_bytes(self, offset: int, value):
        """"""
        if value is None:
            raise TypeError("Cannot write None as bytes")

        if isinstance(value, (bytes, bytearray)):
            b = bytes(value)
        else:
            raise TypeError(f"write_bytes expected bytes or bytearray, got {type(value)}")

        self.write_to_buffer(offset, b)
        return len(b) # Return for write_at_pos()

    # Non-reference Data Types
    def write_object(self, offset: int, obj: primitive | bitfield | union | array | structure | pointer):
        """"""
        if not isinstance(obj, (primitive, bitfield, union, array, structure, pointer)):
            raise TypeError(f"Expected primitive, bitfield, union, array, structure, or pointer, got {type(obj).__name__}")
        b = obj.to_bytes(obj)
        self.write_to_buffer(offset, b)
        return len(b) # Return for write_at_pos()

    # pointer Data Type
    def write_pointer(self, offset: int, obj: pointer | DataType, target_obj: DataType = None) -> None:
        """"""
        if not obj.is_pointer():
            raise TypeError(f"Expected pointer, got {type(obj)}")

        if target_obj and isinstance(target_obj, DataType):
            target_address = getattr(target_obj, 'allocated_address', None)
            if target_address is None:
                target_address = getattr(target_obj, 'original_address', None)
            if target_address is None:
                raise ValueError("Target object not placed in memory")

            obj.reference = target_obj # Update the pointer reference

        return self.write_object(offset, obj) # Return for write_at_pos()
    #endregion