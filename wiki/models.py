import os
import os.path
import random
from subprocess import check_call, check_output, CalledProcessError

from config import REPOSITORIES, GIT_DIR


class PagesCollection(object):

    def __init__(self):
        self.repositories = {name: Repository(name, url) for (name, url) in REPOSITORIES.items()}

    def get_toplevel_categories(self):
        return list(REPOSITORIES.keys())

    def get_available_pages(self):
        files = {}
        for name in self.repositories.keys():
            repo = self.get_repository(name)
            files[name] = [f for f in repo.list_files() if f.endswith('.md')]

        return files

    def get_repository(self, name):
        repo = self.repositories[name]
        # this is temporary to fulfill the MVP requirement ;)
        if not repo.is_initialized():
            repo.clone()
        elif random.randrange(3) == 0:
            repo.update()


        return self.repositories[name]


class Repository(object):
    """
    A Git repository which is being worked on. This class allows cloning, updating and extracting particular files from
    a bare repository stored under `config.GIT_DIR` directory
    """

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def clone(self):
        try:
            check_call(['git', 'clone', '--bare', '--depth', '1', self.url, self.repo_dir])
        except CalledProcessError as e:
            raise GitException("Failed to clone the repository from '{0}'".format(self.url)) from e

    def update(self):
        assert os.path.isdir(self.repo_dir)

        check_call(['git', 'fetch', '--depth', '1'], env={'GIT_DIR': self.repo_dir})

    def list_files(self):
        assert os.path.isdir(self.repo_dir)

        try:
            output = check_output(['git', 'ls-tree', '-r', '--name-only', 'HEAD'],
                                  env={'GIT_DIR': self.repo_dir}, universal_newlines=True)
        except CalledProcessError as e:
            raise GitException("Failed to list files from repository '{0}'".format(self.name)) from e

        return output.split(os.linesep)

    def checkout_file(self, file_path):
        assert os.path.isdir(self.repo_dir)

        try:
            return check_output(['git', 'show', 'HEAD:{0}'.format(file_path)], env={'GIT_DIR': self.repo_dir})
        except CalledProcessError as e:
            raise GitException(
                "Failed to checkout file '{1}' from repository '{0}'".format(self.name, file_path)) from e

    def is_initialized(self):
        return os.path.isdir(self.repo_dir)

    @property
    def repo_dir(self):
        return os.path.join(GIT_DIR, "{0}.git".format(self.name))


class GitException(Exception):
    pass
