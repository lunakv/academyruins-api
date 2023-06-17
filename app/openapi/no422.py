_no422_attribute_tag = "_remove_422_tag_"


def no422(func):
    """
    Decorator tag to remove 422 response from the API docs (because sometimes it just doesn't make sense)
    """
    setattr(func, _no422_attribute_tag, True)
    return func


def is_marked_no422(func):
    """
    Check whether a function was annotated with @no422
    """
    return getattr(func, _no422_attribute_tag, False)
