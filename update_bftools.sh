#! /usr/bin/env sh

BF_VERSION="5.1.5"
BF_URL="https://downloads.openmicroscopy.org/bio-formats/$BF_VERSION/artifacts/"

BFTOOLS_PATH=$1

rm -fr $BFTOOLS_PATH/bftools 2> /dev/null
wget "$BF_URL/bftools.zip" -O $BFTOOLS_PATH/bftools.zip
unzip $BFTOOLS_PATH/bftools.zip -d $BFTOOLS_PATH
chmod +x $BFTOOLS_PATH/bftools/*
rm -f $BFTOOLS_PATH/bftools.zip
