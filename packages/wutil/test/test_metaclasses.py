import unittest
from abc import abstractmethod

from wutil.metaclasses import make_ABCMeta_metaclass_which_store_class_brothers
from wutil.test import BaseTestCase
from wutil._six import add_metaclass


__author__ = 'pahaz'


class MetaClassTest(BaseTestCase):
    def test_make_ABCMeta_metaclass_which_store_class_brothers(self):
        ABCMeta = make_ABCMeta_metaclass_which_store_class_brothers()

        @add_metaclass(ABCMeta)
        class Z(object):
            pass

        z = Z()

        self.assertIs(ABCMeta.class_brothers[0], Z)
        self.assertIs(Z.class_brothers[0], Z)

    def test_make_ABCMeta_metaclass_which_store_class_brothers_check_abc(self):
        ABCMeta = make_ABCMeta_metaclass_which_store_class_brothers()

        @add_metaclass(ABCMeta)
        class Z(object):
            @abstractmethod
            def foo(self):
                return 1

        with self.assertRaises(TypeError):
            z = Z()

        class ZZ(Z):
            def foo(self):
                return super(ZZ, self).foo()

        z = ZZ()
        self.assertEqual(z.foo(), 1)


    def test_many_class_brothers(self):
        ABCMeta = make_ABCMeta_metaclass_which_store_class_brothers()

        @add_metaclass(ABCMeta)
        class Z1(object):
            @abstractmethod
            def foo(self):
                return 1

        @add_metaclass(ABCMeta)
        class Z2(object):
            @abstractmethod
            def foo(self):
                return 1

        class ZZ1(Z1):
            def foo(self):
                return 9

        class ZZ2(Z2):
            def foo(self):
                return 9

        z1 = ZZ1()
        z2 = ZZ2()

        self.assertEqual(Z1.class_brothers, ZZ2.class_brothers)
        self.assertEqual(set(ZZ2.class_brothers), {Z1, Z2, ZZ1, ZZ2})

    def test_abstractclassmethod(self):
        ABCMeta = make_ABCMeta_metaclass_which_store_class_brothers()

        @add_metaclass(ABCMeta)
        class Z1(object):
            @classmethod
            @abstractmethod
            def bar(cls):
                return False
            @abstractmethod
            def foo(self):
                return 1

        class XXX(Z1):
            @classmethod
            def bar(cls):
                return True
            def foo(self):
                pass

        for X in XXX.class_brothers:
            X.bar()

        with self.assertRaises(TypeError):
            for X in XXX.class_brothers:
                X().bar()

    def test_instance_order(self):
        ABCMeta = make_ABCMeta_metaclass_which_store_class_brothers()

        @add_metaclass(ABCMeta)
        class Interface(object):
            @classmethod
            @abstractmethod
            def bar(cls):
                return False
            @abstractmethod
            def foo(self):
                return 1

        class Z1(Interface):
            def bar(cls):
                return 1
            def foo(self):
                return 1

        self.assertEqual(Interface.class_brothers[0], Z1)
        self.assertEqual(len(Interface.class_brothers), 2)
        self.assertEqual(Interface.class_brothers[1], Interface)
