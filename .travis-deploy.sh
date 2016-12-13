#!/usr/bin/env sh
set -e

# Define some variables
export IJ_PATH="$HOME/Fiji.app"
export USER="Hadim"
export UPDATE_SITE="Hadim"
export URL="http://sites.imagej.net/$UPDATE_SITE/"
export IJ_LAUNCHER="$IJ_PATH/ImageJ-linux64"
export PATH="$IJ_PATH:$PATH"

# Install ImageJ
mkdir -p $IJ_PATH/
cd $HOME/
wget --no-check-certificate https://downloads.imagej.net/fiji/latest/fiji-linux64.zip
unzip fiji-linux64.zip
/home/travis/Fiji.app/ImageJ-linux64  --help
ls
ls $IJ_PATH/
ls -l /home/travis/Fiji.app/ImageJ-linux64

# Install the package
cd $TRAVIS_BUILD_DIR/
mvn clean install -Dimagej.app.directory=$IJ_PATH -Ddelete.other.versions=true

# Deploy the package
/home/travis/Fiji.app/ImageJ-linux64 --update edit-update-site $UPDATE_SITE $URL "webdav:$USER:$WIKI_UPLOAD_PASS" .
/home/travis/Fiji.app/ImageJ-linux64 --update upload-complete-site --force --force-shadow $UPDATE_SITE
