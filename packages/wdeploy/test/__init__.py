from __future__ import unicode_literals, print_function, generators, division
import unittest

from wdeploy.project_builder_loader import ProjectBuilderLoader
from wdeploy.project_info import ProjectInfo
from wdeploy.validators import check_project_name

__author__ = 'pahaz'


class MockProjectInfo(ProjectInfo):
    def make_project_dirs_if_not_exists(self):
        pass

    def validate(self):
        check_project_name(self.name)


def make_mock_project_info(name="default", repo_path='/tmp'):
    return MockProjectInfo(repo_path, name, {}, [])


class BaseTestCase(unittest.TestCase):
    def mock_project_info(self, name="default", repo_path='/tmp/default'):
        return make_mock_project_info(repo_path, name)

    def make_project_builder_loader(self):
        return ProjectBuilderLoader()
