#! /usr/bin/env sh

BFTOOLS_PATH=$1

rm -fr $BFTOOLS_PATH/bftools 2> /dev/null
wget http://downloads.openmicroscopy.org/latest/bio-formats/artifacts/bftools.zip -O $BFTOOLS_PATH/bftools.zip
unzip $BFTOOLS_PATH/bftools.zip -d $BFTOOLS_PATH
chmod +x $BFTOOLS_PATH/bftools/*
rm -f $BFTOOLS_PATH/bftools.zip
