import os
from pprint import pprint
import random
import string
import tempfile
import types
import unittest
from wdeploy.builders.docker import _make_container_name

from wdeploy.builders.docker.builder import DockerProjectBuilder
from wdeploy.builders.docker.container import DockerContainer
from wdeploy.project_info import ProjectInfo
from wdeploy.project_runner import WorkWithRemovedContainerError
from wutil.execute3 import execute


__author__ = 'pahaz'


class TestDockerDeploy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TEST_PROJECTS = ['tests/apps/python-simple']
        cls.TEST_DIR = TEST_DIR = tempfile.mkdtemp(prefix='wflow-docker-')
        cls.TEST_PROJECTS = [os.path.basename(p) for p in TEST_PROJECTS]
        print('TEST_DIR = {0}; TEST_PROJECTS = {1}'
              .format(TEST_DIR, cls.TEST_PROJECTS))
        for t_project in TEST_PROJECTS:
            name = os.path.basename(t_project)
            t_project = os.path.abspath(t_project)
            t_project_path = os.path.abspath(os.path.join(TEST_DIR, name))
            t_project_path_source = os.path.join(t_project_path, 'SOURCE')
            execute('mkdir {path}'.format(path=t_project_path))
            # execute('mkdir {path}'.format(path=t_project_path_source))
            execute('cp -r "{0}" "{1}"'.format(t_project,
                                               t_project_path_source))
            execute('git init --bare', cwd=t_project_path)
            execute('git init', cwd=t_project_path_source)
            execute('git add *', cwd=t_project_path_source)
            execute('git commit -am "init"', cwd=t_project_path_source,
                    check_return_code_and_raise_error=False)
            execute('git push "{0}" master'.format(t_project_path),
                    cwd=t_project_path_source)

    @classmethod
    def tearDownClass(cls):
        execute('rm -r "{0}"'.format(cls.TEST_DIR))

    @unittest.skip("long")
    def test_build_add_image(self):
        name = type(self).TEST_PROJECTS[-1]
        root = type(self).TEST_DIR
        info = ProjectInfo(root, name, {}, [])
        d = DockerProjectBuilder(info, {})
        r = d.make_project_runner()
        c = d._client

        print(r.containers)
        print(r.images)
        print(r._latest_image)

        r2 = d.build()

        self.assertEqual(len(r.containers), len(r2.containers))
        self.assertTrue(len(r.images) < len(r2.images))

        d.close()
        r.close()
        r2.close()

    # @unittest.skip("long")
    def test_runner(self):
        name = type(self).TEST_PROJECTS[-1]
        root = type(self).TEST_DIR
        info = ProjectInfo(root, name, {}, [])
        builder = DockerProjectBuilder(info, {})
        runner = builder.make_project_runner()

        name = ''.join([random.choice(string.ascii_letters) for _ in range(5)])
        py = "'" + 'python -c "print(\'aw\\nd\'*100)"' \
            .replace("'", "'\"'\"'") + "'"
        cont1 = runner.create('test' + name, '''/bin/sh -c {0}'''.format(py))
        cont1._debug()

        # check status
        self.assertEqual(cont1.status, cont1.STATUS_STOPPED)
        self.assertFalse(cont1.is_running)

        # check new container in containers
        self.assertIn(cont1.id, set(c.id for c in runner.containers))

        cont1.start()
        cont1._debug()

        self.assertEqual(cont1.status, cont1.STATUS_RUNNING)
        self.assertTrue(cont1.is_running)

        cont1.wait()

        self.assertEqual(cont1.status, cont1.STATUS_STOPPED)
        self.assertFalse(cont1.is_running)

        log = cont1.logs()
        self.assertIsInstance(log, types.GeneratorType)

        for x in log:
            print(x)

        z_id = cont1.id
        runner.remove(cont1)

        # check container is removed
        self.assertNotIn(z_id, set(c.id for c in runner.containers))

        builder.close()
        runner.close()

    # @unittest.skip("long")
    def test_invalidate(self):
        name = type(self).TEST_PROJECTS[-1]
        root = type(self).TEST_DIR
        info = ProjectInfo(root, name, {}, [])
        d = DockerProjectBuilder(info, {})
        r = d.make_project_runner()

        name = ''.join([random.choice(string.ascii_letters) for _ in range(5)])
        z = r.create('test' + name, '''/bin/sh -c "echo 123"''')
        z._debug()

        z.invalidate()
        z.invalidate()

        with self.assertRaises(WorkWithRemovedContainerError):
            z.id

        d.close()
        r.close()

    # @unittest.skip("long")
    def test_scale(self):
        name = type(self).TEST_PROJECTS[-1]
        root = type(self).TEST_DIR
        info = ProjectInfo(root, name, {}, [])
        builder = DockerProjectBuilder(info, {})
        runner = builder.make_project_runner()

        process_type = 'test' + ''.join([random.choice(string.ascii_letters)
                                         for _ in range(5)])
        len_containers = len(runner.containers)
        len_images = len(runner.images)
        containers = set(x.name for x in runner.containers)
        new_containers = set(
            _make_container_name(runner._latest_image, process_type, str(i))
            for i in range(1, 6))

        runner.scale(process_type, 5)

        scaled_containers = set(x.name for x in runner.containers)
        print(scaled_containers - containers)
        print(new_containers)
        self.assertEqual(len_containers + 5, len(runner.containers))
        self.assertEqual(len_images, len(runner.images))
        self.assertEqual(len(scaled_containers - containers), 5)
        self.assertEqual(scaled_containers - containers, new_containers)

        builder.close()
        runner.close()

    @unittest.skip("interactive")
    def test_interactive(self):
        name = type(self).TEST_PROJECTS[-1]
        root = type(self).TEST_DIR
        info = ProjectInfo(root, name, {}, [])
        builder = DockerProjectBuilder(info, {})
        runner = builder.make_project_runner()

        x = runner.create('test' + name, '/bin/bash', interactive=True)
        x._debug()
        x.start()

        builder.close()
        runner.close()

