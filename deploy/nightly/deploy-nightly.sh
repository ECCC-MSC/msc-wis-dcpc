#!/bin/bash
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

BASEDIR=/data/web/msc-wis-dcpc-nightly
PYCSW_GITREPO=https://github.com/geopython/pycsw.git
MSC_WIS_DCPC_GITREPO=https://github.com/ECCC-MSC/msc-wis-dcpc.git
DAYSTOKEEP=7
MSC_WIS_DCPC_URL=https://geomet-dev-03-nightly.cmc.ec.gc.ca/msc-wis-dcpc/nightly/latest
MSC_DISCOVERY_METADATA_REPO=https://gccode.ssc-spc.gc.ca/ec-msc/discovery-metadata/-/archive/master/discovery-metadata-master.zip

# you should be okay from here

DATETIME=`date +%Y%m%d`
TIMESTAMP=`date +%Y%m%d.%H%M`
NIGHTLYDIR=msc-wis-dcpc-$TIMESTAMP

export MSC_WIS_DCPC_DATABASE_URI=sqlite:///$BASEDIR/$NIGHTLYDIR/data/records.db
export MSC_WIS_DCPC_DATABASE_TABLE=records

echo "Deleting nightly builds > $DAYSTOKEEP days old"

cd $BASEDIR

for f in `find . -type d -name "msc-wis-dcpc-20*"`
do
    DATETIME2=`echo $f | awk -F- '{print $4}' | awk -F. '{print $1}'`
    let DIFF=(`date +%s -d $DATETIME`-`date +%s -d $DATETIME2`)/86400
    if [ $DIFF -gt $DAYSTOKEEP ]; then
        rm -fr $f
    fi
done

rm -fr latest
echo "Generating nightly build for $TIMESTAMP"
python3.6 -m venv $NIGHTLYDIR && cd $NIGHTLYDIR
source bin/activate
git clone $MSC_WIS_DCPC_GITREPO
git clone $PYCSW_GITREPO
cd msc-wis-dcpc
python3 setup.py install
cd ../pycsw
pip install cython "pyproj<3" OWSLib
python3 setup.py install
pip3 install -r requirements-standalone.txt
cd ..

cp msc-wis-dcpc/deploy/default/msc-wis-dcpc-pycsw-config.cfg msc-wis-dcpc/deploy/nightly

echo "Generating metadata repository"

rm -fr /tmp/discovery-metadata-master.zip /tmp/discovery-metadata-master/

mkdir data
curl -o /tmp/disovery-metadata-master.zip $MSC_DISCOVERY_METADATA_REPO
unzip /tmp/disovery-metadata-master.zip -d /tmp
pycsw-admin.py setup-db -c msc-wis-dcpc/deploy/nightly/msc-wis-dcpc-pycsw-config.cfg
pycsw-admin.py load-records -c msc-wis-dcpc/deploy/nightly/msc-wis-dcpc-pycsw-config.cfg -p /tmp/discovery-metadata-master/legacy/wis/records -r -y
msc-wis-dcpc metadata add --type OGC:CSW --url https://geo.woudc.org/csw
msc-wis-dcpc metadata add --type MSC:GeoMet:config --config /data/web/geomet2-nightly/latest/build/etc/geomet.yml --mcf-dir /tmp/discovery-metadata-master

cd ..

rm -fr /tmp/discovery-metadata-master.zip /tmp/discovery-metadata-master/

ln -s $NIGHTLYDIR latest
