# -*- coding:utf-8 -*-
# R. Souweine, 2015
#
# Required packages has intentionally not been packed in this setup as I think it's quite intrusive for the user:
# [unittest, matplotlib, mpl_toolkits.basemap, numpy, psycopg2, pandas, geopandas]

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='pgmap',
    version='0.0.1-beta',
    description='Plot map from the result of PostgreSQL queries.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 0.0.1 - Beta',
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
    zip_safe=False)