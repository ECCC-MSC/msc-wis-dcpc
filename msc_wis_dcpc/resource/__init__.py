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

import logging
import os

from msc_wis_dcpc.catalogue import PycswCatalogue, PygeoapiCatalogue


LOGGER = logging.getLogger(__name__)


class Resource:
    def __init__(self):
        self.type = None

    def add_to_catalogue(self, **kwargs: dict):
        catalogue_type = os.environ.get('MSC_WIS_DCPC_CATALOGUE_TYPE', 'pycsw')
        catalogue_backend = os.environ.get('MSC_WIS_DCPC_DATABASE_URI', None)

        if catalogue_type == 'pycsw':
            catalogue_init = PycswCatalogue
        elif catalogue_type == 'pygeoapi':
            catalogue_init = PygeoapiCatalogue

        self.catalogue = catalogue_init(catalogue_type, catalogue_backend)
