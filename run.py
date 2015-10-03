#!/usr/bin/env python3
import logging

from wiki.app import create_app

logging.root.level = logging.DEBUG

create_app().run(debug=True)
