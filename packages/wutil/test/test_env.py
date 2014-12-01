import unittest
from wutil.env import Env
from wutil.test import BaseTestCase

__author__ = 'pahaz'


class TestEnv(BaseTestCase):
    def test_default_env(self):
        e = Env({'OK': 22})
        self.assertEqual(e.OK, 22)
        with self.assertRaises(AttributeError):
            self.assertIs(e.SECRET, None)

        with self.assertRaises(TypeError):
            e['OK']

        with self.assertRaises(TypeError):
            e['Z'] = 2

        with self.assertRaises(TypeError):
            e['OK'] = 5

        with self.assertRaises(TypeError):
            'OK' in e

        with self.assertRaises(TypeError):
            'OK' not in e

        with self.assertRaises(TypeError):
            iter(e)

    def test_suppress_error(self):
        e = Env({'OK': 22}, suppress_attribute_error=True)
        self.assertEqual(e.OK, 22)
        self.assertIs(e.SECRET, None)

    def test_items(self):
        e = Env({'OK': 22, 'NOT_OK': 33})
        z = e.items()
        self.assertIn(('OK', 22), z)
        self.assertIn(('NOT_OK', 33), z)

    def test_get(self):
        e = Env({'OK': 22, 'NOT_OK': None})
        self.assertEqual(e.OK, 22)
        with self.assertRaises(AttributeError):
            self.assertIs(e.SECRET, None)

        self.assertEqual(e.get('OK'), 22)
        self.assertEqual(e.get('NOT_OK'), None)
        self.assertEqual(e.get('SECRET'), None)

    def test_immutable(self):
        e = Env({'OK': 22})

        with self.assertRaises(TypeError):
            e.OK = 2
        with self.assertRaises(TypeError):
            e.Z = 2

        with self.assertRaises(TypeError):
            del e.OK
        with self.assertRaises(TypeError):
            del e.Z

        with self.assertRaises(TypeError):
            e.get = lambda z: z

    def test_as_dict(self):
        z = [0]
        e = Env({'OK': z})
        d = e.as_dict()
        zz = d['OK']
        self.assertTrue(z is not zz)
        z.append(2)
        self.assertEqual(len(z), 2)
        self.assertEqual(len(zz), 1)

if __name__ == "__main__":
    unittest.main()
