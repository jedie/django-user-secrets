#!/usr/bin/env python3

import os
import sys

from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands.createsuperuser import Command as CreateSuperUser
from django.contrib.staticfiles.management.commands.collectstatic import Command as CollectStatic
from django.contrib.staticfiles.management.commands.runserver import Command as RunServer
from django.core.management import BaseCommand, call_command
from django.core.management.commands.check import Command as Check
from django.core.management.commands.makemigrations import Command as MakeMigrations
from django.core.management.commands.migrate import Command as Migrate


print("sys.real_prefix:", getattr(sys, "real_prefix", "-"))
print("sys.prefix:", sys.prefix)


class Command(BaseCommand):
    """
    Expand django.contrib.staticfiles runserver
    """
    help = "Setup test project and run django developer server"

    def verbose_call(self, *, command, **kwargs):
        assert isinstance(command, BaseCommand), f'{command!r} is not a Command class!'
        command_name = command.__module__.rpartition('.')[2]
        self.stderr.write("_" * 79)
        self.stdout.write(f"Call {command_name!r} with: {kwargs!r}")
        sys.argv = [sys.argv[0], command_name]
        call_command(command, **kwargs)

    def handle(self, *args, **options):

        if "RUN_MAIN" not in os.environ:
            # RUN_MAIN added by auto reloader, see: django/utils/autoreload.py
            self.verbose_call(command=MakeMigrations())  # helpfull for developming
            self.verbose_call(command=Migrate(), run_syncdb=True)
            self.verbose_call(command=CollectStatic(), interactive=False, link=True, verbosity=1)

            User = get_user_model()
            qs = User.objects.filter(is_active=True, is_superuser=True)
            if qs.count() == 0:
                self.verbose_call(command=CreateSuperUser())

            self.verbose_call(command=Check())

        self.verbose_call(command=RunServer(), use_threading=False, use_reloader=True, verbosity=2)
