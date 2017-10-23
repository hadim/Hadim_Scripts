#!/bin/sh
curl -fsLO https://raw.githubusercontent.com/scijava/scijava-scripts/master/travis-build.sh
sh travis-build.sh

if [ -v ${TRAVIS_TAG} ];
then
	echo "Upload the package to update site.";

	export UPDATE_SITE="Hadim"
	export URL="http://sites.imagej.net/$UPDATE_SITE/"

	# Paths:
	export IJ_PATH="$HOME/Fiji.app"
	export IJ_LAUNCHER="$IJ_PATH/ImageJ-linux64"
	export PATH="$IJ_PATH:$PATH"

	# Install IJ
	mkdir -p $IJ_PATH/
	cd $HOME/
	wget --no-check-certificate https://downloads.imagej.net/fiji/latest/fiji-linux64.zip
	unzip fiji-linux64.zip
	$IJ_LAUNCHER --update update-force-pristine

	# Install artifact
	cd $TRAVIS_BUILD_DIR/
	mvn clean install -Dimagej.app.directory=$IJ_PATH -Ddelete.other.versions=true

	# Deploy if release version
	VERSION=`mvn help:evaluate -Dexpression=project.version | grep -e '^[^\[]'`

	echo "Uploading to $URL..."
	$IJ_LAUNCHER --update edit-update-site $UPDATE_SITE $URL "webdav:$UPDATE_SITE:$WIKI_UPLOAD_PASS" .
	$IJ_LAUNCHER --update upload-complete-site --force-shadow "$UPDATE_SITE"

fi