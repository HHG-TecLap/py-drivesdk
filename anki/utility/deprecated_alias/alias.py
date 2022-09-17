from inspect import getmembers, isfunction
from functools import wraps
from warnings import warn

_DEFAULT_WARNING = "Use of method {0}.{1} is deprecated. Use {0}.{2} instead"

def _universal_alias(alias_name: str, deprecated: bool=False, deprecation_message: str=None):
    def decorator(func):
        if not hasattr(func,"__alias_info__"):
            func.__alias_info__ = []
            pass

        func.__alias_info__.append({
            "name": alias_name,
            "deprecated": deprecated,
            "deprecation_message": deprecation_message
        })
        return func
        pass

    return decorator
    pass

def alias(alias_name: str):
    return _universal_alias(alias_name)
    pass

def deprecated_alias(alias_name: str, deprecation_message: str=None):
    return _universal_alias(alias_name,True,deprecation_message)
    pass


def _generate_deprecation_wrapper(cls,fname, func, alias_name, is_deprecated, deprecation_message):
    # This needed to be exported because of Python variable nonsense (basically, it only used the variables from the last loop iteration)
    @wraps(func)
    def wrapper(*args, **kwargs):
        if is_deprecated:
            warn(
                _DEFAULT_WARNING.format(cls.__name__,alias_name,fname)
                if deprecation_message is None else 
                deprecation_message,
                DeprecationWarning,
                stacklevel=2
            )

        return func(*args,**kwargs)
        pass
    return wrapper
    pass

def alias_class(cls: type):
    for (fname, func) in getmembers(
        cls,
        lambda func: isfunction(func) and hasattr(func,"__alias_info__")
    ):
        for alias in func.__alias_info__:
            alias_name = alias["name"]
            is_deprecated = alias["deprecated"]
            deprecation_message = alias["deprecation_message"]

            setattr(
                cls,
                alias_name,
                _generate_deprecation_wrapper(
                    cls,
                    fname,
                    func,
                    alias_name,
                    is_deprecated,
                    deprecation_message
                )
            )
            pass
        pass

    return cls
    pass