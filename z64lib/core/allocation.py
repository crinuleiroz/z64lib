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
        self.address: int = start
        self.entries: list[tuple[int, object]] = []

    def reserve_mem(self, obj: object, size: int, alignment: int = 0x10, aligned: bool = False):
        if not aligned:
            self.address = self.align_to(self.address, alignment)

        setattr(obj, 'allocated_address', self.address)
        self.entries.append((self.address, obj))
        self.address += size

        return getattr(obj, 'allocated_address')

    #region Helpers
    def align_to(self, value: int, alignment: int):
        return (value + (alignment - 1)) & ~(alignment - 1)
    #endregion