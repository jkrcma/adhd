import flask
from flask import Flask, render_template, abort

from .models import PagesCollection, GitException
from .util import load_markdown

app = Flask(__name__)
collection = PagesCollection()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<repo>/<path:page_path>')
def page(repo, page_path):
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
