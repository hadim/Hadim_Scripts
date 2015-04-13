#!/usr/bin/sh

BF_VERSION="5.1"
BF_URL="http://downloads.openmicroscopy.org/latest/bio-formats$BF_VERSION/artifacts/"

FIJI_PATH=$1

rm -f $FIJI_PATH/plugins/bio-formats_plugins-*.jar

rm -f $FIJI_PATH/jars/bio-formats/jai_imageio-5.0.7.jar
rm -f $FIJI_PATH/jars/bio-formats/formats-gpl-5.0.7.jar
rm -f $FIJI_PATH/jars/bio-formats/formats-common-5.0.7.jar
rm -f $FIJI_PATH/jars/bio-formats/turbojpeg-5.0.7.jar
rm -f $FIJI_PATH/jars/bio-formats/ome-xml-5.0.7.jar
rm -f $FIJI_PATH/jars/bio-formats/formats-bsd-5.0.7.jar
rm -f $FIJI_PATH/jars/bio-formats/ome-poi-5.0.7.j.ar
rm -f $FIJI_PATH/jars/bio-formats/specification-5.0.7.jar
rm -f $FIJI_PATH/jars/bio-formats/mdbtools-java-5.0.7.jar
rm -f $FIJI_PATH/jars/bio-formats/metakit-5.0.7.jar
rm -f $FIJI_PATH/jars/bio-formats/formats-api-5.0.7.jar

wget $BF_URL/bioformats_package.jar -O $FIJI_PATH/plugins/bioformats_package.jar

wget $BF_URL/jai_imageio.jar -O $FIJI_PATH/jars/bio-formats/jai_imageio.jar
wget $BF_URL/formats-gpl.jar -O $FIJI_PATH/jars/bio-formats/formats-gpl.jar
wget $BF_URL/formats-common.jar -O $FIJI_PATH/jars/bio-formats/formats-common.jar
wget $BF_URL/turbojpeg.jar -O $FIJI_PATH/jars/bio-formats/turbojpeg.jar
wget $BF_URL/ome-xml.jar -O $FIJI_PATH/jars/bio-formats/ome-xml.jar
wget $BF_URL/formats-bsd.jar -O $FIJI_PATH/jars/bio-formats/formats-bsd.jar
wget $BF_URL/ome-poi.jar -O $FIJI_PATH/jars/bio-formats/ome-poi.jar
wget $BF_URL/specification.jar -O $FIJI_PATH/jars/bio-formats/specification.jar
wget $BF_URL/mdbtools-java.jar -O $FIJI_PATH/jars/bio-formats/mdbtools-java.jar
wget $BF_URL/metakit.jar -O $FIJI_PATH/jars/bio-formats/metakit.jar
wget $BF_URL/formats-api.jar -O $FIJI_PATH/jars/bio-formats/formats-api.jar
