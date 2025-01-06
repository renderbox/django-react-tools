import requests

from django.urls import reverse_lazy
from django import http
from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import render
from django.template import engines
from django.templatetags.static import static

from html.parser import HTMLParser
from reacttools.models import ReactAppSettings

REACT_DEV_MODE = getattr(settings, "REACT_DEV_MODE", False)
REACT_DEV_SERVER = getattr(settings, "REACT_DEV_SERVER", "http://localhost:3000/")

"""
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
"""


class ReactHTMLParser(HTMLParser):
    """
    This is a very targeted to extract what is needed when developing a hybrid app.
    """

    in_head = False
    in_body = False
    data = {"react_scripts": [], "react_manifest": None}

    def handle_starttag(self, tag, attrs):

        if tag == "head":
            self.in_head = True

        if tag == "body":
            self.in_body = True

        if tag == "script" and self.in_body:  # Extract the Script Tags
            for attr in attrs:
                if attr[0] == "src":
                    self.data["react_scripts"].append(
                        attr[1][1:]
                    )  # Strips off the leading "/"

        if tag == "link" and self.in_head:  # Extract the Manifest Tags
            manifest_tag = False
            for attr in attrs:
                if manifest_tag and attr[0] == "href":
                    self.data["react_manifest"] = attr[1][
                        1:
                    ]  # Strips off the leading "/"
                    manifest_tag = False
                if attr[0] == "rel" and attr[1] == "manifest":
                    manifest_tag = True

    def handle_endtag(self, tag):

        if tag == "head":
            self.in_head = False

        if tag == "body":
            self.in_body = False


# --------------
# MIXINS
# --------------


class ReactEmbedMixin(object):

    react_dev_server = REACT_DEV_SERVER  # todo: Figure out way to support different servers at the same time in the proxy
    react_settings = None

    def get_context_data(self, **kwargs):

        kwargs = super().get_context_data(**kwargs)

        if REACT_DEV_MODE:
            # Query the server for the scripts to proxy
            response = requests.get(self.react_dev_server)
            content = engines["django"].from_string(response.text).render()

            parser = ReactHTMLParser()
            parser.feed(content)

            kwargs["react_root"] = []
            kwargs["react_styles"] = []
            kwargs["react_scripts"] = [
                "%s%s" % (self.react_dev_server, p)
                for p in parser.data["react_scripts"]
            ]
            kwargs["react_manifest"] = "%s%s" % (
                self.react_dev_server,
                parser.data["react_manifest"],
            )
        else:
            kwargs["react_root"] = []
            kwargs["react_scripts"] = []
            kwargs["react_styles"] = []
            kwargs["react_manifest"] = []

            for config in ReactAppSettings.objects.filter(slug=self.react_settings):
                kwargs["react_root"].append(config.react_root)
                kwargs["react_scripts"].extend(config.js_paths())
                kwargs["react_styles"].extend(config.css_paths())
                kwargs["react_manifest"].append(config.manifest)

        return kwargs


class ReactProxyMixin(object):

    react_dev_server = REACT_DEV_SERVER  # todo: Figure out way to support different servers at the same time in the proxy
    react_proxy_resource_name = "reacttools-proxy"
    react_settings = None

    def get_context_data(self, **kwargs):

        kwargs = super().get_context_data(**kwargs)

        if REACT_DEV_MODE:
            # Query the server for the scripts to proxy
            response = requests.get(self.react_dev_server)
            content = engines["django"].from_string(response.text).render()

            parser = ReactHTMLParser()
            parser.feed(content)

            kwargs["react_styles"] = []
            kwargs["react_scripts"] = [
                reverse_lazy(self.react_proxy_resource_name, args=(p,))
                for p in parser.data["react_scripts"]
            ]
            kwargs["react_manifest"] = reverse_lazy(
                self.react_proxy_resource_name, args=(parser.data["react_manifest"],)
            )
        else:
            config = ReactAppSettings.objects.get(slug=self.react_settings)
            kwargs["react_scripts"] = config.js_paths()
            kwargs["react_styles"] = config.css_paths()
            kwargs["react_manifest"] = config.manifest

        return kwargs


# --------------
# VIEWS
# --------------


class IndexView(ReactEmbedMixin, TemplateView):
    template_name = "reacttools/index.html"


# import requests
# from django import http
# from django.conf import settings
# from django.template import engines
# from django.shortcuts import render
# from django.views.generic import TemplateView
# from django.contrib.auth.mixins import LoginRequiredMixin

# --------------
# BASE VIEWS - Any base level views you will inherit in your views
# --------------


# --------------
# MIXINS - Local Mixins that you create
# --------------


# --------------
# VIEWS - Views for your app
# --------------


class ReactAppView(TemplateView):
    """
    View for serving React apps using the App config model.
    """

    template_name = "reacttools/react_app_view.html"
    react_settings = "react-app"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["js_debug"] = settings.REACT_DEBUG

        ctx["react_root"] = []
        ctx["react_scripts"] = []
        ctx["react_styles"] = []
        ctx["react_manifest"] = []

        for config in ReactAppSettings.objects.filter(slug=self.react_settings):
            ctx["react_root"].append(config.react_root)
            ctx["react_scripts"].extend(config.js_paths())
            ctx["react_styles"].extend(config.css_paths())
            ctx["react_manifest"].append(config.manifest)

        return ctx


def proxy(request, path):
    """
    Based on the guide from Aymeric Augustin
    https://fractalideas.com/blog/making-react-and-django-play-well-together-hybrid-app-model/
    """

    if settings.DEBUG:
        print("PROXY-ING: %s" % (REACT_DEV_SERVER + path))  # todo: move to logger?

    response = requests.get(REACT_DEV_SERVER + path)
    content_type = response.headers.get("Content-Type")

    # print(request.META)

    if (
        request.META.get("HTTP_UPGRADE", "").lower() == "websocket"
    ):  # REDIRECT TO NODE SERVER
        # return http.HttpResponse(
        #     content="WebSocket connections aren't supported",
        #     status=501,
        #     reason="Not Implemented"
        # )
        return http.HttpResponseRedirect(REACT_DEV_SERVER + path)  # This might work

    elif content_type == "text/html; charset=UTF-8":
        result = http.HttpResponse(
            content=engines["django"].from_string(response.text).render(),
            status=response.status_code,
            reason=response.reason,
        )

    else:
        return http.StreamingHttpResponse(
            streaming_content=response.iter_content(2**12),
            content_type=content_type,
            status=response.status_code,
            reason=response.reason,
        )

    # set headers to NOT cache so the scripts are always live
    # header("Cache-Control: no-cache, must-revalidate"); //HTTP 1.1
    # header("Pragma: no-cache"); //HTTP 1.0
    # header("Expires: Sat, 26 Jul 1997 05:00:00 GMT"); // Date in the past

    result["Cache-Control"] = "no-cache, must-revalidate"
    result["Pragma"] = "no-cache"

    return result
