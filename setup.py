# -*- coding:utf-8 -*-
# R. Souweine, 2015

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


def grep_version():
    with open('pgmap/__init__.py') as f:
        for line in f.readlines():
            if line.startswith('__version__'):
                return line.split("=")[1].replace(" ", "").replace("\n", "").replace('"', "")

setup(
    name='pgmap',
    version=grep_version(),  # version='0.0.1b0',
    description='Plot map from the result of PostgreSQL queries.',
    long_description=readme(),
    classifiers=[
        'Development Status :: Beta',
        'License :: OSI Approved :: GNU',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    keywords='PostgreSQL map query SQL',
    url='https://github.com/rhum1s/pgmap',
    author='Romain Souweine',
    author_email='romain.souweine@hotmail.fr',
    license='GNU',
    packages=['pgmap'],
    include_package_data=True,
    install_requires=[
        "psycopg2",
        "pandas",
        "geopandas",
        "matplotlib",
        "numpy"
    ],
    zip_safe=False)