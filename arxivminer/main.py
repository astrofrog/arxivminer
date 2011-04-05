#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import urllib
import gzip
import tarfile
from StringIO import StringIO


def get_tar_file(arxiv_id):

    # Open URL to tar.gz file
    u = urllib.urlopen('http://arxiv.org/e-print/%s' % arxiv_id)

    # Retrieve gzipped tar file
    gzipped_file = gzip.GzipFile(fileobj=StringIO(u.read()))

    # Retrieve tar file
    tar_file = tarfile.TarFile(fileobj=gzipped_file)

    return tar_file


class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')


class Viewer(webapp.RequestHandler):
    def get(self):
        arxiv_id = self.request.get('arxiv_id')
        self.response.out.write('ArXiV ID:')
        self.response.out.write(arxiv_id)
        self.response.out.write('<br>Contains files:')
        tar_file = get_tar_file(arxiv_id)
        for filename in tar_file.getnames():
            self.response.out.write(filename + "<br>")


def main():
    application = webapp.WSGIApplication([
                                         ('/', MainHandler),
                                         ('/view', Viewer)
                                         ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
