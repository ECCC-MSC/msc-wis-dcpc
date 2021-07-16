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

# you should be okay from here

DATETIME=`date +%Y%m%d`
TIMESTAMP=`date +%Y%m%d.%H%M`
NIGHTLYDIR=msc-wis-dcpc-$TIMESTAMP

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
cd ../pycsw
pip install cython "pyproj<3" OWSLib
python3 setup.py install
pip3 install -r requirements-standalone.txt
cd ..

cp msc-wis-dcpc/deploy/default/msc-wis-dcpc-pycsw-config.cfg msc-wis-dcpc/deploy/nightly
cd ..

ln -s $NIGHTLYDIR latest
