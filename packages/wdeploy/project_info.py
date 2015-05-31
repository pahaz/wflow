from __future__ import unicode_literals, print_function, generators, division
import os

from wdeploy.validators import check_project_name, check_path_is_dir, \
    ValidationError
from wutil.fs import mkdir_if_not_exists


__author__ = 'pahaz'


class ProjectInfo(object):
    SOURCE_DIR_NAME = 'SOURCE'
    BUILDS_DIR_NAME = 'BUILDS'
    DATA_DIR_NAME = 'DATA'
    DATA_CACHE_NAME = 'CACHE'

    def validate(self):
        check_project_name(self.name)
        check_path_is_dir(self.repo_path)
        check_path_is_dir(self.source_path)

    def make_project_dirs_if_not_exists(self):
        mkdir_if_not_exists(self.builds_path)
        mkdir_if_not_exists(self.data_path)
        mkdir_if_not_exists(self.cache_path)

    def __init__(self, project_repo_path, project_name, project_environment,
                 project_services, **kwargs):
        self._name = project_name
        self._project_repo_path = project_repo_path
        self._environment = project_environment
        try:
            self.validate()
        except ValidationError as e:
            raise TypeError(str(e))
        self.make_project_dirs_if_not_exists()

    @property
    def name(self):
        return self._name

    @property
    def environment(self):
        return self._environment

    # exists ...

    @property
    def source_path(self):
        return os.path.join(self.repo_path, self.SOURCE_DIR_NAME)

    @property
    def repo_path(self):
        return os.path.join(self._project_repo_path, self._name)

    # may not exists ...

    @property
    def builds_path(self):
        return os.path.join(self.repo_path, self.BUILDS_DIR_NAME)

    @property
    def data_path(self):
        return os.path.join(self.repo_path, self.DATA_DIR_NAME)

    @property
    def cache_path(self):
        return os.path.join(self.repo_path, self.DATA_CACHE_NAME)
