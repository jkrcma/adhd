import os

import flask
from flask import render_template, abort

from .models import PagesCollection, GitException
from .util import load_markdown

blueprint = flask.Blueprint('page', __name__)

collection = PagesCollection()
markdown = load_markdown()


def initialize_app(app):
    app.register_blueprint(blueprint)


@blueprint.route('/')
def index():
    return render_template('index.html')


@blueprint.route('/<repo>/<path:page_path>')
def page(repo, page_path):
    try:
        repo = collection.get_repository(repo)
        _, ext = os.path.splitext(page_path)

        if not repo or ext.lower() != '.md':
            abort(404)

        data = repo.checkout_file(page_path)
    except (IndexError, GitException):
        abort(404)

    content = markdown.convert(data.decode('utf-8'))

    return render_template('page.html', repo=repo, path=page_path, content=content, toc=markdown.toc)


@blueprint.before_request
def load_pages_list():
    flask.g.pages = collection.get_available_pages()
