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
from ij2_tools.patch import extract_patch
from ij2_tools.mask import apply_mask


# Parameters
show_images = False
save_images = True

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
for t in range(thresholded.dimension(Axes.TIME)):

	t_dim = thresholded.dimensionIndex(Axes.TIME)
	interval_start = []
	interval_end = []
	for d in range(0, thresholded.numDimensions()):
	    if d != t_dim:
	        interval_start.append(0)
	        interval_end.append(thresholded.dimension(d) - 1)
	    else:
	        interval_start.append(t)
	        interval_end.append(t)
	         
	interval = interval_start + interval_end
	interval = Intervals.createMinMax(*interval)

	frame_masked = ij.op().run("transform.crop", thresholded.getImgPlus(), interval, True)
	frame_raw = ij.op().run("transform.crop", masked.getImgPlus(), interval, True)

	labeled_img = ij.op().run("cca", frame_masked, StructuringElement.EIGHT_CONNECTED)
	labelRegions = LabelRegions(labeled_img)

	regions_frame = [labelRegions.getLabelRegion(label) for label in labelRegions.getExistingLabels()]

	log.info("Get %i particles on frame %i" % (len(regions_frame), t))

	# Create patch for each particles
	# TODO : use Views only ?
	for i, region in enumerate(regions_frame):
		center = region.getCenterOfMass()
		
		x = center.getDoublePosition(0)
		y = center.getDoublePosition(1)
		origin = [x, y]
		
		if center.numDimensions() >= 3:
			z = center.getDoublePosition(2)
			origin.append(z)
		else:
			origin.append(0)
	
		# TODO : Adjust the orientation according to the particle
		orientation = 0
		patch = extract_patch(ij, ij.dataset().create(frame_raw), origin, orientation, patch_size)
		patch.setName("Frame_%0.4d_Patch_%0.4d" % (t, i))

		patches_list.append(patch.getImgPlus())

# Stack the patches
patches = Views.stack(patches_list)
if show_images:
	ij.ui().show("patches", patches)

if save_images:
    fname = os.path.join(output_dir, "Patches.tif")
    ij.log().info("Saving at %s" % fname)
    ij.io().save(patches, fname)

# Do the mean of all the patches = average comet
mean_patch = do_projection(ij, patches, axis_type="TIME", method="Mean", save=save_images, output_dir=output_dir)
if show_images:
	ij.ui().show("mean_patch", patches)

# Compute correlation between each patches and mean_patch

# Do threshold and scale it with k2

# Keep only patches with score below the threshold

# Save patches

# Display patches