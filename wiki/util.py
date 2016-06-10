import markdown
from markdown.extensions import toc
from pymdownx import github


def load_markdown():
    ext_toc = toc.TocExtension(marker=None)
    ext_github = github.GithubExtension(no_nl2br=True)
    extensions = [ext_github, 'markdown.extensions.codehilite', ext_toc]

    return markdown.Markdown(extensions=extensions)

