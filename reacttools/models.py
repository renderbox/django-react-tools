from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.utils.text import slugify
from django.templatetags.static import static

REACT_MANIFEST_FILE = getattr(settings, 'REACT_MANIFEST_FILE', "asset-manifest.json")
REACT_BUILD_COMMAND = getattr(settings, 'REACT_BUILD_COMMAND', "npm run build")

class ReactAppSettings(models.Model):

    name = models.CharField(_("React App Name"), max_length=32, help_text="The React App name you want to use.")
    slug = models.SlugField(max_length=32)
    js_data = models.TextField(blank=True)
    css_data = models.TextField(blank=True)
    static_path_prefix = models.CharField(max_length=128, blank=True, help_text="Tells collectreact wether or not to insert an extra directory into the static file path (i.e. js/prefix/main.chunk.js).  Blank is no prefix.")
    manifest = models.CharField(max_length=128, blank=True, help_text="Defaults to '%s' from the REACT_MANIFEST_FILE value in settings.py." % (REACT_MANIFEST_FILE) )
    build_cmd = models.CharField(max_length=128, blank=True, help_text="Defaults to '%s' from the REACT_BUILD_COMMAND value in settings.py." % (REACT_BUILD_COMMAND) )
    project_dir = models.CharField(max_length=128, help_text="This can be a relative path and will be expanded on use.")
    build_dir = models.CharField(max_length=128, blank=True, help_text="Default assumes that the build path is at the root of the project (i.e. project_dir/build/).")
    react_root = models.CharField(max_length=64, blank=True, default='root', help_text="Defaults the DIV id to 'root' for attaching the React App to." )
    enabled = models.BooleanField(_("Enabled"), default=False)      # Is this location available?

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):

        if not self.manifest:
            self.manifest = REACT_MANIFEST_FILE

        self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    @property
    def js(self):
        return str(self.js_data).split()

    @property
    def css(self):
        return str(self.css_data).split()

    def js_paths(self):
        if self.static_path_prefix:
            return [ static("js/%s/%s" % (self.static_path_prefix, s) ) for s in self.js ]
        return [ static("js/%s" % (s) ) for s in self.js ]
    
    def css_paths(self):
        if self.static_path_prefix:
            return [ static("css/%s/%s" % (self.static_path_prefix, s) ) for s in self.css ]
        return [ static("css/%s" % (s) ) for s in self.css ]
