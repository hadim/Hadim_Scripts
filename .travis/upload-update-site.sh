#!/bin/sh
set -x

if [ -n "$TRAVIS_TAG" ];
then

	echo "Travis tag detected. Start uploading the specified update site."

	if [ -z "$WIKI_UPLOAD_PASS" ];
		echo "The variable WIKI_UPLOAD_PASS is not set. You need to set it in the Travis configuration."
		exit -1
	fi

	# Configuration
	UPDATE_SITE="Hadim"
	UPLOAD_WITH_DEPENDENCIES=false
	
	# Variables
	URL="http://sites.imagej.net/$UPDATE_SITE/"
	IJ_PATH="$HOME/Fiji.app"
	IJ_LAUNCHER="$IJ_PATH/ImageJ-linux64"

	echo "Installing Fiji."
	mkdir -p $IJ_PATH/
	cd $HOME/
	wget --no-check-certificate "https://downloads.imagej.net/fiji/latest/fiji-linux64.zip"
	unzip fiji-linux64.zip

	echo "Updating Fiji."
	$IJ_LAUNCHER --update update-force-pristine

	echo "Install project to Fiji directory."
	cd $TRAVIS_BUILD_DIR/
	mvn clean install -Dimagej.app.directory=$IJ_PATH -Ddelete.other.versions=true

	echo "Gather some project informations."
	VERSION=`mvn help:evaluate -Dexpression=project.version | grep -e '^[^\[]'`
	NAME=`mvn help:evaluate -Dexpression=project.name | grep -e '^[^\[]'`

	echo "Adding $URL as an Update Site."
	$IJ_LAUNCHER --update edit-update-site $UPDATE_SITE $URL "webdav:$UPDATE_SITE:$WIKI_UPLOAD_PASS" .

	if [ "$UPLOAD_WITH_DEPENDENCIES" = false ] ; then
	    echo "Upload only \"jars/$NAME.jar\"."
	    $IJ_LAUNCHER --update upload --update-site "$UPDATE_SITE" --force-shadow "jars/$NAME.jar"
	else
		echo "Upload $NAME with its dependencies."
		$IJ_LAUNCHER --update upload-complete-site --force-shadow "$UPDATE_SITE"
	fi
fi