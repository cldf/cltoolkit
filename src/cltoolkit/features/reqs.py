"""
Features may have different requirements regarding the kind of data needed to perform the
computation. These requirements can be expressed (and enforced) by decorating the callable
(function or method) using the :func:`cltoolkit.features.requires` decorator, parametrized with
the appropriate callables from the `cltoolkit.features.reqs` module - or any other callable
accepting a :class:`cltoolkit.models.Language` instance as argument, returning `True` if the
requirement is met.
"""
import logging
import functools

__all__ = ['MissingRequirement', 'inventory', 'graphemes', 'concepts', 'requires',
           'inventory_with_occurrences']


class MissingRequirement(ValueError):
    """
    Exception raised by :func:`requires` (before calling the decorated function) when a
    requirement is not met
    """


def inventory(language):
    """
    Make sure a language has a precomputed sound inventory.
    """
    try:
        return bool(len(language.sound_inventory))
    except (AttributeError, TypeError):
        return False


def inventory_with_occurrences(language):
    """
    Make sure a language has a precomputed sound inventory with occurrence lists per sound.
    """
    return inventory(language) and bool(len(language.sound_inventory.sounds[0].occurrences))


def graphemes(language):
    """
    Make sure a language has segmented forms, i.e. lists of graphemes for each form.
    """
    try:
        return bool(len(language.forms_with_graphemes))
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

    .. code-block:: python

        @requires(graphemes)
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
            try:
                return func(*args)
            except:  # noqa: E722
                log = logging.getLogger('cltoolkit')
                log.debug('dataset: {}; language: {}'.format(
                    getattr(language, 'dataset'), language))
                raise
        return wrapper_requires
    return decorator_requires
