# --------------------------------------------
# Copyright 2019, Grant Viklund
# @Author: Grant Viklund
# @Date:   2019-1-22 13:50:49
# --------------------------------------------

from os import path
from setuptools import setup, find_packages

file_path = path.abspath(path.dirname(__file__))
with open(path.join(file_path, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

package_metadata = {
    'name': 'django-react-tools',
    'version': '0.1.12',
    'description': 'Tools for helping integrate ReactJS into a Django project.',
    'long_description': long_description,
    'url': 'https://github.com/renderbox/django-react-tools',
    'author': 'Grant Viklund',
    'author_email': 'renderbox@gmail.com',
    'license': '',
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
}

setup(
    **package_metadata,
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "Django>=2.1,<2.2",
        "requests>=2.21.0",
        ],
    extras_require={
        'dev': [
            'django-cors-headers==3.0.2',
        ],
        'test': [],
        'prod': [],
        'build': [],
        'docs': [
            'coverage==4.4.1',
            'Sphinx==1.6.4'],
    }
)