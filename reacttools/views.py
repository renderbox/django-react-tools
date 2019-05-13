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

#--------------
# MIXINS
#--------------

class ReactProxyMixin(object):

    react_dev_server = REACT_DEV_SERVER
    react_scripts = []
    react_styles = []

    def get_context_data(self, **kwargs):

        kwargs = super().get_context_data(**kwargs)

        if REACT_DEV_MODE:
            # Query the server for the scripts to proxy
            kwargs['react_styles'] = [ reverse_lazy( 'reacttools-proxy', args=(p,) ) for p in ['static/css/main.chunk.css'] ]
            kwargs['react_scripts'] = [ reverse_lazy( 'reacttools-proxy', args=(p,) ) for p in ['static/js/bundle.js', 'static/js/0.chunk.js', 'static/js/main.chunk.js'] ]
        else:
            kwargs['react_scripts'] = [ static(s) for s in self.react_scripts ]
            wargs['react_styles'] = [ static(s) for s in self.react_styles ]

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
