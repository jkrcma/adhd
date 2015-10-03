import logging

from config import REPOSITORIES
from .models import Repository

logger = logging.getLogger(__name__)

def update_git_repository(name):
    """Performs an update (git fetch) of a given repo name
    """
    try:
        repo = Repository(name, REPOSITORIES[name])
        repo.update()
    except Exception:
        logger.exception("Failed to update the Git repository '{0}'".format(name))
        return False

    return True


def schedule_update(name):
    """Actually does nothing, but the result TTL of this function works as a timer
    """
    return True
