import collections

from wutil.env import EnvStackLayer, is_hashable_type
from wutil.env_stack import EnvStack
from wutil.test import BaseTestCase


__author__ = 'pahaz'


class TestEnv(BaseTestCase):
    def make_env_stack(self, init=None):
        return EnvStack(init)

    def test_support_dict_and_env(self):
        init = EnvStackLayer({'a': 1})
        s = self.make_env_stack(init)
        self.assertEqual(s['a'], 1)

        init = {'a': 1}
        s = self.make_env_stack(init)
        self.assertEqual(s['a'], 1)

    def test_push_override(self):
        s = self.make_env_stack({'a': 1})
        s.push({'a': 2})

        self.assertEqual(s['a'], 2)

    def test_pop_restore_overridden(self):
        s = self.make_env_stack({'a': 1})
        s.push({'a': 2})
        s.pop()

        self.assertEqual(s['a'], 1)

    def test_three_push_layers_overridden(self):
        s = self.make_env_stack({'a': 1})
        s.push({'a': 2, 'b': 2})
        s.push({'a': 3, 'b': 3, 'c': 3})
        self.assertEqual(s['a'], 3)
        self.assertEqual(s['b'], 3)
        self.assertEqual(s['c'], 3)
        s.pop()
        self.assertEqual(s['a'], 2)
        self.assertEqual(s['b'], 2)
        with self.assertRaises(KeyError):
            s['c']
        s.pop()
        self.assertEqual(s['a'], 1)
        with self.assertRaises(KeyError):
            s['b']
        with self.assertRaises(KeyError):
            s['c']

    def test_three_push_layers_work_correct_with_len_iter_as_dict(self):
        s = self.make_env_stack({'a': 1})
        s.push({'a': 2, 'b': 2})
        s.push({'a': 3, 'b': 3, 'c': 3})
        self.assertEqual(len(s), 3)
        self.assertEqual(set(iter(s)), {'a', 'b', 'c'})
        self.assertEqual(s.as_dict(), {'a': 3, 'b': 3, 'c': 3})
        s.pop()
        self.assertEqual(len(s), 2)
        self.assertEqual(set(iter(s)), {'a', 'b'})
        self.assertEqual(s.as_dict(), {'a': 2, 'b': 2})
        s.pop()
        self.assertEqual(len(s), 1)
        self.assertEqual(set(iter(s)), {'a'})
        self.assertEqual(s.as_dict(), {'a': 1})

    def test_lookup_down_throw_overridden_layers(self):
        s = self.make_env_stack({'a': 1, 'b': 1, 'c': 1})
        self.assertEqual(len(s), 3)
        self.assertEqual(set(iter(s)), {'a', 'b', 'c'})
        self.assertEqual(s.as_dict(), {'a': 1, 'b': 1, 'c': 1})
        s.push({'a': 2, 'b': 2})
        self.assertEqual(len(s), 3)
        self.assertEqual(set(iter(s)), {'a', 'b', 'c'})
        self.assertEqual(s.as_dict(), {'a': 2, 'b': 2, 'c': 1})
        s.push({'a': 3})
        self.assertEqual(len(s), 3)
        self.assertEqual(set(iter(s)), {'a', 'b', 'c'})
        self.assertEqual(s.as_dict(), {'a': 3, 'b': 2, 'c': 1})
        s.pop()
        self.assertEqual(len(s), 3)
        self.assertEqual(set(iter(s)), {'a', 'b', 'c'})
        self.assertEqual(s.as_dict(), {'a': 2, 'b': 2, 'c': 1})
        s.pop()
        self.assertEqual(len(s), 3)
        self.assertEqual(set(iter(s)), {'a', 'b', 'c'})
        self.assertEqual(s.as_dict(), {'a': 1, 'b': 1, 'c': 1})

    def test_get_top_default_return_new_dict(self):
        s = self.make_env_stack()
        z1 = s._get_top()
        z2 = s._get_top()
        self.assertIsNot(z1, z2)
        self.assertIsInstance(z1, dict)
        self.assertIsInstance(z2, dict)
        self.assertEqual(z1, {})
        self.assertEqual(z2, {})

    def test_changes_in_layers_not_change_stack(self):
        base = {'a': 1}
        s = self.make_env_stack(base)
        base['a'] = 2
        self.assertEqual(s['a'], 1)

    def test_pop_on_empty_raise_index_error(self):
        s = self.make_env_stack()
        with self.assertRaises(IndexError):
            s.pop()

    def test_items(self):
        s = self.make_env_stack({'a': 1})
        self.assertIn(('a', 1), s.items())

    def test_iter(self):
        s = self.make_env_stack({'a': 1, 'b': 2})
        self.assertEqual(set(iter(s)), {'a', 'b'})

    def test_get(self):
        s = self.make_env_stack({'OK': 22, 'NOT_OK': None})
        self.assertEqual(s.get('OK'), 22)
        self.assertEqual(s.get('NOT_OK'), None)
        self.assertEqual(s.get('SECRET'), None)

    def test_immutable(self):
        e = self.make_env_stack({'OK': 22})

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
        e = self.make_env_stack({'OK': z})
        d = e.as_dict()
        zz = d['OK']
        self.assertEqual(z, zz)

    def test_empty_correct_for_getitem_len_as_dict_layers_count(self):
        s = self.make_env_stack()
        self.assertEqual(s.layers_count(), 0)
        self.assertEqual(len(s), 0)
        self.assertIs(s.get('key'), None)
        self.assertEqual(s.as_dict(), {})

    def test_pop_on_empty_stack_raise_index_error(self):
        s = self.make_env_stack()
        with self.assertRaises(IndexError):
            s.pop()

    def test_raise_unhashable(self):
        for x in ([], set(), {}):
            with self.assertRaises(TypeError):
                self.make_env_stack({'OK': x})
