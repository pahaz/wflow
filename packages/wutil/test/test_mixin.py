from __future__ import unicode_literals, print_function, generators, division
from wutil.mixin import InvalidateMixin, AttributeImmutableMixin
from wutil.test import BaseTestCase

__author__ = 'pahaz'


class TestInvalidateMixin(BaseTestCase):
    def test_raise_runtime_error_after_invalidate(self):
        class MyObject(InvalidateMixin):
            pass

        a = MyObject()
        a.invalidate()
        with self.assertRaises(RuntimeError):
            a.qwer

    def test_many_invalidate_call_not_produce_error(self):
        class MyObject(InvalidateMixin):
            pass

        a = MyObject()
        a.invalidate()
        a.invalidate()
        a.invalidate()

    def test_set_and_get_value_on_valid_object(self):
        class MyObject(InvalidateMixin):
            pass

        a = MyObject()
        a.qwe = 2
        self.assertEqual(a.qwe, 2)

    def test_set_value_on_valid_object_raise_error_after_invalidate_call(self):
        class MyObject(InvalidateMixin):
            pass

        a = MyObject()
        a.qwe = 2
        self.assertEqual(a.qwe, 2)

        a.invalidate()
        with self.assertRaises(RuntimeError):
            a.qwe = 8

    def test_raise_custom_error(self):
        class MyObject(InvalidateMixin):
            invalid_object_error = ValueError('Invalid object')

        a = MyObject()
        a.invalidate()
        with self.assertRaises(ValueError):
            a.qwer
        with self.assertRaises(ValueError):
            a.qwer = 2


class TestAttributeImmutableMixin(BaseTestCase):
    def make_simple_class(self):
        class MyObject(AttributeImmutableMixin):
            a = 1

            def __init__(self, b=2):
                self.__dict__['b'] = b

            def return_b(self):
                return self.b

        return MyObject

    def make_simple_class_instance(self):
        MyObject = self.make_simple_class()
        return MyObject()

    def test_make_instance(self):
        obj = self.make_simple_class_instance()

        self.assertEqual(obj.a, 1)
        self.assertEqual(obj.b, 2)

    def test_setattr(self):
        obj = self.make_simple_class_instance()

        with self.assertRaises(TypeError):
            obj.a = None

        with self.assertRaises(TypeError):
            obj.b = None

        with self.assertRaises(TypeError):
            obj.return_b = lambda x: x

    def test_delattr(self):
        obj = self.make_simple_class_instance()

        with self.assertRaises(TypeError):
            del obj.a

        with self.assertRaises(TypeError):
            del obj.b

        with self.assertRaises(TypeError):
            del obj.return_b
