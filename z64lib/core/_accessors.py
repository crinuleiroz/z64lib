class UnionAccessor:
    """ Helper class to provide attribute-style acces to union members. """
    def __init__(self, values: dict, active: str | None = None):
        self._values = values
        self._active = active or list(values.keys())[0]

    def __getattr__(self, name):
        if name in self._values:
            return self._values[name]
        raise AttributeError(f"'UnionAccessor' has no atribute '{name}'")

    def __setattr__(self, name, value):
        if name in ("_values", "_active"):
            super().__setattr__(name, value)
        elif name in self._values:
            self._values[name] = value
            self._active = name
        else:
            raise AttributeError()

    def set_active(self, name: str):
        """ Explicitly mark a union member as active for serialization. """
        if name not in self._values:
            raise ValueError()
        self._active = name

    @property
    def active_field(self) -> str:
        return self._active

    def as_dict(self):
        """ Return all union fields as a dictionary. """
        return self._values

    def __repr__(self):
        return f"<Union {self._values}>"
