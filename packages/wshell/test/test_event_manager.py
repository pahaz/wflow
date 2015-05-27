from __future__ import unicode_literals, print_function, generators, division
import unittest
import sys

from wshell.event_manager import EventManager
from wutil.env_stack import EnvStack

__author__ = 'pahaz'


class TestEventManager(unittest.TestCase):
    def make_event_manager(self):
        return EventManager()

    def make_event_listener(self):
        listener = lambda manager, env: 1
        return listener

    def test_add_event_listener(self):
        em = self.make_event_manager()
        r = self.make_event_listener()
        em.add_event_listener('e1', r)
        em.add_event_listener('some super event', r)

    def test_has_event_listener(self):
        em = self.make_event_manager()
        r = self.make_event_listener()
        em.add_event_listener('event1', r)
        self.assertTrue(em.has_event_listener('event1', r))

    def test_invalid_receiver_signature_raise_error(self):
        em = self.make_event_manager()

        r = lambda x: 1
        with self.assertRaises(TypeError) as c:
            em.add_event_listener('event1', r)

        r = lambda env, **kwargs: 1
        with self.assertRaises(TypeError) as c:
            em.add_event_listener('event1', r)

        r = lambda *args: 1
        with self.assertRaises(TypeError) as c:
            em.add_event_listener('event1', r)

        r = lambda env=2: 1
        with self.assertRaises(TypeError) as c:
            em.add_event_listener('event1', r)

        r = lambda env, x=2: 1
        with self.assertRaises(TypeError) as c:
            em.add_event_listener('event1', r)

    def test_add_class_call_as_event_listener(self):
        em = self.make_event_manager()

        class R(object):
            def __call__(self, manager, env):
                return 1

        r = R()
        em.add_event_listener('test1', r)

    @unittest.skipIf(sys.version_info < (3, 4), "old python bugs")
    def test_raise_type_error_if_used_wrong_class_constructor(self):
        em = self.make_event_manager()

        class R(object):
            def __call__(self, manager, env):
                return 1

        with self.assertRaises(TypeError):
            em.add_event_listener('test1', R)

    def test_use_bounded_method_as_listener(self):
        em = self.make_event_manager()

        class R(object):
            def listen(self, manager, env):
                return 1

        em.add_event_listener('test1', R().listen)

    def test_use_bound_class_method_as_listener(self):
        em = self.make_event_manager()

        class R(object):
            @classmethod
            def listen(cls, manager, env):
                return 1

        em.add_event_listener('test1', R.listen)

    def test_use_static_method_as_listener(self):
        em = self.make_event_manager()

        class R(object):
            @staticmethod
            def listen(cls, manager, env):
                return 1

        em.add_event_listener('test1', R.listen)
        em.add_event_listener('test1', R().listen)

    @unittest.skipIf(sys.version_info < (3, 4), "old python bugs")
    def test_add_class_constructor_as_event_listener(self):
        em = self.make_event_manager()

        class r(object):
            def __init__(self, manager, env):
                pass

        em.add_event_listener('test1', r)

    def test_trigger_event(self):
        em = self.make_event_manager()
        r = self.make_event_listener()

        em.add_event_listener('e1', r)
        rez = em.trigger_event('e1', EnvStack())
        self.assertEqual(rez, [(r, 1, None)])

    def test_rm_event_listener(self):
        em = self.make_event_manager()
        r = self.make_event_listener()

        em.add_event_listener('e1', r)
        rez = em.trigger_event('e1', EnvStack())
        self.assertEqual(rez, [(r, 1, None)])

        em.remove_event_listener('e1', r)
        rez = em.trigger_event('e1', EnvStack())
        self.assertEqual(rez, [])

    def test_listen(self):
        em = self.make_event_manager()

        @em.listen('e1')
        def r(manager, env):
            return 1

        rez = em.trigger_event('e1', EnvStack())
        self.assertEqual(rez, [(r, 1, None)])

    def test_extra_context(self):
        em = self.make_event_manager()

        @em.listen('e1')
        def r(manager, env):
            return env['a']

        rez = em.trigger_event('e1', EnvStack({'a': 1}), {'a': 2})
        self.assertEqual(rez, [(r, 2, None)])

    def test_pop_context(self):
        EVENT = 'e1'
        em = self.make_event_manager()
        el = lambda manager, env: env['a']
        em.add_event_listener(EVENT, el)

        env = EnvStack({'a': 1})
        rez = em.trigger_event(EVENT, env, {'a': 2, 'b': 1})
        self.assertEqual(rez, [(el, 2, None)])
        self.assertEqual(env, {'a': 1})
        self.assertEqual(env.as_dict(), {'a': 1})

    def test_pop_context_if_non_listeners(self):
        EVENT = 'e1'
        em = self.make_event_manager()
        env = EnvStack({'a': 1})
        rez = em.trigger_event(EVENT, env, {'a': 2, 'b': 1})
        self.assertEqual(rez, [])
        self.assertEqual(env.layers_count(), 1)
        self.assertEqual(env, {'a': 1})
        self.assertEqual(env.as_dict(), {'a': 1})
