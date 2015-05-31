from __future__ import unicode_literals, print_function, generators, division

from .project_builder_loader import ProjectBuilderLoader

__author__ = 'pahaz'


def deploy(info, settings, do_on_build_message=None):
    loader = ProjectBuilderLoader()
    builder = loader.get_builder_for_project(info, settings)
    runner = builder.build(do_on_build_message)
    builder.close()
    return runner  # need .close() !!


def make_runner(info, settings):
    loader = ProjectBuilderLoader()
    builder = loader.get_builder_for_project(info, settings)
    runner = builder.make_project_runner()
    return runner
