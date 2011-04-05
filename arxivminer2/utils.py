from django.http import HttpResponse, HttpRequest
from django.template import RequestContext, loader

import urllib
import gzip
import tarfile
from StringIO import StringIO
import base64
import os

import cgi

def get_tar_file(arxiv_id):

    # Open URL to tar.gz file
    u = urllib.urlopen('http://arxiv.org/e-print/%s' % arxiv_id)

    # Retrieve gzipped tar file
    gzipped_file = gzip.GzipFile(fileobj=StringIO(u.read()))

    # Retrieve tar file
    tar_file = tarfile.TarFile(fileobj=gzipped_file)

    return tar_file

def get_abstract(content):
    content = content.split('\\begin{abstract}')[1]
    abstract = content.split('\\end{abstract}')[0]
    return abstract

def view(*args, **kwargs):

    arxiv_id = kwargs['arxiv_id']

    if not os.path.exists('cache/%s' % arxiv_id):
        os.mkdir('cache/%s' % arxiv_id)

    tar_file = get_tar_file(arxiv_id)

    # Create list of figures
    figures = []

    # Extract main tex
    tex = tar_file.extractfile('ms.tex').read().replace('\n','')

    figure_strings = []

    for filename in tar_file.getnames():

        if '.eps' in filename:

            if not os.path.exists('cache/%s/%s' % (arxiv_id, filename)):

                # Make PNG thumbnail
                open('cache/%s/%s' % (arxiv_id, filename), 'wb').write(tar_file.extractfile(filename).read())
                os.system('convert -resize 200x200 -gravity center -extent 200x200 cache/%s/%s cache/%s/%s' % (arxiv_id, filename, arxiv_id, filename.replace('.eps', '.png')))

            # Encode in base 64 to include directly into HTML
            string = base64.b64encode(open('cache/%s/%s' % (arxiv_id, filename.replace('.eps', '.png')), 'rb').read())

            # Append figure to list
            figure_strings.append(string)

    abstract = get_abstract(tex)

    tables = []

    t = loader.get_template('view.html')
    c = RequestContext(HttpRequest(), {'arxiv_id':arxiv_id, 'figures':figure_strings, 'abstract':abstract, 'tables':tables})

    return HttpResponse(t.render(c))
