from typing import Generic, TypeVar

T = TypeVar('T')

def _generate_ref_comp(comp_type: str):
    def comp(self: "Reference[T]", obj: object) -> bool:
        if not isinstance(obj, Reference):
            return NotImplemented
        
        return getattr(self.value, comp_type)(obj.value)
    
    return comp

class Reference(Generic[T]):
    """
    Store a value as a reference type.
    This is intended to be used for types like 
    :class:`int` or :class:`float` that are passed by value.

    Two references can be compared using common operators like `==` or `>`
    if and only if the types they implement can be compared like that.
    The references will then compare their own type.

    .. note::
        Use the `is` operator to check if two reference objects are identical.
    """
    __slots__ = ("value", )

    def __init__(self, value: T, /):
        self.value = value
    
    __eq__ = _generate_ref_comp("__eq__") # type: ignore
    __ne__ = _generate_ref_comp("__ne__") # type: ignore
    __lt__ = _generate_ref_comp("__lt__")
    __le__ = _generate_ref_comp("__le__")
    __gt__ = _generate_ref_comp("__gt__")
    __ge__ = _generate_ref_comp("__ge__")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value!r})"