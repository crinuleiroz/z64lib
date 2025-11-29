from ._z64_struct import Z64Struct
from z64lib.types.base import Field
from z64lib.types.markers import *


class DynaStruct(Z64Struct):
    """ Dynamic-sized Zelda64 struct. """
    # Type Flags
    is_struct: bool = True

    # Static/Dynamic Flags
    is_static: bool = True
    is_dyna: bool = False

    def _generate_layout(self) -> list[Field]:
        """"""
        offset = 0
        layout = []

        for name, data_type in self._fields_:
            attr = getattr(self, name, None)
            field, offset = self._describe_field(name, data_type, offset, attr)

            layout.append(field)

        if self._align_ > 1:
            offset = self.align_to(offset, self._align_)

        return layout

    def size(self) -> int:
        """"""
        layout = self._generate_layout()
        if not layout:
            return 0

        size = max(field.offset + field.size for field in layout)

        if self._align_ > 1:
            size = self.align_to(size, self._align_)

        return size