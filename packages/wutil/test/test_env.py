import collections

from wutil.env import EnvStackLayer, is_hashable_type
from wutil.test import BaseTestCase


__author__ = 'pahaz'


class TestEnv(BaseTestCase):
    def test_default_env(self):
        e = EnvStackLayer({'OK': 22})
        with self.assertRaises(AttributeError):
            e.OK
        self.assertEqual(e['OK'], 22)

        with self.assertRaises(AttributeError):
            e.SECRET

        with self.assertRaises(TypeError):
            e['Z'] = 2

        with self.assertRaises(TypeError):
            e['OK'] = 5

        with self.assertRaises(TypeError):
            e.Z = 2

        with self.assertRaises(TypeError):
            e.OK = 5

        self.assertIn('OK', e)
        self.assertIsInstance(e, collections.Mapping)

    def test_items(self):
        e = EnvStackLayer({'OK': 22, 'NOT_OK': 33})
        z = e.items()
        self.assertIn(('OK', 22), z)
        self.assertIn(('NOT_OK', 33), z)

    def test_iter(self):
        e = EnvStackLayer({'OK': 22, 'NOT_OK': 33})
        i = iter(e)
        self.assertEqual(set(i), {'OK', 'NOT_OK'})

    def test_get(self):
        e = EnvStackLayer({'OK': 22, 'NOT_OK': None})
        self.assertEqual(e.get('OK'), 22)
        self.assertEqual(e.get('NOT_OK'), None)
        self.assertEqual(e.get('SECRET'), None)

    def test_immutable(self):
        e = EnvStackLayer({'OK': 22})

        with self.assertRaises(TypeError):
            e['OK'] = 2
        with self.assertRaises(TypeError):
            e['Z'] = 2

        with self.assertRaises(TypeError):
            del e['OK']
        with self.assertRaises(TypeError):
            del e['Z']

        with self.assertRaises(TypeError):
            e.get = lambda z: z

    def test_as_dict(self):
        z = (2, 3, 4, 5, 6)
        e = EnvStackLayer({'OK': z})
        d = e.as_dict()
        zz = d['OK']
        self.assertEqual(z, zz)

    def test_raise_unhashable(self):
        for x in ([], set(), {}):
            with self.assertRaises(TypeError):
                e = EnvStackLayer({'OK': x})

    def test_is_simple_type(self):
        for x in (1, 1.2, 'qwe'):
            self.assertTrue(is_hashable_type(x), repr(type(x)))
