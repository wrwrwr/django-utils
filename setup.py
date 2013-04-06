from setuptools import setup, find_packages


setup(
    name='Django utils',
    version='0.1',
    author='Wojtek Ruszczewski',
    author_email='django@wr.waw.pl',
    description='Collection of random utilities for Django.',
    license='MIT',
    url='https://github.com/wrwrwr/django-utils',
    include_package_data=True,
    packages=find_packages())
