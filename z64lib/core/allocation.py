class MemoryAllocator:
    """
    Reserves memory and assigns offsets from the given buffer.

    Attributes
    ----------
    addr: int
        ...
    entries: list[tuple[int, object]]
        ...

    Parameters
    ----------
    start: int
        ...
    """
    def __init__(self, start: int = 0x10):
        self.addr: int = start
        self.entries: list[tuple[int, object]] = []

    def _align_mem(self, value: int, alignment: int):
        return (value + (alignment - 1)) & ~(alignment - 1)

    def reserve_mem(self, obj: object, size: int, alignment: int = 0x10, aligned: bool = False):
        if not aligned:
            self.addr = self._align_mem(self.addr, alignment)

        obj._address = self.addr
        self.entries.append((self.addr, obj))
        self.addr += size

        return obj._address