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

from pycsw.core import metadata as pycsw_metadata, util
from pycsw.core.etree import etree

from msc_wis_dcpc.catalogue import Catalogue


LOGGER = logging.getLogger(__name__)


class Resource:
    def __init__(self):
        self.type = None

    def add_to_catalogue(self, **kwargs: dict) -> bool:
        self.catalogue = Catalogue(os.environ.get('MSC_WIS_DCPC_DATABASE_URI'))

    def parse_and_upsert_metadata(self, xml: str):
        LOGGER.debug('Parsing XML')
        try:
            xml = etree.fromstring(xml)
        except Exception as err:
            LOGGER.error(f'XML parsing failed: {err}')
            raise

        LOGGER.debug('Processing metadata')
        try:
            record = pycsw_metadata.parse_record(self.catalogue.context,
                                                 xml, self.catalogue.repo)[0]
            record.xml = record.xml.decode()
            LOGGER.info(f'identifier: {record.identifier}')
        except Exception as err:
            LOGGER.error(f'Metadata parsing failed: {err}')
            raise

        if self.catalogue.repo.query_ids([record.identifier]):
            LOGGER.info('Updating record')
            try:
                self.catalogue.repo.update(record)
                LOGGER.info('record updated')
            except Exception as err:
                LOGGER.error(f'record update failed: {err}')
                raise
        else:
            LOGGER.info('Inserting record')
            try:
                self.catalogue.repo.insert(record, 'local',
                                           util.get_today_and_now())
                LOGGER.info('record inserted')
            except Exception as err:
                LOGGER.error(f'record insertion failed: {err}')
                raise

        return
