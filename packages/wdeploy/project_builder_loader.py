from __future__ import unicode_literals, print_function, generators, division

from wdeploy.project_builder import BaseProjectBuilder

__author__ = 'pahaz'


class ProjectBuilderNotFoundError(Exception):
    pass


class ProjectBuilderLoader(object):
    @staticmethod
    def get_builder_for_project(info, options):
        for Builder in BaseProjectBuilder.class_brothers:
            builder = Builder.make_ProjectBuilder_or_None(info, options)
            if builder is not None:
                return builder
        raise ProjectBuilderNotFoundError
