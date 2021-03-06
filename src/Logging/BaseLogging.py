#!/usr/bin/env python
#
# Logging.py
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA  02111-1307  USA

import os
import logging
import base64
import tempfile
import hashlib
import zipfile
import pefile

try:
    from io import StringIO
except ImportError:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

log = logging.getLogger("Thug")

class BaseLogging(object):
    def __init__(self):
        self.types = ('PE',
                      'PDF',
                      'JAR',
                      'SWF', )

    def is_pe(self, data):
        try:
            pefile.PE(data = data, fast_load = True)
        except:
            return False

        return True

    def get_imphash(self, data):
        try:
            pe = pefile.PE(data = data)
        except:
            return None

        return pe.get_imphash()

    def is_pdf(self, data):
        return (data[:1024].find('%PDF') != -1)

    def is_jar(self, data):
        fd, jar = tempfile.mkstemp()
        with open(jar, 'wb') as fd:
            fd.write(data)

        try:
            z = zipfile.ZipFile(jar)
            if [t for t in z.namelist() if t.endswith('.class')]:
                os.remove(jar)
                return True
        except:
            pass

        os.remove(jar)
        return False

    def is_swf(self, data):
        return data.startswith('CWS') or data.startswith('FWS')

    def get_sample_type(self, data):
        for t in self.types:
            p = getattr(self, 'is_%s' % (t.lower(), ), None)
            if p and p(data):
                return t

        return None

    def build_sample(self, data, url = None):
        if not data:
            return None

        p = dict()
        p['type'] = self.get_sample_type(data)
        if p['type'] is None:
            return None

        p['md5']  = hashlib.md5(data).hexdigest()
        p['sha1'] = hashlib.sha1(data).hexdigest()
        
        if p['type'] in ('PE', ):
            imphash = self.get_imphash(data)
            if imphash:
                p['imphash'] = imphash
        if url:
            p['url'] = url

        p['data'] = base64.b64encode(data)

        return p
