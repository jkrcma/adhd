from functools import partial

from markdown2 import markdown


def load_markdown():
    extras = [
        'fenced-code-blocks',
        'footnotes',
        'header-ids',
        'tables',
        'toc',
    ]

    return partial(markdown, extras=extras)

