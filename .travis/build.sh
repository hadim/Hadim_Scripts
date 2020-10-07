#!/bin/sh
curl -fsLO https://raw.githubusercontent.com/scijava/scijava-scripts/master/travis-build.sh
sh travis-build.sh $encrypted_ec357eaf7e31_key $encrypted_ec357eaf7e31_iv
