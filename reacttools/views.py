import requests

from django.urls import reverse_lazy
from django import http
from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import render
from django.template import engines
from django.contrib.staticfiles.templatetags.staticfiles import static

REACT_DEV_MODE = getattr(settings, 'REACT_DEV_MODE', True)
REACT_DEV_SERVER = getattr(settings, 'REACT_DEV_SERVER', 'http://localhost:3000/')

'''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <link rel="shortcut icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="theme-color" content="#000000">
    <!--
      manifest.json provides metadata used when your web app is added to the
      homescreen on Android. See https://developers.google.com/web/fundamentals/web-app-manifest/
    -->
    <link rel="manifest" href="/manifest.json">

    <!--
      Notice the use of  in the tags above.
      It will be replaced with the URL of the `public` folder during the build.
      Only files inside the `public` folder can be referenced from the HTML.

      Unlike "/favicon.ico" or "favicon.ico", "/favicon.ico" will
      work correctly both with client-side routing and a non-root public URL.
      Learn how to configure a non-root public URL by running `npm run build`.
    -->
    <title>React App</title>
  </head>
  <body>
    <!-- <script>window._apiHostname = 'http://localhost:8000';</script>
    <script>window._imageUploadHostname = 'http://172.30.202.141:8000';</script> -->
    <noscript>
      You need to enable JavaScript to run this app.
    </noscript>
    <div id="root"></div>
    <!--
      This HTML file is a template.
      If you open it directly in the browser, you will see an empty page.

      You can add webfonts, meta tags, or analytics to this file.
      The build step will place the bundled scripts into the <body> tag.

      To begin the development, run `npm start` or `yarn start`.
      To create a production bundle, use `npm run build` or `yarn build`.
    -->
  <script src="/static/js/bundle.js"></script><script src="/static/js/0.chunk.js"></script><script src="/static/js/main.chunk.js"></script><script src="/main.1f54ed002f058a14d437.hot-update.js"></script></body>
</html>
'''

#--------------
# MIXINS
#--------------

class ReactProxyMixin(object):

    react_dev_server = REACT_DEV_SERVER
    react_scripts = []
    react_styles = []
    react_manifest = None

    def get_context_data(self, **kwargs):

        kwargs = super().get_context_data(**kwargs)

        if REACT_DEV_MODE:
            # Query the server for the scripts to proxy
            kwargs['react_styles'] = [ reverse_lazy( 'reacttools-proxy', args=(s,) ) for s in ['static/css/main.chunk.css'] ]
            kwargs['react_scripts'] = [ reverse_lazy( 'reacttools-proxy', args=(p,) ) for p in ['static/js/bundle.js', 'static/js/0.chunk.js', 'static/js/main.chunk.js'] ]
            kwargs['react_manifest'] = reverse_lazy( 'reacttools-proxy', args=('manifest.json', ) )
        else:
            kwargs['react_scripts'] = [ static(s) for s in self.react_scripts ]
            kwargs['react_styles'] = [ static(s) for s in self.react_styles ]
            kwargs['react_manifest'] = self.react_manifest

        return kwargs

#--------------
# VIEWS
#--------------

def proxy(request, path, upstream=REACT_DEV_SERVER):
    '''
    Based on the tutorial from Aymeric Augustin
    https://fractalideas.com/blog/making-react-and-django-play-well-together-hybrid-app-model/    
    '''
    print("PROXY-ING: %s" % (REACT_DEV_SERVER + path) )
    
    response = requests.get(REACT_DEV_SERVER + path)
    content_type = response.headers.get('Content-Type')

    if request.META.get('HTTP_UPGRADE', '').lower() == 'websocket':
        return http.HttpResponse(
            content="WebSocket connections aren't supported",
            status=501,
            reason="Not Implemented"
        )

    elif content_type == 'text/html; charset=UTF-8':
        result = http.HttpResponse(
            content=engines['django'].from_string(response.text).render(),
            status=response.status_code,
            reason=response.reason,
        )

    else:
        result = http.StreamingHttpResponse(
            streaming_content=response.iter_content(2 ** 12),
            content_type=content_type,
            status=response.status_code,
            reason=response.reason,
        )

    # //set headers to NOT cache a page
    # header("Cache-Control: no-cache, must-revalidate"); //HTTP 1.1
    # header("Pragma: no-cache"); //HTTP 1.0
    # header("Expires: Sat, 26 Jul 1997 05:00:00 GMT"); // Date in the past

    result['Cache-Control'] = "no-cache, must-revalidate"
    result['Pragma'] = "no-cache"

    return result
