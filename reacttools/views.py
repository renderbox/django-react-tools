import requests

from django.urls import reverse_lazy
from django import http
from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import render
from django.template import engines
from django.contrib.staticfiles.templatetags.staticfiles import static

from html.parser import HTMLParser

REACT_DEV_MODE = getattr(settings, 'REACT_DEV_MODE', False)
REACT_DEV_SERVER = getattr(settings, 'REACT_DEV_SERVER', 'http://localhost:3000/')

'''
Sample React Node Server Data:

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
    <script src="/static/js/bundle.js"></script>
    <script src="/static/js/0.chunk.js"></script>
    <script src="/static/js/main.chunk.js"></script>
    <script src="/main.1f54ed002f058a14d437.hot-update.js"></script>
  </body>
</html>
'''

class ReactHTMLParser(HTMLParser):
    '''
    This is a very targeted to extract what is needed when developing a hybrid app.
    '''
    in_head = False
    in_body = False
    data = { 'react_scripts':[], 'react_manifest':None }

    def handle_starttag(self, tag, attrs):

        if tag == "head":
            self.in_head = True

        if tag == "body":
            self.in_body = True

        if tag == "script" and self.in_body:     # Extract the Script Tags
            for attr in attrs:
                if attr[0] == 'src':
                    self.data['react_scripts'].append(attr[1][1:])  # Strips off the leading "/"

        if tag == "link" and self.in_head:     # Extract the Manifest Tags
            manifest_tag = False
            for attr in attrs:
                if manifest_tag and attr[0] == 'href':
                    self.data['react_manifest'] = attr[1][1:]       # Strips off the leading "/"
                    manifest_tag = False
                if attr[0] == 'rel' and attr[1] == 'manifest':
                    manifest_tag = True

    def handle_endtag(self, tag):

        if tag == "head":
            self.in_head = False

        if tag == "body":
            self.in_body = False


#--------------
# MIXINS
#--------------

class ReactProxyMixin(object):

    react_dev_server = REACT_DEV_SERVER       # todo: Figure out way to support different servers at the same time in the proxy
    react_proxy_resource_name = 'reacttools-proxy'
    react_scripts = []
    react_styles = []
    react_manifest = None

    def get_context_data(self, **kwargs):

        kwargs = super().get_context_data(**kwargs)

        if REACT_DEV_MODE:
            # Query the server for the scripts to proxy
            response = requests.get(self.react_dev_server)
            content = engines['django'].from_string(response.text).render()
            
            parser = ReactHTMLParser()
            parser.feed(content)

            kwargs['react_styles'] = []
            kwargs['react_scripts'] = [ reverse_lazy( self.react_proxy_resource_name, args=(p,) ) for p in parser.data['react_scripts'] ]
            kwargs['react_manifest'] = reverse_lazy( self.react_proxy_resource_name, args=(parser.data['react_manifest'], ) )
        else:
            kwargs['react_scripts'] = [ static(s) for s in self.react_scripts ]
            kwargs['react_styles'] = [ static(s) for s in self.react_styles ]
            kwargs['react_manifest'] = self.react_manifest

        return kwargs

#--------------
# VIEWS
#--------------

class IndexView(ReactProxyMixin, TemplateView):
    template_name = "reacttools/index.html"


def proxy(request, path):
    '''
    Based on the guide from Aymeric Augustin
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

    # set headers to NOT cache so the scripts are always live
    # header("Cache-Control: no-cache, must-revalidate"); //HTTP 1.1
    # header("Pragma: no-cache"); //HTTP 1.0
    # header("Expires: Sat, 26 Jul 1997 05:00:00 GMT"); // Date in the past

    result['Cache-Control'] = "no-cache, must-revalidate"
    result['Pragma'] = "no-cache"

    return result
