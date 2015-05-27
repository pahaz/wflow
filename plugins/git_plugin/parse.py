from .secure import secure_filename
from .serialize import unpack
from wutil.env_keys import REPO_DIR_NAME_KEY, DNS_NAME_KEY

__author__ = 'pahaz'


class ParseError(Exception):
    pass


def parse_git_url(repo):
    """Parse repo string.

        from wutil.env_keys import REPO_DIR_NAME_KEY, DNS_NAME_KEY
        context = {
                REPO_DIR_NAME_KEY: 'example_ru',
                DNS_NAME_KEY: 'example.ru',
        }

    :raise ParseError:
    :param repo: string (ex: "/qwer" or "/!nFfwfwW2aw")
    :return: parsed context
    """
    repo = repo.lstrip('/')

    if repo.startswith('!'):
        repo = repo[1:]
        context = unpack(repo)
        if REPO_DIR_NAME_KEY not in context:
            raise ParseError('unpacked repo does\'t contain REPO_DIR_NAME_KEY')
        if DNS_NAME_KEY not in context:
            raise ParseError('unpacked repo does\'t contain DNS_NAME_KEY')
    else:
        context = {
            REPO_DIR_NAME_KEY: repo,
            DNS_NAME_KEY: repo,
        }

    repo_dir_name = context[REPO_DIR_NAME_KEY]
    if "/" in repo_dir_name:
        raise ParseError('invalid repo_dir_name string "/" unexpected')

    if secure_filename(repo_dir_name) != repo_dir_name:
        raise ParseError('repo_dir_name security problem')

    return context
