import functools

__all__ = ['MissingRequirement', 'inventory', 'segments', 'concepts', 'requires']


class MissingRequirement(ValueError):
    pass


def inventory(language):
    """
    Make sure a language has a precomputed sound inventory.
    """
    try:
        return bool(len(language.sound_inventory))
    except (AttributeError, TypeError):
        return False


def segments(language):
    """
    Make sure a language has segmented forms.
    """
    try:
        return bool(len(language.segmented_forms))
    except (AttributeError, TypeError):
        return False


def concepts(language):
    """
    Make sure a language has forms linked to concepts, i.e. senses with Concepticon mapping.
    """
    try:
        return bool(len(language.concepts))
    except (AttributeError, TypeError):
        return False


def requires(*what):
    """
    Decorator to specify requirements of a feature callable.

    .. code-block: python

        @requires(segments)
        def count_tokens(language):
            return 5
    """
    def decorator_requires(func):
        func.requires = what

        @functools.wraps(func)
        def wrapper_requires(*args):
            language = args[-1]
            status = [(req.__name__, req(language)) for req in what]
            if not all([s[1] for s in status]):
                raise MissingRequirement(' '.join(s[0] for s in status if not s[1]))
            return func(*args)
        return wrapper_requires
    return decorator_requires
