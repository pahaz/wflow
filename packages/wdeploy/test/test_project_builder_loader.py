from __future__ import unicode_literals
import unittest

from wdeploy.project_builder_loader import BaseProjectBuilder, \
    ProjectBuilderNotFoundError
from wdeploy.test import BaseTestCase

__author__ = 'pahaz'


class TestProjectBuilderLoader(BaseTestCase):
    @unittest.skip("Docker Builder loaded defore. Check it!")
    def test_raise_not_found(self):
        loader = self.make_project_builder_loader()
        info = self.mock_project_info()
        with self.assertRaises(ProjectBuilderNotFoundError):
            print(loader.get_builder_for_project(info, {}))

    @unittest.skip("Docker Builder loaded defore. Check it!")
    def test_load_my_builder(self):
        FAKE_PROJECT_NAME = 'random-name'

        loader = self.make_project_builder_loader()
        info = self.mock_project_info(name=FAKE_PROJECT_NAME)

        class __MyBuilder(BaseProjectBuilder):
            is_called = False

            @classmethod
            def make_ProjectBuilder_or_None(cls, info, options):
                cls.is_called = True
                if info.name == FAKE_PROJECT_NAME:
                    return cls(info, options)

            make_image_name = build = make_project_runner = lambda x: x

        Builder = loader.get_builder_for_project(info, {})
        self.assertEqual(__MyBuilder.is_called, True)
        self.assertIsInstance(Builder, __MyBuilder)
        self.assertEqual(__MyBuilder.class_brothers[0], __MyBuilder)
