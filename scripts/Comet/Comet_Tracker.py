# @ImageJ ij
# @Dataset data
# @LogService log

import sys; sys.modules.clear()

import math
import os

from net.imagej.axis import Axes
from net.imagej.ops import Ops

from net.imglib2.algorithm.labeling.ConnectedComponents import StructuringElement
from net.imglib2.roi.labeling import LabelRegions

from ij2_tools import do_z_projection
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
patch_size = 10

output_dir = os.path.join(os.path.dirname(data.getSource()), "Analysis_Comets")
if not os.path.exists(output_dir):
	os.makedirs(output_dir)

## Z Projection
z_projected = do_z_projection(ij, data, save=save_images, output_dir=output_dir)
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
	
## Analyze particles
labeled_img = ij.op().run("cca", thresholded, StructuringElement.EIGHT_CONNECTED)
regions = LabelRegions(labeled_img)
region_labels = list(regions.getExistingLabels())
 
ij.log().info("%i possible comets detected" % len(region_labels))
 
for i, label in enumerate(region_labels[:77]):
	region = regions.getLabelRegion(label)
	center = region.getCenterOfMass()
	
	x = center.getDoublePosition(0)
	y = center.getDoublePosition(1)
	origin = [x, y]
	
	if center.numDimensions() >= 3:
		z = center.getDoublePosition(2)
		origin.append(z)
	else:
		origin.append(0)

	print(origin)

	# Adjust the orientation according to the particle
	orientation = 0
	patch = extract_patch(ij, masked, origin, orientation, patch_size)
	patch.setName("Patch_%0.4d" % i)

print(label)
print(origin)
ij.ui().show(patch)