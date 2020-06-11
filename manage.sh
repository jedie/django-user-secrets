#!/bin/sh

set -ex

exec poetry run python manage.py "$@"