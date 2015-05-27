from __future__ import unicode_literals, print_function, generators, division

__author__ = 'pahaz'


class InvalidateMixin(object):
    _invalid = False
    invalid_object_error = RuntimeError('Invalid object')

    def invalidate(self):
        self._invalid = True

    def __getattribute__(self, attr):
        if attr in ('_invalid', 'invalidate', 'invalid_object_error'):
            return super(InvalidateMixin, self).__getattribute__(attr)
        if self._invalid:
            raise self.invalid_object_error
        return super(InvalidateMixin, self).__getattribute__(attr)

    def __setattr__(self, key, value):
        if key in ('_invalid', 'invalidate', 'invalid_object_error'):
            return super(InvalidateMixin, self).__setattr__(key, value)
        if self._invalid:
            raise self.invalid_object_error
        return super(InvalidateMixin, self).__setattr__(key, value)

    def __delattr__(self, attr):
        if self._invalid:
            raise self.invalid_object_error
        return super(InvalidateMixin, self).__delattr__(attr)


class AttributeImmutableMixin(object):
    def __setattr__(self, key, value):
        raise TypeError('This object does not support __setattr__')

    def __delattr__(self, item):
        raise TypeError('This object does not support __delattr__')
