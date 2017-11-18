from os import path
from setuptools import setup, find_packages
import codecs

here = path.abspath(path.dirname(__file__))

with codecs.open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'spotify-token.pickle'), 'w') as f:
    f.write('sample-spotify-token')

setup(
    name='gwa_spotify_api',
    version='0.0.2',
    description='wrapper for spotify web api',
    long_description=long_description,
    url='https://github.com/goodwordalchemy/spotify-api',
    author='David Goldberg',
    author_email='goodwordalchemy@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    keywords='spotify api wrapper',
    packages=find_packages(),
    data_files=[('data', ['spotify-token.pickle'])],
    python_requires='>=3',
    install_requires=['rauth']
)

