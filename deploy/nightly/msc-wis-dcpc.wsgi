# =================================================================
#
# Author: Tom Kralidis <tom.kralidis@ec.gc.ca>
#
# Copyright (c) 2021 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import os

os.environ['MSC_WIS_DCPC_LOGGING_LOGLEVEL'] = 'ERROR'
os.environ['MSC_WIS_DCPC_LOGGING_LOGFILE'] = '/tmp/msc-wis-dcpc.log'
os.environ['MSC_WIS_DCPC_DATABASE_URI'] = 'sqlite:////data/web/msc-wis-dcpc-nightly/data/records.db'
os.environ['MSC_WIS_DCPC_DATABASE_TABLE'] = 'records'
os.environ['MSC_WIS_DCPC_URL'] = 'https://geomet-dev-03-nightly.cmc.ec.gc.ca/msc-wis-dcpc/nightly/latest'
os.environ['PYCSW_CONFIG'] = 'data/web/msc-wis-dcpc-nightly/latest/msc-wis-dcpc/deploy/nightly/msc-wis-dcpc-pycsw-config.cfg'


from pycsw.wsgi_flask import APP as application
