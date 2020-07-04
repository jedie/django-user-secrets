===================
django-user-secrets
===================

Store user secrets encrypted into database.

Current project state: "Pre-Alpha"

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

* *dev* - `compare v0.1.0...master <https://github.com/jedie/django-user-secrets/compare/v0.1.0...master>`_

* TBC

* v0.1.0 - 04.07.2020 - `compare init...v0.1.0 <https://github.com/jedie/django-user-secrets/compare/d5700b952...v0.1.0>`_ 

    * first release on PyPi

------------

``Note: this file is generated from README.creole 2020-07-04 18:52:44 with "python-creole"``