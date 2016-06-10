## ADHD

_Automated Docs for Heureka Development_ is an aggregator of Markdown files directly from configured Git repositories,
allowing users to browse them directly over HTTP in one place.

The greatest features so far are:

* GitHub flavored Markdown support
* Table of Contents extraction
* asynchronous repository updates over Redis-queued workers
* simplicity in mind ;)

### Dependencies

- Python 3.4+ (could probably run on lower versions, **untested**)
- Redis 2.6+

### Building

Create file `config.py` as specified by `config.dist.py` file, then run:

```sh
make clean && make
```

### Tests

No tests implented yet ;(

### Usage

```sh
# For development only
. .venv/bin/activate
python run.py
```

In production environment you should use any appropriate WSGI wrapper, such as _uWSGI_.

#### Workers queue

```sh
. .venv/bin/activate
rqworker wiki-updates
```

In production environment you should use any process manager to keep the worker manager running,
such as _Upstart_ or _Supervisor_.

### Bugs & contributing

Fill the bug report on [GitHub](https://github.com/jkrcma/adhd/issues) or just fork the project and send me a pull request :)

### TODO

* Live notification after the page was changed by the background worker
* Optimizations for large installations