# code_dir = '/vagrant/tests/apps/python-flask'
# execute('rm -r /tmp/py-test/', check_return_code_and_raise_error=False)
# execute('mkdir -p /tmp/py-test')
# execute('git init --bare', cwd='/tmp/py-test/')
# execute('cp -r {0} /tmp/py-test'.format(code_dir))
# execute('git init', cwd='/tmp/py-test/python-flask')
# execute('git add *', cwd='/tmp/py-test/python-flask')
# execute('git commit -am "init"', cwd='/tmp/py-test/python-flask',
# check_return_code_and_raise_error=False)
# execute('cp -r /tmp/py-test/python-flask /tmp/py-test/SOURCE')
# execute('git push /tmp/py-test master')
#
# print('-----------------------')
# info = ProjectInfo('/tmp/', 'py-test', {}, [])
# d = DockerProjectBuilder(info, {})
# c = d._client

# pprint(c.containers(all=True))
# pprint(c.images())

# remove_exit_containers(c)
# remove_none_images(c)
# print(len(c.images(all=True)))  # 7
# print(len(c.containers(all=True)))  # 2

# d.build()

# print(len(c.images(all=True)))  # 9
# print(len(c.containers(all=True)))  # 2


# runner = d.make_project_runner()
# print(runner.containers)
# print(runner.images)
# print(runner._latest_image)

# runner.run_nodes()
# a = runner._run_node(runner._latest_image.name, 1)
# c.start(a)

# runner.discover()
# print(runner.containers)
# print(runner.images)


# runner.run_shell()
# pprint(c.containers(all=True))
# for x in (c.images(all=True)):
# pprint(c.inspect_image(x['Id']))

# pprint(c.ping())
# pprint(c.logs(name))

# z = (c.events())
#
# for x in z:
# pprint(x)

# info = ProjectInfo('/home/wflow', 'n7', {}, [])
# d = DockerProjectBuilder(info, {})
# r = d.make_project_runner()
# c = d._client
# print(r.containers)
# print(r.images)
# print(r._latest_image)
#
# z = r.create('test1', '/bin/bash', interactive=True)
# z.start()
#
# do_on_build_message = lambda x: print(x.decode().rstrip())
# d.build(do_on_build_message)

# remove_exit_containers(c)
# remove_none_images(c)

# for x in c.containers(all=True):
# c.remove_container(x, force=True)

# for x in r.containers:
#     # x._debug()
#     print(x.image)

unittest.main()
