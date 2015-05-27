import os
import stat

__author__ = 'pahaz'


def read_content(path):
    with open(path) as f:
        content = f.read().strip()
    return content


def write_content(path, content):
    with open(path, 'wb') as f:
        f.write(content.encode('utf-8'))


def set_executable(path):
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)


def mkdir_if_not_exists(path):
    path = path.rstrip('/\\')
    if not os.path.exists(path):
        base = os.path.dirname(path)
        mkdir_if_not_exists(base)
        os.mkdir(path)
        return True
    return False
