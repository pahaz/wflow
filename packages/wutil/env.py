from __future__ import unicode_literals, print_function, generators, division
from copy import deepcopy
import collections

from wutil.mixin import AttributeImmutableMixin

__author__ = 'pahaz'


def is_hashable_type(t):
    try:
        hash(t)
    except TypeError:
        return False
    return True


class EnvStackLayer(collections.Mapping, AttributeImmutableMixin):
    def __init__(self, dict_):
        for k, v in dict_.items():
            if not is_hashable_type(v):
                raise TypeError('EnvStackLayer object does`t support '
                                'unhashable value: {0}'.format(v))
        self.__dict__['_secret'] = deepcopy(dict_)

    def as_dict(self):
        return deepcopy(self._secret)

    # Mapping

    def __getitem__(self, key):
        return self._secret[key]

    def __iter__(self):
        return iter(self._secret)

    def __len__(self):
        return len(self._secret)
