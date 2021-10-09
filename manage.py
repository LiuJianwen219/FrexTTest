#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import logging
import os
import socket
import sys


rootPath = "/data/FrexT"
log_path = os.path.join(rootPath, "FrexTTestServer_" + socket.gethostname() + ".log")

# encoding='utf-8'
logging.basicConfig(filename=log_path, level=logging.DEBUG,
                    filemode='w', format='%(levelname)s:%(asctime)s:%(message)s',
                    datefmt='%Y-%d-%m %H:%M:%S')
logging.debug('Welcome to use FrexT Test System!')
logging.info('This component a sub component of FrexT project.')
logging.warning('Providing testing service,')
logging.error('Current version is v1.0.0,')
logging.critical("For helping, please see localhost:8030/help/")


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FrexTTest.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
