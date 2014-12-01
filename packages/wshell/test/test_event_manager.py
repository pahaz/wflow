import unittest
from wshell.manager import EventManager

__author__ = 'pahaz'


class TestEventManager(unittest.TestCase):
    def test_add_event_listener(self):
        em = EventManager()
        r = lambda **kwargs: 1

        em.add_event_listener('e1', r)
        em.add_event_listener('some super event', r)

        r = lambda x: 1
        with self.assertRaises(TypeError) as c:
            em.add_event_listener('some 2', r)

        self.assertIn("**kwargs", str(c.exception))

        class R(object):
            def __call__(self, **kwargs):
                return 1

        r = R()
        em.add_event_listener('test2', r)

    def test_trigger_event(self):
        em = EventManager()

        def r(**kwargs):
            self.assertIn('t1', kwargs)
            self.assertEqual(kwargs['t1'], 7)
            raise AssertionError('Ok')

        em.add_event_listener('e1', r)
        with self.assertRaises(AssertionError):
            em.trigger_event('e1', t1=7)

    def test_rm_event_listener(self):
        em = EventManager()

        def r(**kwargs):
            raise AssertionError('Ok')

        em.add_event_listener('e1', r)
        with self.assertRaises(AssertionError):
            em.trigger_event('e1')
        em.rm_event_listener('e1', r)
        em.trigger_event('e1')

    def test_listen(self):
        em = EventManager()

        @em.listen('ev1')
        def r(**kwargs):
            raise AssertionError('Ok ev1')

        with self.assertRaises(AssertionError) as c:
            em.trigger_event('ev1')

        self.assertEqual('Ok ev1', str(c.exception))

        calls = 0

        @em.listen('ev2', 'ev4')
        def r(**kwargs):
            nonlocal calls
            calls += 1

        em.trigger_event('ev2', z1=1)
        em.trigger_event('ev4', z1=2)

        self.assertEqual(calls, 2)


if __name__ == "__main__":
    unittest.main()
