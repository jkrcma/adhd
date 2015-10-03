import logging

from flask import Flask

import wiki.page

logging.basicConfig(level=logging.INFO, format='%(asctime)s ' + logging.BASIC_FORMAT, datefmt='%Y-%m-%dT%H:%M:%SZ')
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    wiki.page.initialize_app(app)

    return app
