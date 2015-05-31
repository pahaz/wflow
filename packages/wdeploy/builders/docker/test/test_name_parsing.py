from __future__ import unicode_literals, print_function, generators, division
import unittest
from wdeploy.builders.docker import _parse_container_name, _parse_image_name, \
    _clean_image_name, _clean_container_name

__author__ = 'pahaz'


class ParseContainerNameTest(unittest.TestCase):
    def test_parse_container_name(self):
        NAME = 'build__n10__2015.05.18.07h.54m.52s__web__1'
        TYPE = 'web'
        INDEX = 1
        IMAGE = 'build__n10__2015.05.18.07h.54m.52s'
        image, type, index = _parse_container_name(NAME)
        self.assertEqual(image, IMAGE)
        self.assertEqual(type, TYPE)
        self.assertEqual(index, INDEX)

    def test_parse_container_name_with_slash(self):
        NAME = '/build__n10__2015.05.18.07h.54m.52s__web__1'
        TYPE = 'web'
        INDEX = 1
        IMAGE = 'build__n10__2015.05.18.07h.54m.52s'
        image, type, index = _parse_container_name(NAME)
        self.assertEqual(image, IMAGE)
        self.assertEqual(type, TYPE)
        self.assertEqual(index, INDEX)

    def test_parse_container_name_2(self):
        NAME = 'build__test-runner__1__scale-2__2'
        TYPE = 'scale-2'
        INDEX = 2
        IMAGE = 'build__test-runner__1'
        image, type, index = _parse_container_name(NAME)
        self.assertEqual(image, IMAGE)
        self.assertEqual(type, TYPE)
        self.assertEqual(index, INDEX)

    def test_parse_container_name_2_with_slash(self):
        NAME = '/build__test-runner__1__scale-2__2'
        TYPE = 'scale-2'
        INDEX = 2
        IMAGE = 'build__test-runner__1'
        image, type, index = _parse_container_name(NAME)
        self.assertEqual(image, IMAGE)
        self.assertEqual(type, TYPE)
        self.assertEqual(index, INDEX)

    def test_parse_container_name_check_image(self):
        NAME = 'bad__n10__2015.05.18.07h.54m.52s__web__1'
        TYPE = INDEX = IMAGE = None
        image, type, index = _parse_container_name(NAME)
        self.assertEqual(image, IMAGE)
        self.assertEqual(type, TYPE)
        self.assertEqual(index, INDEX)

    def test_parse_container_name_with_wrong_format(self):
        NAME = 'super_container_web'
        TYPE = None
        INDEX = None
        IMAGE = None
        image, type, index = _parse_container_name(NAME)
        self.assertEqual(image, IMAGE)
        self.assertEqual(type, TYPE)
        self.assertEqual(index, INDEX)


class ParseContainerImageNameTest(unittest.TestCase):
    def test_parse_image_name(self):
        NAME = 'build__n10__2015.05.18.07h.54m.52s'
        PROJECT = 'n10'
        VERSION = '2015.05.18.07h.54m.52s'
        project, version = _parse_image_name(NAME)
        self.assertEqual(project, PROJECT)
        self.assertEqual(version, VERSION)

    def test_parse_image_name_with_tag(self):
        NAME = 'build__n10__2015.05.18.07h.54m.52s:latest'
        PROJECT = 'n10'
        VERSION = '2015.05.18.07h.54m.52s'
        project, version = _parse_image_name(NAME)
        self.assertEqual(project, PROJECT)
        self.assertEqual(version, VERSION)

    def test_parse_image_name_2(self):
        NAME = 'build__test-runner__1'
        PROJECT = 'test-runner'
        VERSION = '1'
        project, version = _parse_image_name(NAME)
        self.assertEqual(project, PROJECT)
        self.assertEqual(version, VERSION)

    def test_parse_image_name_2_with_tag(self):
        NAME = 'build__test-runner__1:dev'
        PROJECT = 'test-runner'
        VERSION = '1'
        project, version = _parse_image_name(NAME)
        self.assertEqual(project, PROJECT)
        self.assertEqual(version, VERSION)

    def test_parse_image_name_with_wrong_name_format(self):
        NAME = 'busybox'
        PROJECT = None
        VERSION = None
        project, version = _parse_image_name(NAME)
        self.assertEqual(project, PROJECT)
        self.assertEqual(version, VERSION)


class CleanImageNameTest(unittest.TestCase):
    def test_clean_image_name(self):
        NAME = 'build__test3__2015.05.06-10H-29M-14S:latest'
        RESULT = 'build__test3__2015.05.06-10H-29M-14S'
        name = _clean_image_name(NAME)
        self.assertEqual(name, RESULT)

    def test_clean_none_image_name(self):
        NAME = None
        RESULT = None
        name = _clean_image_name(NAME)
        self.assertEqual(name, RESULT)

    def test_clean_bad_image_name(self):
        NAME = 'bad__n10__2015.05.18.07h.54m.52s'
        RESULT = None
        name = _clean_image_name(NAME)
        self.assertEqual(name, RESULT)


class CleanContainerNameTest(unittest.TestCase):
    def test_clean_bad_container_name(self):
        NAME = '/jovial_bartik'
        RESULT = None
        name = _clean_container_name(NAME)
        self.assertEqual(name, RESULT)

    def test_clean_container_name(self):
        NAME = 'build__test-runner__1__scale-2__2'
        RESULT = 'build__test-runner__1__scale-2__2'
        name = _clean_container_name(NAME)
        self.assertEqual(name, RESULT)

    def test_clean_container_name_2(self):
        NAME = '/build__test-runner__1__scale-2__2'
        RESULT = 'build__test-runner__1__scale-2__2'
        name = _clean_container_name(NAME)
        self.assertEqual(name, RESULT)

