import logging

logger = logging.getLogger(__name__)


def clone_git_repository(repo):
    """Performs a clone of a given repo name
    """
    try:
        repo.clone()
    except Exception:
        logger.exception("Clone failed")

    return True


def update_git_repository(repo):
    """Performs an update (git fetch) of a given repo name
    """
    try:
        repo.update()
    except Exception:
        logger.exception("Update failed")

    return True


def schedule_update():
    """Actually does nothing, but the result TTL of this function works as a timer
    """
    return True
