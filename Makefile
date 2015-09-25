.PHONY: build configcheck clean test

build: configcheck .venv

configcheck:
	test -s $(CURDIR)/config.py || { echo "File 'config.py' is missing."; exit 1; }

.venv:
	virtualenv -p `which python3` $(CURDIR)/.venv
	$(CURDIR)/.venv/bin/pip install -r requirements.txt

clean:
	rm -rf $(CURDIR)/.venv

test: build
	$(CURDIR)/.venv/bin/python -m unittest discover
