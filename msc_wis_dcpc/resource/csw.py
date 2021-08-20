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

from owslib.csw import CatalogueServiceWeb
from owslib.fes import SortBy, SortProperty

from msc_wis_dcpc.resource import Resource


LOGGER = logging.getLogger(__name__)


class OGCCSWResource(Resource):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def add_to_catalogue(self):
        super().add_to_catalogue()
        startposition = 0
        sort_property = 'dc:title'  # a supported queryable of the CSW
        sort_order = 'ASC'  # should be 'ASC' or 'DESC'
        outputschema = 'http://www.isotc211.org/2005/gmd'

        csw = CatalogueServiceWeb(self.url)

        if 'MaxRecordDefault' in csw.constraints:
            pagesize = int(csw.constraints['MaxRecordDefault'].values[0])
        else:
            pagesize = 10

        sortby = SortBy([SortProperty(sort_property, sort_order)])

        LOGGER.info('Downloading metadata from CSW: {csw.url}')
        while True:
            LOGGER.info(f'getting records {startposition} to {startposition+pagesize}')  # noqa
            csw.getrecords2(startposition=startposition,
                            maxrecords=pagesize,
                            outputschema=outputschema,
                            esn='full',
                            sortby=sortby)
            LOGGER.debug(csw.request)
            LOGGER.debug(csw.response)
            for key, value in csw.records.items():
                LOGGER.debug('Metadata: {value.xml}')
                LOGGER.info('Saving {key} to repository')
                self.parse_and_upsert_metadata(value.xml)
            if csw.results['nextrecord'] == 0:
                break
            startposition += pagesize

        LOGGER.info('Done')
