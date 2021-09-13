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

import json
import logging

import pycsw.core.admin
import pycsw.core.config
from pycsw.core import metadata as pycsw_metadata, repository, util
from pycsw.core.etree import etree

from tinydb import Query, TinyDB


LOGGER = logging.getLogger(__name__)


class Catalogue:
    def __init__(self, type_: str, backend: str) -> None:
        self.type = type_
        self.backend = backend

    def upsert_metadata(self, metadata: str) -> bool:
        raise NotImplementedError()


class PycswCatalogue(Catalogue):
    def __init__(self, type_, database_uri):
        super().__init__(type_, database_uri)
        LOGGER.debug('Setting up static context')
        self.context = pycsw.core.config.StaticContext()

        LOGGER.debug('Initializing pycsw repository')
        self.repo = repository.Repository(database_uri,
                                          self.context, table='records')

    def upsert_metadata(self, metadata: str) -> None:
        LOGGER.debug('Parsing XML')
        try:
            xml = etree.fromstring(metadata)
        except Exception as err:
            LOGGER.error(f'XML parsing failed: {err}')
            raise

        LOGGER.debug('Processing metadata')
        try:
            record = pycsw_metadata.parse_record(self.context,
                                                 xml, self.repo)[0]
            record.xml = record.xml.decode()
            LOGGER.info(f'identifier: {record.identifier}')
        except Exception as err:
            LOGGER.error(f'Metadata parsing failed: {err}')
            raise

        if self.repo.query_ids([record.identifier]):
            LOGGER.info('Updating record')
            try:
                self.repo.update(record)
                LOGGER.info('record updated')
            except Exception as err:
                LOGGER.error(f'record update failed: {err}')
                raise
        else:
            LOGGER.info('Inserting record')
            try:
                self.repo.insert(record, 'local', util.get_today_and_now())
                LOGGER.info('record inserted')
            except Exception as err:
                LOGGER.error(f'record insertion failed: {err}')
                raise

        return


class PygeoapiCatalogue(Catalogue):
    def __init__(self, type_, database_uri):
        super().__init__(type_, database_uri)

    def upsert_metadata(self, metadata: str) -> None:
        json_record = json.loads(metadata)

        anytext = ' '.join([
            json_record['properties']['title'],
            json_record['properties']['description']
        ])

        json_record['properties']['_metadata-anytext'] = anytext

        db = TinyDB(self.backend)
        record = Query()

        try:
            res = db.upsert(json_record, record.id == json_record['id'])
            LOGGER.info(f"Record {json_record['id']} upserted with internal id {res}")  # noqa
        except Exception as err:
            LOGGER.error(f'record insertion failed: {err}')
            raise
