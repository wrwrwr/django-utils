from setuptools import setup, find_packages


setup(
    name='Yet another Django utils',
    version='0.2',
    author='Wojtek Ruszczewski',
    author_email='django@wr.waw.pl',
    description='Collection of random utilities for Django.',
    license='MIT',
    url='https://github.com/wrwrwr/django-utils',
    include_package_data=True,
    packages=find_packages())
