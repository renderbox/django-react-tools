# django-react-tools
Tools for helping integrate ReactJS into a Django project.

The current iteration of this tool adds a simple management command to your Django project that will build, copy to a Django static directory and rename accordingly.



To start run 

```bash
pip install django-react-tools
```

then add 'reacttools' to your django project's list of apps.

next in settings, set where to find the React project:

```python
REACT_PROJECT_DIRECTORY = "/path/to/project"
```

The default destination location is the Static Root directory for your Django project.  You can change it by modifying the setting variable.

```python
REACT_DJANGO_DEST = settings.STATIC_ROOT
```

To run all you need to do is call the management command.

```bash
> ./manage.py collectreact
```

By default the React project is buit using "yarn build".  If you want to change the command you can:

```python
REACT_BUILD_COMMAND = "npm build"
```

If you want to skip the build you can run the comman this way:
```bash
> ./manage.py collectreact --no-build
```

