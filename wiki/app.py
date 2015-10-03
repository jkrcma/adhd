import logging

import flask
from flask import Flask, render_template, abort
from redis import Redis
from rq import Queue

import config
from .models import PagesCollection, GitException
from .util import after_this_request, load_markdown
from .workers import schedule_update, update_git_repository

logging.basicConfig(level=logging.INFO, format='%(asctime)s ' + logging.BASIC_FORMAT, datefmt='%Y-%m-%dT%H:%M:%SZ')
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    collection = PagesCollection()

    redis = Redis(config.REDIS_HOST, config.REDIS_PORT, config.REDIS_DB, config.REDIS_AUTH)
    queue = Queue('wiki-updates', connection=redis)

    @app.route('/')
    def index():
        return render_template('index.html')


    @app.route('/<repo>/<path:page_path>')
    def page(repo, page_path):
        @after_this_request
        def check_repo_scheduler(response):
            job_id = "update:{0}".format(repo)
            job = queue.fetch_job(job_id)
            if not job:
                logger.debug("Updating repo {0} and scheduling timer, job_id={1}".format(repo, job_id))
                # enqueue a job with fixed id which actually determines a timer for the updated itself
                queue.enqueue_call(func=schedule_update, result_ttl=config.UPDATE_INTERVAL, args=[repo], job_id=job_id)
                # and now the updater job itself
                queue.enqueue_call(func=update_git_repository, args=[repo])

            return response

        try:
            data = collection.get_repository(repo).checkout_file(page_path)
        except (IndexError, GitException):
            abort(404)

        markdownize = load_markdown()
        content = markdownize(data.decode('utf-8'))

        return render_template('page.html', repo=repo, path=page_path, content=content)

    @app.before_request
    def load_pages_list():
        flask.g.pages = collection.get_available_pages()

    @app.after_request
    def per_request_callbacks(response):
        for func in getattr(flask.g, 'call_after_request', {}):
            response = func(response)
        return response

    return app
