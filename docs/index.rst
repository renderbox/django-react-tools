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

then add ‘reacttools’ & 'django.contrib.sites' to your django project’s list of apps.

The default destination location is the Static Root directory for your
Django project. You can change it by modifying the setting variable.

.. code:: python

   REACT_DJANGO_DEST = settings.STATIC_ROOT

The default React Manifest file is set to "asset-manifest.json".  If you are 
using a newer version of React (16.8+) you will want to change this value to 
"manifest.json" in your settings.py file.

.. code:: python

   REACT_MANIFEST_FILE = "asset-manifest.json"

By default the React project is buit using “yarn build”. If you want to
change the command you can:

.. code:: python

   REACT_BUILD_COMMAND = "npm build"

**Updated in v0.2.0**

Starting with v0.2.0 much of the configuration has been moved into Django models.  This is so we can support multiple React projects within the same Django Project.

To create the configurations, you need first migrate to create the tables:

.. code:: python

   ./manage.py migrate

In the admin panel, navigate to ReactTools > ReactAppSettings.

Here, create a new React App Settings record.  The only two required fields are the "React App Name" and "Project Dir".  

It's also reconmended that you make sure the settings are set to 'enabled'.  This allows the 'collectreact' management command know which apps to look for.

After you save your React App Settings, you will notice at the bottom of the page, the slug field.  You will need this for your view class that hosts your app.

The next step is to place the 'ReactEmbedMixin' view to the view controlling your React app.  In there add the attribute: react_settings = "react-app-slug" to the view class.  Notice that the value is for the slug from the model.  This is so the view knows which React app to use.

.. code:: python
    
    from reacttools.views import ReactProxyMixin
    
    class MyAppView(ReactProxyMixin, TemplateView):
        template_name = "myapp/template.html"
        react_settings = "react-app-slug"


To run all you need to do is call the management command.

.. code:: bash

   > ./manage.py collectreact

This will find all the enabled react app settings and run the processing for each.

If you want to skip the build you can run the comman this way:

.. code:: bash

   > ./manage.py collectreact --no-build
   

Experimental Features
---------------------

These features are a work in progress and do have some small known issues (like hot reload on Dev Server can lead to multiple reloads of JS files).  If you have a suggestion on how to better aproach them, I'd love to hear from you.

There are a couple of helpers for working with React running inside of a Django rendered page, refered to as a Hybrid App.

To work with this we need include two more variables to help enable the features.

.. code:: bash

    REACT_DEV_SERVER = 'http://localhost:3000/'
    REACT_DEV_MODE = True

The REACT_DEV_SERVER defaults to 'http://localhost:3000/' so you only need to include it if you are using a different address and port.

Setting REACT_DEV_MODE to True tells the ReactProxyMixin to use the proxy (REACT_DEV_SERVER) for finding the scripts instead of using the ones provided to a View using ReactProxyMixin in production.

To make this all work in development, we end up proxying the JavaScript and manifest files through the Django Project from the Node Server.  We do this so the App is loaded in the page's context while still letting the developer stay in managed mode from create-react-app so they can nearly hot-load their changes.

.. code:: python

    path('reacttools/', include('reacttools.urls'))

If you have a view that is hosting the Hybrid App, it's easiest to use a Generic Class Based View with the ReactProxyMixin also inherited.

.. code:: python

    class MyReactAppView(ReactProxyMixin, TemplateView):
        template_name = "reactapp/react_app_view.html"
        react_scripts = ['js/bundle.js', 'js/0.chunk.js', 'js/main.chunk.js']    # These are the production scripts
        react_styles = []

In the above example, the react_scripts would be the scripts used in production.  When you have REACT_DEV_MODE = True set, these are ignored and the mixin will query the server to get a list of JS files.

To make this all show up properly, you will want to include these tags in your template.

Put these in the <head> to make sure to get the manifest and and CSS files.

.. code:: python

    {% if react_manifest %}
        <link rel="manifest" href="{{ react_manifest }}">
    {% endif %}

    {% for css in react_styles %}
    <link href="{{ css }}" rel="stylesheet">
    {% endfor %}

Put this at the bottom of your body, near the closing tag to include the JS files.

.. code:: python

    {% for js in react_scripts %}
    <script src="{{ js }}"></script>
    {% endfor %}

In case the proxy's resource name (URL / named path) is different than the default, the Attribute on ReactProxyMixin can be changed to reflect the new name.  The default is 'reacttools-proxy'.

.. code:: python

    react_proxy_reverse_name = 'reacttools-proxy'


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
