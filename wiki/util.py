from functools import partial

from flask import g
from markdown2 import markdown


def after_this_request(func):
    if not hasattr(g, 'call_after_request'):
        g.call_after_request = []
    g.call_after_request.append(func)
    return func


def load_markdown():
    extras = [
        'fenced-code-blocks',
        'footnotes',
        'header-ids',
        'tables',
        'toc',
    ]

    return partial(markdown, extras=extras)

