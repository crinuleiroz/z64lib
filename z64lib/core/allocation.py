import hashlib
from typing import overload
from z64lib.types import *


class MemoryAllocator:
    """
    Reserves memory and assigns offsets from the given buffer.

    Attributes
    ----------
    address: int
        ...
    entries: list[tuple[int, object]]
        ...

    Parameters
    ----------
    start: int
        ...
    """
    class Block:
        __slots__ = ('address', 'size', 'obj', 'data', 'hash')

        def __init__(self, address: int, size: int, obj=None, data=None):
            self.address = address
            self.size = size
            self.obj = obj
            self.data = data
            self.hash = None

        def get_bytes(self):
            if self.obj is not None:
                return self.obj.to_bytes()
            return self.data or b'\x00' * self.size

        def compute_hash(self):
            self.hash = hashlib.sha256(self.get_bytes()).hexdigest()
            return self.hash

    def __init__(self, start: int = 0x10):
        self.address: int = start
        self.blocks: list[MemoryAllocator.Block] = []
        self.dedupe_registry = {}

    #region Allocation
    def _check_overlap(self, start: int, size: int):
        end = start + size
        for blk in self.blocks:
            blk_end = blk.address + blk.size
            if not (end <= blk.address or start >= blk_end):
                raise ValueError(f"Memory overlap detected at {start:#x}-{end:#x} overlaps {blk.address:#x}-{blk_end:#x}")

    def reserve_at(self, address: int, size: int, obj=None, data=None, deduplicate=True):
        block_bytes = obj.to_bytes() if obj else data or b'\x00' * size
        block_hash = hashlib.sha256(block_bytes).hexdigest() if deduplicate else None
        if deduplicate and block_hash in self.dedupe_registry:
            existing_block = self.dedupe_registry[block_hash]
            if obj:
                setattr(obj, 'allocated_address', existing_block.address)
            return existing_block.address

        self._check_overlap(address, size)

        block = MemoryAllocator.Block(address, size, obj=obj, data=data)
        block.hash = block_hash
        self.blocks.append(block)
        if block_hash:
            self.dedupe_registry[block_hash] = block

        if obj is not None:
            setattr(obj, 'allocated_address', address)

        self.address = max(self.address, address + size)
        return address

    def reserve_mem(self, obj, size: int, alignment: int = 0x10, aligned: bool = False):
        """"""
        if not aligned:
            self.address = self.align_to(self.address, alignment)
        return self.reserve_at(self.address, size, obj=obj)

    def malloc(self, size: int, data: bytes = None, alignment: int = 0x10) -> int:
        """"""
        addr = self.align_to(self.address, alignment)
        return self.reserve_at(addr, size, data=data)
    #endregion

    #region Read and Write
    def read(self, address: int, size: int):
        for blk in self.blocks:
            if blk.address == address:
                if size > blk.size:
                    raise ValueError("Read exceeds block size")
                return blk.get_bytes()[:size]
        raise ValueError("Invalid address")

    def write(self, address: int, data: bytes):
        for blk in self.blocks:
            if blk.address == address:
                if len(data) > blk.size:
                    raise ValueError("Write exceeds block size")
                blk.data = data
                return
        raise ValueError("Invalid address")
    #endregion

    #region Assembly
    def assemble(self, pad_alignment: int = 0x10, auto_patch_pointer: bool = True) -> bytes:
        """"""
        if not self.blocks:
            return b''

        self.blocks.sort(key=lambda b: b.address)

        if auto_patch_pointer:
            for blk in self.blocks:
                if blk.obj is None:
                    continue

                for field_name in getattr(blk.obj, '_fields_', []):
                    attr = getattr(blk.obj, field_name[0], None)
                    if getattr(attr, 'is_pointer', False):
                        setattr(
                            attr,
                            'target_address',
                            getattr(attr.reference, 'allocated_address', 0)
                        )

                blk.data = blk.obj.to_bytes()

        end = self.align_to(self.blocks[-1].address + self.blocks[-1].size, pad_alignment)
        buffer = bytearray(end)

        for blk in self.blocks:
            data = blk.get_bytes()
            if len(data) != blk.size:
                data = data.ljust(blk.size, b'\x00')

            buffer[blk.address:blk.address + blk.size] = data

        return bytes(buffer)
    #endregion

    #region Helpers
    def align_to(self, value: int, alignment: int):
        """"""
        return (value + (alignment - 1)) & ~(alignment - 1)
    #endregion


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
    def read(self, offset: int, T: u8) -> u8: ...
    @overload
    def read(self, offset: int, T: s8) -> s8: ...
    @overload
    def read(self, offset: int, T: u16) -> u16: ...
    @overload
    def read(self, offset: int, T: s16) -> s16: ...
    @overload
    def read(self, offset: int, T: u32) -> u32: ...
    @overload
    def read(self, offset: int, T: s32) -> s32: ...
    @overload
    def read(self, offset: int, T: u64) -> u64: ...
    @overload
    def read(self, offset: int, T: s64) -> s64: ...
    @overload
    def read(self, offset: int, T: f32) -> f32: ...
    @overload
    def read(self, offset: int, T: f64) -> f64: ...
    @overload
    def read(self, offset: int, T: bitfield, *, bools: set[str] | None = None, enums: dict[str, type] | None = None) -> bitfield: ...
    @overload
    def read(self, offset: int, T: union) -> union: ...
    @overload
    def read(self, offset: int, T: array, *, length: int = 0, deref_ptrs: bool = True) -> array: ...
    @overload
    def read(self, offset: int, T: Z64Struct, *, deref_ptrs: bool = True) -> Z64Struct: ...
    @overload
    def read(self, offset: int, T: DynaStruct, *, deref_ptrs: bool = True) -> DynaStruct: ...
    @overload
    def read(self, offset: int, T: pointer, *, is_nullable: bool = True, deref_ptrs: bool = True, resolve_all: bool = True) -> pointer | DataType: ...
    # Implementation
    def read(self, offset: int, T, *, bools=None, enums=None, length=0, is_nullable=True, deref_ptrs=True, resolve_all=True, size=None):
        if T is bytes:
            return self.read_bytes(offset, size)
        elif getattr(T, 'is_primitive', False):
            return self.read_primitive(offset, T)
        elif getattr(T, 'is_bitfield', False):
            return self.read_bitfield(offset, T, bools=bools, enums=enums)
        elif getattr(T, 'is_union', False):
            return self.read_union(offset, T)
        elif getattr(T, 'is_array', False):
            return self.read_array(offset, T, length=length, deref_ptrs=deref_ptrs)
        elif getattr(T, 'is_struct', False):
            return self.read_struct(offset, T, deref_ptrs=deref_ptrs)
        elif getattr(T, 'is_pointer', False):
            return self.read_pointer(offset, T, is_nullable=is_nullable, deref_ptrs=deref_ptrs, resolve_all=resolve_all)
        else:
            raise TypeError(f"Cannot read object of type {type(T)}")

    @overload
    def read_at_pos(self, T: bytes, *, size: int) -> bytes: ...
    @overload
    def read_at_pos(self, T: u8) -> u8: ...
    @overload
    def read_at_pos(self, T: s8) -> s8: ...
    @overload
    def read_at_pos(self, T: u16) -> u16: ...
    @overload
    def read_at_pos(self, T: s16) -> s16: ...
    @overload
    def read_at_pos(self, T: u32) -> u32: ...
    @overload
    def read_at_pos(self, T: s32) -> s32: ...
    @overload
    def read_at_pos(self, T: u64) -> u64: ...
    @overload
    def read_at_pos(self, T: s64) -> s64: ...
    @overload
    def read_at_pos(self, T: f32) -> f32: ...
    @overload
    def read_at_pos(self, T: f64) -> f64: ...
    @overload
    def read_at_pos(self, T: bitfield, *, bools: set[str] | None = None, enums: dict[str, type] | None = None) -> bitfield: ...
    @overload
    def read_at_pos(self, T: union) -> union: ...
    @overload
    def read_at_pos(self, T: array, *, length: int = 0, deref_ptrs: bool = True) -> array: ...
    @overload
    def read_at_pos(self, T: Z64Struct, *, deref_ptrs: bool = True) -> Z64Struct: ...
    @overload
    def read_at_pos(self, T: DynaStruct, *, deref_ptrs: bool = True) -> DynaStruct: ...
    @overload
    def read_at_pos(self, T: pointer, *, is_nullable: bool = True, deref_ptrs: bool = True, resolve_all: bool = True) -> pointer | DataType: ...
    # Implementation
    def read_at_pos(self, T, *, bools=None, enums=None, length=0, is_nullable=True, deref_ptrs=True, resolve_all=True, size=None):
        if T is bytes:
            r = self.read_bytes(self.pos, size)
            self.pos += size
        elif getattr(T, 'is_primitive', False):
            r = self.read_primitive(self.pos, T)
            self.pos += T.size()
        elif getattr(T, 'is_bitfield', False):
            r = self.read_bitfield(self.pos, T, bools=bools, enums=enums)
            self.pos += T.size()
        elif getattr(T, 'is_union', False):
            r = self.read_union(self.pos, T)
            self.pos += T.size()
        elif getattr(T, 'is_array', False):
            r = self.read_array(self.pos, T, length=length, deref_ptrs=deref_ptrs)
            self.pos += T.size()
        elif getattr(T, 'is_struct', False):
            r = self.read_struct(self.pos, T, deref_ptrs=deref_ptrs)
            self.pos += T.size()
        elif getattr(T, 'is_pointer', False):
            r = self.read_pointer(self.pos, T, is_nullable=is_nullable, deref_ptrs=deref_ptrs, resolve_all=resolve_all)
            self.pos += T.size()
        else:
            raise TypeError(f"Cannot read object of type {type(T)}")

        return r

    # Raw Bytes
    def read_bytes(self, offset: int, size: int) -> bytes:
        """"""
        self._ensure_range(offset, size)
        return self.buffer[offset:offset + size]

    # Primitives
    def read_primitive(self, offset: int, T: u8 | s8 | u16 | s16 | u32 | s32 | u64 | s64 | f32 | f64 | DataType) -> u8 | s8 | u16 | s16 | u32 | s32 | u64 | s64 | f32 | f64 | DataType:
        """"""
        if not issubclass(T, DataType):
            raise TypeError(f"Expected primitive DataType for T, got {T}")
        return T.from_bytes(self.buffer, offset)

    # Composites
    def read_bitfield(self, offset: int, T: bitfield, bools: set[str] = None, enums: dict[str, type] = None) -> bitfield:
        """
        Parameters
        ----------
        T: bitfield[DataType, list[tuple(str, int)]]
            ...
        """
        return T.from_bytes(self.buffer, offset, bools, enums)

    def read_union(self, offset: int, T) -> union:
        """
        Parameters
        ----------
        T: union[int, list[tuple(str, DataType)]]
            ...
        """
        return T.from_bytes(self.buffer, offset)

    def read_array(self, offset: int, T: array, length: int = 0, deref_ptrs: bool = True) -> array:
        """
        Parameters
        ----------
        T: array[DataType, int]
            ...
        """
        return T.from_bytes(self.buffer, offset, length=length, deref_ptrs=deref_ptrs)

    def read_struct(self, offset: int, T: Z64Struct | DynaStruct, deref_ptrs: bool = True) -> Z64Struct | DynaStruct:
        """
        Parameters
        ----------
        T: Z64Struct | DynaStruct
            ...
        """
        return T.from_bytes(self.buffer, offset, deref_ptrs)

    # References
    def read_pointer(self, offset: int, T: DataType, is_nullable: bool = True, deref_ptrs: bool = True, resolve_all: bool = True) -> pointer | DataType:
        """
        Parameters
        ----------
        T: pointer[type, int]
            ...
        """
        ptr = T.from_bytes(self.buffer, offset, is_nullable)
        if deref_ptrs:
            return ptr.dereference(self.buffer, resolve_all)
        return ptr
    #endregion

    #region Write
    @overload
    def write(self, offset: int, raw: bytes | bytearray) -> None: ...
    @overload
    def write(self, offset: int, obj: u8) -> None: ...
    @overload
    def write(self, offset: int, obj: s8) -> None: ...
    @overload
    def write(self, offset: int, obj: u16) -> None: ...
    @overload
    def write(self, offset: int, obj: s16) -> None: ...
    @overload
    def write(self, offset: int, obj: u32) -> None: ...
    @overload
    def write(self, offset: int, obj: s32) -> None: ...
    @overload
    def write(self, offset: int, obj: u64) -> None: ...
    @overload
    def write(self, offset: int, obj: s64) -> None: ...
    @overload
    def write(self, offset: int, obj: f32) -> None: ...
    @overload
    def write(self, offset: int, obj: f64) -> None: ...
    @overload
    def write(self, offset: int, obj: bitfield, bools: set[str] = None, enums: dict[str, type] = None) -> None: ...
    @overload
    def write(self, offset: int, obj: union) -> None: ...
    @overload
    def write(self, offset: int, obj: array) -> None: ...
    @overload
    def write(self, offset: int, obj: Z64Struct) -> None: ...
    @overload
    def write(self, offset: int, obj: DynaStruct) -> None: ...
    @overload
    def write(self, offset: int, obj: pointer, target_obj: DataType = None) -> None: ...
    # Implementation
    def write(self, offset: int, obj, *, bools=None, enums=None, target_obj=None) -> None:
        """"""
        if isinstance(obj, (bytes, bytearray)):
            self.write_bytes(offset, obj)
        elif getattr(obj, 'is_primitive', False):
            self.write_primitive(offset, obj)
        elif getattr(obj, 'is_bitfield', False):
            self.write_bitfield(offset, obj, bools=bools, enums=enums)
        elif getattr(obj, 'is_union', False):
            self.write_union(offset, obj)
        elif getattr(obj, 'is_array', False):
            self.write_array(offset, obj)
        elif getattr(obj, 'is_struct', False):
            self.write_struct(offset, obj)
        elif getattr(obj, 'is_pointer', False):
            self.write_pointer(offset, obj, target_obj=target_obj)
        else:
            raise TypeError(f"Cannot write object of type {type(obj)}")

    @overload
    def write_at_pos(self, raw: bytes | bytearray) -> None: ...
    @overload
    def write_at_pos(self, obj: u8) -> None: ...
    @overload
    def write_at_pos(self, obj: s8) -> None: ...
    @overload
    def write_at_pos(self, obj: u16) -> None: ...
    @overload
    def write_at_pos(self, obj: s16) -> None: ...
    @overload
    def write_at_pos(self, obj: u32) -> None: ...
    @overload
    def write_at_pos(self, obj: s32) -> None: ...
    @overload
    def write_at_pos(self, obj: u64) -> None: ...
    @overload
    def write_at_pos(self, obj: s64) -> None: ...
    @overload
    def write_at_pos(self, obj: f32) -> None: ...
    @overload
    def write_at_pos(self, obj: f64) -> None: ...
    @overload
    def write_at_pos(self, obj: bitfield, bools: set[str] = None, enums: dict[str, type] = None) -> None: ...
    @overload
    def write_at_pos(self, obj: union) -> None: ...
    @overload
    def write_at_pos(self, obj: array) -> None: ...
    @overload
    def write_at_pos(self, obj: Z64Struct) -> None: ...
    @overload
    def write_at_pos(self, obj: DynaStruct) -> None: ...
    @overload
    def write_at_pos(self, obj: pointer, target_obj: DataType = None) -> None: ...
    # Implementation
    def write_at_pos(self, obj, *, bools=None, enums=None, target_obj=None) -> None:
        """"""
        if isinstance(obj, (bytes, bytearray)):
            d = self.write_bytes(self.pos, obj)
        elif getattr(obj, 'is_primitive', False):
            d = self.write_primitive(self.pos, obj)
        elif getattr(obj, 'is_bitfield', False):
            d = self.write_bitfield(self.pos, obj, bools=bools, enums=enums)
        elif getattr(obj, 'is_union', False):
            d = self.write_union(self.pos, obj)
        elif getattr(obj, 'is_array', False):
            d = self.write_array(self.pos, obj)
        elif getattr(obj, 'is_struct', False):
            d = self.write_struct(self.pos, obj)
        elif getattr(obj, 'is_pointer', False):
            d = self.write_pointer(self.pos, obj, target_obj=target_obj)
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

    # Primitives
    def write_primitive(self, offset: int, obj: u8 | s8 | u16 | s16 | u32 | s32 | u64 | s64 | f32 | f64 | DataType):
        """"""
        if isinstance(obj, (int, float)) and not isinstance(obj, DataType):
            raise TypeError(f"Expected primitive DataType, got {type(obj)}")
        b = obj.__class__.to_bytes(obj)
        self.write_to_buffer(offset, b)
        return len(b) # Return for write_at_pos()

    # Composites
    def write_bitfield(self, offset: int, obj: bitfield | DataType, bools: set[str] = None, enums: dict[str, type] = None):
        """"""
        if not getattr(obj, 'is_bitfield', False):
            raise TypeError(f"Expected bitfield[], got {type(obj)}")
        b = obj.to_bytes(bools=bools, enums=enums)
        self.write_to_buffer(offset, b)
        return len(b) # Return for write_at_pos()

    def write_union(self, offset: int, obj: union | DataType) -> None:
        """"""
        if not getattr(obj, 'is_union', False):
            raise TypeError(f"Expected union[], got {type(obj)}")
        b = obj.to_bytes()
        self.write_to_buffer(offset, b)
        return len(b) # Return for write_at_pos()

    def write_array(self, offset: int, obj: array | DataType) -> None:
        """"""
        if not getattr(obj, 'is_array', False):
            raise TypeError(f"Expected array[], got {type(obj)}")
        b = obj.to_bytes()
        self.write_to_buffer(offset, b)
        return len(b) # Return for write_at_pos()

    def write_struct(self, offset: int, obj: Z64Struct | DynaStruct | DataType) -> None:
        """"""
        if not getattr(obj, 'is_struct', False):
            raise TypeError(f"Expected struct, got {type(obj)}")
        b = obj.to_bytes()
        self.write_to_buffer(offset, b)
        return len(b) # Return for write_at_pos()

    def write_pointer(self, offset: int, obj: pointer | DataType, target_obj: DataType = None) -> None:
        """"""
        if not getattr(obj, 'is_pointer', False):
            raise TypeError(f"Expected pointer[], got {type(obj)}")

        if target_obj and isinstance(target_obj, DataType):
            target_address = getattr(target_obj, 'allocated_address', None)
            if target_address is None:
                target_address = getattr(target_obj, 'original_address', None)
            if target_address is None:
                raise ValueError("Target object not placed in memory")

            obj.reference = target_obj # Update the pointer reference

        b = obj.to_bytes()
        self.write_to_buffer(offset, b)
        return len(b) # Return for write_at_pos()
    #endregion


__all__ = [
    'MemoryAllocator',
    'MemoryStream',
]