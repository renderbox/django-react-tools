.. Django React Tools documentation master file, created by
   sphinx-quickstart on Wed Feb 20 10:01:02 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Django React Tools's documentation!
==============================================

Tools for helping integrate ReactJS into a Django project.

The current iteration of this tool adds a simple management command to
your Django project that will build, copy to a Django static directory
and rename accordingly.

To start run

.. code:: bash

   pip install django-react-tools

then add ‘reacttools’ to your django project’s list of apps.

next in settings, set where to find the React project:

.. code:: python

   REACT_PROJECT_DIRECTORY = "/path/to/project"

The default destination location is the Static Root directory for your
Django project. You can change it by modifying the setting variable.

.. code:: python

   REACT_DJANGO_DEST = settings.STATIC_ROOT

The default React Manifest file is set to "asset-manifest.json".  If you are 
using a newer version of React (16.8+) you will want to change this value to 
"manifest.json" in your settings.py file.

.. code:: python

   REACT_MANIFEST_FILE = "asset-manifest.json"


To run all you need to do is call the management command.

.. code:: bash

   > ./manage.py collectreact

By default the React project is buit using “yarn build”. If you want to
change the command you can:

.. code:: python

   REACT_BUILD_COMMAND = "npm build"

If you want to skip the build you can run the comman this way:

.. code:: bash

   > ./manage.py collectreact --no-build
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
