# @ImageJ ij
# @Dataset data
# @LogService log

import sys; sys.modules.clear()

import math
import os

from net.imagej.axis import Axes
from net.imagej.ops import Ops
from net.imglib2.util import Intervals

from net.imglib2.algorithm.labeling.ConnectedComponents import StructuringElement
from net.imglib2.roi.labeling import LabelRegions
from net.imglib2.view import Views

from ij2_tools import do_projection
from ij2_tools import apply_dog_filter
from ij2_tools import do_threshold
from ij2_tools import subtract_first_image
from ij2_tools.mask import apply_mask
from ij2_tools import crop
from ij2_tools.rotation import rotate_stack


# Parameters
show_images = False
save_images = False

sigma1 = 4.2
sigma2 = 1.25
threshold_method = "otsu"
k1 = 1
k2 = 1
patch_size = 10

output_dir = os.path.join(os.path.dirname(data.getSource()), "Analysis_Comets")
if not os.path.exists(output_dir):
	os.makedirs(output_dir)

## Z Projection
z_projected = do_projection(ij, data, axis_type="Z", method="Max", save=save_images, output_dir=output_dir)
if show_images:
	ij.ui().show("z_projected", z_projected)

# Subtract stack to its first image
subtracted = subtract_first_image(ij, z_projected, save=save_images, output_dir=output_dir)
if show_images:
	ij.ui().show("subtracted", subtracted)

## DOG Filtering
dog = apply_dog_filter(ij, subtracted, sigma1, sigma2, save=save_images, output_dir=output_dir)
if show_images:
	ij.ui().show("dog", dog)

## Segmentation
thresholded = do_threshold(ij, dog, threshold_method, k1, save=save_images, output_dir=output_dir)
if show_images:
	ij.ui().show("thresholded", thresholded)

## Mask DOG image with the threshold
masked = apply_mask(ij, dog, thresholded, save=save_images, output_dir=output_dir)
if show_images:
	ij.ui().show("masked", masked)
	
## Get particles on each timepoints
patches_list = []
axis = Axes.TIME
for t in range(thresholded.dimension(axis)):

	frame_masked = crop(ij, thresholded, {"TIME": [t, t]})
	frame_raw = crop(ij, masked, {"TIME": [t, t]})

	# Analyze particles
	try:
		labeled_img = ij.op().run("cca", frame_masked, StructuringElement.EIGHT_CONNECTED)
		labelRegions = LabelRegions(labeled_img)
		regions_frame = [labelRegions.getLabelRegion(label) for label in labelRegions.getExistingLabels()]
	except Exception:
		regions_frame = []

	log.info("Get %i particles on frame %i" % (len(regions_frame), t))

	# Create patch for each particles
	# TODO : use Views only ?
	for i, region in enumerate(regions_frame):
		center = region.getCenterOfMass()
		origin = [center.getDoublePosition(d) for d in range(0, frame_masked.numDimensions())]
	
		# TODO : Adjust the orientation according to the particle
		orientation = 0

		rect = [[int(round(p - (patch_size//2))), int(round((p + patch_size//2)))] for p in origin]
		intervals = {'X' : rect[0],
		             'Y' : rect[1]}
		
		patch = crop(ij, ij.dataset().create(frame_raw), intervals)
		patch = rotate_stack(ij, patch, orientation)
		patches_list.append(patch)

# Stack the patches
axis_types = [Axes.X, Axes.Y, Axes.TIME]
from net.imagej import ImgPlus

patches = Views.stack(patches_list)
print(patches)

intervals_start = [patch.min(d) for d in range(0, patch.numDimensions())]
intervals_end = [patch.max(d) for d in range(0, patch.numDimensions())]
intervals_start += [0]
intervals_end += [len(patches_list)]
finalIntervals = Intervals.createMinMax(*(intervals_start + intervals_end))
patches = ij.op().run("transform.intervalView", patches, finalIntervals)
print(patches)

#patches = ij.dataset().create(patches)
	
print(patches)

ij.ui().show("patches", patches)

if save_images:
    fname = os.path.join(output_dir, "Patches.tif")
    ij.log().info("Saving at %s" % fname)
    ij.io().save(patches, fname)

# Do the mean of all the patches = average comet
#mean_patch = do_projection(ij, patches, axis_type="X", method="Mean", save=save_images, output_dir=output_dir)
#ij.ui().show("mean_patch", mean_patch)

# Compute correlation between each patches and mean_patch

# Do threshold and scale it with k2

# Keep only patches with score below the threshold

# Save patches

# Display patches