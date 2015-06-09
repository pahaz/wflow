from __future__ import unicode_literals, print_function, generators, division

from wshell.test import BaseTestCase

__author__ = 'pahaz'


class TestCommandManager(BaseTestCase):
    def test_add_command(self):
        cm = self.make_command_manager()
        c1 = self.make_command_cls('Go1')
        c2 = self.make_command_cls('Go2')

        cm.add_command(c1)
        cm.add_command(c2)

        self.assertEqual(set(dict(list(cm)).keys()), {'go2', 'go1'})

    def test_find_command(self):
        Cmd = self.make_command_cls()
        class T1(Cmd):
            @classmethod
            def get_name(cls):
                return 'go 3'

        cm = self.make_command_manager()
        c1 = self.make_command_cls('Go1')
        c2 = self.make_command_cls('Go2')
        c3 = T1

        cm.add_command(c1)
        cm.add_command(c2)
        cm.add_command(c3)

        self.assertEqual(set(dict(list(cm)).keys()),
                         {'go1', 'go2', 'go 3'})

        with self.assertRaises(TypeError) as c:
            cm.find_command('go1 --help')

        command, name, search_args = cm.find_command(['go1', '--help'])
        self.assertEqual(command, c1)
        self.assertEqual(name, "go1")
        self.assertEqual(search_args, ['--help'])

        self.assertEqual(c3.get_name(), 'go 3')
        command, name, search_args = cm.find_command(['go', '3', '--help'])
        # print(command, name, search_args, set(dict(list(cm)).keys()))
        self.assertEqual(command, c3)
        self.assertEqual(name, "go 3")
        self.assertEqual(search_args, ['--help'])

        with self.assertRaises(ValueError) as c:
            cm.find_command(['awfawfawfaw', '--help'])

    def test_register_two_command_with_same_name_raise_error(self):
        name = "some"
        c1 = self.make_command_cls(name)
        c2 = self.make_command_cls(name)

        cm = self.make_command_manager()
        cm.add_command(c1)

        with self.assertRaises(ValueError):
            cm.add_command(c1)
        with self.assertRaises(ValueError):
            cm.add_command(c2)

    def test_simple_run_command_return_0(self):
        c1 = self.make_command_cls('test')
        cm = self.make_command_manager()
        env = self.make_env()
        cm.add_command(c1)
        return_code, error = cm.run_command(['test'], env)
        self.assertEqual(return_code, 0)

    def test_simple_run_raise_error_command_return_1(self):
        ERROR = RuntimeError('test')

        def check_raise_error(self_, args):
            raise ERROR

        c1 = self.make_command_cls('test', take_action=check_raise_error)
        cm = self.make_command_manager()
        env = self.make_env()
        cm.add_command(c1)
        return_code, error = cm.run_command(['test'], env)
        self.assertEqual(return_code, 1)
        self.assertEqual(error, ERROR)

    def test_pop_context(self):
        def check_env_context(self_, args):
            env = self_.env
            self.assertEqual(env['a'], 2)
            self.assertEqual(env['b'], 1)

        c1 = self.make_command_cls('test', take_action=check_env_context)
        cm = self.make_command_manager()
        env = self.make_env({'a': 1})
        cm.add_command(c1)
        cm.run_command(['test'], env, {'a': 2, 'b': 1})
        self.assertEqual(env.as_dict(), {'a': 1})
