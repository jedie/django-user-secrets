===================
django-user-secrets
===================

Store user secrets encrypted into database.

+--------------------------+-------------------------------------------------+
| |Build Status on github| | `github.com/jedie/django-user-secrets/actions`_ |
+--------------------------+-------------------------------------------------+

.. |Build Status on github| image:: https://github.com/jedie/django-user-secrets/workflows/test/badge.svg?branch=master
.. _github.com/jedie/django-user-secrets/actions: https://github.com/jedie/django-user-secrets/actions

Current project state: "Beta"

Licence: GPL v3 or above

--------
the idea
--------

Store a user's secrets in the database encrypted with his password.

Only the user can decrypt the stored data. His password is used for encryption and decryption. This password is only transmitted in plain text when logging in (Django itself only saves a salted hash of the password).

The intermediate-user-secret is decrypted and stored with the clear text password in RAM after successful login. All user secrets will be encrypted and decrypted with his intermediate-user-secret.

Limitations and/or facts:

* Only the same user can decrypt his own data.

* The decrypted data can only be used during an active session.

* A intermediate-user-secret is used, so that a password can be changed without losing the encrypted data.

-----
usage
-----

The encrypted user secrets are stored via ``EncryptedField`` in the user model. Your project must implement a own ``settings.AUTH_USER_MODEL`` inherith from ``AbstractUserSecretsModel`` e.g.:

`/your_project/your_app/models.py <https://github.com/jedie/django-user-secrets/edit/master/user_secrets_tests/models.py>`_

::

    from user_secrets.model_fields import EncryptedField
    from user_secrets.models import AbstractUserSecretsModel
    
    class UserSecretsModel(AbstractUserSecretsModel):
        example_secret = EncryptedField(max_length=256, blank=True, null=True)  # can have one or more EncryptedField's!

Add this own user model to the Django Admin and add the own ``EncryptedField``, so the user can fill it in the admin, e.g.:

`/your_project/your_app/admin.py <https://github.com/jedie/django-user-secrets/edit/master/user_secrets_tests/admin.py>`_

::

    from django.contrib import admin
    from django.utils.translation import gettext_lazy as _
    
    from user_secrets.admin import UserSecretsAdmin
    from user_secrets_tests.models import UserSecretsModel
    
    
    @admin.register(UserSecretsModel)
    class ExampleModelAdmin(UserSecretsAdmin):
        fieldsets = (
            (None, {'fields': ('username', 'password')}),
            (_('User Secrets'), {'fields': ('encrypted_secret', 'example_secret')}),  # <<< own fields
            (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
            (_('Permissions'), {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            }),
            (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )

It's also possible to implement a own "edit" view just for the ``EncryptedField`` values. Have a look at the demo app view: `/user_secrets_tests/views/edit.py <https://github.com/jedie/django-user-secrets/blob/master/user_secrets_tests/views/edit.py>`_
For this you can easy get `a model form <https://github.com/jedie/django-user-secrets/blob/master/user_secrets_tests/forms.py>`_, e.g.:

::

    from user_secrets.forms import UserSecretsBaseModelModelForm
    from user_secrets_tests.models import UserSecretsModel
    
    
    class ExampleModelForm(UserSecretsBaseModelModelForm):
        class Meta:
            model = UserSecretsModel
            fields = ['example_secret']

To use the stored secret in a view, e.g.:

::

    user = request.user  # get current user
    example_secret = user.example_secret  # the the example field value (encrypted)
    # decrypt the example
    decrypted_value = user_decrypt(user=user, encrypted_data=example_secret)
    # ...do something with the value...

Complete example is: `/user_secrets_tests/views/display.py <https://github.com/jedie/django-user-secrets/blob/master/user_secrets_tests/views/display.py>`_

Needed settings:

::

    # The SECRET_KEY should never changed after django-user-secrets are created!
    SECRET_KEY = 'Use a long random string and keep this value secret!'
    
    INSTALLED_APPS = (
        #...
        'user_secrets.apps.UserSecretsConfig',
        #...
    )
    
    # Must point to a own UserModel class
    # This class must inherit from user_secrets.models.AbstractUserSecretsModel
    AUTH_USER_MODEL = 'your_app.YourUserModel'
    
    
    AUTHENTICATION_BACKENDS = [
        'user_secrets.auth_backend.UserSecretsAuthBackend',  # Must be at first
        'django.contrib.auth.backends.ModelBackend'
    ]
    
    
    CACHES = {
        'default': {  # Can use any backend.
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'default',
        },
        'user_secrets': {  # Should be use the LocMemCache!
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'user_secrets',
        }
    }
    
    
    MIDDLEWARE = (
        #...
        'user_secrets.middleware.UserSecretsMiddleware',  # inserted after AuthenticationMiddleware
    )

Complete example is: `/user_secrets_tests/settings.py <https://github.com/jedie/django-user-secrets/blob/master/user_secrets_tests/settings.py>`_

----
DEMO
----

Prepare: `install poetry <https://python-poetry.org/docs/#installation>`_ e.g.:

::

    ~$ sudo apt install python3-pip
    ~$ pip3 install -U pip --user
    ~$ pip3 install -U poerty --user

Clone the sources, e.g.:

::

    ~$ git clone https://github.com/jedie/django-user-secrets.git
    ~$ cd django-user-secrets
    
    # install via poetry:
    ~/django-user-secrets$ poetry install
    
    # Start Django dev. server:
    ~/django-user-secrets$ poetry run dev_server

You can also use our Makefile, e.g.:

::

    ~/django-user-secrets$ make help
    help                 List all commands
    install-poetry       install or update poetry
    install              install django-user-secrets via poetry
    update               update the sources and installation
    lint                 Run code formatters and linter
    fix-code-style       Fix code formatting
    tox-listenvs         List all tox test environments
    tox                  Run pytest via tox with all environments
    tox-py36             Run pytest via tox with *python v3.6*
    tox-py37             Run pytest via tox with *python v3.7*
    tox-py38             Run pytest via tox with *python v3.8*
    pytest               Run pytest
    update-rst-readme    update README.rst from README.creole
    publish              Release new version to PyPi
    start-dev-server     Start Django dev. server with the test project

Alternative/Related projects:
=============================

* `https://github.com/erikvw/django-crypto-fields <https://github.com/erikvw/django-crypto-fields>`_

* `https://github.com/incuna/django-pgcrypto-fields <https://github.com/incuna/django-pgcrypto-fields>`_

* `https://github.com/georgemarshall/django-cryptography <https://github.com/georgemarshall/django-cryptography>`_

(Random order: No prioritization)

-------
history
-------

* `*dev* <https://github.com/jedie/django-user-secrets/compare/v0.2.0...master>`_ 

    * TBC

* `v0.2.0 - 06.07.2020 <https://github.com/jedie/django-user-secrets/compare/v0.1.0...v0.2.0>`_ 

    * refactor:

        * Move EncryptedFields into user model and don't use a extra model for them

        * Move code parts from demo app into main package

    * Update demo app

    * update README

    * Bugfix Makefile

* `v0.1.0 - 04.07.2020 <https://github.com/jedie/django-user-secrets/compare/d5700b952...v0.1.0>`_ 

    * first release on PyPi

------------

``Note: this file is generated from README.creole 2020-07-06 11:30:39 with "python-creole"``