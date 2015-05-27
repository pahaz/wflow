# coding=utf-8
import logging
import os
import sys
import subprocess

from wshell.abc_command import AbstractCommand
from wutil.env_keys import PLATFORM_DATA_PATH_KEY
from wutil.env_keys import REPO_DIR_NAME_KEY, DNS_NAME_KEY
from wutil.execute3 import execute

from .parse import parse_git_url, ParseError


__author__ = 'pahaz'


def get_git_context(git_url, log):
    try:
        context = parse_git_url(git_url)
    except ParseError as e:
        log_msg = "parse repo-url error: {0}".format(e)
        log.error(log_msg)
        log.debug(log_msg, exc_info=True)
        raise RuntimeError('error: repository parsing problem')
    return context


class GitReceivePackCommand(AbstractCommand):
    """
    Receive push into the repository.
    """

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        env = self.env
        context = get_git_context(parsed_args.git_url, self.log)
        data_path = env[PLATFORM_DATA_PATH_KEY]
        secure_repo_dir_name = context[REPO_DIR_NAME_KEY]
        dns_name = context[DNS_NAME_KEY]

        repo_local_path = os.path.join(data_path, secure_repo_dir_name)

        self.log.debug('init new repo {0}'.format(repo_local_path))

        self.write_message_for_user("receive {0} project".format(dns_name))

        execute(
            "git init --bare '{name}'".format(name=secure_repo_dir_name),
            cwd=data_path,
            stderr_to_stdout=True,
            do_on_read_stdout=lambda x: self.log.debug(x.decode()),
        )

        self.log.debug('start git-receive-pack')

        try:
            subprocess.check_call(
                'cd {0} && git-receive-pack {name}'
                .format(data_path, name=secure_repo_dir_name),
                shell=True
            )
        except subprocess.CalledProcessError as e:
            self.log.error("git-receive-pack problem #{0}"
                           .format(e.returncode))
            return
        except OSError as e:
            self.log.exception(e)
            raise

        self.trigger_event('git-receive-pack', env, context)

        self.log.debug('finish git-receive-pack')

    @classmethod
    def get_name(cls):
        return 'git-receive-pack'

    def get_parser(self, run_command):
        parser = super(GitReceivePackCommand, self).get_parser(run_command)
        parser.add_argument('git_url', help="The repository url to sync into.")
        return parser

    @classmethod
    def is_hidden_for_command_list(cls):
        return True


class GitUploadPackCommand(AbstractCommand):
    """
    Send source from the repository.
    """

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        env = self.env
        context = get_git_context(parsed_args.git_url, self.log)
        data_path = env[PLATFORM_DATA_PATH_KEY]
        secure_repo_dir_name = context[REPO_DIR_NAME_KEY]
        dns_name = context[DNS_NAME_KEY]
        repo_local_path = os.path.join(data_path, secure_repo_dir_name)

        self.log.debug('Receive repo request {1} from {0}'
                       .format(data_path, secure_repo_dir_name))
        self.log.warning("----> {0}".format(dns_name))  # user info

        if not os.path.isdir(repo_local_path):
            raise RuntimeError("error: repository not exists")

        self.log.debug('start git-upload-pack')

        os.system(
            'cd {0} && git-upload-pack {name}'
            .format(data_path, name=secure_repo_dir_name)
        )

        self.trigger_event('git-upload-pack', env, context)

        self.log.debug('uploaded')

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
