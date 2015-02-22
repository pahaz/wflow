from abc import ABCMeta
import collections

__author__ = 'pahaz'


def make_ABCMeta_metaclass_which_store_class_brothers():
    """Create the new ABCMeta metaclass which store the own instances
    (classes).

    :return: metaclass
    """
    class ABCMetaWhichStoreClassBrothers(ABCMeta):
        class_brothers = collections.deque()
        def __init__(cls, what, bases=None, dict=None):
            ABCMetaWhichStoreClassBrothers.class_brothers.appendleft(cls)
            super(ABCMetaWhichStoreClassBrothers, cls).__init__(what, bases, dict)
    return ABCMetaWhichStoreClassBrothers
