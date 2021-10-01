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

from copy import deepcopy
import logging
import os
from typing import Tuple
from urllib.parse import urlencode
import yaml

try:
    from pygeometa.core import read_mcf
    from pygeometa.schemas.ogcapi_records import OGCAPIRecordOutputSchema
    from pygeometa.schemas.wmo_cmp import WMOCMPOutputSchema
except ImportError:
    pass

from msc_wis_dcpc.resource import Resource


LOGGER = logging.getLogger(__name__)


class GeoMetResource(Resource):
    def __init__(self, config: str, mcf_dir: str):
        super().__init__()
        self.url = 'https://geo.weather.gc.ca/geomet'
        self.config = config
        self.mcf_dir = mcf_dir

    def add_to_catalogue(self):
        super().add_to_catalogue()

        passed = 0
        failed = 0

        with open(self.config) as fh:
            d = yaml.load(fh, Loader=yaml.CLoader)
            for key, value in d['layers'].items():
                try:
                    identifier, metadata = self.generate_metadata(key, value)
                    self.catalogue.upsert_metadata(metadata)
                    passed += 1
                except Exception as err:
                    failed += 1
                    msg = f"ERROR {value['forecast_model']['mcf']}: {err}"
                    LOGGER.error(msg)
                    continue
                # break

        LOGGER.debug(f"TOTAL: {len(d['layers'])}")
        LOGGER.debug(f'PASSED: {passed}')
        LOGGER.debug(f'FAILED: {failed}')

    def generate_metadata(self, layer_name: str,
                          layer_values: str) -> Tuple[str, str]:
        LOGGER.info(f'processing layer {layer_name}')
        mcf = os.path.join(self.mcf_dir, 'mcf',
                           layer_values['forecast_model']['mcf'])

        try:
            m = read_mcf(mcf)
        except Exception as err:
            msg = f'ERROR {mcf}: {err}'
            LOGGER.error(msg)
            raise

        identifier = f"urn:x-wmo:md:int.wmo.wis::{m['metadata']['identifier']}-{layer_name}"  # noqa

        m['metadata']['identifier'] = identifier

        m['identification']['title']['en'] += f" - {layer_values['label_en']}"
        m['identification']['title']['fr'] += f" - {layer_values['label_fr']}"

        m['identification']['otherconstraints_wmo_data_policy'] = 'WMOEssential'  # noqa
        m['identification']['otherconstraints_wmo_gts_priority'] = 'GTSPriority1'  # noqa

        m['identification']['keywords']['wmo'] = {
            'keywords': {
                'en': ['weatherObservations']
            },
            'keywords_type': 'theme'
        }

        wms_params = {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetCapabilities',
            'layer': layer_name
        }

        wms_link_base = {
            'name': {
                'en': layer_values['label_en'],
                'fr': layer_values['label_fr']
            },
            'type': 'OGC:WMS',
            'description': {
                'en': m['identification']['abstract']['en'],
                'fr': m['identification']['abstract']['fr']
            },
            'function': 'download',
            'hnap_contenttype': {
                'en': 'Web Service',
                'fr': 'Service Web',
            },
            'format': {
                'en': 'WMS',
                'fr': 'WMS'
            },
            'format_version': '1.3.0'
        }

        bbox = ','.join(map(
            str, m['identification']['extents']['spatial'][0]['bbox']))

        wms_browse_graphic_params = {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetMap',
            'layers': layer_name,
            'bbox': bbox,
            'crs': f"EPSG:{m['identification']['extents']['spatial'][0]['crs']}",  # noqa
            'format': 'image/png',
            'width': 400,
            'height': 300
        }

        m['identification']['browsegraphic'] = generate_url(
            self.url, wms_browse_graphic_params)

        m['distribution']['wms_eng-CAN'] = deepcopy(wms_link_base)

        m['distribution']['wms_eng-CAN']['url'] = generate_url(
            self.url, wms_params)

        m['distribution']['wms_fra-CAN'] = deepcopy(wms_link_base)

        wms_params['lang'] = 'fr'

        m['distribution']['wms_fra-CAN']['url'] = generate_url(
            self.url, wms_params)

        if self.catalogue.type == 'pycsw':
            output_schema = WMOCMPOutputSchema
        elif self.catalogue.type == 'pygeoapi':
            output_schema = OGCAPIRecordOutputSchema

        try:
            metadata = output_schema().write(m)
        except Exception as err:
            msg = f'ERROR {mcf}: {err}'
            LOGGER.error(msg)
            raise

        return identifier, metadata


def generate_url(url_base: str, url_params: str) -> str:
    """
    Generates URL from url and query string KVPs

    :param url_base: base URL
    :param url_params: `dict` of query string KVPs

    :returns: URL
    """

    return f'{url_base}?{urlencode(url_params)}'
