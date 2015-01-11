# coding=utf-8
import logging
import os
import sys

from wshell.command_interface import AbstractCommand
from wutil.execute import execute

from .parse import parse_repo, ParseError


__author__ = 'pahaz'


class GitReceivePackCommand(AbstractCommand):
    """
    Receive push into the repository.
    """

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        env = self.get_env()
        try:
            context = parse_repo(parsed_args.repo)
        except ParseError:
            self.log.exception("parse repo problem")
            raise RuntimeError('error: repository parsing problem')

        secure_repo_dir_name = context['repo_dir_name']
        repo_dns = context['repo_dns']

        self.log.debug('New repo {1} in {0}'
                       .format(env.SCRIPT_DATA_PATH, secure_repo_dir_name))
        self.log.warning("----> {0}".format(repo_dns))  # user info

        r, _, _ = execute(
            "git init --bare '{name}'".format(name=secure_repo_dir_name),
            cwd=env.SCRIPT_DATA_PATH,

            stderr_to_stdout=True,
            is_collecting_to_buf_stdout=False,
            is_collecting_to_buf_stderr=False,
            stdout=sys.stderr.buffer,
            stderr=None, )

        self.log.debug('start git-receive-pack')

        os.system(
            'cd {0} && git-receive-pack {name}'
            .format(env.SCRIPT_DATA_PATH, name=secure_repo_dir_name)
        )

        self.log.debug('received')

    @classmethod
    def get_name(cls):
        return 'git-receive-pack'

    def get_parser(self, run_command):
        p = super(GitReceivePackCommand, self).get_parser(run_command)
        p.add_argument('repo', help="The repository to sync into.")
        return p

    @classmethod
    def is_hidden_for_command_list(cls):
        return True


class GitUploadPackCommand(AbstractCommand):
    """
    Send source from the repository.
    """

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        env = self.get_env()
        try:
            context = parse_repo(parsed_args.repo)
        except ParseError:
            self.log.exception("parse repo problem")
            raise RuntimeError("error: repository parsing problem")

        secure_repo_dir_name = context['repo_dir_name']
        repo_dns = context['repo_dns']
        repo_local_path = os.path.join(env.SCRIPT_DATA_PATH,
                                       secure_repo_dir_name)

        self.log.debug('Receive repo request {1} from {0}'
                       .format(env.SCRIPT_DATA_PATH, secure_repo_dir_name))
        self.log.warning("----> {0}".format(repo_dns))  # user info

        if not os.path.isdir(repo_local_path):
            raise RuntimeError("error: repository not exists")

        self.log.debug('start git-upload-pack')

        os.system(
            'cd {0} && git-upload-pack {name}'
            .format(env.SCRIPT_DATA_PATH, name=secure_repo_dir_name)
        )

        self.log.debug('sent')

    @classmethod
    def get_name(cls):
        return 'git-upload-pack'

    def get_parser(self, run_command):
        p = super(GitUploadPackCommand, self).get_parser(run_command)
        p.add_argument('repo', help="The repository to sync into.")
        return p

    @classmethod
    def is_hidden_for_command_list(cls):
        return True
