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
mkdir -p $IJ_PATH/
cd $IJ_PATH/
wget http://update.imagej.net/bootstrap.js
jrunscript bootstrap.js update-force-pristine

# Install the package
cd $TRAVIS_BUILD_DIR/
mvn clean install -Dimagej.app.directory=$IJ_PATH -Ddelete.other.versions=true

# Find IJ launcher
# determine correct launcher to launch MiniMaven and the Updater
case "$(uname -s), $(uname -m)" in
    Linux,x86_64 )
        IJ_LAUNCHER="$IJ_PATH/ImageJ-linux64" ;;
    Linux,*)
        IJ_LAUNCHER="$IJ_PATH/ImageJ-linux32" ;;
    Darwin,*)
        IJ_LAUNCHER="$IJ_PATH/Contents/MacOS/ImageJ-tiger" ;;
    MING*,*)
        IJ_LAUNCHER="$IJ_PATH/ImageJ-win32.exe" ;;
    *)
        echo "Unknown platform" >&2; exit 1 ;;
esac

echo "Found launcher : $IJ_LAUNCHER"

# Deploy the package
$IJ_LAUNCHER --update edit-update-site $UPDATE_SITE $URL "webdav:$USER:$WIKI_UPLOAD_PASS" .
$IJ_LAUNCHER --update upload-complete-site --force --force-shadow $UPDATE_SITE
