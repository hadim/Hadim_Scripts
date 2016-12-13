#!/usr/bin/env sh
set -e

# Define some variables
export IJ_PATH="$HOME/ImageJ.app/"
export USER="Hadim"
export UPDATE_SITE="Hadim"
export URL="http://sites.imagej.net/$UPDATE_SITE/"
export IJ_LAUNCHER="$IJ_PATH/ImageJ-linux64"
export PATH="$IJ_PATH:$PATH"

# Install ImageJ
mkdir -p $HOME/ImageJ.app/
wget http://update.imagej.net/bootstrap.js -O $HOME/ImageJ.app/bootstrap.js


# Install the package
cd $TRAVIS_BUILD_DIR/
mvn clean install -Dimagej.app.directory=$IJ_PATH -Ddelete.other.versions=true

# Deploy the package
$IJ_LAUNCHER --update edit-update-site $UPDATE_SITE $URL "webdav:$USER:$WIKI_UPLOAD_PASS" .
$IJ_LAUNCHER --update upload-complete-site --force --force-shadow $UPDATE_SITE
