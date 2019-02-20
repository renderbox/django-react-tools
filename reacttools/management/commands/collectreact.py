#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-12-21 15:12:35
#--------------------------------------------
import os
import subprocess
import json

from django.core.management.base import BaseCommand
# from django.contrib.staticfiles.storage import staticfiles_storage
# from django.core.files.storage import FileSystemStorage
from django.conf import settings

REACT_PROJECT_DIRECTORY = os.path.join(settings.BASE_DIR, "..", "react-test-app")
REACT_BUILD_DIRECTORY = os.path.join(REACT_PROJECT_DIRECTORY, "build")
REACT_BUILD_COMMAND = "yarn build"
REACT_FILE_TYPES = ['js', 'css', 'svg']
REACT_DJANGO_DEST = settings.STATIC_ROOT

class Command(BaseCommand):

    help = "Collects the static files generated from a React project and moves them to the project's static directory"
    debug = True

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-build', action='store_true', dest='no_build',
            help="Including this will skip the React build step.",
        )
        parser.add_argument(
            '-n', '--dry-run', action='store_true',
            help="Do everything except modify the filesystem.",
        )

    def set_options(self, **options):
        """
        Set instance variables based on an options dict
        """
        self.nobuild = options['no_build']

    def handle(self, *args, **options):
        self.set_options(**options)

        try:
            # print("Done")
            self.process()

        except KeyboardInterrupt:
            print("\nExiting...")
            return

    def process(self):

        if self.nobuild:
            print("Skipping Build")
        else:
            print("Building React Project")
            completed = subprocess.run("yarn build", shell=True, cwd=REACT_PROJECT_DIRECTORY)
            print('returncode:', completed.returncode)

        asset_manifest = os.path.join(REACT_BUILD_DIRECTORY, "asset-manifest.json")
        
        with open(asset_manifest) as json_file:  
            manifest = json.load(json_file)

        for key, value in manifest.items():

            if key.split(".")[-1] in REACT_FILE_TYPES:
                # print(key)
                relative_value = value[1:]
                source = os.path.abspath(os.path.join( REACT_BUILD_DIRECTORY, relative_value ))
                dest = self.destination_path(relative_value) 

                print("Copying: %s -> %s" % (source, dest) )
                
    def destination_path(self, file_path):

        # Pop static
        path_parts = file_path.split("/")
        if path_parts[0] == "static":
            path_parts.pop(0)

        result = os.path.abspath(os.path.join( REACT_DJANGO_DEST, *path_parts ))

        return result