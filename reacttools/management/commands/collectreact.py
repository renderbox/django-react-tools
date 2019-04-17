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
import fileinput

from django.core.management.base import BaseCommand
# from django.contrib.staticfiles.storage import staticfiles_storage    # For future use
# from django.core.files.storage import FileSystemStorage
from django.conf import settings


# Settings Variables

REACT_PROJECT_DIRECTORY = getattr(settings, 'REACT_PROJECT_DIRECTORY', os.path.join(settings.BASE_DIR, "..", "react-test-app"))
REACT_BUILD_DIRECTORY = getattr(settings, 'REACT_BUILD_DIRECTORY', os.path.join(REACT_PROJECT_DIRECTORY, "build"))
REACT_BUILD_COMMAND = getattr(settings, 'REACT_BUILD_COMMAND', "yarn build")
REACT_FILE_TYPES = getattr(settings, 'REACT_FILE_TYPES', ['js', 'css', 'svg'])
REACT_DJANGO_DEST = getattr(settings, 'REACT_DJANGO_DEST', settings.STATIC_ROOT)
REACT_INCLUDE_MAP_FILES = getattr(settings, 'REACT_INCLUDE_MAP_FILES', 'map' in REACT_FILE_TYPES)
REACT_FILE_PREFIX = getattr(settings, 'REACT_FILE_PREFIX', None)
REACT_INCLUDED_NON_STATIC = getattr(settings, 'REACT_INCLUDED_NON_STATIC', False)
REACT_MANIFEST_FILE = getattr(settings, 'REACT_MANIFEST_FILE', "asset-manifest.json")


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
            print("Building React Project: '%s'" % REACT_BUILD_COMMAND)
            completed = subprocess.run(REACT_BUILD_COMMAND, shell=True, cwd=REACT_PROJECT_DIRECTORY)
            print('returncode:', completed.returncode)

        asset_manifest = os.path.join(REACT_BUILD_DIRECTORY, REACT_MANIFEST_FILE)
        
        with open(asset_manifest) as json_file:  
            manifest = json.load(json_file)

        for key, value in manifest.items():

            if key.split(".")[-1] in REACT_FILE_TYPES:
                # print(key)
                relative_value = value[1:]
                source = os.path.abspath(os.path.join( REACT_BUILD_DIRECTORY, relative_value ))
                dest = self.destination_path(relative_value)

                if dest == None:    # If the destination is not valid, it will return None
                    continue

                print("Copying: %s -> %s" % (source, dest) )
                # Copy the files here and overwrite the old files
                # modify any text files here

                # Check the destination folder exists
                dest_folder = os.path.dirname(dest)

                if not os.path.isdir(dest_folder):
                    os.mkdir(dest_folder)

                # Check to see if this is a file type that should be edited
                # if source.split(".")[-1] not in ['js', 'css', 'map']:
                subprocess.run("cp %s %s" % (source, dest), shell=True)
                # else:
                #     with open(source, 'r') as file :
                #         filedata = file.read()

                #     # filedata = filedata.replace('ram', 'abcd')    # Do this for each 

                #     with open(dest, 'w') as file:
                #         file.write(filedata)
            
                
    def destination_path(self, file_path):
        '''
        Returns the destination path or None.  If it's None, that means 
        the path is invalid and should be skipped.
        '''

        # Pop static
        path_parts = file_path.split("/")

        if path_parts[0] == "static":
            path_parts.pop(0)
        else:
            if not REACT_INCLUDED_NON_STATIC:
                return None

        path_parts[-1] = self.clean_name(path_parts[-1])

        if REACT_FILE_PREFIX:
            path_parts[-1] = REACT_FILE_PREFIX + path_parts[-1]

        # FORCE FILES TO BE IN APROPRIATE DIRECTORIES? (for example: 'service-worker.js', 'precache-manifest.js' default to static root)

        result = os.path.abspath(os.path.join( REACT_DJANGO_DEST, *path_parts ))

        return result

    def clean_name(self, file_name):

        parts = file_name.split(".")

        if len(parts) > 2:
            junk = parts.pop(1)

            if self.debug:
                print("Removing '%s' from '%s'" % (junk, file_name) )

        return ".".join(parts)