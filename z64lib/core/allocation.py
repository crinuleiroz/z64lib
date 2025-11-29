import hashlib


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