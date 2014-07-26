#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "humansort.settings")

    from django.core.management import execute_from_command_line

    paths = ["sort/"]

    for path in paths:
        if path not in sys.path:
                sys.path.append(path)

    execute_from_command_line(sys.argv)
