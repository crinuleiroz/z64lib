"""
Class Helpers
=====
"""
def make_property(raw_attr_name, transform):
    def getter(self):
        return transform(getattr(self, f"_{raw_attr_name}_raw"))

    def setter(self, value):
        setattr(self, f'_{raw_attr_name}_raw', value)

    return property(getter, setter)