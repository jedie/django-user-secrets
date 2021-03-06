from pathlib import Path

from creole.setup_utils import update_rst_readme
from poetry_publish.publish import poetry_publish
from poetry_publish.utils.subprocess_utils import verbose_check_call

import user_secrets


PACKAGE_ROOT = Path(user_secrets.__file__).parent.parent


def update_readme():
    return update_rst_readme(
        package_root=PACKAGE_ROOT,
        filename='README.creole'
    )


def publish():
    """
        Publish to PyPi
        Call this via:
            $ poetry run publish
    """
    verbose_check_call('make', 'pytest')  # don't publish if tests fail
    verbose_check_call('make', 'fix-code-style')  # don't publish if code style wrong

    poetry_publish(
        package_root=PACKAGE_ROOT,
        version=user_secrets.__version__,
        creole_readme=True  # don't publish if README.rst is not up-to-date
    )


if __name__ == '__main__':
    update_readme()
