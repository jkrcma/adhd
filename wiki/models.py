import logging
import os
import os.path
from collections import OrderedDict
from redis import Redis
from rq import Queue
from shutil import rmtree
from subprocess import check_call, check_output, CalledProcessError

import config
from config import REPOSITORIES, GIT_DIR, UPDATE_INTERVAL
from .workers import schedule_update, clone_git_repository, update_git_repository

logger = logging.getLogger(__name__)

redis = Redis(config.REDIS_HOST, config.REDIS_PORT, config.REDIS_DB, config.REDIS_AUTH)
queue = Queue('wiki-updates', connection=redis)


class PagesCollection(object):

    def __init__(self):
        unordered = {name: Repository(name, url) for (name, url) in REPOSITORIES.items()}
        self.repositories = OrderedDict(sorted(unordered.items(), key=lambda x: x[0]))

        for repo in self.repositories.values():
            repo.refresh()

    def get_toplevel_categories(self):
        return list(REPOSITORIES.keys())

    def get_available_pages(self):
        files = OrderedDict()
        for name in self.repositories.keys():
            repo = self.get_repository(name)

            if not repo or not repo.is_initialized():
                continue

            try:
                files[name] = [f for f in repo.list_files() if f.lower().endswith('.md')]
            except GitException:
                logger.exception("Model error")

        return files

    def get_repository(self, name):
        repo = self.repositories[name]
        repo.refresh()

        return repo if repo.is_initialized() else None


class Repository(object):
    """
    A Git repository which is being worked on. This class allows cloning, updating and extracting particular files from
    a bare repository stored under `config.GIT_DIR` directory
    """

    JOB_ID_FMT = 'update:{0}'

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self._initializing = True

    def clone(self):
        try:
            rmtree(self.repo_dir, ignore_errors=True)
            check_call(['git', 'clone', '--bare', '--depth', '1', self.url, self.repo_dir])
        except CalledProcessError as e:
            raise GitException("Failed to clone the repository from '{0}'".format(self.url)) from e

    def update(self):
        assert os.path.isdir(self.repo_dir)

        try:
            check_call(['git', 'fetch', '--depth', '1'], env={'GIT_DIR': self.repo_dir})
        except CalledProcessError as e:
            raise GitException("Failed to fetch the repository '{0}'".format(self.name)) from e

    def list_files(self):
        assert os.path.isdir(self.repo_dir)

        try:
            output = check_output(['git', 'ls-tree', '-r', '--name-only', 'FETCH_HEAD'],
                                  env={'GIT_DIR': self.repo_dir}, universal_newlines=True)
        except CalledProcessError as e:
            raise GitException("Failed to list files from repository '{0}'".format(self.name)) from e

        return output.split(os.linesep)

    def checkout_file(self, file_path):
        assert os.path.isdir(self.repo_dir)

        try:
            return check_output(['git', 'show', 'FETCH_HEAD:{0}'.format(file_path)], env={'GIT_DIR': self.repo_dir})
        except CalledProcessError as e:
            raise GitException(
                "Failed to checkout file '{1}' from repository '{0}'".format(self.name, file_path)) from e

    def is_initialized(self):
        if not self._async_job or not self._async_job.result:
            self.refresh()
            return False

        try:
            return check_call(['git', 'show-ref', '-q'], env={'GIT_DIR': self.repo_dir}) == 0
        except CalledProcessError:
            return False

    def refresh(self):
        if self._async_job:
            return True

        job_id = self.JOB_ID_FMT.format(self.name)

        logger.debug("Updating repo {0} and scheduling timer, job_id={1}".format(self.name, job_id))
        # enqueue a job with fixed id which actually determines a timer for the updated itself
        queue.enqueue_call(func=schedule_update, result_ttl=UPDATE_INTERVAL, job_id=job_id)

        # and now the updater job itself
        if not os.path.isdir(self.repo_dir):
            queue.enqueue_call(func=clone_git_repository, args=[self])
            # repository will become available once clone finishes
        else:
            queue.enqueue_call(func=update_git_repository, args=[self])

        return False

    @property
    def repo_dir(self):
        return os.path.join(GIT_DIR, "{0}.git".format(self.name))

    @property
    def _async_job(self):
        return queue.fetch_job(self.JOB_ID_FMT.format(self.name))


class GitException(Exception):
    pass
