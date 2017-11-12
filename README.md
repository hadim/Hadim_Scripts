# Fiji Scripts
[![Build Status](https://travis-ci.org/hadim/fiji_scripts.svg?branch=master)](https://travis-ci.org/hadim/fiji_scripts)

A set of scripts and small plugins for Fiji.

Use it, hack it, share it.

## Installation

You need to add the `Hadim` update site:

- Go to `Help ▶ Update Fiji`.
- In the new window, click on `Manage update sites`.
- Scroll to find `Hadim` in the column `Name`. Click on it.
- Click `Close` and then `Apply changes`.

## The scripts

To open and run the scripts do the following:

- Click on `File ▶ New ▶ Script...`
- The Script Editor window will open.
- Scripts are available in `Templates ▶ Hadim Scripts`.

## The plugins

The package also contains very specific small plugins (often wrappers around [Image Ops](https://github.com/imagej/imagej-ops)). They can be found under `Plugins ▶ Hadim`.

- `Pseudo Flat-Field Correction` : A preprocessing step that try to remove the backgound from your image.
- `DOG Filter` : A preprocessing step that filter small and large features from your image.


## The `ij2_tools` library

The package also contains a [Python library](src/main/resources/ij2_tools) for ImageJ (not maintained anymore).

## License

Under BSD license. See [LICENSE](LICENSE).

## Authors

- Hadrien Mary <hadrien.mary@gmail.com>
