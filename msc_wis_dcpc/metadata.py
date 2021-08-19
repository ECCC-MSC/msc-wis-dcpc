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

import click
from owslib.csw import CatalogueServiceWeb
from owslib.fes import SortBy, SortProperty
from pycsw.core import metadata as pycsw_metadata, repository, util
from pycsw.core.etree import etree
import pycsw.core.admin
import pycsw.core.config


LOGGER = logging.getLogger(__name__)


class Catalogue:
    def __init__(self, database_uri):
        LOGGER.debug('Setting up static context')
        self.context = pycsw.core.config.StaticContext()

        LOGGER.debug('Initializing pycsw repository')
        self.repo = repository.Repository(database_uri,
                                          self.context, table='records')


class Resource:
    def __init__(self):
        self.type = None

    def add_to_catalogue(self, **kwargs: dict) -> bool:
        self.catalogue = Catalogue(os.environ.get('MSC_WIS_DCPC_DATABASE_URI'))


class OGCCSWResource(Resource):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def add_to_catalogue(self) -> bool:
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

        return True

    def parse_and_upsert_metadata(self, xml):
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


@click.group()
def metadata():
    """Metadata management"""
    pass


@click.command()
@click.pass_context
@click.option('--type', '-t', 'type_',
              type=click.Choice(['MSC:GeoMet:config', 'OGC:CSW']),
              help='Resource type')
@click.option('--url', '-u', help='URL')
@click.option('--verbosity',
              type=click.Choice(['ERROR', 'WARNING', 'INFO', 'DEBUG']),
              help='Verbosity')
def add(ctx, type_, url, verbosity):
    """Add to metadata catalogue"""

    if verbosity is not None:
        logging.basicConfig(level=getattr(logging, verbosity))

    if type_ is None:
        raise click.ClickException('Missing -t/--type')

    if type_ == 'OGC:CSW':
        if url is None:
            raise click.ClickException('Missing -u/--url')
        csw = OGCCSWResource(url)
        csw.add_to_catalogue()


metadata.add_command(add)
