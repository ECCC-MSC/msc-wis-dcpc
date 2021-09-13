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

import click

from msc_wis_dcpc.resource.csw import OGCCSWResource
from msc_wis_dcpc.resource.geomet import GeoMetResource
from msc_wis_dcpc.resource.msc_open_data import MSCOpenDataResource


LOGGER = logging.getLogger(__name__)


@click.group()
def metadata():
    """Metadata management"""
    pass


@click.command()
@click.pass_context
@click.option('--type', '-t', 'type_',
              type=click.Choice(['MSC:GeoMet:config', 'MSC:OpenData',
                                 'OGC:CSW']), help='Resource type')
@click.option('--url', '-u', help='URL')
@click.option('--config', '-c', help='MSC GeoMet configuration file')
@click.option('--mcf-dir', '-md', 'mcf_dir',
              help='Directory of MCFs associated with MSC GeoMet')
@click.option('--verbosity',
              type=click.Choice(['ERROR', 'WARNING', 'INFO', 'DEBUG']),
              help='Verbosity')
def add(ctx, type_, url, config, mcf_dir, verbosity):
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
    elif type_ == 'MSC:GeoMet:config':
        if config is None:
            raise click.ClickException('Missing -c/--config')
        if mcf_dir is None:
            raise click.ClickException('Missing -md/--mcf_dir')
        geomet = GeoMetResource(config, mcf_dir)
        geomet.add_to_catalogue()
    elif type_ == 'MSC:OpenData':
        if mcf_dir is None:
            raise click.ClickException('Missing -md/--mcf_dir')
        mod = MSCOpenDataResource(mcf_dir)
        mod.add_to_catalogue()


metadata.add_command(add)
