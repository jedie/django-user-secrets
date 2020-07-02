#!/usr/bin/env python3

import os
import sys


def cli():
    # assert "DJANGO_SETTINGS_MODULE" not in os.environ, 'Do not set DJANGO_SETTINGS_MODULE !'
    os.environ["DJANGO_SETTINGS_MODULE"] = "user_secrets_tests.settings"
    print(f"\nUse DJANGO_SETTINGS_MODULE={os.environ['DJANGO_SETTINGS_MODULE']!r}")
    from django.core.management import execute_from_command_line

    print(f'Execute command line: {" ".join(sys.argv)}')
    execute_from_command_line(sys.argv)


def start_test_server():
    sys.argv = [__file__, "run_testserver"]
    cli()


if __name__ == "__main__":
    cli()
